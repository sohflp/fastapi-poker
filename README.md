# Poker Club

How to install dependencies:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

How to run locally:

```bash
uvicorn app.main:app --reload
```

Open:

```
http://127.0.0.1:8000
```

Pages available:

- `/` – Main dashboard
- `/timer` – Poker timer
- `/leaderboard` – Leaderboard
- `/f1leaderboard` – F1 leaderboard
- `/finance` - Finance dashboard
- `/performance` – Player performance over time
- `/admin` – Admin page