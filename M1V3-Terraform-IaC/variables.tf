# ============================================================
# VARIABLE DEFINITIONS
# ============================================================

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "llm-inference"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "demo"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "admin_ip" {
  description = "Admin IP for SSH access (CIDR notation)"
  type        = string
  default     = "0.0.0.0/0"  # CHANGE THIS to your IP/32
}

# ============================================================
# COMPUTE CONFIGURATION
# ============================================================

variable "instance_type" {
  description = "EC2 instance type for LLM inference"
  type        = string
  default     = "t3.xlarge"  # 4 vCPU, 16GB RAM - good for CPU inference
}

variable "spot_max_price" {
  description = "Maximum spot price (leave empty for on-demand price)"
  type        = string
  default     = "0.10"  # ~70% discount vs on-demand
}

variable "min_size" {
  description = "Minimum number of instances"
  type        = number
  default     = 2
}

variable "max_size" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "desired_capacity" {
  description = "Desired number of instances"
  type        = number
  default     = 2
}

# ============================================================
# STORAGE
# ============================================================

variable "model_bucket" {
  description = "S3 bucket for model weights (optional)"
  type        = string
  default     = "llm-models-demo"
}
