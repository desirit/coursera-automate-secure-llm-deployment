# ============================================================
# OUTPUT VALUES
# ============================================================

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.llm_vpc.id
}

output "load_balancer_dns" {
  description = "Load balancer DNS name"
  value       = aws_lb.llm_alb.dns_name
}

output "load_balancer_url" {
  description = "URL for LLM inference API"
  value       = "http://${aws_lb.llm_alb.dns_name}"
}

output "asg_name" {
  description = "Auto Scaling Group name"
  value       = aws_autoscaling_group.llm_inference.name
}

output "security_group_id" {
  description = "Security group ID for inference servers"
  value       = aws_security_group.llm_inference.id
}

output "estimated_monthly_cost" {
  description = "Estimated monthly cost (spot pricing)"
  value       = "~$${var.desired_capacity * 0.04 * 730} USD/month (${var.desired_capacity}x ${var.instance_type} spot)"
}
