# TenderHub API

Welcome to TenderHub API. This repository is a backend for TenderHub website


## Prerequisites

- Python (v3.12.9 or higher)
- PostgreSQL (v12 or higher)
- pip

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Rigelyon/tenderhubapi.git
    cd tenderhubapi
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv .venv

    # Linux
    source .env/bin/activate

    # Windows
    .venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up PostgreSQL:
    ```bash
    # Create database
    psql -U postgres
    CREATE DATABASE tenderhub;
    ```

5. Configure environment variables:
    ```bash
    cp .env.example .env
    ```
    Update the `.env` file with your configuration:
    ```
    SECRET_KEY='your_django_secret_key'
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1,localhost

    # Database settings
    DB_NAME=tenderhub
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=localhost
    DB_PORT=5432

    # CORS settings
    CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
    ```

6. Apply database migrations:
    ```bash
    python manage.py migrate
    ```

7. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```

8. Start the development server:
    ```bash
    python manage.py runserver
    ```

## Contributing

Contributions are not accepted as this is a personal project.

## License

This project is licensed under the [MIT License](LICENSE).