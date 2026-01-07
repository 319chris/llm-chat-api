FROM python:3.11-slim

ARG TERRAFORM_VERSION=1.6.6

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip zip ca-certificates bash make \
 && rm -rf /var/lib/apt/lists/*

# Install Terraform (>= 1.6)
RUN curl -fsSL -o /tmp/terraform.zip "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" \
 && unzip -o /tmp/terraform.zip -d /usr/local/bin \
 && rm -f /tmp/terraform.zip \
 && terraform version

# Install Python deps (dev + runtime)
COPY requirements.txt requirements-dev.txt /tmp/
RUN python -m pip install --upgrade pip \
 && pip install -r /tmp/requirements.txt -r /tmp/requirements-dev.txt

# No source copy here (CI runs with volume mount to keep parity with local)
CMD ["bash"]