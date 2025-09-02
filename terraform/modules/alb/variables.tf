variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs"
  type        = list(string)
}

variable "alb_security_group_id" {
  description = "ALB security group ID"
  type        = string
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 50051
}

variable "certificate_arn" {
  description = "SSL certificate ARN"
  type        = string
  default     = ""
}
