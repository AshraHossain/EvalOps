# Terraform Infrastructure

AWS infrastructure-as-code for EvalOps production deployment.

## What's Included

- **VPC & Networking**: VPC, subnets across 3 AZs, security groups
- **ECR Registries**: Container image repositories for EvalOps and KnowledgeOps
- **RDS Aurora PostgreSQL**: Managed relational database with backups
- **CloudWatch**: Log groups for application and RDS logging
- **Secrets Manager**: Secure storage for database credentials
- **IAM Roles**: Monitoring and service roles

## Prerequisites

1. AWS Account with appropriate permissions
2. Terraform >= 1.0
3. AWS CLI configured with credentials

## Setup

1. **Clone and navigate:**
   ```bash
   cd terraform
   ```

2. **Create secrets file (DO NOT COMMIT):**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your actual values
   ```

3. **Initialize Terraform:**
   ```bash
   terraform init
   ```

4. **Review plan:**
   ```bash
   terraform plan -var-file=terraform.tfvars
   ```

5. **Apply infrastructure:**
   ```bash
   terraform apply -var-file=terraform.tfvars
   ```

## Outputs

After applying, view outputs:
```bash
terraform output

# Get specific output:
terraform output rds_endpoint
terraform output evalops_ecr_repository_url
```

## Variables

Key variables (see `variables.tf` for full list):

- `aws_region`: AWS region (default: us-east-1)
- `environment`: dev/staging/prod
- `vpc_cidr`: VPC CIDR block
- `db_master_username`: RDS master user
- `db_master_password`: RDS master password (min 20 chars)
- `db_instance_class`: RDS instance type (default: db.t3.medium)
- `skip_final_snapshot`: Skip final snapshot on destroy

## Security Best Practices

1. **Never commit secrets**: Use `.tfvars` files with `*.tfvars` in `.gitignore`
2. **Use Secrets Manager**: Database passwords stored in AWS Secrets Manager
3. **Encryption**: RDS encryption enabled by default
4. **Backups**: 7-day retention configured
5. **VPC**: Resources in private subnets (no public access)

## Updating Deployments

To apply infrastructure changes:

```bash
# Make changes to *.tf files
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Destroying Infrastructure

⚠️ **WARNING**: This destroys all resources and data.

```bash
terraform destroy -var-file=terraform.tfvars -auto-approve
```

Set `skip_final_snapshot=true` to skip final DB snapshot (faster destroy).

## Troubleshooting

**RDS creation timeout**: Check security group and subnet configuration
**ECR login failure**: Verify AWS credentials and IAM permissions
**Terraform state lock**: Check for stale locks in S3 backend

## Monitoring

View CloudWatch logs:
```bash
aws logs tail /aws/k8s/evalops --follow
aws logs tail /aws/k8s/knowledgeops --follow
```

Check RDS metrics:
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=evalops-postgres-1 \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average
```

## Cost Estimation

Use `terraform plan` to see resources that will be created.

Example costs (us-east-1):
- RDS Aurora PostgreSQL (2 x db.t3.medium): ~$300/month
- VPC/NAT: ~$50/month
- ECR storage: ~$10/month per 10GB

Total estimate: **~$360/month** for dev environment
