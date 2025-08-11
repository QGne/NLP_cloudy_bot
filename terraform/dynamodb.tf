# terraform/dynamodb.tf
resource "aws_dynamodb_table" "conversations" {
  name           = "${var.project_name}-conversations-${random_id.suffix.hex}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "conversation_id"
  range_key      = "timestamp"

  attribute {
    name = "conversation_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  attribute {
    name = "session_id"
    type = "S"
  }

  global_secondary_index {
    name     = "session-index"
    hash_key = "session_id"
    range_key = "timestamp"
  }

  tags = {
    Name        = "${var.project_name}-conversations"
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "chatbot_configs" {
  name           = "${var.project_name}-configs-${random_id.suffix.hex}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "config_id"

  attribute {
    name = "config_id"
    type = "S"
  }

  tags = {
    Name        = "${var.project_name}-configs"
    Environment = var.environment
  }
}