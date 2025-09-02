variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "private_subnets" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "public_subnets" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "zameenpecharcha"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "zpc_admin"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

# Service scaling variables
variable "auth_service_desired_count" {
  description = "Desired count for auth service"
  type        = number
  default     = 2
}

variable "user_service_desired_count" {
  description = "Desired count for user service"
  type        = number
  default     = 2
}

variable "property_service_desired_count" {
  description = "Desired count for property service"
  type        = number
  default     = 2
}

variable "posts_service_desired_count" {
  description = "Desired count for posts service"
  type        = number
  default     = 2
}

# Container configuration
variable "container_port" {
  description = "Container port"
  type        = number
  default     = 50051
}

variable "container_cpu" {
  description = "Container CPU units"
  type        = number
  default     = 256
}

variable "container_memory" {
  description = "Container memory in MiB"
  type        = number
  default     = 512
}

# ECS Configuration
variable "ecs_service_role_arn" {
  description = "ECS service role ARN"
  type        = string
  default     = ""
}

variable "ecs_task_role_arn" {
  description = "ECS task role ARN"
  type        = string
  default     = ""
}

# ECR Configuration
variable "ecr_repository_url" {
  description = "ECR repository URL for container images"
  type        = string
  default     = ""
}

# SSL Certificate
variable "certificate_arn" {
  description = "ARN of the SSL certificate for HTTPS"
  type        = string
  default     = ""
}
