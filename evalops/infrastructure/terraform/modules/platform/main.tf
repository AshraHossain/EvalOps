variable "environment" {
  type = string
}

resource "aws_s3_bucket" "evalops_artifacts" {
  bucket = "evalops-${var.environment}-artifacts"
}
