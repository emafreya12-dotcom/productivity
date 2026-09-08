# Luma

A small Streamlit productivity workspace combining quick notes, tasks, and a calm Today view.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app stores account and workspace data in `.luma_data.json` by default. Set `LUMA_DATA_PATH` to choose another location. Passwords are stored as PBKDF2-SHA256 hashes; this local JSON store is intended for an MVP, not production multi-user hosting.

## Deploy to Streamlit Community Cloud

Push this repository to GitHub, then create a new app at [share.streamlit.io](https://share.streamlit.io) with `app.py` as the entrypoint and `requirements.txt` as the dependency file. For a real production deployment, replace the JSON store with a hosted database and add account recovery and email verification.