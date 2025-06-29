# Use official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_CREATE=false

# Set working directory
WORKDIR /app

# system dependencies
RUN apt-get update --fix-missing && \
    apt-get clean && \
    apt-get install -y --no-install-recommends --allow-unauthenticated \
    build-essential \
    curl \
    git \
    libpq-dev \
    ca-certificates \
    && apt-get autoremove -y \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* /var/tmp/* \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# install packages
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-interaction --no-ansi

# Copy the rest of the code
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "chat_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]