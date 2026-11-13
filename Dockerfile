# Production Container for OpenTTD Autonomous Freight Planning & Control
# Uses official Astral UV image with Python 3.14 on Debian Bookworm Slim
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS runtime

# Prevent Python from buffering stdout/stderr and writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /opt/softdev2

# Create non-root execution user (Principle of Least Privilege)
RUN groupadd --system appgroup && useradd --system --gid appgroup --create-home appuser

# Copy dependency authority files first to leverage Docker layer caching
COPY pyproject.toml uv.lock README.md alembic.ini ./

# Install locked production dependencies deterministically without dev tools
RUN uv sync --locked --no-dev --no-install-project

# Copy application source, examples, migrations, and authority manifests
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY examples/ ./examples/
COPY docs/authority/ ./docs/authority/

# Install the application package non-editably, create runtime dir, and transfer ownership
RUN uv sync --locked --no-dev --no-editable && \
    mkdir -p /opt/softdev2/artifacts/demos && \
    chown -R appuser:appgroup /opt/softdev2

USER appuser

# Default entrypoint runs offline deterministic planner; native runs remain user-gated
ENTRYPOINT [".venv/bin/python", "-m", "app.openttd_demo"]
CMD ["plan"]
