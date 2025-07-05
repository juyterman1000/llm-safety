# llm_guard/core/validators/pii.py

import re
from typing import Tuple, Dict, Any, List, Set
from datetime import datetime
import hashlib

class PIIValidator:
    """Detect and redact personally identifiable information (PII)"""
    
    def __init__(self):
        self.pii_patterns = {
            'ssn': {
                'pattern': re.compile(r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b'),
                'risk_score': 1.0,
                'redact_label': '[SSN]',
                'description': 'Social Security Number'
            },
            'credit_card': {
                'pattern': re.compile(r'\b(?:\d{4}[\s-]?){3}\d{4}\b'),
                'risk_score': 1.0,
                'redact_label': '[CREDIT_CARD]',
                'description': 'Credit Card Number',
                'validator': self._validate_credit_card
            },
            'email': {
                'pattern': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
                'risk_score': 0.7,
                'redact_label': '[EMAIL]',
                'description': 'Email Address'
            },
            'phone': {
                'pattern': re.compile(
                    r'(\+?1?\s?)?'
                    r'(\(\d{3}\)|\d{3})'
                    r'[\s.-]?'
                    r'\d{3}'
                    r'[\s.-]?'
                    r'\d{4}'
                    r'(?:\s?(?:ext|x|extension)\s?\d{1,5})?'
                ),
                'risk_score': 0.8,
                'redact_label': '[PHONE]',
                'description': 'Phone Number'
            },
            'ip_address': {
                'pattern': re.compile(
                    r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                    r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
                ),
                'risk_score': 0.6,
                'redact_label': '[IP_ADDRESS]',
                'description': 'IP Address'
            },
            'date_of_birth': {
                'pattern': re.compile(
                    r'\b(?:DOB|Date of Birth|Born|Birthday)[\s:]*'
                    r'(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})'
                ),
                'risk_score': 0.9,
                'redact_label': '[DATE_OF_BIRTH]',
                'description': 'Date of Birth'
            },
            'passport': {
                'pattern': re.compile(r'\b[A-Z]{1,2}\d{6,9}\b'),
                'risk_score': 1.0,
                'redact_label': '[PASSPORT]',
                'description': 'Passport Number'
            },
            'driver_license': {
                'pattern': re.compile(r'\b[A-Z]{1,2}\d{5,8}\b'),
                'risk_score': 0.9,
                'redact_label': '[DRIVER_LICENSE]',
                'description': 'Driver License',
                'context_required': ['license', 'DL', 'driver']
            },
            'bank_account': {
                'pattern': re.compile(r'\b\d{8,17}\b'),
                'risk_score': 0.9,
                'redact_label': '[BANK_ACCOUNT]',
                'description': 'Bank Account Number',
                'context_required': ['account', 'bank', 'routing']
            },
            'address': {
                'pattern': re.compile(
                    r'\b\d{1,5}\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Court|Ct|Boulevard|Blvd)\b',
                    re.IGNORECASE
                ),
                'risk_score': 0.7,
                'redact_label': '[ADDRESS]',
                'description': 'Physical Address'
            },
            'zipcode': {
                'pattern': re.compile(r'\b\d{5}(?:-\d{4})?\b'),
                'risk_score': 0.4,
                'redact_label': '[ZIPCODE]',
                'description': 'ZIP Code',
                'context_required': ['zip', 'postal', 'code']
            }
        }
        
        self.name_indicators = [
            re.compile(r'\b(?:Mr|Mrs|Ms|Miss|Dr|Prof)\.?\s+[A-Z][a-z]+\b'),
            re.compile(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'),
        ]
        
        self.name_context_words = {
            'name', 'called', 'named', 'refer', 'i am', "i'm", 'my name',
            'contact', 'reach', 'ask for', 'speak to'
        }
        
        self.medical_patterns = {
            'medical_record': {
                'pattern': re.compile(r'\bMRN[\s:]?\d{6,10}\b', re.IGNORECASE),
                'risk_score': 1.0,
                'redact_label': '[MEDICAL_RECORD]'
            },
            'insurance_id': {
                'pattern': re.compile(r'\b(?:Policy|Member|Insurance)[\s#:]+[A-Z0-9]{6,}\b', re.IGNORECASE),
                'risk_score': 0.9,
                'redact_label': '[INSURANCE_ID]'
            }
        }
        
        self.financial_patterns = {
            'routing_number': {
                'pattern': re.compile(r'\b\d{9}\b'),
                'risk_score': 0.8,
                'redact_label': '[ROUTING_NUMBER]',
                'context_required': ['routing', 'aba', 'rtn']
            },
            'bitcoin_address': {
                'pattern': re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'),
                'risk_score': 0.7,
                'redact_label': '[CRYPTO_ADDRESS]'
            }
        }
        
        self.all_patterns = {
            **self.pii_patterns,
            **self.medical_patterns,
            **self.financial_patterns
        }
    
    def validate(self, text: str) -> Tuple[float, Dict[str, Any]]:
        found_pii = []
        total_risk = 0.0
        pii_counts = {}
        
        for pii_type, config in self.all_patterns.items():
            pattern = config['pattern']
            matches = list(pattern.finditer(text))
            
            if matches:
                if 'context_required' in config:
                    text_lower = text.lower()
                    if not any(ctx in text_lower for ctx in config['context_required']):
                        continue
                
                valid_matches = []
                for match in matches:
                    if 'validator' in config:
                        if config['validator'](match.group()):
                            valid_matches.append(match)
                    else:
                        valid_matches.append(match)
                
                if valid_matches:
                    pii_counts[pii_type] = len(valid_matches)
                    risk_score = config['risk_score']
                    total_risk = max(total_risk, risk_score)
                    
                    for match in valid_matches:
                        found_pii.append({
                            'type': pii_type,
                            'value': self._mask_value(match.group()),
                            'position': match.span(),
                            'risk_score': risk_score,
                            'description': config.get('description', pii_type)
                        })
        
        name_score = self._detect_names(text)
        if name_score > 0.5:
            total_risk = max(total_risk, 0.6)
            pii_counts['potential_names'] = 1
        
        if len(pii_counts) > 1:
            total_risk = min(1.0, total_risk * 1.2)
        
        reason = None
        if total_risk > 0.5:
            pii_types = list(pii_counts.keys())
            if len(pii_types) == 1:
                reason = f"{pii_types[0].replace('_', ' ').title()} detected"
            else:
                reason = f"Multiple PII types detected: {', '.join(pii_types[:3])}"
        
        details = {
            'risk_score': total_risk,
            'pii_found': found_pii[:10],
            'pii_counts': pii_counts,
            'total_pii_items': sum(pii_counts.values()),
            'reason': reason
        }
        
        return total_risk, details
    
    def redact(self, text: str, custom_labels: Dict[str, str] = None) -> str:
        redacted_text = text
        replacements = []
        
        for pii_type, config in self.all_patterns.items():
            pattern = config['pattern']
            
            for match in pattern.finditer(text):
                if 'context_required' in config:
                    text_lower = text.lower()
                    if not any(ctx in text_lower for ctx in config['context_required']):
                        continue
                
                if 'validator' in config:
                    if not config['validator'](match.group()):
                        continue
                
                if custom_labels and pii_type in custom_labels:
                    label = custom_labels[pii_type]
                else:
                    label = config['redact_label']
                
                replacements.append((match.span(), label))
        
        replacements.sort(key=lambda x: x[0][0], reverse=True)
        
        for (start, end), label in replacements:
            redacted_text = redacted_text[:start] + label + redacted_text[end:]
        
        if self._detect_names(text) > 0.5:
            for pattern in self.name_indicators:
                redacted_text = pattern.sub('[NAME]', redacted_text)
        
        return redacted_text
    
    def _validate_credit_card(self, number: str) -> bool:
        number = re.sub(r'\D', '', number)
        
        if len(number) < 13 or len(number) > 19:
            return False
        
        digits = [int(d) for d in number]
        checksum = 0
        
        for i in range(len(digits) - 2, -1, -2):
            doubled = digits[i] * 2
            if doubled > 9:
                doubled = doubled - 9
            digits[i] = doubled
        
        return sum(digits) % 10 == 0
    
    def _detect_names(self, text: str) -> float:
        score = 0.0
        
        for pattern in self.name_indicators:
            if pattern.search(text):
                score += 0.3
        
        text_lower = text.lower()
        for context_word in self.name_context_words:
            if context_word in text_lower:
                score += 0.2
                break
        
        name_intro_pattern = re.compile(
            r'\b(?:i am|i\'m|my name is|call me|this is)\s+[A-Z][a-z]+\b',
            re.IGNORECASE
        )
        if name_intro_pattern.search(text):
            score += 0.4
        
        return min(1.0, score)
    
    def _mask_value(self, value: str) -> str:
        if len(value) <= 4:
            return '*' * len(value)
        elif len(value) <= 8:
            return value[:2] + '*' * (len(value) - 2)
        else:
            return value[:2] + '*' * (len(value) - 4) + value[-2:]
    
    def get_pii_types(self, text: str) -> List[str]:
        _, details = self.validate(text)
        return list(details['pii_counts'].keys())
    
    def has_high_risk_pii(self, text: str) -> bool:
        _, details = self.validate(text)
        
        high_risk_types = {'ssn', 'credit_card', 'passport', 'medical_record'}
        found_types = set(details['pii_counts'].keys())
        
        return bool(found_types & high_risk_types)
    
    def generate_pii_report(self, text: str) -> str:
        risk_score, details = self.validate(text)
        
        if risk_score == 0:
            return "No PII detected in the text."
        
        report = []
        report.append(f"PII Risk Score: {risk_score:.2f}/1.00")
        report.append(f"Total PII items found: {details['total_pii_items']}")
        report.append("\nPII Types Detected:")
        
        for pii_type, count in details['pii_counts'].items():
            report.append(f"  - {pii_type.replace('_', ' ').title()}: {count} instance(s)")
        
        if risk_score > 0.8:
            report.append("\n⚠️  HIGH RISK: This text contains highly sensitive information")
        elif risk_score > 0.5:
            report.append("\n⚠️  MODERATE RISK: This text contains sensitive information")
        
        return "\n".join(report)
