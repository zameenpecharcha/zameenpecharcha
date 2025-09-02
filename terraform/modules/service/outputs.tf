output "service_id" {
  description = "ECS service ID"
  value       = aws_ecs_service.main.id
}

output "service_arn" {
  description = "ECS service ARN"
  value       = aws_ecs_service.main.arn
}

output "service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.main.name
}

output "desired_count" {
  description = "Desired count of tasks"
  value       = aws_ecs_service.main.desired_count
}

output "running_count" {
  description = "Running count of tasks"
  value       = aws_ecs_service.main.running_count
}

output "pending_count" {
  description = "Pending count of tasks"
  value       = aws_ecs_service.main.pending_count
}
