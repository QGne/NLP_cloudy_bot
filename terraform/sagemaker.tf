# terraform/sagemaker.tf

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

# IAM role for SageMaker
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

resource "aws_iam_role_policy" "sagemaker_policy" {
  name = "${var.project_name}-sagemaker-policy"
  role = aws_iam_role.sagemaker_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.model_bucket.arn,
          "${aws_s3_bucket.model_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Use a simpler approach with a known working image
# Option 1: Use the latest available Hugging Face image
data "aws_sagemaker_prebuilt_ecr_image" "huggingface_inference" {
  repository_name = "huggingface-pytorch-inference"
  image_tag       = "2.0.0-transformers4.28.1-cpu-py310-ubuntu20.04"
}

# SageMaker model
resource "aws_sagemaker_model" "chatbot" {
  name               = "${var.project_name}-model-${random_id.suffix.hex}"
  execution_role_arn = aws_iam_role.sagemaker_role.arn

  primary_container {
    image = data.aws_sagemaker_prebuilt_ecr_image.huggingface_inference.registry_path

    environment = {
      HF_MODEL_ID                   = var.model_name
      HF_TASK                       = "text-generation"
      SAGEMAKER_CONTAINER_LOG_LEVEL = "20"
      SAGEMAKER_REGION              = var.aws_region
    }
  }

  tags = {
    Name        = "${var.project_name}-model"
    Environment = var.environment
  }
}

# SageMaker endpoint configuration (using instance-based instead of serverless for stability)
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

# SageMaker endpoint
resource "aws_sagemaker_endpoint" "chatbot" {
  name                 = "${var.project_name}-endpoint-${random_id.suffix.hex}"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.chatbot.name

  tags = {
    Name        = "${var.project_name}-endpoint"
    Environment = var.environment
  }
}