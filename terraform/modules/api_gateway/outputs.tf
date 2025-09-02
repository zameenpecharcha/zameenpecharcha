output "api_id" {
  description = "API Gateway ID"
  value       = aws_api_gateway_rest_api.main.id
}

output "api_arn" {
  description = "API Gateway ARN"
  value       = aws_api_gateway_rest_api.main.arn
}

output "api_url" {
  description = "API Gateway URL"
  value       = "${aws_api_gateway_rest_api.main.execution_arn}${aws_api_gateway_stage.main.stage_name}"
}

output "stage_url" {
  description = "API Gateway stage URL"
  value       = "${aws_api_gateway_deployment.main.invoke_url}${aws_api_gateway_stage.main.stage_name}"
}

output "vpc_link_id" {
  description = "VPC Link ID"
  value       = aws_api_gateway_vpc_link.main.id
}
