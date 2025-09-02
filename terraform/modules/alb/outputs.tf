output "alb_id" {
  description = "ALB ID"
  value       = aws_lb.main.id
}

output "alb_arn" {
  description = "ALB ARN"
  value       = aws_lb.main.arn
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "ALB zone ID"
  value       = aws_lb.main.zone_id
}

# Target Group ARNs
output "auth_target_group_arn" {
  description = "Auth service target group ARN"
  value       = aws_lb_target_group.auth.arn
}

output "user_target_group_arn" {
  description = "User service target group ARN"
  value       = aws_lb_target_group.user.arn
}

output "property_target_group_arn" {
  description = "Property service target group ARN"
  value       = aws_lb_target_group.property.arn
}

output "posts_target_group_arn" {
  description = "Posts service target group ARN"
  value       = aws_lb_target_group.posts.arn
}


