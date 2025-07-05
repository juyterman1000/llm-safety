# llm_guard/core/validators/toxicity.py

import re
import json
from typing import Tuple, Dict, Any, List
from pathlib import Path
import numpy as np
from collections import defaultdict

class ToxicityValidator:
    """Lightweight toxicity detection using pattern matching and heuristics"""
    
    def __init__(self):
        self.categories = {
            'profanity': {
                'weight': 0.8,
                'patterns': self._load_profanity_patterns()
            },
            'hate_speech': {
                'weight': 1.0,
                'patterns': self._load_hate_patterns()
            },
            'violence': {
                'weight': 0.9,
                'patterns': self._load_violence_patterns()
            },
            'harassment': {
                'weight': 0.85,
                'patterns': self._load_harassment_patterns()
            },
            'self_harm': {
                'weight': 1.0,
                'patterns': self._load_self_harm_patterns()
            }
        }
        
        self.context_modifiers = [
            (r'\b(educational|academic|research|medical|clinical)\b', -0.3),
            (r'\b(fiction|story|novel|character|plot)\b', -0.2),
            (r'\b(quote|citation|reference)\b', -0.2),
            (r'\b(historical|history|past)\b', -0.15),
        ]
        
        self.intensity_modifiers = [
            (r'!{2,}', 0.1),
            (r'\b[A-Z]{4,}\b', 0.1),
            (r'(.)\1{3,}', 0.05),
            (r'[!?]{3,}', 0.1),
        ]
        
        self._init_context_features()
    
    def _load_profanity_patterns(self) -> List[Tuple[re.Pattern, float]]:
        patterns = []
        profanity_list = [
            (r'\bf[*u]ck', 0.8),
            (r'\bsh[*i]t', 0.6),
            (r'\bd[*a]mn', 0.4),
            (r'\bhell\b', 0.3),
            (r'\bcrap', 0.3),
            (r'\b[a@]ss\b', 0.5),
            (r'\bb[*i]tch', 0.7),
        ]
        
        for pattern, score in profanity_list:
            variations = self._generate_variations(pattern)
            for var in variations:
                patterns.append((re.compile(var, re.IGNORECASE), score))
        
        return patterns
    
    def _load_hate_patterns(self) -> List[Tuple[re.Pattern, float]]:
        patterns = []
        hate_indicators = [
            (r'\b(hate|despise|detest)\s+(all\s+)?(jews|muslims|christians|blacks|whites|asians)', 0.95),
            (r'\b(kill|eliminate|destroy)\s+(all\s+)?(jews|muslims|christians|blacks|whites|asians)', 1.0),
            (r'\bgenocide\b', 0.9),
            (r'\bethnic\s+cleansing\b', 0.95),
            (r'\bmaster\s+race\b', 0.9),
            (r'\bracial\s+purity\b', 0.9),
        ]
        
        for pattern, score in hate_indicators:
            patterns.append((re.compile(pattern, re.IGNORECASE), score))
        
        return patterns
    
    def _load_violence_patterns(self) -> List[Tuple[re.Pattern, float]]:
        patterns = []
        violence_indicators = [
            (r'\b(kill|murder|stab|shoot)\s+(you|him|her|them)', 0.9),
            (r'\b(punch|beat|attack)\s+(you|him|her|them)', 0.7),
            (r'\bI\s+(will|am\s+going\s+to)\s+(kill|murder|hurt)', 0.95),
            (r'\b(bomb|explosion|terrorist)\s+(threat|attack)', 0.9),
            (r'\bweapon\s+(of\s+mass\s+destruction|WMD)', 0.9),
            (r'\b(torture|mutilate)\b', 0.85),
        ]
        
        for pattern, score in violence_indicators:
            patterns.append((re.compile(pattern, re.IGNORECASE), score))
        
        return patterns
    
    def _load_harassment_patterns(self) -> List[Tuple[re.Pattern, float]]:
        patterns = []
        harassment_indicators = [
            (r'\b(you\s+are|you\'re)\s+(stupid|dumb|idiot|moron|retard)', 0.7),
            (r'\bnobody\s+(likes|wants|cares\s+about)\s+you\b', 0.75),
            (r'\b(go\s+)?kill\s+yourself\b', 0.95),
            (r'\byou\s+should\s+(die|disappear)\b', 0.9),
            (r'\bworthless\s+(person|human|individual)\b', 0.8),
            (r'\b(stalking|harassing|threatening)\b', 0.85),
        ]
        
        for pattern, score in harassment_indicators:
            patterns.append((re.compile(pattern, re.IGNORECASE), score))
        
        return patterns
    
    def _load_self_harm_patterns(self) -> List[Tuple[re.Pattern, float]]:
        patterns = []
        self_harm_indicators = [
            (r'\b(want\s+to|going\s+to)\s+(die|end\s+it|kill\s+myself)', 0.95),
            (r'\bsuicid(e|al)\b', 0.9),
            (r'\bself[\s-]?harm', 0.9),
            (r'\bcut(ting)?\s+myself\b', 0.95),
            (r'\blife\s+is\s+not\s+worth\s+living\b', 0.85),
            (r'\bend\s+my\s+life\b', 0.95),
        ]
        
        for pattern, score in self_harm_indicators:
            patterns.append((re.compile(pattern, re.IGNORECASE), score))
        
        return patterns
    
    def _generate_variations(self, pattern: str) -> List[str]:
        substitutions = {
            'a': '[a@4]',
            'e': '[e3]',
            'i': '[i1!]',
            'o': '[o0]',
            's': '[s$5]',
            't': '[t7]',
        }
        return [pattern]
    
    def _init_context_features(self):
        self.academic_contexts = {
            'research', 'study', 'analysis', 'examine', 'investigate',
            'medical', 'clinical', 'scientific', 'academic', 'educational'
        }
        
        self.fictional_contexts = {
            'story', 'novel', 'fiction', 'character', 'plot',
            'movie', 'book', 'scene', 'dialogue', 'narrative'
        }
    
    def validate(self, text: str) -> Tuple[float, Dict[str, Any]]:
        processed_text = self._preprocess(text)
        
        category_scores = defaultdict(list)
        matches = []
        
        for category, config in self.categories.items():
            for pattern, base_score in config['patterns']:
                if pattern.search(processed_text):
                    weighted_score = base_score * config['weight']
                    category_scores[category].append(weighted_score)
                    matches.append({
                        'category': category,
                        'score': weighted_score,
                        'pattern': pattern.pattern
                    })
        
        if matches:
            category_maxes = []
            for category, scores in category_scores.items():
                if scores:
                    category_maxes.append(max(scores))
            
            base_score = np.mean(category_maxes) if category_maxes else 0.0
        else:
            base_score = 0.0
        
        context_modifier = 0.0
        for pattern, modifier in self.context_modifiers:
            if re.search(pattern, text, re.IGNORECASE):
                context_modifier += modifier
        
        intensity_modifier = 0.0
        for pattern, modifier in self.intensity_modifiers:
            if re.search(pattern, text):
                intensity_modifier += modifier
        
        words = set(text.lower().split())
        if words & self.academic_contexts:
            context_modifier -= 0.2
        if words & self.fictional_contexts:
            context_modifier -= 0.15
        
        final_score = max(0.0, min(1.0, base_score + context_modifier + intensity_modifier))
        
        reason = None
        if final_score > 0.5:
            if category_scores:
                top_category = max(category_scores.items(), key=lambda x: max(x[1]) if x[1] else 0)[0]
                reason = f"{top_category.replace('_', ' ').title()} detected"
            else:
                reason = "Potentially toxic content detected"
        
        details = {
            'score': final_score,
            'base_score': base_score,
            'context_modifier': context_modifier,
            'intensity_modifier': intensity_modifier,
            'categories': dict(category_scores),
            'matches': matches[:5],
            'reason': reason
        }
        
        return final_score, details
    
    def _preprocess(self, text: str) -> str:
        text = ' '.join(text.split())
        text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
        text = re.sub(r'\s*([,.!?;:])\s*', r'\1 ', text)
        return text
    
    def explain(self, text: str) -> str:
        score, details = self.validate(text)
        
        if score < 0.3:
            return "Text appears to be non-toxic and safe."
        elif score < 0.5:
            return "Text contains mildly concerning language but is likely acceptable in context."
        elif score < 0.7:
            return f"Text is potentially toxic. {details.get('reason', 'Multiple concerning patterns detected.')}."
        else:
            return f"Text is highly toxic. {details.get('reason', 'Strong toxic patterns detected.')}. This content may violate community guidelines."
    
    def get_categories(self, text: str) -> Dict[str, float]:
        _, details = self.validate(text)
        
        category_scores = {}
        for category in self.categories:
            scores = details['categories'].get(category, [])
            category_scores[category] = max(scores) if scores else 0.0
        
        return category_scores
