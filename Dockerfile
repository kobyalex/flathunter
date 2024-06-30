FROM arm32v7/python:3.11-slim-bullseye

# Setting environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Use a single RUN command for apt-get to reduce the number of layers
RUN apt-get update && apt-get install -y \
    chromium \
    git \
    build-essential \
    pkg-config \
    zlib1g-dev \
    curl \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Rust using the official installer script
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add Rust to PATH (this might vary depending on the base image)
ENV PATH="/root/.cargo/bin:${PATH}"

# Confirm installation by printing Rust version
RUN rustc --version

# Upgrade pip and install pipenv in one RUN command
RUN pip install --upgrade pip && pip install pipenv

# Set the working directory
WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
# Generate requirements.txt and install dependencies from there
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .