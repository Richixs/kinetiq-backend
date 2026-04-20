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
    ├── health/             # Health Check module
    │   ├── controller.py
    │   ├── router.py
    │   └── service.py
    └── simulations/        # Kinematics simulation module
        ├── models.py       # Pydantic models (Movil, SimulationRequest)
        ├── service.py      # Manim render orchestration
        ├── controller.py   # HTTP boundary
        ├── router.py       # Route definitions
        └── scenes/
            └── mru_scene.py  # Parametrized Manim scene (MRU + MRUV)
```

## System Prerequisites

Before installing the project dependencies, make sure the following are available on your system:

### uv (Python package manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, ensure `~/.local/bin` is in your `PATH`.

### System libraries required by Manim

Manim depends on FFmpeg, LaTeX, and Cairo/Pango for rendering animations. Install them with your system package manager:

**Debian / Ubuntu:**

```bash
sudo apt install ffmpeg texlive texlive-latex-extra libcairo2-dev libpango1.0-dev
```

**Arch Linux:**

```bash
sudo pacman -S ffmpeg texlive-core cairo pango
```

**macOS (Homebrew):**

```bash
brew install ffmpeg mactex cairo pango
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

This will also install the correct Python version (3.10) automatically if it's not available.

### 3. Run the Development Server

Start the application with live-reloading enabled for development:

```bash
uv run uvicorn app.main:app --reload
```

The server starts at `http://127.0.0.1:8000` by default.

## API Documentation

Once the server is running, FastAPI automatically generates interactive documentation:

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Simulation API

### `POST /api/v1/simulations/render`

Renders a 1D kinematics simulation (MRU or MRUV) using Manim and returns an MP4 video.

**Request body:**

```json
{
  "t_max": 20,
  "moviles": [
    { "label": "A", "x_0": 0,  "v":  5, "a": 0,   "t_start": 0, "color": "#e74c3c" },
    { "label": "B", "x_0": 80, "v": -3, "a": 0.5, "t_start": 2, "color": "#3498db" }
  ]
}
```

| Field     | Type   | Description                                              |
| --------- | ------ | -------------------------------------------------------- |
| `t_max`   | float  | Total physical simulation time in seconds                |
| `label`   | string | Short name for the movil (max 4 characters)              |
| `x_0`     | float  | Initial position in meters                               |
| `v`       | float  | Initial velocity in m/s (sign determines direction)      |
| `a`       | float  | Acceleration in m/s² (default 0 = MRU, nonzero = MRUV)   |
| `t_start` | float  | Time at which the movil starts moving (default 0)        |
| `color`   | string | Hex color code (#RRGGBB)                                 |

**Response:** `video/mp4` (binary stream)

**Example with curl:**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/simulations/render \
  -H 'Content-Type: application/json' \
  -d '{"t_max":20,"moviles":[{"label":"A","x_0":0,"v":5,"t_start":0,"color":"#e74c3c"},{"label":"B","x_0":80,"v":-3,"t_start":2,"color":"#3498db"}]}' \
  -o simulation.mp4
```

**Notes:**

- Maximum 3 moviles per request.
- Render takes approximately 15–25 seconds depending on the number of moviles.
- Output is 480p at 15 fps, with a fixed animation duration of 15 seconds.
