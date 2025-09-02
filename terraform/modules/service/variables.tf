variable "service_name" {
  description = "Name of the service"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "ecs_cluster_id" {
  description = "ECS cluster ID"
  type        = string
}

variable "ecs_cluster_name" {
  description = "ECS cluster name"
  type        = string
}

variable "task_definition_arn" {
  description = "Task definition ARN"
  type        = string
}

variable "target_group_arn" {
  description = "Target group ARN"
  type        = string
}

variable "desired_count" {
  description = "Desired count of tasks"
  type        = number
  default     = 2
}

variable "private_subnet_ids" {
  description = "Private subnet IDs"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security group IDs"
  type        = list(string)
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 50051
}

# Auto Scaling variables
variable "max_capacity" {
  description = "Maximum capacity for auto scaling"
  type        = number
  default     = 10
}

variable "min_capacity" {
  description = "Minimum capacity for auto scaling"
  type        = number
  default     = 1
}

variable "cpu_target_value" {
  description = "CPU target value for scaling"
  type        = number
  default     = 70
}

variable "memory_target_value" {
  description = "Memory target value for scaling"
  type        = number
  default     = 80
}
