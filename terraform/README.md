# Zameen Pe Charcha - AWS Terraform Infrastructure

This Terraform configuration deploys the complete Zameen Pe Charcha microservices platform on AWS.

## Architecture Overview

The infrastructure consists of:

- **VPC** with public and private subnets across 2 availability zones
- **RDS PostgreSQL** database for persistent data storage
- **ElastiCache Redis** for caching and session management
- **ECS Fargate** cluster for running microservices
- **Application Load Balancer** for traffic distribution
- **API Gateway** for external API access
- **Auto Scaling** for all microservices

## Microservices

1. **Auth Service** - User authentication and authorization
2. **User Service** - User profile management
3. **Property Service** - Property listings and management
4. **Posts Service** - Content and media management

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** version >= 1.0
3. **Docker** for building and pushing container images
4. **AWS ECR** repositories for each service

## Quick Start

### 1. Clone and Setup

```bash
cd zameenpecharcha/terraform
cp terraform.tfvars.example terraform.tfvars
```

### 2. Configure Variables

Edit `terraform.tfvars` with your specific values:

```bash
# Required variables
aws_region = "us-east-1"
environment = "production"
db_password = "your-secure-password"

# Optional: SSL certificate for HTTPS
certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/your-cert-id"
```

### 3. Initialize Terraform

```bash
terraform init
```

### 4. Plan Deployment

```bash
terraform plan
```

### 5. Deploy Infrastructure

```bash
terraform apply
```

## Infrastructure Components

### VPC Module (`./modules/vpc`)
- Creates VPC with public and private subnets
- Sets up NAT gateways for private subnet internet access
- Configures route tables and internet gateway

### RDS Module (`./modules/rds`)
- PostgreSQL 15.7 database instance
- Multi-AZ deployment for high availability
- Automated backups and maintenance windows
- Security groups for ECS access

### Redis Module (`./modules/redis`)
- ElastiCache Redis 7 cluster
- Single node for development, multi-node for production
- Security groups for ECS access

### ECS Module (`./modules/ecs`)
- Fargate cluster for serverless container management
- Task definitions for all microservices
- IAM roles and policies
- CloudWatch log groups

### ALB Module (`./modules/alb`)
- Application Load Balancer with HTTPS support
- Target groups for each microservice
- Path-based routing
- Health checks and auto-scaling

### Service Module (`./modules/service`)
- Individual ECS service deployment
- Auto-scaling policies (CPU and memory-based)
- Load balancer integration

### API Gateway Module (`./modules/api_gateway`)
- REST API with VPC link to ALB
- Proxy integration for all microservices
- Stage management and deployment

## Configuration Options

### Environment Variables

Each service receives these environment variables:
- `ENVIRONMENT` - Environment name
- `DB_HOST` - RDS endpoint
- `DB_PORT` - Database port
- `DB_NAME` - Database name
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password

### Scaling Configuration

Default scaling settings:
- **Min Capacity**: 1 task per service
- **Max Capacity**: 10 tasks per service
- **CPU Target**: 70% utilization
- **Memory Target**: 80% utilization

### Security

- All services run in private subnets
- Security groups restrict access between components
- RDS and Redis are not publicly accessible
- HTTPS termination at ALB level

## Deployment Steps

### 1. Build and Push Container Images

```bash
# For each service directory
docker build -t zpc-auth-service .
docker tag zpc-auth-service:latest $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/zpc-auth-service:latest
docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/zpc-auth-service:latest
```

### 2. Update ECR Repository URLs

Update the `ecr_repository_url` variable in `main.tf` for each service.

### 3. Deploy Infrastructure

```bash
terraform apply
```

### 4. Verify Deployment

Check the outputs for service URLs and endpoints:

```bash
terraform output
```

## Monitoring and Logging

### CloudWatch Logs
- Each service has dedicated log group
- 30-day retention by default
- Structured logging with service prefixes

### Metrics
- ECS service metrics (CPU, memory, network)
- ALB metrics (request count, latency, errors)
- RDS metrics (connections, performance)
- Redis metrics (cache hits, memory usage)

## Cost Optimization

### Development Environment
- Use `t3.micro` instances for RDS and Redis
- Single AZ deployment
- Minimal service replicas

### Production Environment
- Use `t3.small` or larger for RDS
- Multi-AZ deployment
- Auto-scaling enabled
- Reserved instances for predictable workloads

## Security Best Practices

1. **Network Security**
   - Private subnets for all services
   - Security groups with minimal required access
   - VPC endpoints for AWS services

2. **Data Security**
   - RDS encryption at rest
   - Secrets management for sensitive data
   - Regular security updates

3. **Access Control**
   - IAM roles with least privilege
   - API Gateway authentication (can be added)
   - VPC link for private service access

## Troubleshooting

### Common Issues

1. **ECS Service Won't Start**
   - Check task definition logs
   - Verify security group rules
   - Check IAM role permissions

2. **Database Connection Issues**
   - Verify security group rules
   - Check subnet group configuration
   - Verify database credentials

3. **Load Balancer Health Check Failures**
   - Check service health endpoints
   - Verify target group configuration
   - Check security group rules

### Debug Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster production-zpc-cluster --services auth-service

# Check RDS status
aws rds describe-db-instances --db-instance-identifier production-zpc-db

# Check ALB target health
aws elbv2 describe-target-health --target-group-arn $TARGET_GROUP_ARN
```

## Cleanup

To destroy the infrastructure:

```bash
terraform destroy
```

**Warning**: This will delete all resources including databases and data.

## Support

For issues and questions:
1. Check CloudWatch logs for service errors
2. Verify Terraform state and outputs
3. Check AWS service quotas and limits
4. Review security group and IAM configurations

## Contributing

1. Follow Terraform best practices
2. Use consistent naming conventions
3. Document all variables and outputs
4. Test changes in development environment first
