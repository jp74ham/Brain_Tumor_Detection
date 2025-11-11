# Flask Starter (from PDF spec)

This is a minimal Flask app created from the provided tutorial.

## Quickstart

```bash
# 1) (Optional) Create and activate a virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the server
python app.py
# Visit http://127.0.0.1:5000/
```

## Structure

```
flask_app/
├── app.py
├── requirements.txt
├── templates/
│   ├── index.html
│   └── about.html
└── static/
    └── css/
        └── styles.css
```

- `app.py`: Main Flask application with two routes (`/` and `/about`).
- `templates/`: Jinja2 HTML templates.
- `static/css/styles.css`: Example stylesheet to confirm static files work.
