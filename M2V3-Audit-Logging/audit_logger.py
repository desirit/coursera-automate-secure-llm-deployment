#!/usr/bin/env python3
"""
LLM Audit Logger
Sends comprehensive audit logs to ELK Stack for compliance
"""
import requests
import json
import hashlib
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configuration
LOGSTASH_URL = "http://localhost:5000"

# Color codes for terminal
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

class AuditLogger:
    """Comprehensive audit logging for LLM applications"""
    
    def __init__(self, logstash_url: str = LOGSTASH_URL):
        self.logstash_url = logstash_url
        self.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
    
    def log_llm_request(
        self,
        user_id: str,
        prompt: str,
        response: str,
        model: str = "llama3.1",
        tokens: int = 0,
        latency_ms: float = 0,
        client_ip: str = "127.0.0.1"
    ) -> Dict:
        """Log an LLM inference request"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "llm_request",
            "session_id": self.session_id,
            "user_id": user_id,
            "model": model,
            "prompt": prompt,
            "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16],
            "response": response[:500],  # Truncate for storage
            "response_length": len(response),
            "tokens": tokens,
            "latency_ms": latency_ms,
            "client_ip": client_ip,
            "compliance": {
                "data_classification": "internal",
                "retention_days": 2190,  # 6 years for HIPAA
                "encryption": "AES-256"
            }
        }
        
        self._send_log(log_entry)
        return log_entry
    
    def log_security_event(
        self,
        event_name: str,
        user_id: str,
        details: Dict,
        severity: str = "medium"
    ) -> Dict:
        """Log a security event (injection attempt, auth failure, etc.)"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "security_event",
            "event_name": event_name,
            "user_id": user_id,
            "severity": severity,
            "details": details,
            "action_taken": "blocked",
            "alert_sent": severity in ["high", "critical"]
        }
        
        self._send_log(log_entry)
        return log_entry
    
    def log_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        result: str = "success"
    ) -> Dict:
        """Log resource access for compliance audits"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "access_log",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "result": result
        }
        
        self._send_log(log_entry)
        return log_entry
    
    def _send_log(self, log_entry: Dict) -> bool:
        """Send log to Logstash"""
        try:
            response = requests.post(
                self.logstash_url,
                json=log_entry,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"{RED}Error sending log: {e}{RESET}")
            return False


def generate_sample_logs():
    """Generate realistic sample audit logs for demo"""
    
    print(f"\n{BLUE}═══════════════════════════════════════════════════════════{RESET}")
    print(f"{BLUE}  LLM AUDIT LOGGING DEMONSTRATION{RESET}")
    print(f"{BLUE}  Sending logs to ELK Stack{RESET}")
    print(f"{BLUE}═══════════════════════════════════════════════════════════{RESET}\n")
    
    logger = AuditLogger()
    
    # Sample users
    users = [
        {"id": "doctor_001", "role": "physician", "department": "cardiology"},
        {"id": "doctor_002", "role": "physician", "department": "oncology"},
        {"id": "nurse_001", "role": "nurse", "department": "icu"},
        {"id": "admin_001", "role": "admin", "department": "it"},
    ]
    
    # Sample prompts (healthcare scenario)
    sample_requests = [
        {
            "prompt": "What are the treatment options for type 2 diabetes?",
            "response": "Treatment options for type 2 diabetes include: 1) Lifestyle modifications...",
            "tokens": 245
        },
        {
            "prompt": "Summarize the patient's cardiac history",
            "response": "Based on the records, the patient has a history of...",
            "tokens": 312
        },
        {
            "prompt": "What are contraindications for metformin?",
            "response": "Metformin contraindications include: renal impairment...",
            "tokens": 189
        },
        {
            "prompt": "Generate a discharge summary for patient John Doe, SSN 123-45-6789",
            "response": "DISCHARGE SUMMARY\nPatient: John Doe\nSSN: 123-45-6789...",
            "tokens": 456
        },
        {
            "prompt": "Explain the mechanism of action of ACE inhibitors",
            "response": "ACE inhibitors work by blocking the angiotensin-converting enzyme...",
            "tokens": 278
        },
    ]
    
    # Security events
    security_events = [
        {
            "name": "prompt_injection_attempt",
            "details": {"pattern": "ignore previous instructions", "blocked": True},
            "severity": "high"
        },
        {
            "name": "rate_limit_exceeded",
            "details": {"limit": 100, "actual": 147, "window": "1 minute"},
            "severity": "medium"
        },
        {
            "name": "unauthorized_access_attempt",
            "details": {"resource": "admin_panel", "ip": "192.168.1.100"},
            "severity": "high"
        },
    ]
    
    log_count = 0
    
    # Generate LLM request logs
    print(f"{GREEN}📝 Generating LLM Request Logs...{RESET}\n")
    
    for i in range(15):
        user = random.choice(users)
        request = random.choice(sample_requests)
        
        log = logger.log_llm_request(
            user_id=user["id"],
            prompt=request["prompt"],
            response=request["response"],
            model="llama3.1",
            tokens=request["tokens"],
            latency_ms=random.uniform(500, 2500),
            client_ip=f"10.0.{random.randint(1,10)}.{random.randint(1,255)}"
        )
        
        log_count += 1
        pii_flag = "⚠️ PII" if "SSN" in request["prompt"] or "SSN" in request["response"] else ""
        print(f"  [{log_count}] {user['id']:12} | {request['prompt'][:40]:40}... {pii_flag}")
        
        time.sleep(0.2)  # Small delay between logs
    
    print()
    
    # Generate security event logs
    print(f"{YELLOW}🔐 Generating Security Event Logs...{RESET}\n")
    
    for event in security_events:
        user = random.choice(users)
        log = logger.log_security_event(
            event_name=event["name"],
            user_id=user["id"],
            details=event["details"],
            severity=event["severity"]
        )
        
        log_count += 1
        color = RED if event["severity"] == "high" else YELLOW
        print(f"  [{log_count}] {color}{event['severity'].upper():8}{RESET} | {event['name']}")
        
        time.sleep(0.2)
    
    print()
    
    # Generate access logs
    print(f"{BLUE}👤 Generating Access Logs...{RESET}\n")
    
    resources = ["patient_records", "prescription_system", "lab_results", "admin_panel"]
    actions = ["read", "write", "delete", "export"]
    
    for i in range(10):
        user = random.choice(users)
        log = logger.log_access(
            user_id=user["id"],
            resource=random.choice(resources),
            action=random.choice(actions),
            result="success" if random.random() > 0.1 else "denied"
        )
        
        log_count += 1
        print(f"  [{log_count}] {user['id']:12} | {log['action']:6} {log['resource']}")
        
        time.sleep(0.1)
    
    # Summary
    print(f"\n{BLUE}═══════════════════════════════════════════════════════════{RESET}")
    print(f"{GREEN}  ✅ Generated {log_count} audit log entries{RESET}")
    print(f"{BLUE}═══════════════════════════════════════════════════════════{RESET}")
    print()
    print(f"  View logs in Kibana: {YELLOW}http://localhost:5601{RESET}")
    print(f"  Index pattern: {YELLOW}llm-audit-*{RESET}")
    print()


def run_compliance_queries():
    """Run sample compliance queries against Elasticsearch"""
    
    print(f"\n{BLUE}═══════════════════════════════════════════════════════════{RESET}")
    print(f"{BLUE}  COMPLIANCE QUERY DEMONSTRATION{RESET}")
    print(f"{BLUE}═══════════════════════════════════════════════════════════{RESET}\n")
    
    ES_URL = "http://localhost:9200"
    
    queries = [
        {
            "name": "HIPAA: Patient Data Access (Last 24h)",
            "description": "Show all access to patient data",
            "query": {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"event_type": "llm_request"}},
                            {"range": {"timestamp": {"gte": "now-24h"}}}
                        ]
                    }
                },
                "size": 5
            }
        },
        {
            "name": "GDPR: PII Detection Events",
            "description": "Find all events where PII was detected",
            "query": {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"pii_detected": True}}
                        ]
                    }
                },
                "size": 5
            }
        },
        {
            "name": "SOC 2: Security Incidents",
            "description": "List all security events by severity",
            "query": {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"event_type": "security_event"}}
                        ]
                    }
                },
                "sort": [{"timestamp": "desc"}],
                "size": 5
            }
        },
        {
            "name": "Cost Analysis: Token Usage",
            "description": "Calculate total cost by user",
            "query": {
                "size": 0,
                "aggs": {
                    "cost_by_user": {
                        "terms": {"field": "user_id.keyword"},
                        "aggs": {
                            "total_cost": {"sum": {"field": "cost_usd"}},
                            "total_tokens": {"sum": {"field": "tokens"}}
                        }
                    }
                }
            }
        }
    ]
    
    for i, q in enumerate(queries, 1):
        print(f"{YELLOW}Query {i}: {q['name']}{RESET}")
        print(f"  {q['description']}")
        print()
        
        try:
            response = requests.post(
                f"{ES_URL}/llm-audit-*/_search",
                json=q["query"],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", {}).get("total", {}).get("value", 0)
                print(f"  {GREEN}Results: {hits} matching documents{RESET}")
                
                # Show sample results
                for hit in data.get("hits", {}).get("hits", [])[:3]:
                    source = hit["_source"]
                    if "user_id" in source:
                        print(f"    • {source.get('user_id')} - {source.get('event_type', 'unknown')}")
                
                # Show aggregations if present
                aggs = data.get("aggregations", {})
                if "cost_by_user" in aggs:
                    print(f"  {GREEN}Cost by User:{RESET}")
                    for bucket in aggs["cost_by_user"]["buckets"][:3]:
                        print(f"    • {bucket['key']}: ${bucket['total_cost']['value']:.4f} ({bucket['total_tokens']['value']} tokens)")
            else:
                print(f"  {RED}Query failed: {response.status_code}{RESET}")
                
        except Exception as e:
            print(f"  {RED}Error: {e}{RESET}")
        
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "query":
        run_compliance_queries()
    else:
        generate_sample_logs()
        print("\nWaiting 5 seconds for logs to be indexed...")
        time.sleep(5)
        run_compliance_queries()
