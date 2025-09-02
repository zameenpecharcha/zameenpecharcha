# VPC Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "VPC CIDR block"
  value       = module.vpc.vpc_cidr_block
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

# RDS Outputs
output "db_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.db_endpoint
}

output "db_port" {
  description = "RDS port"
  value       = module.rds.db_port
}

output "db_name" {
  description = "Database name"
  value       = module.rds.db_name
}

# Redis Outputs
output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.redis.redis_endpoint
}

output "redis_port" {
  description = "Redis port"
  value       = module.redis.redis_port
}

# ECS Outputs
output "ecs_cluster_id" {
  description = "ECS cluster ID"
  value       = module.ecs.cluster_id
}

output "ecs_cluster_arn" {
  description = "ECS cluster ARN"
  value       = module.ecs.cluster_arn
}

# ALB Outputs
output "alb_id" {
  description = "ALB ID"
  value       = module.alb.alb_id
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  description = "ALB zone ID"
  value       = module.alb.alb_zone_id
}

# API Gateway Outputs
output "api_gateway_url" {
  description = "API Gateway URL"
  value       = module.api_gateway.stage_url
}

output "api_gateway_id" {
  description = "API Gateway ID"
  value       = module.api_gateway.api_id
}

# Service URLs
output "auth_service_url" {
  description = "Auth service URL"
  value       = "https://${module.alb.alb_dns_name}/auth"
}

output "user_service_url" {
  description = "User service URL"
  value       = "https://${module.alb.alb_dns_name}/user"
}

output "property_service_url" {
  description = "Property service URL"
  value       = "https://${module.alb.alb_dns_name}/property"
}

output "posts_service_url" {
  description = "Posts service URL"
  value       = "https://${module.alb.alb_dns_name}/posts"
}
