# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.environment}-zpc-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = var.environment == "production" ? true : false

  tags = {
    Name        = "${var.environment}-zpc-alb"
    Environment = var.environment
  }
}

# Target Groups
resource "aws_lb_target_group" "auth" {
  name        = "${var.environment}-auth-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name        = "${var.environment}-auth-tg"
    Environment = var.environment
  }
}

resource "aws_lb_target_group" "user" {
  name        = "${var.environment}-user-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name        = "${var.environment}-user-tg"
    Environment = var.environment
  }
}

resource "aws_lb_target_group" "property" {
  name        = "${var.environment}-property-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name        = "${var.environment}-property-tg"
    Environment = var.environment
  }
}

resource "aws_lb_target_group" "posts" {
  name        = "${var.environment}-posts-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name        = "${var.environment}-posts-tg"
    Environment = var.environment
  }
}



# Listeners
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.certificate_arn

  default_action {
    type = "fixed-response"

    fixed_response {
      content_type = "text/plain"
      message_body = "Service not found"
      status_code  = "404"
    }
  }
}

# Listener Rules
resource "aws_lb_listener_rule" "auth" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.auth.arn
  }

  condition {
    path_pattern {
      values = ["/auth/*", "/api/auth/*"]
    }
  }
}

resource "aws_lb_listener_rule" "user" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.user.arn
  }

  condition {
    path_pattern {
      values = ["/user/*", "/api/user/*"]
    }
  }
}

resource "aws_lb_listener_rule" "property" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 300

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.property.arn
  }

  condition {
    path_pattern {
      values = ["/property/*", "/api/property/*"]
    }
  }
}

resource "aws_lb_listener_rule" "posts" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 400

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.posts.arn
  }

  condition {
    path_pattern {
      values = ["/posts/*", "/api/posts/*"]
    }
  }
}

resource "aws_lb_listener_rule" "feed" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 500

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.feed.arn
  }

  condition {
    path_pattern {
      values = ["/feed/*", "/api/feed/*"]
    }
  }
}

resource "aws_lb_listener_rule" "search" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 600

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.search.arn
  }

  condition {
    path_pattern {
      values = ["/search/*", "/api/search/*"]
    }
  }
}

resource "aws_lb_listener_rule" "notification" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 700

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.notification.arn
  }

  condition {
    path_pattern {
      values = ["/notification/*", "/api/notification/*"]
    }
  }
}

resource "aws_lb_listener_rule" "trending" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 800

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.trending.arn
  }

  condition {
    path_pattern {
      values = ["/trending/*", "/api/trending/*"]
    }
  }
}
