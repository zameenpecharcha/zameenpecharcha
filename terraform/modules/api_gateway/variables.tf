variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs"
  type        = list(string)
}

variable "alb_arn" {
  description = "ALB ARN"
  type        = string
}

variable "alb_dns_name" {
  description = "ALB DNS name"
  type        = string
}
