variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "ap-southeast-2"
}

variable "project_name" {
  type        = string
  description = "Project name prefix"
  default     = "llm-chat-api"
}

variable "env" {
  type        = string
  description = "Environment name"
  default     = "dev"
}

variable "openai_secret_name" {
  type        = string
  description = "Secrets Manager secret name for OpenAI API key"
  default     = "/llm-chat-api/openai_api_key"
}

variable "openai_model" {
  type        = string
  description = "Default OpenAI model"
  default     = "gpt-4o-mini"
}

variable "openai_base_url" {
  type        = string
  description = "OpenAI-compatible base URL (no trailing slash)"
  default     = "https://api.openai.com/v1"
}

variable "lambda_package_path" {
  type        = string
  description = "Path to Lambda deployment zip (build artifact)"
  default     = "../dist/lambda.zip"
}

variable "lambda_timeout" {
  type        = number
  description = "Lambda timeout in seconds"
  default     = 30
}

variable "lambda_memory_mb" {
  type        = number
  description = "Lambda memory size in MB"
  default     = 512
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch Logs retention days"
  default     = 14
}

variable "cors_allow_origins" {
  type        = list(string)
  description = "CORS allow origins"
  default     = ["*"]
}