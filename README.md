# Personal Movie Watch List

CS 4300/5300 Fall 2026 - Team 4 group project

Django walking skeleton for CS 4300/5300 Sprint 0-3.

## Team 4

- Danny Cruz
- Katie Navarre
- Bernadette Williamson
- Samson Lemma
- Eleasia Allen

## Production Deployment

# Production URL: https://movie-watchlist-ccejbcbpdmb2frd0.northcentralus-01.azurewebsites.net/

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

7. Create a `.env` file in the project root (the same folder as `manage.py`) and add your TMDB API key (see [TMDB API key](#tmdb-api-key) below):
```text
TMDB_API_KEY=your_key_here
```
 
The file must be named exactly `.env` (a dot, then `env`, no `.txt`). Do not use quotes or spaces around the `=`. This file is listed in `.gitignore` and must never be committed.

8. Start the development server:

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

9. Run the automated tests:

```bash
python manage.py test
```

## TMDB API Key

The application uses The Movie Database (TMDB) API for movie-related functionality.

To obtain an API key, visit the TMDB website and follow its API registration instructions.

Store your key in the .env file as described in the setup instructions. Do not share or commit your key.

## AI Use
AI Tools: Pardot (Claude), ChatGPT

AI was used to create diagrams (Sprint 0-2).

AI assisted in README.md, Django app templates, configuring Django for Render deployment, and generating movie recommendations with brief descriptions (Sprint 0-3).

AI assisted with understanding and troubleshooting Django application code and Behave BDD tests, including feature scenarios and step definitions. Suggestions were reviewed and adapted to the project as needed. We also used it to give feedback when reviewing pull requests (PRs). Also AI assisted with creating HTML/CSS pages and configuring Django for Azure deployment (Sprint 1)
