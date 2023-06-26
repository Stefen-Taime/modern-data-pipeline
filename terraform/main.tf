provider "aws" {
  region = "ca-central-1"
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "iam_lambda_cloudwatch_logs_policy" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "custom_s3_policy" {
  name        = "custom_s3_policy"
  description = "Custom S3 policy for Lambda"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["s3:PutObject"]
        Effect   = "Allow"
        Resource = "${aws_s3_bucket.bucket.arn}/*"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "iam_lambda_s3_policy" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.custom_s3_policy.arn
}

resource "aws_s3_bucket" "bucket" {
  bucket = "ingestion-rawdata"
}

resource "aws_lambda_function" "ingestion_function" {
  filename      = "my_lambda_package.zip"
  function_name = "https_to_s3"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "app.lambda_handler"

  source_code_hash = filebase64sha256("my_lambda_package.zip")

  runtime = "python3.10"

  timeout = 900
  memory_size = 1024

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.bucket.bucket
    }
  }
}


resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingestion_function.function_name
  principal     = "apigateway.amazonaws.com"
}

output "bucket_name" {
  description = "The name of the bucket"
  value       = aws_s3_bucket.bucket.bucket
}

output "lambda_function_name" {
  description = "The name of the lambda function"
  value       = aws_lambda_function.ingestion_function.function_name
}