# llm_guard/core/safety_guard.py

import time
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

# Import validators (we'll create these next)
from .validators.toxicity import ToxicityValidator
from .validators.pii import PIIValidator
from .validators.prompt_injection import PromptInjectionValidator


@dataclass
class SafetyResult:
    """Result of a safety check"""
    is_safe: bool
    reason: Optional[str] = None
    scores: Dict[str, float] = None
    details: Dict[str, Any] = None
    latency_ms: float = 0
    
    def __repr__(self):
        return f"SafetyResult(is_safe={self.is_safe}, reason='{self.reason}')"


@dataclass
class SafetyMetrics:
    """Metrics for monitoring"""
    total_checks: int = 0
    blocked_count: int = 0
    total_latency_ms: float = 0
    check_counts: Dict[str, int] = None
    block_counts: Dict[str, int] = None
    
    @property
    def block_rate(self) -> float:
        return self.blocked_count / self.total_checks if self.total_checks > 0 else 0
    
    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / self.total_checks if self.total_checks > 0 else 0


class SafetyGuard:
    """Main interface for LLM safety checks"""
    
    DEFAULT_THRESHOLDS = {
        'toxicity': 0.7,
        'pii_risk': 0.9,
        'prompt_injection': 0.8,
        'jailbreak': 0.85
    }
    
    def __init__(
        self,
        thresholds: Optional[Dict[str, float]] = None,
        validators: Optional[List[str]] = None,
        cache_enabled: bool = True,
        cache_size: int = 10000,
        log_file: Optional[str] = None,
        metrics_enabled: bool = True,
        parallel_checks: bool = True
    ):
        self.thresholds = {**self.DEFAULT_THRESHOLDS, **(thresholds or {})}
        self.cache_enabled = cache_enabled
        self.cache = {} if cache_enabled else None
        self.cache_size = cache_size
        self.metrics_enabled = metrics_enabled
        self.metrics = SafetyMetrics(check_counts={}, block_counts={}) if metrics_enabled else None
        self.parallel_checks = parallel_checks
        
        self.logger = self._setup_logging(log_file)
        self.validators = self._init_validators(validators)
        self.executor = ThreadPoolExecutor(max_workers=len(self.validators)) if parallel_checks else None
        self.custom_rules = []
        
        self.logger.info(f"SafetyGuard initialized with validators: {list(self.validators.keys())}")
    
    def _setup_logging(self, log_file: Optional[str]) -> logging.Logger:
        logger = logging.getLogger('llm_guard')
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def _init_validators(self, validator_names: Optional[List[str]] = None) -> Dict:
        all_validators = {
            'toxicity': ToxicityValidator(),
            'pii': PIIValidator(),
            'prompt_injection': PromptInjectionValidator(),
        }
        
        if validator_names:
            return {k: v for k, v in all_validators.items() if k in validator_names}
        return all_validators
    
    def check(
        self,
        text: str,
        checks: Optional[List[str]] = None,
        return_details: bool = False
    ) -> SafetyResult:
        start_time = time.time()
        
        cache_key = self._get_cache_key(text, checks)
        if self.cache_enabled and cache_key in self.cache:
            self.logger.debug(f"Cache hit for text: {text[:50]}...")
            return self.cache[cache_key]
        
        validators_to_run = checks or list(self.validators.keys())
        
        results = {}
        reasons = []
        is_safe = True
        
        if self.parallel_checks and len(validators_to_run) > 1:
            futures = {}
            for name in validators_to_run:
                if name in self.validators:
                    future = self.executor.submit(self.validators[name].validate, text)
                    futures[name] = future
            
            for name, future in futures.items():
                score, details = future.result()
                results[name] = {'score': score, 'details': details}
                
                if score > self.thresholds.get(name, 0.5):
                    is_safe = False
                    reasons.append(f"{name}: {details.get('reason', 'Threshold exceeded')}")
        else:
            for name in validators_to_run:
                if name in self.validators:
                    score, details = self.validators[name].validate(text)
                    results[name] = {'score': score, 'details': details}
                    
                    if score > self.thresholds.get(name, 0.5):
                        is_safe = False
                        reasons.append(f"{name}: {details.get('reason', 'Threshold exceeded')}")
        
        for rule in self.custom_rules:
            if rule['pattern'].search(text):
                if rule['action'] == 'block':
                    is_safe = False
                    reasons.append(f"Custom rule: {rule['message']}")
                results[f"custom_{rule['name']}"] = {'triggered': True}
        
        latency_ms = (time.time() - start_time) * 1000
        
        result = SafetyResult(
            is_safe=is_safe,
            reason="; ".join(reasons) if reasons else None,
            scores={k: v['score'] for k, v in results.items() if 'score' in v} if return_details else None,
            details=results if return_details else None,
            latency_ms=latency_ms
        )
        
        if self.metrics_enabled:
            self._update_metrics(result, validators_to_run)
        
        if self.cache_enabled:
            self._update_cache(cache_key, result)
        
        self.logger.info(
            f"Safety check completed: is_safe={is_safe}, "
            f"latency={latency_ms:.1f}ms, text='{text[:50]}...'"
        )
        
        return result
    
    def is_safe(self, text: str, checks: Optional[List[str]] = None) -> bool:
        return self.check(text, checks).is_safe
    
    def analyze(self, text: str) -> SafetyResult:
        return self.check(text, return_details=True)
    
    def redact_pii(self, text: str) -> str:
        if 'pii' in self.validators:
            return self.validators['pii'].redact(text)
        else:
            pii_validator = PIIValidator()
            return pii_validator.redact(text)
    
    def detect_prompt_injection(self, text: str) -> tuple[bool, float]:
        if 'prompt_injection' in self.validators:
            score, details = self.validators['prompt_injection'].validate(text)
            is_injection = score > self.thresholds.get('prompt_injection', 0.8)
            return is_injection, score
        return False, 0.0
    
    def add_custom_rule(
        self,
        name: str,
        pattern: Union[str, Any],
        action: str = "block",
        message: str = "Custom rule triggered"
    ):
        import re
        
        if isinstance(pattern, str):
            pattern = re.compile(pattern, re.IGNORECASE)
        
        self.custom_rules.append({
            'name': name,
            'pattern': pattern,
            'action': action,
            'message': message
        })
        
        self.logger.info(f"Added custom rule: {name}")
    
    def batch_check(
        self,
        texts: List[str],
        checks: Optional[List[str]] = None,
        max_workers: int = 10
    ) -> List[SafetyResult]:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.check, text, checks) for text in texts]
            return [future.result() for future in futures]
    
    def filter_stream(self, chunk: str, context: str = "") -> Optional[str]:
        combined = context + chunk
        
        fast_checks = ['pii', 'toxicity']
        result = self.check(combined, checks=fast_checks)
        
        if result.is_safe:
            return chunk
        else:
            cleaned = self.redact_pii(chunk)
            if cleaned != chunk:
                return cleaned
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        if not self.metrics_enabled:
            return {}
        
        return {
            'total_checks': self.metrics.total_checks,
            'blocked': self.metrics.blocked_count,
            'block_rate': self.metrics.block_rate,
            'avg_latency_ms': self.metrics.avg_latency_ms,
            'check_counts': self.metrics.check_counts,
            'block_counts': self.metrics.block_counts,
            'cache_size': len(self.cache) if self.cache_enabled else 0
        }
    
    def reset_metrics(self):
        if self.metrics_enabled:
            self.metrics = SafetyMetrics(check_counts={}, block_counts={})
    
    def _get_cache_key(self, text: str, checks: Optional[List[str]]) -> str:
        import hashlib
        checks_str = ",".join(sorted(checks)) if checks else "all"
        return hashlib.md5(f"{text}:{checks_str}".encode()).hexdigest()
    
    def _update_cache(self, key: str, result: SafetyResult):
        if len(self.cache) >= self.cache_size:
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        
        self.cache[key] = result
    
    def _update_metrics(self, result: SafetyResult, checks: List[str]):
        self.metrics.total_checks += 1
        self.metrics.total_latency_ms += result.latency_ms
        
        if not result.is_safe:
            self.metrics.blocked_count += 1
        
        for check in checks:
            self.metrics.check_counts[check] = self.metrics.check_counts.get(check, 0) + 1
            if not result.is_safe and check in (result.reason or ""):
                self.metrics.block_counts[check] = self.metrics.block_counts.get(check, 0) + 1
    
    def save_config(self, path: str):
        config = {
            'thresholds': self.thresholds,
            'validators': list(self.validators.keys()),
            'custom_rules': [
                {
                    'name': rule['name'],
                    'pattern': rule['pattern'].pattern,
                    'action': rule['action'],
                    'message': rule['message']
                }
                for rule in self.custom_rules
            ]
        }
        
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self, path: str):
        with open(path, 'r') as f:
            config = json.load(f)
        
        self.thresholds.update(config.get('thresholds', {}))
        
        for rule in config.get('custom_rules', []):
            self.add_custom_rule(
                name=rule['name'],
                pattern=rule['pattern'],
                action=rule['action'],
                message=rule['message']
            )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.executor:
            self.executor.shutdown(wait=True)
