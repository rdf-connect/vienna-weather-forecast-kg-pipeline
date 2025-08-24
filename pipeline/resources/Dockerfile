# Base: Alpine with Python 3.13
FROM python:3.13-slim-trixie AS base

# Install dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    curl \
    wget \
    unzip \
    git \
    openjdk-21-jdk-headless \
    nodejs \
    npm \
    make \
    g++ \
    libc-dev

# Install Gradle 8.10.2
ARG GRADLE_VERSION=8.10.2
RUN wget https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip -P /tmp \
    && unzip /tmp/gradle-${GRADLE_VERSION}-bin.zip -d /opt \
    && ln -s /opt/gradle-${GRADLE_VERSION}/bin/gradle /usr/bin/gradle \
    && rm -rf /tmp/*.zip

# Install Hatch and uv (Python tools)
RUN pip install --no-cache-dir hatch uv

# Set working directory to /workspace (to mount host files here)
WORKDIR /workspace

# Default entrypoint: keep bash so we can run npm, gradle, hatch, uv, etc.
CMD ["/bin/bash"]
