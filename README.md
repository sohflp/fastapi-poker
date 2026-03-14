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

- `/` – main dashboard
- `/timer` – poker timer
- `/stats` – stats page
- `/admin` – admin page