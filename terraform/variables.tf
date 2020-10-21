variable "service_name" {
  default = "neurogui"
}

variable "init_task_count" {
  default = "0"
}

variable "subnets" {
  default = ["subnet-f1f1cfbb"]
}

variable "task_cpu" {
  default = "1024"
}

variable "task_memory" {
  default = "4096"
}

variable "environment" {
  default = "develop"
}

variable "aws_region" {
  default = "us-east-1"
}

variable "deployment_profile" {
  default = "personal"
}

variable "image_uri" {
  default = "488724466663.dkr.ecr.us-east-1.amazonaws.com/neurogui:latest"
}
