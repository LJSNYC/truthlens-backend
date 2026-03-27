# TruthLens Backend

Python/Flask backend for AI-generated image and deepfake detection.

## Setup

**1. Create and activate a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the server**

```bash
python app.py
```

The server starts at `http://localhost:5000`.

**4. Verify it's running**

```bash
curl http://localhost:5000/health
# {"status": "ok"}
```

## Project Structure

```
backend/
├── app.py          — Flask app and routes
├── detector.py     — Detection logic (stub)
└── requirements.txt
```

## Deactivate the virtualenv

```bash
deactivate
```
