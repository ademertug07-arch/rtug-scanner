# UW5 v5 Docker Sandbox — isolated execution environment
# Build: docker build -t uw5-sandbox -f Dockerfile .
# Usage: docker run --rm -v ${UW5_ROOT}:/workspace uw5-sandbox powershell -Command "..."

FROM mcr.microsoft.com/powershell:lts-7.4-ubuntu-22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/uw5-venv && \
    /opt/uw5-venv/bin/pip install --no-cache-dir numpy scikit-learn

ENV PATH="/opt/uw5-venv/bin:${PATH}"
ENV UW5_SANDBOX=1

WORKDIR /workspace

ENTRYPOINT ["pwsh", "-NoLogo", "-NoProfile", "-Command"]
