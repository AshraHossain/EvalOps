resource "aws_db_subnet_group" "main" {
  name       = "evalops-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "evalops-db-subnet-group"
  }
}

resource "aws_rds_cluster" "main" {
  cluster_identifier      = "evalops-postgres"
  engine                  = "aurora-postgresql"
  engine_version          = "15.3"
  database_name           = "evalops"
  master_username         = var.db_master_username
  master_password         = var.db_master_password
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  storage_encrypted       = true
  backup_retention_period = 7
  enabled_cloudwatch_logs_exports = [
    "postgresql"
  ]
  skip_final_snapshot = var.skip_final_snapshot

  tags = {
    Name = "evalops-postgres"
  }
}

resource "aws_rds_cluster_instance" "main" {
  count              = 2
  identifier         = "evalops-postgres-${count.index + 1}"
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = var.db_instance_class
  engine              = aws_rds_cluster.main.engine
  engine_version      = aws_rds_cluster.main.engine_version

  performance_insights_enabled    = true
  performance_insights_retention_period = 7
  monitoring_interval             = 60
  monitoring_role_arn             = aws_iam_role.rds_monitoring.arn

  tags = {
    Name = "evalops-postgres-${count.index + 1}"
  }
}

resource "aws_iam_role" "rds_monitoring" {
  name = "evalops-rds-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# RDS Secrets
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "evalops/db-password"
  recovery_window_in_days = 7

  tags = {
    Name = "evalops-db-password"
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id      = aws_secretsmanager_secret.db_password.id
  secret_string  = jsonencode({
    username = var.db_master_username
    password = var.db_master_password
    host     = aws_rds_cluster.main.endpoint
    port     = 5432
    dbname   = aws_rds_cluster.main.database_name
  })
}

# Output
output "rds_endpoint" {
  value       = aws_rds_cluster.main.endpoint
  description = "RDS cluster endpoint"
}

output "rds_reader_endpoint" {
  value       = aws_rds_cluster.main.reader_endpoint
  description = "RDS cluster reader endpoint"
}

output "db_secret_arn" {
  value       = aws_secretsmanager_secret.db_password.arn
  description = "ARN of the database secret"
}
