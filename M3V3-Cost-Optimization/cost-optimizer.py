#!/usr/bin/env python3
"""
LLM Cost Optimization - Hybrid Architecture
Local Ollama (8B) + Cerebras Cloud (70B)
Demonstrates: Caching, Model Routing, Hybrid Cloud Strategy
"""
import redis
import hashlib
import json
import time
import requests
import os

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'
RED = '\033[91m'

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
CEREBRAS_URL = "https://api.cerebras.ai/v1/chat/completions"
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

# Model costs per 1K tokens
MODEL_COSTS = {
    'llama3.1-8b-local': {
        'input': 0.0001,   # Local hosting cost amortized
        'output': 0.0002,
        'label': '8B (Local Ollama)'
    },
    'llama3.3-70b-cloud': {
        'input': 0.0006,   # Cerebras pricing
        'output': 0.0006,
        'label': '70B (Cerebras Cloud)'
    }
}

class CostOptimizer:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=5, decode_responses=True)
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'local_model': 0,
            'cloud_model': 0,
            'total_cost': 0.0,
            'baseline_cost': 0.0,
            'total_latency': 0.0
        }

    def get_cache_key(self, query: str) -> str:
        return "llm:" + hashlib.sha256(query.encode()).hexdigest()[:16]

    def route_model(self, query: str) -> str:
        """Route based on query complexity"""
        complex_keywords = [
            'analyze', 'explain', 'compare', 'detail', 'step-by-step',
            'architecture', 'trade-off', 'advantage', 'disadvantage',
            'evaluate', 'assess', 'comprehensive'
        ]

        word_count = len(query.split())
        has_complex_keyword = any(kw in query.lower() for kw in complex_keywords)

        # Route to cloud if complex query
        if word_count > 12 or has_complex_keyword:
            return 'llama3.3-70b-cloud'
        else:
            return 'llama3.1-8b-local'

    def call_ollama(self, prompt: str) -> dict:
        """Call local Ollama"""
        response = requests.post(
            OLLAMA_URL,
            json={"model": "llama3.1:8b", "prompt": prompt, "stream": False},
            timeout=30
        )
        return response.json()

    def call_cerebras(self, prompt: str) -> dict:
        """Call Cerebras Cloud API"""
        headers = {
            "Authorization": f"Bearer {CEREBRAS_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama3.3-70b",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.7
        }

        response = requests.post(
            CEREBRAS_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        return response.json()

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost"""
        cost = (
            (prompt_tokens / 1000) * MODEL_COSTS[model]['input'] +
            (completion_tokens / 1000) * MODEL_COSTS[model]['output']
        )
        return cost

    def process_query(self, query_num: int, query: str):
        """Process query with optimization"""
        cache_key = self.get_cache_key(query)

        # Check cache first
        cached = self.redis_client.get(cache_key)

        if cached:
            # CACHE HIT - FREE!
            self.stats['cache_hits'] += 1
            data = json.loads(cached)

            print(f"\n{CYAN}[{query_num:2d}] 📦 CACHED (Redis){RESET}")
            print(f"     Query: {query[:60]}{'...' if len(query) > 60 else ''}")
            print(f"     Source: {BOLD}Redis Cache{RESET}  | Cost: {GREEN}$0.0000{RESET}   | Latency: {BLUE}~2ms{RESET}")
            print(f"     Response: {data['response'][:80]}...")
            time.sleep(0.1)

        else:
            # CACHE MISS - Route to appropriate model
            self.stats['cache_misses'] += 1
            model = self.route_model(query)
            start = time.time()

            if 'local' in model:
                # LOCAL OLLAMA
                self.stats['local_model'] += 1
                emoji = "🔹"
                model_label = f"{GREEN}LOCAL{RESET} - 8B Ollama"

                print(f"\n{YELLOW}[{query_num:2d}] {emoji} {model_label}{RESET}")
                print(f"     Query: {query[:60]}{'...' if len(query) > 60 else ''}")
                print(f"     Routing: Simple query → Local Ollama")
                print(f"     Calling...", end='', flush=True)

                result = self.call_ollama(query)
                latency = time.time() - start

                prompt_tokens = result.get('prompt_eval_count', len(query.split()) * 1.3)
                completion_tokens = result.get('eval_count', 50)
                response_text = result.get('response', '')[:200]

            else:
                # CLOUD CEREBRAS
                self.stats['cloud_model'] += 1
                emoji = "🔸"
                model_label = f"{BLUE}CLOUD{RESET} - 70B Cerebras"

                print(f"\n{YELLOW}[{query_num:2d}] {emoji} {model_label}{RESET}")
                print(f"     Query: {query[:60]}{'...' if len(query) > 60 else ''}")
                print(f"     Routing: Complex query → Cerebras Cloud")
                print(f"     Calling...", end='', flush=True)

                result = self.call_cerebras(query)
                latency = time.time() - start

                usage = result.get('usage', {})
                prompt_tokens = usage.get('prompt_tokens', len(query.split()) * 1.3)
                completion_tokens = usage.get('completion_tokens', 50)
                response_text = result['choices'][0]['message']['content'][:200]

            # Calculate costs
            cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
            baseline_cost = self.calculate_cost('llama3.3-70b-cloud', prompt_tokens, completion_tokens)
            savings = baseline_cost - cost

            self.stats['total_cost'] += cost
            self.stats['baseline_cost'] += baseline_cost
            self.stats['total_latency'] += latency

            print(f"\r     Cost: {GREEN}${cost:.4f}{RESET}   | Latency: {BLUE}{latency:.2f}s{RESET}   | Tokens: {int(prompt_tokens)}→{int(completion_tokens)}")

            if savings > 0 and 'local' in model:
                print(f"     💰 Saved ${savings:.4f} vs always using Cloud 70B")

            print(f"     Response: {response_text}...")

            # Cache the result
            cache_data = {
                'model': model,
                'cost': cost,
                'response': response_text,
                'tokens': {'prompt': prompt_tokens, 'completion': completion_tokens}
            }
            self.redis_client.setex(cache_key, 3600, json.dumps(cache_data))

            time.sleep(0.3)

    def print_results(self):
        """Print final results"""
        total = self.stats['cache_hits'] + self.stats['cache_misses']
        cache_rate = (self.stats['cache_hits'] / total * 100) if total > 0 else 0

        savings = self.stats['baseline_cost'] - self.stats['total_cost']
        savings_pct = (savings / self.stats['baseline_cost'] * 100) if self.stats['baseline_cost'] > 0 else 0

        # Project to 1M requests
        scale = 1_000_000 / total if total > 0 else 0
        monthly_opt = self.stats['total_cost'] * scale
        monthly_base = self.stats['baseline_cost'] * scale
        monthly_save = savings * scale

        print(f"\n{'='*75}")
        print(f"{BOLD}  COST OPTIMIZATION RESULTS - HYBRID ARCHITECTURE{RESET}")
        print(f"{'='*75}\n")

        print(f"  {BOLD}Architecture:{RESET}")
        print(f"    • Simple Queries  → {GREEN}Local Ollama 8B{RESET} (on-premise, cheap)")
        print(f"    • Complex Queries → {BLUE}Cerebras Cloud 70B{RESET} (cloud API, powerful)")
        print(f"    • Duplicates      → {CYAN}Redis Cache{RESET} (free, instant)\n")

        print(f"  {BOLD}Request Distribution:{RESET}")
        print(f"    Total Requests:     {total}")
        print(f"    {CYAN}Cache Hits (Free):{RESET}   {self.stats['cache_hits']} ({cache_rate:.1f}%)")
        print(f"    {GREEN}Local 8B Model:{RESET}      {self.stats['local_model']}")
        print(f"    {BLUE}Cloud 70B Model:{RESET}     {self.stats['cloud_model']}\n")

        print(f"  {BOLD}Cost Analysis:{RESET}")
        print(f"    With Optimization:    {GREEN}${self.stats['total_cost']:.4f}{RESET}")
        print(f"    Without (All Cloud):  {RED}${self.stats['baseline_cost']:.4f}{RESET}")
        print(f"    Savings:              {GREEN}${savings:.4f} ({savings_pct:.1f}%){RESET}\n")

        print(f"  {BOLD}Projected Monthly (1M requests):{RESET}")
        print(f"    With Optimization:    {GREEN}${monthly_opt:.2f}{RESET}")
        print(f"    Without (All Cloud):  {RED}${monthly_base:.2f}{RESET}")
        print(f"    {BOLD}Monthly Savings:      {GREEN}${monthly_save:.2f}{RESET}\n")

        avg_latency = self.stats['total_latency'] / self.stats['cache_misses'] if self.stats['cache_misses'] > 0 else 0
        print(f"  {BOLD}Performance:{RESET}")
        print(f"    Avg Latency:          {avg_latency:.2f}s per request")
        print(f"    Cache Response Time:  ~2ms\n")

        print(f"{'='*75}\n")

def main():
    if not CEREBRAS_API_KEY:
        print(f"\n{RED}ERROR: CEREBRAS_API_KEY not set{RESET}")
        print("Set it with: export CEREBRAS_API_KEY='your_key'\n")
        return

    print(f"\n{'='*75}")
    print(f"{BOLD}  LLM COST OPTIMIZATION - HYBRID CLOUD ARCHITECTURE{RESET}")
    print(f"  Local Ollama (8B) + Cerebras Cloud (70B) + Redis Cache")
    print(f"{'='*75}\n")

    opt = CostOptimizer()

    queries = [
        # Simple → Local Ollama 8B
        "What is 2+2?",
        "What is the capital of France?",
        "Who wrote Hamlet?",
        "What year did WWII end?",

        # Complex → Cerebras Cloud 70B
        "Analyze the trade-offs between microservices and monolithic architecture in detail.",
        "Explain step-by-step how transformer attention mechanisms work in modern LLMs.",

        # Duplicates → Redis Cache (FREE)
        "What is 2+2?",
        "Analyze the trade-offs between microservices and monolithic architecture in detail.",
    ]

    print(f"Processing {len(queries)} queries...\n{'─'*75}")

    for i, q in enumerate(queries, 1):
        try:
            opt.process_query(i, q)
        except Exception as e:
            print(f"\n{RED}Error processing query {i}: {e}{RESET}")

    print(f"\n{'─'*75}")
    opt.print_results()

    print(f"{BOLD}Key Insights:{RESET}")
    print(f"  • Hybrid architecture = Best of both worlds")
    print(f"  • Redis caching = Instant responses, zero cost")
    print(f"  • Intelligent routing = Right model for right job")
    print(f"  • Real production strategy used by enterprises\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Demo stopped{RESET}\n")
