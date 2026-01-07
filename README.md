# llm-chat-api (Phase 1)

A minimal, production-style LLM Chat API on AWS (API Gateway HTTP API + Lambda, Python 3.11).
Phase 1 focuses on a clean, reproducible deployment pipeline with strong security defaults.
Phase 2 will add RAG / tool calling / integrations.

## What it does

- **Endpoint:** `POST /chat`
- **Input:** `{ messages: [{role, content}], temperature, max_tokens }`
- **Output:** `{ id, model, content, usage, latency_ms, request_id }`
- **Provider:** OpenAI-compatible Chat Completions (default OpenAI)
- **Secrets:** OpenAI API key stored in **AWS Secrets Manager** (no plaintext in repo)
- **Observability:** JSON structured logs + request_id + latency + token usage
- **IaC:** Terraform deploys Lambda, HTTP API, IAM, logs, and outputs the invoke URL
- **CI (Docker):** `pytest` + `build` + `terraform fmt/validate` (no apply/destroy)

## Architecture (Phase 1)

Client
→ API Gateway (HTTP API, payload v2.0)
→ Lambda (`src/handler.py`)
→ Secrets Manager (read API key)
→ OpenAI API (chat completions)
→ Response back to client

## Repo layout

- `src/handler.py` – Lambda entrypoint, request parsing + validation + response shaping
- `src/models.py` – Pydantic request validation models
- `src/llm/` – provider abstraction (OpenAI implementation + factory)
- `src/secrets.py` – Secrets Manager read with in-memory caching
- `infra/` – Terraform (Lambda, HTTP API, IAM least privilege, logs, outputs)
- `tests/` – pytest coverage for validation, handler response shape, provider mock
- `scripts/build_lambda_zip.sh` – builds `dist/lambda.zip` deployment artifact
- `.github/workflows/ci.yml` – CI pipeline definition

## Quick start (local, Docker)

```bash
docker build -t llm-chat-api-ci .
docker run --rm -v "$PWD:/app" -w /app llm-chat-api-ci make test
docker run --rm -v "$PWD:/app" -w /app llm-chat-api-ci make build
docker run --rm -v "$PWD:/app" -w /app llm-chat-api-ci make tf-validate
```

## Build for AWS Lambda (recommended)

If you’re on macOS (especially Apple Silicon), building the Lambda zip locally can produce
platform-specific wheels (e.g. pydantic_core) that fail on Lambda’s Linux runtime.
Use the amd64 build target to generate a Lambda-compatible artifact:

```bash
make build-amd64
```

## Deploy to AWS (manual)

Region defaults to ap-southeast-2 (Sydney).
CI does not apply Terraform – deploy is manual.

```bash
cd infra
terraform init
terraform apply
```

Terraform outputs:
	•	chat_url – invoke URL for POST /chat
	•	openai_secret_arn – Secrets Manager ARN used by Lambda

## Configure OpenAI API key (Secrets Manager)

The Lambda reads the API key from Secrets Manager. Do not put keys in code or git.

```bash
cd infra
SECRET_ARN="$(terraform output -raw openai_secret_arn)"

# Paste key when prompted (input hidden)
echo -n "Paste OpenAI API key: "
stty -echo
read OPENAI_KEY
stty echo
echo

aws secretsmanager put-secret-value \
  --region ap-southeast-2 \
  --secret-id "$SECRET_ARN" \
  --secret-string "$OPENAI_KEY"

unset OPENAI_KEY
```

## Test the API

```bash
cd infra
CHAT_URL="$(terraform output -raw chat_url)"

curl -sS -X POST "$CHAT_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role":"user","content":"Say hello in one sentence."}],
    "temperature": 0.2,
    "max_tokens": 64
  }'

```

## Example response

```bash
{
  "id": "chatcmpl-...",
  "model": "gpt-4o-mini-...",
  "content": "Hello ...",
  "usage": {
    "prompt_tokens": 13,
    "completion_tokens": 9,
    "total_tokens": 22
  },
  "latency_ms": 2433,
  "request_id": "..."
}
```

## Security notes
	•	OpenAI API key is stored in AWS Secrets Manager and referenced by ARN in Lambda env vars.
	•	Lambda IAM policy is least-privilege:
	•	secretsmanager:GetSecretValue only for the configured secret
	•	CloudWatch Logs write permissions only
	•	The handler never logs request bodies or secrets.

## Phase 2 expansion points
	•	src/rag/ – placeholder for retrieval + prompt assembly
	•	src/tools/ – placeholder for tool calling router/registry
	•	src/integrations/autoprice/ – placeholder for external integration

## Troubleshooting
	•	500 / ImportModuleError (pydantic_core) on Lambda: rebuild with make build-amd64 and terraform apply.
	•	Upstream 429: check OpenAI billing/credits or reduce request rate.
	•	Secrets errors: confirm secret value exists and Lambda role can read the secret ARN.