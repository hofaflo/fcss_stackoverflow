# %% Imports & configuration
import warnings

import numpy as np
import pandas as pd
from tqdm import tqdm

timeunit = 'W'
maxtime = 52
data_dir = './data'
badge_names = ('Mortarboard', 'Epic', 'Legendary')
outfile = f'{data_dir}/activity_preprocessed.csv'

def z_standardize(x: np.ndarray) -> np.ndarray:
    return (x - np.nanmean(x)) / np.nanstd(x)


# %% Parse dataframes
badges = pd.read_csv(f'{data_dir}/badges.csv', index_col='name')
print('Loaded badges')

comments = pd.read_csv(f'{data_dir}/comments.csv', index_col='user_id')
print('Loaded comments')

posts = pd.read_csv(f'{data_dir}/posts.csv', index_col='owner_user_id')
print('Loaded posts')

# The timestamps contain timezone information, but it's always UTC.
# Truncating the string to remove ` UTC` speeds up conversion time.
badges['date'] = pd.to_datetime(badges.date.str.slice(stop=-4))
comments['creation_date'] = pd.to_datetime(comments.creation_date.str.slice(stop=-4))
posts['creation_date'] = pd.to_datetime(posts.creation_date.str.slice(stop=-4))

print('Converted datetimes')

# Split posts into questions and answers
questions = posts.loc[posts.post_type_id == 1, ['creation_date']]
answers = posts.loc[posts.post_type_id == 2, ['creation_date']]
del posts

questions.index.rename('user_id', inplace=True)
answers.index.rename('user_id', inplace=True)

# %%
# BigQuery's comments table was updated rather recently, but posts are from 2016.
# Activities outside of the range where all activity types are present will be ignored.
first_date = max([
    answers.creation_date.min(),
    comments.creation_date.min(),
    questions.creation_date.min(),
])

last_date = min([
    answers.creation_date.max(),
    comments.creation_date.max(),
    questions.creation_date.max(),
])

badges = badges[(first_date < badges['date']) & (badges['date'] < last_date)]
answers = answers[
    (first_date < answers['creation_date'])
    & (answers['creation_date'] < last_date)
    & (answers.index.isin(badges['user_id']))
]
comments = comments[
    (first_date < comments['creation_date'])
    & (comments['creation_date'] < last_date)
    & (comments.index.isin(badges['user_id']))
]
questions = questions[
    (first_date < questions['creation_date'])
    & (questions['creation_date'] < last_date)
    & (questions.index.isin(badges['user_id']))
]

activity_dfs = {
    'questions': questions,
    'answers': answers,
    'comments': comments
}

# %% Count user activities
badges_by_user = badges.reset_index().set_index('user_id')
timestep = np.timedelta64(1, timeunit)
time_offsets_ints = np.arange(-maxtime, maxtime)
time_offsets = time_offsets_ints[np.newaxis, :] * timestep

dfs = []

for activity_name, activity_df in activity_dfs.items():
    for user_id, user_act in tqdm(
        activity_df.groupby('user_id'),
        desc=f'{activity_name} - all badges - active',
        total=activity_df.index.nunique(),
    ):
        for _, (badge_name, badge_date) in badges_by_user.loc[[user_id]].iterrows():
            start_dates = badge_date + time_offsets
            end_dates = start_dates + timestep
            user_act_times = user_act.creation_date.values[:, np.newaxis]
            user_act_mask = (start_dates < user_act_times) & (user_act_times <= end_dates)

            invalid_mask = ((start_dates < first_date) | (end_dates > last_date)).ravel()

            # storing counts as float allows to use np.nan to mark invalid samples
            user_act_counts = user_act_mask.sum(0).astype(float)
            user_act_counts[invalid_mask] = np.nan

            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                user_act_counts_standardized = z_standardize(user_act_counts)

            dfs.append(pd.DataFrame({
                'user_id': user_id,
                'activity_count': user_act_counts,
                'activity_count_standardized': user_act_counts_standardized,
                'activity_name': activity_name[0],
                'badge_name': badge_name[0].lower(),
                'week_offset': time_offsets_ints,
            }))

    # for users who did not post a question/answer/comment, but received a
    # badge, set activity counts in valid range to 0
    for badge_name, badge_df in badges.groupby('name'):
        inactive_mask = ~badge_df['user_id'].isin(activity_df.index)
        for _, (user_id, badge_date) in tqdm(
                badge_df.loc[inactive_mask].iterrows(),
                desc=f'{activity_name} - {badge_name} - inactive',
                total=inactive_mask.sum(),
            ):
            start_dates = badge_date + time_offsets
            end_dates = start_dates + timestep
            invalid_mask = ((start_dates < first_date) | (end_dates > last_date)).ravel()
            user_act_counts = np.zeros_like(time_offsets.ravel(), dtype=float)
            user_act_counts[invalid_mask] = np.nan

            dfs.append(pd.DataFrame({
                'user_id': user_id,
                'activity_count': user_act_counts,
                'activity_count_standardized': user_act_counts,
                'activity_name': activity_name[0],
                'badge_name': badge_name[0].lower(),
                'week_offset': time_offsets_ints,
            }))

df_all = pd.concat(dfs).astype({'user_id': int})
df_all.to_csv(outfile, index=False)
print(f'Exported to {outfile}')
