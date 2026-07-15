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

  default_tags {
    tags = {
      Project     = "EvalOps"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# VPC and Networking
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "evalops-vpc"
  }
}

resource "aws_subnet" "private" {
  count                   = 3
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 2, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = false

  tags = {
    Name = "evalops-private-${count.index + 1}"
  }
}

resource "aws_security_group" "rds" {
  name        = "evalops-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "evalops-rds-sg"
  }
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# ECR Registries
resource "aws_ecr_repository" "evalops" {
  name                 = "evalops-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "evalops-backend"
  }
}

resource "aws_ecr_repository" "knowledgeops" {
  name                 = "knowledgeops-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "knowledgeops-backend"
  }
}

# ECR Lifecycle Policy (keep last 10 images)
resource "aws_ecr_lifecycle_policy" "evalops" {
  repository = aws_ecr_repository.evalops.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus       = "any"
          countType       = "imageCountMoreThan"
          countNumber     = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_ecr_lifecycle_policy" "knowledgeops" {
  repository = aws_ecr_repository.knowledgeops.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus       = "any"
          countType       = "imageCountMoreThan"
          countNumber     = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "evalops" {
  name              = "/aws/k8s/evalops"
  retention_in_days = 30

  tags = {
    Name = "evalops-logs"
  }
}

resource "aws_cloudwatch_log_group" "knowledgeops" {
  name              = "/aws/k8s/knowledgeops"
  retention_in_days = 30

  tags = {
    Name = "knowledgeops-logs"
  }
}

# Outputs
output "evalops_ecr_repository_url" {
  value       = aws_ecr_repository.evalops.repository_url
  description = "ECR repository URL for EvalOps"
}

output "knowledgeops_ecr_repository_url" {
  value       = aws_ecr_repository.knowledgeops.repository_url
  description = "ECR repository URL for KnowledgeOps"
}

output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID"
}

output "private_subnet_ids" {
  value       = aws_subnet.private[*].id
  description = "Private subnet IDs"
}

output "rds_security_group_id" {
  value       = aws_security_group.rds.id
  description = "RDS security group ID"
}
