SHELL := /bin/bash

.PHONY: test build build-amd64 tf-fmt tf-validate tf-init clean ci

test:
	python -m pytest -q

build:
	bash scripts/build_lambda_zip.sh

# Build Lambda package in a linux/amd64 container to avoid macOS/arm64 wheel issues (e.g., pydantic_core)
build-amd64:
	docker buildx build --platform linux/amd64 -t llm-chat-api-ci-amd64 --load .
	docker run --rm --platform linux/amd64 -v "$$PWD:/app" -w /app llm-chat-api-ci-amd64 make build

tf-fmt:
	terraform -chdir=infra fmt -check -recursive

tf-init:
	terraform -chdir=infra init -backend=false

tf-validate: tf-fmt tf-init
	terraform -chdir=infra validate

clean:
	rm -rf build dist

# Optional: one command to run the CI checks locally (in current env)
ci: test build tf-validate