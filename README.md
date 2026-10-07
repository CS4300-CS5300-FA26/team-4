# Personal Movie Watch List

CS 4300/5300 Fall 2026 - Team 4 group project

Django walking skeleton for CS 4300/5300 Sprint 0-3.

## Team 4

- Danny Cruz
- Katie Navarre
- Bernadette Williamson
- Samson Lemma
- Eleasia Allen

## How to run locally

1. Clone the repository.

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment.

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

4. Install requirements:

```bash
pip install -r requirements.txt
```

5. Apply database migrations:

```bash
python manage.py migrate
```

6. Load the sample movie data:

```bash
python manage.py loaddata movies/fixtures/movies.json
```

7. Start the development server:

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

8. Run the automated tests:

```bash
python manage.py test
```

## AI Use

AI was used to create diagrams (Sprint 0-2).

AI assisted in README.md, Django app templates, configuring Django for Render deployment, and generating movie recommendations with brief descriptions (Sprint 0-3).