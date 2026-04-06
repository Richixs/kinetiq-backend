# syntax=docker/dockerfile:1.7

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
	UV_LINK_MODE=copy \
	UV_PYTHON_DOWNLOADS=never

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	pkg-config \
	libcairo2-dev \
	libpango1.0-dev \
	libgl1-mesa-dev \
	libx11-dev \
	ffmpeg \
	&& rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
	uv sync --frozen --no-dev --no-install-project

COPY app ./app
RUN --mount=type=cache,target=/root/.cache/uv \
	uv sync --frozen --no-dev


FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PATH="/app/.venv/bin:${PATH}"

RUN groupadd --system app && useradd --system --gid app --create-home app

RUN apt-get update && apt-get install -y --no-install-recommends \
	libcairo2 \
	libpango-1.0-0 \
	libgl1 \
	libx11-6 \
	ffmpeg \
	texlive-latex-base \
	texlive-fonts-recommended \
	dvisvgm \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
	CMD python -c "import sys,urllib.request;sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health/', timeout=3).status == 200 else 1)"

USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips=*"]
