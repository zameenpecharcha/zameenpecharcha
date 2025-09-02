# Security Group for Redis
resource "aws_security_group" "redis" {
  name_prefix = "${var.environment}-redis-sg"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.environment}-redis-sg"
    Environment = var.environment
  }
}

# Subnet Group for Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.environment}-redis-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name        = "${var.environment}-redis-subnet-group"
    Environment = var.environment
  }
}

# Parameter Group for Redis
resource "aws_elasticache_parameter_group" "main" {
  family = "redis7"
  name   = "${var.environment}-redis7-params"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  tags = {
    Name        = "${var.environment}-redis7-params"
    Environment = var.environment
  }
}

# Redis Cluster
resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${var.environment}-zpc-redis"
  engine               = "redis"
  node_type            = var.node_type
  num_cache_nodes      = 1
  parameter_group_name = aws_elasticache_parameter_group.main.name
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]

  tags = {
    Name        = "${var.environment}-zpc-redis"
    Environment = var.environment
  }
}
