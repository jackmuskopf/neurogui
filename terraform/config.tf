provider "aws" {
  profile = "${var.deployment_profile}"
  region  = "${var.aws_region}"
}

terraform {
  required_version = ">= 0.12.2"
  backend "s3" {
  }
}
