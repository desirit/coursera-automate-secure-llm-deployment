# Demo configuration - US East
aws_region       = "us-east-1"
project_name     = "llm-inference"
environment      = "demo"
instance_type    = "t3.xlarge"
min_size         = 2
max_size         = 10
desired_capacity = 2
spot_max_price   = "0.10"
admin_ip         = "0.0.0.0/0"  # CHANGE to your IP in production!
