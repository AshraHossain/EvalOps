terraform {
  required_version = ">= 1.7.0"
}

provider "aws" {
  region = var.aws_region
}

module "platform" {
  source      = "../../modules/platform"
  environment = "dev"
}
