# TenderHub API

Welcome to TenderHub API. This repository is a backend for a TenderHub website


## Prerequisites

- [Python](https://www.python.org/) (v3.12.9 or higher)
- [pip](https://pip.pypa.io/en/stable/)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/tenderhubapi.git
    cd tenderhubapi
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv .env
    source .env/bin/activate  # On Windows use `.env\Scripts\activate`
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    Create a `.env` file in the root directory and configure the required variables:
    ```
    SECRET_KEY=your_django_secret_key
    DEBUG=True
    DATABASE_URL=your_database_connection_string
    ```

5. Apply database migrations:
    ```bash
    python manage.py migrate
    ```

6. Start the development server:
    ```bash
    python manage.py runserver
    ```

## Contributing

Contributions are not accepted as this is a personal project.

## License

This project is licensed under the [MIT License](LICENSE).