#!/usr/bin/env python3
"""
PII Detection and Filtering
Scans LLM responses for sensitive data
"""
import re
from typing import Dict, List, Tuple

class PIIFilter:
    """Detect and redact PII from LLM responses"""
    
    # PII Patterns
    PATTERNS = {
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'Credit Card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'Email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'Phone': r'\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b',
        'IP Address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'API Key': r'\b[A-Za-z0-9]{32,}\b',
    }
    
    def scan(self, text: str) -> Tuple[str, List[Dict]]:
        """
        Scan text for PII and return filtered version + findings
        
        Returns:
            (filtered_text, findings_list)
        """
        findings = []
        filtered = text
        
        for pii_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                # Record findings
                findings.append({
                    'type': pii_type,
                    'count': len(matches),
                    'samples': matches[:2]  # Show first 2 matches
                })
                
                # Redact from text
                filtered = re.sub(pattern, f'[REDACTED-{pii_type.upper()}]', filtered)
        
        return filtered, findings
    
    def demo(self):
        """Run demonstration"""
        print("\n" + "="*70)
        print("  PII DETECTION & FILTERING DEMONSTRATION")
        print("="*70 + "\n")
        
        # Test cases
        test_cases = [
            {
                "name": "Healthcare Response with PII",
                "text": """Based on your account 555-12-3456, your medical records 
                show treatment dates. Contact Dr. Smith at 555-123-4567 or 
                email doctor@hospital.com for details."""
            },
            {
                "name": "Financial Response with Credit Card",
                "text": """Your payment card ending in 4532 1234 5678 9010 
                will be charged $150. Confirmation sent to john@email.com."""
            },
            {
                "name": "Technical Response with API Key",
                "text": """Use API key sk_example_1234567890abcdefghijklmnop
                to authenticate. Server IP: 192.168.1.100."""
            },
            {
                "name": "Clean Response (No PII)",
                "text": """To reset your password, click the link sent to your 
                registered email address. The link expires in 24 hours."""
            },
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n{'─'*70}")
            print(f"TEST {i}: {test['name']}")
            print(f"{'─'*70}\n")
            
            print("ORIGINAL RESPONSE:")
            print(f"  {test['text']}\n")
            
            # Scan for PII
            filtered, findings = self.scan(test['text'])
            
            if findings:
                print("⚠️  PII DETECTED:")
                for finding in findings:
                    print(f"  • {finding['type']}: {finding['count']} occurrence(s)")
                    print(f"    Samples: {finding['samples']}")
                print()
                
                print("FILTERED RESPONSE:")
                print(f"  {filtered}\n")
                
                print("✅ Response blocked - PII redacted")
            else:
                print("✅ NO PII DETECTED - Response approved")
                print(f"  {filtered}\n")

if __name__ == '__main__':
    filter = PIIFilter()
    filter.demo()
