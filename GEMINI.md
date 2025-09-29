# GEMINI.MD: AI Collaboration Guide

This document provides essential context for AI models interacting with this project. Adhering to these guidelines will ensure consistency and maintain code quality.

## 1. Project Overview & Purpose

*   **Primary Goal:** To provide a robust and scalable backend for a web application, featuring user authentication, task management, and database persistence.
*   **Business Domain:** General-purpose web application backend.

## 2. Core Technologies & Stack

*   **Languages:** Python 3.11
*   **Frameworks & Runtimes:** FastAPI (0.103.2), Uvicorn (0.23.2), Celery (5.5.3), Redis (6), PostgreSQL (13)
*   **Databases:** PostgreSQL for primary data storage, Redis for Celery message broker.
*   **Key Libraries/Dependencies:**
    *   `fastapi`: Web framework.
    *   `uvicorn`: ASGI server.
    *   `sqlalchemy`: ORM for database interaction.
    *   `alembic`: Database migrations.
    *   `psycopg2-binary`: PostgreSQL adapter.
    *   `celery`: Asynchronous task queue.
    *   `redis`: Redis client and Celery broker.
    *   `pydantic-settings`: Settings management.
    *   `python-dotenv`: Loading environment variables.
    *   `python-jose[cryptography]`: JWT handling.
    *   `passlib[bcrypt]`: Password hashing.
    *   `bcrypt`: Bcrypt hashing algorithm.
    *   `python-multipart`: Handling form data.
    *   `tenacity`: Retry strategies.
*   **Package Manager(s):** Poetry

## 3. Architectural Patterns

*   **Overall Architecture:** Monolithic Application (API, database, and task queue are part of a single deployment unit, though containerized separately).
*   **Directory Structure Philosophy:**
    *   `/app`: Contains all primary source code for the FastAPI application, including models, schemas, security, and main application logic.
    *   `/migrations`: Holds Alembic database migration scripts.
    *   `/create_superuser.py`: A utility script for creating an initial administrator user.
    *   `/Dockerfile`: Defines the Docker image for the FastAPI application and Celery worker.
    *   `/docker-compose.yml`: Orchestrates the multi-service Docker environment (API, DB, Redis, Celery worker).
    *   `/.env`: Stores environment variables for local development.
    *   `/pyproject.toml`: Poetry project configuration and dependency management.

## 4. Coding Conventions & Style Guide

*   **Formatting:** Implicitly follows Python's PEP 8 guidelines. No explicit linter configuration yet.
*   **Naming Conventions:**
    *   `variables`, `functions`: snake_case (`my_variable`, `my_function`)
    *   `classes`, `components`: PascalCase (`MyClass`, `MyComponent`)
    *   `files`: snake_case (`my_module.py`)
*   **API Design:** RESTful principles. Uses standard HTTP verbs (GET, POST). JSON for request/response bodies. OAuth2 for authentication.
*   **Error Handling:** Uses FastAPI's `HTTPException` for API errors. Database operations include `try...except` blocks for rollback.

## 5. Key Files & Entrypoints

*   **Main Entrypoint(s):**
    *   `app/main.py`: The FastAPI application entry point.
    *   `app/celery_app.py`: Celery application instance.
*   **Configuration:**
    *   `.env`: Environment variables for local development.
    *   `app/config.py`: Pydantic-based application settings.
    *   `alembic.ini`: Alembic migration tool configuration.
*   **CI/CD Pipeline:** Not yet implemented.

## 6. Development & Testing Workflow

*   **Local Development Environment:**
    1.  Ensure Docker and Docker Compose are installed.
    2.  Run `docker compose up -d --build` to build images and start all services.
    3.  Access the FastAPI application at `http://localhost:8001` (or your machine's IP).
    4.  Access API documentation at `http://localhost:8001/docs`.
    5.  Create a superuser: `docker compose exec api poetry run python create_superuser.py` (prompts for details).
*   **Testing:** No explicit testing framework or tests have been set up yet.
*   **CI/CD Process:** Not yet implemented.

## 7. Specific Instructions for AI Collaboration

*   **Contribution Guidelines:**
    *   All new database schema changes must be managed via Alembic migrations. Generate new migrations using `docker compose exec api alembic revision --autogenerate -m "Your message"`.
    *   Ensure models are imported in `app/main.py` and `migrations/env.py` for Alembic to detect changes.
*   **Infrastructure (IaC):** Changes to `Dockerfile` or `docker-compose.yml` directly affect the deployment environment. Always rebuild images (`docker compose build`) after modifying these files or `pyproject.toml`.
*   **Security:**
    *   Be mindful of security best practices. Do not hardcode secrets or keys. Use `app/config.py` for settings.
    *   Authentication logic is handled in `app/security.py` and `app/main.py`. Ensure any modifications adhere to secure JWT and password handling principles.
*   **Dependencies:** When adding new Python dependencies, update `pyproject.toml` and then rebuild Docker images (`docker compose build`).
*   **Commit Messages:** No specific convention enforced yet. Use descriptive messages.

---

**Current Status:**

The project is set up with a functional FastAPI application, PostgreSQL database, Celery task queue, and Redis broker. User authentication with JWT and refresh tokens is implemented, including role-based access control and a superuser creation script. All core services are containerized and orchestrated with Docker Compose. The database schema includes a `users` table with `first_name`, `last_name`, `email`, `hashed_password`, `role`, `created_at`, and `updated_at` fields. All known issues have been resolved.

**Next Steps for User:**

*   Define additional SQLAlchemy models in `app/models.py`.
*   Create corresponding Pydantic schemas in `app/schemas.py`.
*   Implement new API endpoints in `app/main.py` to expose application functionality.
*   Add Celery tasks in `app/tasks.py` for background processing.
*   Consider implementing unit and integration tests.

---
