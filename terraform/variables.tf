variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "chatbot-saas"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prototype"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "model_name" {
  description = "HuggingFace model name"
  type        = string
  default     = "deepset/roberta-base-squad2"
}