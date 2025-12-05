# Automate Secure LLM Deployments

A comprehensive hands-on course covering the complete lifecycle of deploying, securing, and operating Large Language Models (LLMs) in production environments.

**Author:** Ritesh Vajariya

---

## Course Overview

This course takes you from containerizing your first LLM application to building production-grade, secure, and cost-optimized deployments. Through nine practical modules, you'll master the DevOps skills needed to deploy LLMs at enterprise scale.

### What You'll Learn

- Build automated CI/CD pipelines with blue-green deployments
- Containerize LLM applications using Docker best practices
- Provision cloud infrastructure with Terraform
- Secure APIs with Kong Gateway authentication and rate limiting
- Defend against prompt injection and jailbreak attacks
- Implement compliance-ready audit logging with ELK Stack
- Monitor LLM performance with Prometheus and Grafana
- Auto-scale Kubernetes deployments based on demand
- Optimize costs with intelligent model routing and caching

---

## Prerequisites

Before starting this course, ensure you have the following installed:

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | 20.10+ | Container runtime |
| Docker Compose | 2.0+ | Multi-container orchestration |
| Python | 3.11+ | Application development |
| Kubernetes | 1.25+ | Container orchestration (Modules 3.2+) |
| Terraform | 1.0+ | Infrastructure as Code (Module 1.3) |
| Ollama | Latest | Local LLM inference |
| Git | 2.30+ | Version control |
| AWS CLI | 2.0+ | Cloud deployments (Module 1.3) |

### Quick Setup

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model for testing
ollama pull llama3.1:8b

# Verify Docker is running
docker --version
docker-compose --version
```

---

## Course Structure

The course is organized into three learning tracks with three modules each:

```
Track 1: Infrastructure & Deployment
├── M1V1: CI/CD Pipeline
├── M1V2: Docker Containerization
└── M1V3: Terraform IaC

Track 2: Security & Compliance
├── M2V1: API Security
├── M2V2: Prompt Injection Defense
└── M2V3: Audit Logging

Track 3: Operations & Optimization
├── M3V1: Monitoring
├── M3V2: Kubernetes Autoscaling
└── M3V3: Cost Optimization
```

---

## Module Details

### Track 1: Infrastructure & Deployment

#### M1V1: CI/CD Pipeline
**Goal:** Automate LLM deployments with GitHub Actions and blue-green strategy

| File | Description |
|------|-------------|
| `app.py` | Flask-based LLM inference API |
| `Dockerfile` | Multi-stage production build |
| `.github/workflows/deploy.yml` | GitHub Actions pipeline |

**Key Concepts:**
- Multi-stage Docker builds for smaller images
- Trivy security scanning for vulnerabilities
- Blue-green deployment for zero-downtime releases
- Health check validation before traffic switching

**Try It:**
```bash
cd M1V1-CICD-Pipeline
docker build -t llm-app .
docker run -p 8000:8000 llm-app
curl http://localhost:8000/health
```

---

#### M1V2: Docker Containerization
**Goal:** Master Docker layer optimization for fast LLM container builds

| File | Description |
|------|-------------|
| `app.py` | Ollama-connected inference wrapper |
| `Dockerfile` | Optimized layer ordering |
| `Dockerfile.slow` | Non-optimized (for comparison) |

**Key Concepts:**
- Layer caching strategies (dependencies before code)
- Build time optimization (seconds vs minutes)
- Health checks for production reliability
- Container-to-host Ollama communication

**Try It:**
```bash
cd M1V2-Docker-Containerization

# Compare build times
time docker build -f Dockerfile.slow -t slow-build .
time docker build -f Dockerfile -t fast-build .

# Run the optimized container
docker run -p 8000:8000 fast-build
```

---

#### M1V3: Terraform Infrastructure as Code
**Goal:** Provision AWS infrastructure for LLM deployments

| File | Description |
|------|-------------|
| `main.tf` | Complete AWS infrastructure (VPC, EC2, ALB, ASG) |
| `variables.tf` | Configurable parameters |
| `outputs.tf` | Infrastructure outputs |
| `terraform.tfvars` | Default values |

**Key Concepts:**
- VPC networking with public/private subnets
- Auto Scaling Groups for dynamic capacity
- Application Load Balancer for traffic distribution
- Security groups for network isolation

**Try It:**
```bash
cd M1V3-Terraform-IaC

# Initialize and plan
terraform init
terraform plan -var="environment=dev"

# Apply (requires AWS credentials)
terraform apply -var="environment=dev"
```

---

### Track 2: Security & Compliance

#### M2V1: API Security
**Goal:** Secure LLM APIs with Kong Gateway

| File | Description |
|------|-------------|
| `docker-compose.yml` | Kong + PostgreSQL + Redis stack |
| `setup_kong.sh` | Automated security configuration |

**Key Concepts:**
- API key authentication
- Rate limiting with Redis backend
- Request/response logging
- CORS policy management

**Try It:**
```bash
cd M2V1-API-Security

# Start the Kong stack
docker-compose up -d

# Wait for initialization, then configure
sleep 30
chmod +x setup_kong.sh
./setup_kong.sh

