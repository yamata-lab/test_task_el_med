# Stage 1: A common base for both builder and final stages.
# Using a specific version tag ensures reproducible builds.
FROM python:3.10-slim-bullseye AS base

# Prevent Python from writing .pyc files and force unbuffered output for cleaner logs.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app


# Stage 2: The builder stage.
# This stage installs all dependencies, including build-time tools that are not
# needed in the final production image.
FROM base AS builder

# Update system packages and install build dependencies for Python packages (e.g., psycopg2).
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc && \
    # Clean up the apt cache to keep the layer size small.
    rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to leverage Docker's layer caching.
# This layer is only rebuilt if requirements.txt changes.
COPY requirements.txt /app/

# Install Python dependencies.
RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# Stage 3: The final production-ready image.
# This stage is optimized for size and security.
FROM base AS final

# It's good practice to also apply security patches to the final base image.
RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the application, following the principle of least privilege.
RUN useradd -m -d /home/appuser -s /bin/bash appuser
USER appuser

# Set user-specific environment variables and working directory.
ENV HOME=/home/appuser
ENV PATH=$HOME/.local/bin:$PATH
WORKDIR $HOME/app

# Copy the pre-installed Python packages from the builder stage.
COPY --from=builder /home/appuser/.local /home/appuser/.local

# Copy the application source code and the entrypoint script.
COPY ./entrypoint.sh .
COPY . .

# Grant execution permissions to the entrypoint script.
RUN chmod +x ./entrypoint.sh

# Specify the entrypoint script to run when the container starts.
ENTRYPOINT ["./entrypoint.sh"]
