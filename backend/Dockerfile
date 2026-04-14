FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /uvx /bin/


WORKDIR /app

# Bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy lock file and pyproject for dependency caching
COPY uv.lock pyproject.toml ./

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Create log directory
RUN mkdir -p /var/log/lolapp

# Place executeables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

USER nonroot

# Expose port
EXPOSE 8000

# Default command (will be overridden in override/prod compose files)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