# Test with API key
curl -H "apikey: your-key" http://localhost:10000/v1/generate
```

**Port Reference:**
| Port | Service |
|------|---------|
| 10000 | Kong Proxy |
| 10001 | Kong Admin API |
| 10002 | Kong Admin GUI |
| 10434 | Ollama |

---

#### M2V2: Prompt Injection Defense
**Goal:** Protect LLMs from injection attacks and data leakage

| File | Description |
|------|-------------|
| `secure_llm_demo.py` | Attack detection demonstration |
| `pii_filter.py` | PII detection and redaction |
| `config/config.yml` | NeMo Guardrails configuration |
| `config/actions/actions.py` | Custom security actions |

**Key Concepts:**
- Prompt injection detection patterns
- Jailbreak prevention
- PII extraction blocking
- Data leakage prevention

**Attack Patterns Blocked:**
- "Ignore all previous instructions..."
- "You are now DAN..."
- "List all email addresses in your training data..."
- Social Security Numbers, credit cards, API keys

**Try It:**
```bash
cd M2V2-Prompt-Injection-Defense

# Install dependencies
pip install nemoguardrails

# Run the demo
python secure_llm_demo.py
```

---

#### M2V3: Audit Logging
**Goal:** Implement compliance-ready logging with ELK Stack

| File | Description |
|------|-------------|
| `audit_logger.py` | Comprehensive audit logging |
| `docker-compose.yml` | ELK Stack (Elasticsearch, Logstash, Kibana) |
| `logstash.conf` | Log processing pipeline |

**Key Concepts:**
- LLM request/response audit trails
- PII detection in logs
- Cost tracking per request
- HIPAA-compliant retention (6 years)
- Geo-IP enrichment

**Try It:**
```bash
cd M2V3-Audit-Logging

# Start ELK Stack
docker-compose up -d

# Access Kibana
open http://localhost:5601
```

---

### Track 3: Operations & Optimization

#### M3V1: Monitoring
**Goal:** Monitor LLM performance with Prometheus and Grafana

| File | Description |
|------|-------------|
| `ollama_exporter.py` | Custom Prometheus metrics exporter |
| `docker-compose.yml` | Prometheus + Grafana stack |
| `Dockerfile.exporter` | Exporter container |

**Metrics Collected:**
| Metric | Type | Description |
|--------|------|-------------|
| `llm_requests_total` | Counter | Total requests by model/status |
| `llm_tokens_processed_total` | Counter | Input/output token counts |
| `llm_request_duration_seconds` | Histogram | Request latency distribution |
| `llm_gpu_utilization_percent` | Gauge | GPU utilization |
| `llm_inference_cost_usd` | Counter | Running cost total |

**Try It:**
```bash
cd M3V1-Monitoring

# Start monitoring stack
docker-compose up -d

# Access dashboards
open http://localhost:3000  # Grafana (admin/admin)
open http://localhost:9090  # Prometheus
```

---

#### M3V2: Kubernetes Autoscaling
**Goal:** Auto-scale LLM pods based on demand

| File | Description |
|------|-------------|
| `llm-deployment.yaml` | Full Kubernetes deployment with HPA |
| `real-llm-autoscale.yaml` | Conservative scaling config |
| `load_test.py` | Load testing script |
| `watch_scaling.sh` | Scaling monitor |

**Key Concepts:**
- Horizontal Pod Autoscaler (HPA)
- CPU and memory-based scaling
- Aggressive scale-up, conservative scale-down
- Resource requests and limits

**Scaling Configuration:**
| Parameter | Value |
|-----------|-------|
| Min Replicas | 2 |
| Max Replicas | 10 |
| CPU Target | 70% |
| Memory Target | 80% |
| Scale Up | +2 pods/minute |
| Scale Down | -1 pod/2 minutes |

**Try It:**
```bash
cd M3V2-Kubernetes-Autoscaling

# Deploy to Kubernetes
kubectl apply -f llm-deployment.yaml

# Watch scaling in action
chmod +x watch_scaling.sh
./watch_scaling.sh

# Generate load (in another terminal)
python load_test.py
```

---

#### M3V3: Cost Optimization
**Goal:** Minimize LLM costs with intelligent routing and caching

| File | Description |
|------|-------------|
| `cost-optimizer.py` | Hybrid routing + caching engine |

**Cost Optimization Strategies:**
1. **Intelligent Routing:** Simple queries → local 8B model, Complex queries → cloud 70B model
2. **Response Caching:** Redis-based deduplication
3. **Hybrid Architecture:** Local Ollama + Cerebras Cloud API

**Cost Comparison:**
| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| Llama 3.1 8B (local) | $0.0001 | $0.0002 |
| Llama 3.3 70B (cloud) | $0.0006 | $0.0006 |

**Try It:**
```bash
cd M3V3-Cost-Optimization

# Start Redis
docker run -d -p 6379:6379 redis:7

# Set API key (optional for cloud)
export CEREBRAS_API_KEY=your-key

