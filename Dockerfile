FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

WORKDIR /gello

# Set environment variables first (less likely to change)
ENV PYTHONPATH=/gello/src

# Group apt updates and installs together
RUN apt update && apt install -y \
    libhidapi-dev \
    python3-pip \
    android-tools-adb \
    libegl1-mesa-dev && \
    rm -rf /var/lib/apt/lists/* 


# Python alias setup
RUN echo "alias python=python3" >> ~/.bashrc

# Install Python dependencies
COPY pyproject.toml uv.lock README.md LICENSE /gello/
RUN pip install uv && uv sync --frozen --no-dev --no-install-project
COPY src /gello/src
RUN uv sync --frozen --no-dev
