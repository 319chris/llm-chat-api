output "api_endpoint" {
  description = "HTTP API base endpoint"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}

output "chat_url" {
  description = "POST endpoint for chat"
  value       = "${aws_apigatewayv2_api.http_api.api_endpoint}/chat"
}

output "lambda_name" {
  value = aws_lambda_function.chat.function_name
}

output "openai_secret_arn" {
  value = aws_secretsmanager_secret.openai_api_key.arn
}