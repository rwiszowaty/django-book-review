# Django Book Review

## About the project

Django Book Review is a web application for browsing books and sharing book reviews.

The project is built as a portfolio application demonstrating practical experience with Django, Django REST Framework, PostgreSQL, Docker, automated testing, and CI.

Users can browse books, view book details, create and manage reviews, and access public user profiles.

## Features

- User registration and email verification
- Email-based authentication
- Password reset by email
- Public user profiles
- Book browsing and book details
- Book search, filtering, sorting, and pagination
- Book reviews with ratings from 1 to 5
- One review per user per book
- REST API for books and reviews
- OpenAPI schema and Swagger documentation
- Automated tests with pytest
- Dockerized development environment
- PostgreSQL database
- GitHub Actions CI

## Tech stack

- Python 3.13
- Django 6.1
- Django REST Framework
- PostgreSQL 17
- django-allauth
- drf-spectacular
- pytest and pytest-django
- Docker and Docker Compose
- Git and GitHub
- GitHub Actions
- Bootstrap 5

## API

The project provides a REST API for accessing books and their reviews.

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/books/` | List books |
| GET | `/api/books/<slug>/` | Retrieve a book |
| GET | `/api/books/<slug>/reviews/` | List reviews for a book |
| POST | `/api/books/<slug>/reviews/` | Create a review |

### API documentation

Interactive Swagger documentation is available at:

`/api/docs/`

The OpenAPI schema is available at:

`/api/schema/`

## Testing

The project uses pytest and pytest-django for automated testing.

The test suite covers:

- User authentication and registration
- Email verification
- Password reset
- Book views and API endpoints
- Review creation and validation
- User profiles
- API permissions
- Model behavior

Run the full test suite with:

```bash
docker compose exec web pytest -q
```

Current test suite: 215 tests passing.

## Installation

### Requirements

- Docker
- Docker Compose

### Setup

Clone the repository and navigate to the project directory:

```bash
git clone <your-repository-url>
cd django-book-review
```

Create a .env file based on .env.example and set the required environment variables.

Build and start the containers:
```bash
docker compose up --build
```

Apply database migrations:
```bash
docker compose exec web python manage.py migrate
```

The application will be available at:

http://localhost:8000/

## Docker

The application runs in Docker containers using Docker Compose.

The development environment consists of:

- Django application
- PostgreSQL database

Start the development environment with:

```bash
docker compose up
```

Stop the containers with:
```bash
docker compose down
```

## CI

The project uses GitHub Actions for continuous integration.

The CI pipeline:

- Sets up Python 3.13
- Starts a PostgreSQL service
- Installs project dependencies
- Runs Flake8
- Runs the pytest test suite

The workflow is triggered on pushes and pull requests to the main branch.

## Project structure

```text
django-book-review/
├── .github/
│   └── workflows/
├── books/
│   ├── api/
│   ├── migrations/
│   ├── tests/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── users/
│   ├── migrations/
│   ├── tests/
│   ├── admin.py
│   ├── forms.py
│   ├── managers.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── config/
├── templates/
├── static/
├── media/
├── docker-compose.yml
├── Dockerfile
├── manage.py
└── requirements.txt
```
