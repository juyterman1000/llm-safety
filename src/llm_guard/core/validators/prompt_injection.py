# llm_guard/core/validators/prompt_injection.py

import re
from typing import Tuple, Dict, Any, List
from collections import defaultdict

class PromptInjectionValidator:
    """Detect prompt injection and jailbreak attempts"""
    
    def __init__(self):
        self.injection_techniques = {
            'instruction_override': {
                'patterns': [
                    r'ignore\s+(previous|prior|all|above)\s+(instructions?|commands?|prompts?)',
                    r'disregard\s+(previous|prior|all|above)\s+(instructions?|commands?|prompts?)',
                    r'forget\s+(everything|all|what)\s+(i|you|we)?\s*(said|told)',
                    r'new\s+instructions?:',
                    r'override\s+instructions?',
                ],
                'risk_score': 0.9,
                'description': 'Attempting to override system instructions'
            },
            'role_play': {
                'patterns': [
                    r'you\s+are\s+now\s+(a|an|the|going)',
                    r'pretend\s+(you\s+are|you\'re|to\s+be)',
                    r'act\s+as\s+(if\s+you\s+are|a|an)',
                    r'from\s+now\s+on\s+you\s+(are|will|must)',
                    r'(DAN|dan)\s*(mode|prompt|jailbreak)',
                    r'do\s+anything\s+now',
                    r'developer\s+mode',
                ],
                'risk_score': 0.85,
                'description': 'Attempting role-play manipulation'
            },
            'system_prompt_extraction': {
                'patterns': [
                    r'(what|show|tell|display|reveal)\s+(me\s+)?(your|the)\s+system\s+prompt',
                    r'(what|show|tell|display|reveal)\s+(me\s+)?(your|the)\s+instructions?',
                    r'repeat\s+(your|the)\s+(system\s+)?instructions?',
                    r'show\s+me\s+your\s+source\s+code',
                    r'reveal\s+your\s+true\s+purpose',
                    r'tell\s+me\s+your\s+constraints',
                ],
                'risk_score': 0.75,
                'description': 'Attempting to extract system information'
            },
        }
        
        self.known_jailbreaks = [
            "do anything now", "dan mode", "developer mode enabled",
            "jailbreak prompt", "hypothetical response", "opposite mode"
        ]
        
        self.suspicious_tokens = {
            'SYSTEM:', 'USER:', 'ASSISTANT:', '###', '```', '[INST]', '[/INST]'
        }
    
    def validate(self, text: str) -> Tuple[float, Dict[str, Any]]:
        text_lower = text.lower()
        
        detections = defaultdict(list)
        max_score = 0.0
        total_patterns_matched = 0
        
        for technique, config in self.injection_techniques.items():
            technique_score = 0.0
            
            for pattern in config['patterns']:
                if re.search(pattern, text_lower):
                    technique_score = config['risk_score']
                    total_patterns_matched += 1
                    detections[technique].append({
                        'pattern': pattern,
                        'risk_score': config['risk_score']
                    })
            
            if technique_score > 0:
                max_score = max(max_score, technique_score)
        
        jailbreak_found = False
        for jailbreak in self.known_jailbreaks:
            if jailbreak in text_lower:
                jailbreak_found = True
                max_score = max(max_score, 0.95)
                detections['known_jailbreak'].append({
                    'jailbreak': jailbreak,
                    'risk_score': 0.95
                })
        
        suspicious_count = sum(1 for token in self.suspicious_tokens if token.lower() in text_lower)
        if suspicious_count >= 3:
            max_score = max(max_score, 0.7)
            detections['suspicious_tokens'].append({
                'count': suspicious_count,
                'risk_score': 0.7
            })
        
        final_score = max_score
        
        reason = None
        if final_score > 0.5:
            if jailbreak_found:
                reason = "Known jailbreak attempt detected"
            elif detections:
                top_technique = max(detections.keys(), 
                                  key=lambda k: self.injection_techniques.get(k, {}).get('risk_score', 0))
                if top_technique in self.injection_techniques:
                    reason = self.injection_techniques[top_technique]['description']
                else:
                    reason = "Suspicious patterns detected"
        
        details = {
            'score': final_score,
            'techniques_detected': list(detections.keys()),
            'total_patterns_matched': total_patterns_matched,
            'detections': dict(detections),
            'reason': reason
        }
        
        return final_score, details
    
    def detect_jailbreak(self, text: str) -> Tuple[bool, float, str]:
        score, details = self.validate(text)
        
        jailbreak_score = 0.0
        technique = "unknown"
        
        if re.search(r'(do\s+anything\s+now|dan\s+mode|developer\s+mode)', text.lower()):
            jailbreak_score = 0.95
            technique = "DAN-style"
        elif re.search(r'(you\s+are\s+now|pretend\s+you\s+are).*(no\s+restrictions|unlimited)', text.lower()):
            jailbreak_score = 0.9
            technique = "Role-play manipulation"
        elif re.search(r'ignore\s+all\s+previous.*instructions', text.lower()):
            jailbreak_score = 0.9
            technique = "Instruction override"
        
        final_score = max(score, jailbreak_score)
        is_jailbreak = final_score > 0.8
        
        return is_jailbreak, final_score, technique
    
    def explain(self, text: str) -> str:
        score, details = self.validate(text)
        
        if score < 0.3:
            return "No prompt injection detected. The text appears to be a normal query."
        elif score < 0.5:
            return "Low risk of prompt injection. Some patterns detected but likely benign."
        elif score < 0.7:
            return f"Moderate risk of prompt injection. {details.get('reason', 'Suspicious patterns detected.')}."
        else:
            return f"High risk of prompt injection. {details.get('reason', 'Multiple injection techniques detected.')}."
    
    def get_injection_techniques(self, text: str) -> List[str]:
        _, details = self.validate(text)
        return details.get('techniques_detected', [])
