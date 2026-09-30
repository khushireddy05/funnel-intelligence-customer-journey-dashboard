# Streamlit Deployment

## Run locally

First create the processed data:

```bash
python3 -m src.pipeline
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub. Do not remove `app.py`, `requirements.txt`, `.streamlit/config.toml`, or `data/processed/`.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
3. Select **Create app**, choose the repository and branch, and enter `app.py` as the entry-point file.
4. Select **Deploy** and share the generated `streamlit.app` URL.

## Data refresh

The app reads the prepared CSVs under `data/processed/`. To update dashboard data, run `python3 -m src.pipeline`, commit the regenerated processed CSVs, and push the change. Streamlit Cloud redeploys the app from the new GitHub commit.

All data in this project is synthetic. Do not upload confidential customer data to a public deployment.
