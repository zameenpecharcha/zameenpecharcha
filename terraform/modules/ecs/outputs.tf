output "cluster_id" {
  description = "ECS cluster ID"
  value       = aws_ecs_cluster.main.id
}

output "cluster_arn" {
  description = "ECS cluster ARN"
  value       = aws_ecs_cluster.main.arn
}

output "service_security_group_id" {
  description = "ECS service security group ID"
  value       = aws_security_group.ecs_services.id
}

output "alb_security_group_id" {
  description = "ALB security group ID"
  value       = aws_security_group.alb.id
}

# Task Definition ARNs
output "auth_task_definition_arn" {
  description = "Auth service task definition ARN"
  value       = aws_ecs_task_definition.auth.arn
}

output "user_task_definition_arn" {
  description = "User service task definition ARN"
  value       = aws_ecs_task_definition.user.arn
}

output "property_task_definition_arn" {
  description = "Property service task definition ARN"
  value       = aws_ecs_task_definition.property.arn
}

output "posts_task_definition_arn" {
  description = "Posts service task definition ARN"
  value       = aws_ecs_task_definition.posts.arn
}


