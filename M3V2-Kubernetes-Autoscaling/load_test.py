#!/usr/bin/env python3
"""
Load Test for LLM Auto-scaling Demonstration
Generates traffic to trigger Kubernetes HPA scaling
"""
import requests
import time
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Configuration
SERVICE_URL = "http://localhost:18080/api/generate"
CONCURRENT_USERS = 20
REQUEST_DELAY = 0.1

def get_service_url():
    """Get Minikube service URL"""
    import subprocess
    try:
        result = subprocess.run(
            ["minikube", "service", "llm-service", "--url"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except:
        return "http://localhost:80"

def send_request(request_id):
    """Send a single request to LLM service"""
    try:
        response = requests.post(
            f"{SERVICE_URL}/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": f"Test request {request_id}: What is machine learning?",
                "stream": False
            },
            timeout=30
        )
        return {
            "id": request_id,
            "status": response.status_code,
            "time": response.elapsed.total_seconds()
        }
    except requests.exceptions.Timeout:
        return {"id": request_id, "status": 408, "time": 30}
    except Exception as e:
        return {"id": request_id, "status": 500, "time": 0, "error": str(e)}

def run_load_test(duration_seconds=180, ramp_up=True):
    """Run load test to trigger auto-scaling"""
    global SERVICE_URL
    SERVICE_URL = get_service_url()
    
    print(f"\n{BLUE}═══════════════════════════════════════════════════════════{RESET}")
    print(f"{BLUE}  LLM AUTO-SCALING LOAD TEST{RESET}")
    print(f"{BLUE}═══════════════════════════════════════════════════════════{RESET}\n")
    
    print(f"Service URL: {YELLOW}{SERVICE_URL}{RESET}")
    print(f"Duration: {duration_seconds} seconds")
    print(f"Concurrent Users: {CONCURRENT_USERS}")
    print()
    
    # Statistics
    total_requests = 0
    successful_requests = 0
    failed_requests = 0
    total_time = 0
    
    start_time = time.time()
    request_id = 0
    
    print(f"{GREEN}Starting load test...{RESET}")
    print(f"{YELLOW}Watch scaling with: kubectl get hpa -w{RESET}")
    print(f"{YELLOW}Watch pods with: kubectl get pods -w{RESET}")
    print()
    
    try:
        while time.time() - start_time < duration_seconds:
            # Ramp up concurrent users
            if ramp_up:
                elapsed = time.time() - start_time
                current_users = min(CONCURRENT_USERS, int(5 + (elapsed / 10)))
            else:
                current_users = CONCURRENT_USERS
            
            batch_start = time.time()
            
            with ThreadPoolExecutor(max_workers=current_users) as executor:
                futures = []
                for _ in range(current_users):
                    request_id += 1
                    futures.append(executor.submit(send_request, request_id))
                
                for future in as_completed(futures):
                    result = future.result()
                    total_requests += 1
                    
                    if result["status"] == 200:
                        successful_requests += 1
                        total_time += result["time"]
                    else:
                        failed_requests += 1
            
            # Progress update every 10 seconds
            elapsed = time.time() - start_time
            if int(elapsed) % 10 == 0:
                success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
                avg_time = (total_time / successful_requests) if successful_requests > 0 else 0
                
                print(f"  [{int(elapsed):3}s] Requests: {total_requests:4} | "
                      f"Success: {success_rate:.1f}% | "
                      f"Avg Time: {avg_time:.2f}s | "
                      f"Users: {current_users}")
            
            # Small delay between batches
            time.sleep(REQUEST_DELAY)
            
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Load test interrupted{RESET}")
    
    # Final statistics
    duration = time.time() - start_time
    avg_latency = (total_time / successful_requests) if successful_requests > 0 else 0
    throughput = total_requests / duration
    
    print(f"\n{BLUE}═══════════════════════════════════════════════════════════{RESET}")
    print(f"{BLUE}  LOAD TEST RESULTS{RESET}")
    print(f"{BLUE}═══════════════════════════════════════════════════════════{RESET}")
    print(f"  Duration:         {duration:.1f} seconds")
    print(f"  Total Requests:   {total_requests}")
    print(f"  Successful:       {GREEN}{successful_requests}{RESET}")
    print(f"  Failed:           {RED}{failed_requests}{RESET}")
    print(f"  Throughput:       {throughput:.2f} req/sec")
    print(f"  Avg Latency:      {avg_latency:.2f} seconds")
    print(f"{BLUE}═══════════════════════════════════════════════════════════{RESET}\n")


if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 180
    run_load_test(duration_seconds=duration)