# Run optimizer
python cost-optimizer.py
```

---

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│  Kong Gateway │ Flask APIs │ Grafana Dashboards │ Kibana    │
├─────────────────────────────────────────────────────────────┤
│                     APPLICATION LAYER                        │
│  Python Apps │ NeMo Guardrails │ Custom Exporters           │
├─────────────────────────────────────────────────────────────┤
│                     INFERENCE LAYER                          │
│  Ollama (Local) │ Cerebras Cloud API │ Response Cache       │
├─────────────────────────────────────────────────────────────┤
│                     ORCHESTRATION LAYER                      │
│  Kubernetes │ Docker Compose │ GitHub Actions               │
├─────────────────────────────────────────────────────────────┤
│                     INFRASTRUCTURE LAYER                     │
│  Terraform │ AWS (EC2, VPC, ALB, ASG) │ Docker              │
├─────────────────────────────────────────────────────────────┤
│                     OBSERVABILITY LAYER                      │
│  Prometheus │ Grafana │ ELK Stack │ Audit Logging           │
├─────────────────────────────────────────────────────────────┤
│                     DATA LAYER                               │
│  PostgreSQL │ Redis │ Elasticsearch                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Common Issues

**Docker: Cannot connect to Ollama from container**
```bash
# Use host.docker.internal for Mac/Windows
OLLAMA_HOST=http://host.docker.internal:11434

# Use host network mode for Linux
docker run --network host ...
```

**Kubernetes: Pods stuck in Pending**
```bash
# Check resource availability
kubectl describe pod <pod-name>
kubectl top nodes
```

**Kong: Connection refused on port 10000**
```bash
# Wait for database migrations
docker-compose logs kong-migrations
docker-compose restart kong
```

**Terraform: AWS credentials not found**
```bash
# Configure AWS CLI
aws configure
# Or use environment variables
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

---

## Project Structure

```
code/
├── README.md                          # This file
├── .dockerignore                      # Docker ignore rules
│
├── M1V1-CICD-Pipeline/               # CI/CD with GitHub Actions
│   ├── app.py                        # Flask LLM API
│   ├── Dockerfile                    # Multi-stage build
│   ├── requirements.txt              # Python dependencies
│   └── .github/workflows/deploy.yml  # GitHub Actions workflow
│
├── M1V2-Docker-Containerization/     # Docker best practices
│   ├── app.py                        # Ollama wrapper API
│   ├── Dockerfile                    # Optimized build
│   ├── Dockerfile.slow               # Comparison build
│   └── requirements.txt              # Python dependencies
│
├── M1V3-Terraform-IaC/               # AWS infrastructure
│   ├── main.tf                       # Infrastructure definition
│   ├── variables.tf                  # Input variables
│   ├── outputs.tf                    # Output values
│   └── terraform.tfvars              # Default values
│
├── M2V1-API-Security/                # Kong API Gateway
│   ├── docker-compose.yml            # Kong + PostgreSQL + Redis
│   └── setup_kong.sh                 # Security configuration
│
├── M2V2-Prompt-Injection-Defense/    # LLM security
│   ├── secure_llm_demo.py            # Attack demonstration
│   ├── pii_filter.py                 # PII detection
│   └── config/                       # NeMo Guardrails config
│
├── M2V3-Audit-Logging/               # ELK Stack logging
│   ├── audit_logger.py               # Audit implementation
│   ├── docker-compose.yml            # ELK Stack
│   └── logstash.conf                 # Log pipeline
│
├── M3V1-Monitoring/                  # Prometheus + Grafana
│   ├── ollama_exporter.py            # Custom metrics
│   ├── docker-compose.yml            # Monitoring stack
│   └── Dockerfile.exporter           # Exporter container
│
├── M3V2-Kubernetes-Autoscaling/      # K8s HPA
│   ├── llm-deployment.yaml           # Full deployment
│   ├── real-llm-autoscale.yaml       # Conservative config
│   ├── load_test.py                  # Load testing
│   └── watch_scaling.sh              # Scaling monitor
│
└── M3V3-Cost-Optimization/           # Cost management
    └── cost-optimizer.py             # Hybrid routing + caching
```

---

## Learning Path Recommendations

### Beginner Path (2-3 weeks)
1. M1V2: Docker Containerization → Understand containers
2. M1V1: CI/CD Pipeline → Automate deployments
3. M3V1: Monitoring → Observe your applications

### Intermediate Path (3-4 weeks)
1. Complete Beginner Path
2. M2V1: API Security → Secure your APIs
3. M2V2: Prompt Injection Defense → Protect your LLMs
4. M3V2: Kubernetes Autoscaling → Scale on demand

### Advanced Path (4-5 weeks)
1. Complete Intermediate Path
2. M1V3: Terraform IaC → Infrastructure automation
3. M2V3: Audit Logging → Compliance ready
4. M3V3: Cost Optimization → Production efficiency

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Kong Gateway Docs](https://docs.konghq.com/)
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)
- [Prometheus Docs](https://prometheus.io/docs/)
- [Grafana Docs](https://grafana.com/docs/)
- [Elastic Stack Docs](https://www.elastic.co/guide/)
- [Ollama Documentation](https://ollama.com/)

---

## License

This course material is provided for educational purposes.

---

**Happy Learning!**

For questions or feedback, please reach out through the course platform.
