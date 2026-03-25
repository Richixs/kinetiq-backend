# Kinetiq Server

A modular, scalable FastAPI application using `uv` as the package and project manager.

## Project Structure

The codebase is organized following a domain-driven design approach to ensure modularity and scalability. Each feature or domain resides in its own module.

```text
app/
├── main.py                 # Application entry point & lifespan events
├── core/                   # Global components
│   └── config.py           # Environment variables and settings management
├── api/
│   └── v1/
│       └── router.py       # Main API V1 router that aggregates all sub-routers
└── modules/                # Domain-specific features
    └── health/             # Example module (Health Check)
        ├── controller.py   # Request handling and dependency injection
        ├── router.py       # Route definitions for the module
        └── service.py      # Core business logic
```

## Getting Started

This project relies on [uv](https://github.com/astral-sh/uv), an extremely fast Python package installer and resolver.

### 1. Configure the Environment

Copy the example environment file to create your local `.env` file:

```bash
cp .env.example .env
```

You can adjust the values inside `.env` to match your local setup (e.g., `ENVIRONMENT`, `DEBUG`).

### 2. Install Dependencies

```bash
uv sync
```

### 3. Run the Development Server

Start the application with live-reloading enabled for development:

```bash
uv run uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, FastAPI automatically generates interactive documentation:

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
