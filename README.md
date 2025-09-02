# test_task_el_med
[![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/yamata-lab/test_task_el_med)

This repository contains a workload migration management system built with Django and Celery. It provides a RESTful API to manage the migration of server workloads (including specific storage volumes) to a target cloud environment. The migration process is handled asynchronously using background tasks.

The application is fully containerized with Docker, allowing for a consistent development and deployment environment.

## Features

*   **REST API**: Exposes endpoints for managing `Workloads`, `Credentials`, `Migrations`, and `MigrationTargets`.
*   **Asynchronous Migrations**: Utilizes Celery with a Redis broker to run migration tasks in the background without blocking API requests.
*   **Secure Credential Storage**: Passwords for credentials are encrypted at the database level using `django-encrypted-model-fields`.
*   **Business Logic Enforcement**:
    *   A workload's IP address is immutable after creation.
    *   A migration job cannot be started unless the system volume (`C:\`) is selected.
    *   Each workload must have a unique IP address.
*   **Containerized Environment**: Packaged with Docker and Docker Compose for easy setup and deployment of the entire service stack (Django app, PostgreSQL, Redis, Celery worker).
*   **API Test Harness**: Includes an end-to-end Python script (`api_test_harness.py`) to verify the entire migration workflow via the API.
*   **Automated Testing & CI**: Configured with pre-commit hooks for code quality and a GitLab CI pipeline for automated testing.

## Technology Stack

*   **Backend**: Python, Django, Django REST Framework
*   **Database**: PostgreSQL
*   **Task Queue**: Celery
*   **Message Broker**: Redis
*   **Containerization**: Docker, Docker Compose
*   **Code Quality**: Black, Flake8, isort
*   **API Authentication**: JWT (JSON Web Tokens)

## Getting Started

### Prerequisites

*   Git
*   Docker
*   Docker Compose

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yamata-lab/test_task_el_med.git
    cd test_task_el_med
    ```

2.  **Configure Environment Variables:**
    Copy the example environment file and update it with your settings.
    ```bash
    cp .env.example .env
    ```
    You must generate a secret key for field encryption. You can do this with the following command and paste the output into the `FIELD_ENCRYPTION_KEY` variable in your `.env` file.
    ```bash
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ```

3.  **Build and Run the Services:**
    Use Docker Compose to build the images and start all the services.
    ```bash
    docker-compose up --build -d
    ```
    This command will start the following containers:
    *   `migration_app`: The Django web server.
    *   `migration_db`: The PostgreSQL database.
    *   `migration_redis`: The Redis message broker.
    *   `migration_celery_worker`: The Celery worker to process migration tasks.

4.  **Create a Superuser:**
    To interact with the API, you need a user account. Create a superuser using the Django management command.
    ```bash
    docker-compose exec app python manage.py createsuperuser
    ```
    Follow the prompts to set a username, email, and password.

## API Usage

The API is served at `http://127.0.0.1:8000/api/v1/`. API documentation is available via Swagger UI:

*   **Swagger UI**: `http://127.0.0.1:8000/api/v1/schema/swagger-ui/`
*   **Redoc**: `http://127.0.0.1:8000/api/v1/schema/redoc/`

### Authentication

The API uses JWT for authentication. To get an access token, send a POST request with your superuser credentials to the token endpoint.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/token/ \
-H "Content-Type: application/json" \
-d '{
    "username": "your-username",
    "password": "your-password"
}'
```

The response will contain an `access` and `refresh` token. Include the access token in the `Authorization` header for all subsequent requests.

```
Authorization: Bearer <your_access_token>
```

### Running the API Test Harness

An end-to-end test script is provided to simulate a full migration workflow. Ensure the Docker services are running before executing the script.

```bash
python api_test_harness.py
```

The script will prompt you for your superuser credentials and then proceed to:
1.  Create source and target credentials.
2.  Create source and target workloads.
3.  Define a migration target.
4.  Create and initiate a migration.
5.  Poll the migration status until it completes.

## Running Tests

To run the project's unit tests, execute the following command:

```bash
docker-compose exec app python manage.py test
