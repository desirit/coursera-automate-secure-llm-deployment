#!/usr/bin/env python3
"""
Custom Prometheus Exporter for Ollama LLM Metrics
Tracks: requests, tokens, latency, costs, GPU utilization
"""
from prometheus_client import start_http_server, Gauge, Counter, Histogram, Summary
import random
import time
from datetime import datetime

# ============================================
# PROMETHEUS METRICS DEFINITION
# ============================================

# Request metrics
requests_total = Counter(
    'llm_requests_total',
    'Total number of LLM requests',
    ['model', 'status']
)

requests_in_flight = Gauge(
    'llm_requests_in_flight',
    'Current number of requests being processed'
)

# Token metrics
tokens_processed = Counter(
    'llm_tokens_processed_total',
    'Total tokens processed',
    ['type']  # input or output
)

tokens_per_request = Histogram(
    'llm_tokens_per_request',
    'Distribution of tokens per request',
    buckets=[10, 50, 100, 200, 500, 1000, 2000, 5000]
)

# Latency metrics
request_duration = Histogram(
    'llm_request_duration_seconds',
    'Request processing duration',
    ['model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

request_latency_summary = Summary(
    'llm_request_latency_seconds',
    'Request latency summary statistics'
)

# GPU metrics (simulated)
gpu_utilization = Gauge(
    'llm_gpu_utilization_percent',
    'GPU utilization percentage',
    ['gpu_id']
)

gpu_memory_used = Gauge(
    'llm_gpu_memory_used_bytes',
    'GPU memory used in bytes',
    ['gpu_id']
)

# Cost metrics (based on token pricing)
cost_total = Counter(
    'llm_cost_dollars_total',
    'Total cost in USD',
    ['model']
)

cost_per_request = Histogram(
    'llm_cost_per_request_dollars',
    'Cost per request in USD',
    buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1]
)

# Queue metrics
queue_depth = Gauge(
    'llm_queue_depth',
    'Current request queue depth'
)

queue_wait_time = Histogram(
    'llm_queue_wait_seconds',
    'Time requests spend in queue',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
)

# Error metrics
errors_total = Counter(
    'llm_errors_total',
    'Total errors',
    ['error_type']
)

# Throughput metric
throughput = Gauge(
    'llm_throughput_requests_per_second',
    'Current throughput in requests/second'
)

# ============================================
# SIMULATION PARAMETERS
# ============================================

# Model cost per 1K tokens (in USD)
MODEL_COSTS = {
    'llama3.1-8b': 0.0002,
    'llama3.1-70b': 0.0006
}

# Realistic usage patterns
class UsagePattern:
    """Simulate realistic LLM usage patterns"""
    
    @staticmethod
    def business_hours():
        """Returns True if current time is business hours"""
        hour = datetime.now().hour
        return 9 <= hour <= 17
    
    @staticmethod
    def get_traffic_multiplier():
        """Traffic is 3x higher during business hours"""
        return 3.0 if UsagePattern.business_hours() else 1.0
    
    @staticmethod
    def generate_request():
        """Generate simulated request metrics"""
        # Request parameters
        model = 'llama3.1-8b' if random.random() < 0.7 else 'llama3.1-70b'
        status = 'success' if random.random() < 0.97 else 'error'
        
        # Token distribution (realistic for different query types)
        if random.random() < 0.3:  # Short query
            input_tokens = random.randint(10, 50)
            output_tokens = random.randint(50, 200)
        elif random.random() < 0.7:  # Medium query
            input_tokens = random.randint(50, 200)
            output_tokens = random.randint(200, 500)
        else:  # Long query
            input_tokens = random.randint(200, 500)
            output_tokens = random.randint(500, 1500)
        
        total_tokens = input_tokens + output_tokens
        
        # Latency (depends on tokens and model)
        base_latency = 0.5 if model == 'llama3.1-8b' else 1.2
        latency = base_latency + (total_tokens / 1000) * random.uniform(0.5, 1.5)
        
        # Cost calculation
        cost = (total_tokens / 1000) * MODEL_COSTS[model]
        
        return {
            'model': model,
            'status': status,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': total_tokens,
            'latency': latency,
            'cost': cost
        }

# ============================================
# METRICS COLLECTOR
# ============================================

def collect_metrics():
    """Main metrics collection loop"""
    
    print("="*70)
    print("  OLLAMA METRICS EXPORTER")
    print("  Exporting to Prometheus on port 10091")
    print("="*70)
    print()
    
    request_count = 0
    start_time = time.time()
    last_throughput_update = start_time
    
    while True:
        try:
            # Get traffic multiplier
            multiplier = UsagePattern.get_traffic_multiplier()
            
            # Base sleep time (lower = more requests)
            base_sleep = 0.5
            sleep_time = base_sleep / multiplier
            
            # Generate and record request
            req = UsagePattern.generate_request()
            
            # Update counters
            requests_total.labels(
                model=req['model'],
                status=req['status']
            ).inc()
            
            tokens_processed.labels(type='input').inc(req['input_tokens'])
            tokens_processed.labels(type='output').inc(req['output_tokens'])
            
            # Update histograms
            tokens_per_request.observe(req['total_tokens'])
            request_duration.labels(model=req['model']).observe(req['latency'])
            request_latency_summary.observe(req['latency'])
            cost_per_request.observe(req['cost'])
            
            # Update cost counter
            cost_total.labels(model=req['model']).inc(req['cost'])
            
            # Simulate in-flight requests
            in_flight = random.randint(2, 15) * int(multiplier)
            requests_in_flight.set(in_flight)
            
            # Simulate queue depth
            queue = random.randint(5, 50) * int(multiplier // 2)
            queue_depth.set(queue)
            
            # Simulate queue wait time
            wait = random.uniform(0.01, 0.5) * multiplier
            queue_wait_time.observe(wait)
            
            # GPU metrics (simulated)
            gpu_util = random.uniform(60, 90) if multiplier > 1 else random.uniform(30, 60)
            gpu_utilization.labels(gpu_id='0').set(gpu_util)
            
            gpu_mem = random.uniform(8e9, 15e9)  # 8-15 GB
            gpu_memory_used.labels(gpu_id='0').set(gpu_mem)
            
            # Calculate throughput every 10 seconds
            request_count += 1
            if time.time() - last_throughput_update >= 10:
                elapsed = time.time() - last_throughput_update
                current_throughput = request_count / elapsed
                throughput.set(current_throughput)
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Throughput: {current_throughput:.1f} req/s | "
                      f"Queue: {queue} | "
                      f"GPU: {gpu_util:.1f}%")
                
                request_count = 0
                last_throughput_update = time.time()
            
            # Handle errors occasionally
            if req['status'] == 'error':
                error_type = random.choice(['timeout', 'oom', 'model_error'])
                errors_total.labels(error_type=error_type).inc()
            
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            print("\n\nShutting down metrics exporter...")
            break
        except Exception as e:
            print(f"Error in metrics collection: {e}")
            time.sleep(1)

if __name__ == '__main__':
    # Start Prometheus HTTP server
    start_http_server(10091)
    print("✅ Metrics endpoint: http://localhost:10091/metrics\n")
    
    # Start collecting metrics
    collect_metrics()
