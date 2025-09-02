terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
module "vpc" {
  source = "./modules/vpc"

  environment        = var.environment
  vpc_cidr          = var.vpc_cidr
  availability_zones = var.availability_zones
  private_subnets   = var.private_subnets
  public_subnets    = var.public_subnets
}

# ECS Cluster and Task Definitions
module "ecs" {
  source = "./modules/ecs"

  environment          = var.environment
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  public_subnet_ids   = module.vpc.public_subnet_ids
  container_port      = var.container_port
  container_cpu       = var.container_cpu
  container_memory    = var.container_memory
  ecr_repository_url  = var.ecr_repository_url
  db_endpoint         = module.rds.db_endpoint
  db_port             = module.rds.db_port
  db_name             = module.rds.db_name
  db_username         = module.rds.db_username
  db_password         = module.rds.db_password
}

# RDS PostgreSQL Database
module "rds" {
  source = "./modules/rds"

  environment          = var.environment
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  db_name             = var.db_name
  db_username         = var.db_username
  db_password         = var.db_password
  db_instance_class   = var.db_instance_class
  ecs_security_group_id = module.ecs.service_security_group_id
}

# Redis Cache
module "redis" {
  source = "./modules/redis"

  environment          = var.environment
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  node_type           = var.redis_node_type
  ecs_security_group_id = module.ecs.service_security_group_id
}

# Application Load Balancer
module "alb" {
  source = "./modules/alb"

  environment          = var.environment
  vpc_id              = module.vpc.vpc_id
  public_subnet_ids   = module.vpc.public_subnet_ids
  alb_security_group_id = module.ecs.alb_security_group_id
  container_port      = var.container_port
  certificate_arn     = var.certificate_arn
}

# API Gateway
module "api_gateway" {
  source = "./modules/api_gateway"

  environment          = var.environment
  vpc_id              = module.vpc.vpc_id
  private_subnet_ids  = module.vpc.private_subnet_ids
  alb_arn             = module.alb.alb_arn
  alb_dns_name        = module.alb.alb_dns_name
}

# Deploy individual services
module "auth_service" {
  source = "./modules/service"

  service_name         = "auth-service"
  environment          = var.environment
  ecs_cluster_id      = module.ecs.cluster_id
  ecs_cluster_name    = module.ecs.cluster_name
  task_definition_arn = module.ecs.auth_task_definition_arn
  target_group_arn    = module.alb.auth_target_group_arn
  desired_count       = var.auth_service_desired_count
  private_subnet_ids  = module.vpc.private_subnet_ids
  security_group_ids  = [module.ecs.service_security_group_id]
  container_port      = var.container_port
}

module "user_service" {
  source = "./modules/service"

  service_name         = "user-service"
  environment          = var.environment
  ecs_cluster_id      = module.ecs.cluster_id
  ecs_cluster_name    = module.ecs.cluster_name
  task_definition_arn = module.ecs.user_task_definition_arn
  target_group_arn    = module.alb.user_target_group_arn
  desired_count       = var.user_service_desired_count
  private_subnet_ids  = module.vpc.private_subnet_ids
  security_group_ids  = [module.ecs.service_security_group_id]
  container_port      = var.container_port
}

module "property_service" {
  source = "./modules/service"

  service_name         = "property-service"
  environment          = var.environment
  ecs_cluster_id      = module.ecs.cluster_id
  ecs_cluster_name    = module.ecs.cluster_name
  task_definition_arn = module.ecs.property_task_definition_arn
  target_group_arn    = module.alb.property_target_group_arn
  desired_count       = var.property_service_desired_count
  private_subnet_ids  = module.vpc.private_subnet_ids
  security_group_ids  = [module.ecs.service_security_group_id]
  container_port      = var.container_port
}

module "posts_service" {
  source = "./modules/service"

  service_name         = "posts-service"
  environment          = var.environment
  ecs_cluster_id      = module.ecs.cluster_id
  ecs_cluster_name    = module.ecs.cluster_name
  task_definition_arn = module.ecs.posts_task_definition_arn
  target_group_arn    = module.alb.posts_target_group_arn
  desired_count       = var.posts_service_desired_count
  private_subnet_ids  = module.vpc.private_subnet_ids
  security_group_ids  = [module.ecs.service_security_group_id]
  container_port      = var.container_port
}
