# terraform/sagemaker.tf - Fixed with proper IAM timing

# S3 bucket for model storage
resource "aws_s3_bucket" "model_bucket" {
  bucket = "${var.project_name}-models-${random_id.suffix.hex}"
}

resource "aws_s3_bucket_versioning" "model_bucket_versioning" {
  bucket = aws_s3_bucket.model_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# IAM role for SageMaker with minimal policy first
resource "aws_iam_role" "sagemaker_role" {
  name = "${var.project_name}-sagemaker-role-${random_id.suffix.hex}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })
}

# Step 1: Attach basic SageMaker execution policy
resource "aws_iam_role_policy_attachment" "sagemaker_execution_role" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

# Step 2: Wait for IAM role to propagate using null_resource with local-exec
resource "null_resource" "wait_for_iam_propagation" {
  provisioner "local-exec" {
    command = "sleep 60" # Wait 60 seconds for IAM propagation
  }

  depends_on = [
    aws_iam_role.sagemaker_role,
    aws_iam_role_policy_attachment.sagemaker_execution_role
  ]
}

# Step 3: Verify the role exists using AWS CLI
resource "null_resource" "verify_iam_role" {
  provisioner "local-exec" {
    command = <<-EOT
      echo "Verifying IAM role exists..."
      aws iam get-role --role-name ${aws_iam_role.sagemaker_role.name}
      echo "Role verification complete"
    EOT
  }

  depends_on = [null_resource.wait_for_iam_propagation]
}

# Use a known working image (different approach - try CPU inference)
locals {
  # Try a more basic/stable image first
  sagemaker_image_uri = "763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04"
}

# SageMaker model - created only after IAM verification
resource "aws_sagemaker_model" "chatbot" {
  name               = "${var.project_name}-model-${random_id.suffix.hex}"
  execution_role_arn = aws_iam_role.sagemaker_role.arn

  primary_container {
    image = local.sagemaker_image_uri

    environment = {
      HF_MODEL_ID = var.model_name
      HF_TASK     = "text-generation"
    }
  }

  depends_on = [
    null_resource.verify_iam_role
  ]

  tags = {
    Name        = "${var.project_name}-model"
    Environment = var.environment
  }
}

# SageMaker endpoint configuration
resource "aws_sagemaker_endpoint_configuration" "chatbot" {
  name = "${var.project_name}-endpoint-config-${random_id.suffix.hex}"

  production_variants {
    variant_name           = "AllTraffic"
    model_name             = aws_sagemaker_model.chatbot.name
    initial_instance_count = 1
    instance_type          = "ml.t2.medium"
    initial_variant_weight = 1
  }

  tags = {
    Name        = "${var.project_name}-endpoint-config"
    Environment = var.environment
  }
}

# SageMaker endpoint - only create after everything is ready
resource "aws_sagemaker_endpoint" "chatbot" {
  name                 = "${var.project_name}-endpoint-${random_id.suffix.hex}"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.chatbot.name

  tags = {
    Name        = "${var.project_name}-endpoint"
    Environment = var.environment
  }
}