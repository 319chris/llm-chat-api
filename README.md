# llm-chat-api (Phase 1)

A minimal Cloud LLM Chat API on AWS:
- API Gateway HTTP API + Lambda (Python 3.11)
- POST /chat
- OpenAI-compatible Chat Completions provider (default OpenAI)
- Secrets Manager for API key (no plaintext in repo)
- Structured logging (AWS Lambda Powertools)
- Terraform deploy (ap-southeast-2 by default)
- CI (Docker): pytest + build + terraform fmt/validate (no apply)

## Quick start (local, Docker)
```bash
docker build -t llm-chat-api-ci .
docker run --rm -v "$PWD:/app" -w /app llm-chat-api-ci make test
docker run --rm -v "$PWD:/app" -w /app llm-chat-api-ci make build
docker run --rm -v "$PWD:/app" -w /app llm-chat-api-ci make tf-validate