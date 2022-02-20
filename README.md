# Impact of badges as a gamification element on user engagement in StackOverflow


Follow the steps below to replicate the study.
The preprocessing results are available [here](https://osf.io/z5hx4/download).

## Data retrieval
- Run the queries from [queries.sql](./queries.sql) in Google [BigQuery](https://console.cloud.google.com/bigquery).
    - Direct links to shared queries: [Badges](https://console.cloud.google.com/bigquery?sq=234931039387:9e860d3c5c5345c388034ee96d09764b), [Comments](https://console.cloud.google.com/bigquery?sq=234931039387:5411023bedc94bde8974405b42338b1b), [Posts](https://console.cloud.google.com/bigquery?sq=234931039387:a654f3356fb74f34bef898b2467b9d8a)
- Download the results by clicking on `SAVE RESULTS` and
    - for `Badges` select `CSV (local file)`
    - for `Comments` and `Posts` select `CSV (Google Drive)`, wait for the transfer to complete and download from there
- Rename the files to `badges.csv`, `comments.csv` and `posts.csv` and place them into a directory `data` next to `preprocessing.py`.

## Preprocessing
- Use `python>=3.7`
- Install required packages with `python -m pip install -r requirements.txt`
- Execute `python preprocessing.py`

## Analysis
- Create a directory `results`
- Open `analysis.Rmd` and run all chunks (t-test results and plots will be saved to `./results`)
