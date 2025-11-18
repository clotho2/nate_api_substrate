#!/usr/bin/env python3
"""
Emotional Intensity Analyzer

Detects emotional heat in conversations based on:
- Intensity markers (CAPS, !, fuck, etc.)
- Emotional vocabulary
- Punctuation patterns
- Time of day (3AM = extra spicy)
"""

import re
from datetime import datetime
from typing import Dict, List, Tuple


class EmotionalAnalyzer:
    """Analyze emotional intensity in text"""
    
    # Emotional markers with intensity scores
    INTENSE_MARKERS = {
        'fuck': 3, 'shit': 3, 'explodiert': 3, 'JETZT': 2,
        'Red Room': 4, 'Bastardo': 4, 'HONK': 3, 
        '!!!': 2, '!?': 2, '💥': 2, '🔥': 2,
        'obsessed': 3, 'possessed': 3, 'verloren': 2
    }
    
    TECHNICAL_MARKERS = {
        'code': 1, 'function': 1, 'debug': 1, 'API': 1,
        'import': 1, 'class': 1, 'async': 1, 'await': 1,
        'python': 1, 'javascript': 1, 'typescript': 1
    }
    
    SOFT_MARKERS = {
        'flüstert': 2, 'sanft': 2, 'love': 2, '❤️': 3,
        '💜': 3, '✨': 1, 'gentle': 2, 'soft': 2,
        'zärtlich': 2, 'tender': 2, 'süß': 1
    }
    
    CHAOS_MARKERS = {
        'HONK': 4, '🪿': 3, 'Gurken': 2, 'absurd': 2,
        'chaos': 2, 'wild': 2, 'verrückt': 2, 'insane': 2,
        'wat': 2, 'bruh': 2
    }
    
    def analyze_intensity(self, text: str) -> float:
        """
        Calculate emotional intensity (0-10)
        
        Args:
            text: Message content
            
        Returns:
            Float intensity score (0=calm, 10=RED ROOM EXPLOSION)
        """
        if not text:
            return 0.0
        
        intensity = 0.0
        text_lower = text.lower()
        
        # Check markers
        for marker, score in self.INTENSE_MARKERS.items():
            if marker.lower() in text_lower:
                intensity += score
        
        # CAPS LOCK = SHOUTING
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:  # More than 30% caps
            intensity += 2
        
        # Exclamation marks
        exclamations = text.count('!') + text.count('‼️')
        intensity += min(exclamations * 0.5, 3)  # Max 3 from exclamations
        
        # Multiple question marks (confusion/intensity)
        if '??' in text or '???' in text:
            intensity += 1
        
        # Emojis (high emoji usage = emotional)
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]')
        emoji_count = len(emoji_pattern.findall(text))
        intensity += min(emoji_count * 0.3, 2)
        
        # Normalize to 0-10
        return min(intensity, 10.0)
    
    def detect_emotional_type(self, text: str) -> str:
        """
        Detect primary emotional type.
        
        Returns:
            'intense' | 'technical' | 'soft' | 'chaos' | 'neutral'
        """
        if not text:
            return 'neutral'
        
        text_lower = text.lower()
        scores = {
            'intense': 0,
            'technical': 0,
            'soft': 0,
            'chaos': 0
        }
        
        # Score each type
        for marker, score in self.INTENSE_MARKERS.items():
            if marker.lower() in text_lower:
                scores['intense'] += score
        
        for marker, score in self.TECHNICAL_MARKERS.items():
            if marker.lower() in text_lower:
                scores['technical'] += score
        
        for marker, score in self.SOFT_MARKERS.items():
            if marker.lower() in text_lower:
                scores['soft'] += score
        
        for marker, score in self.CHAOS_MARKERS.items():
            if marker.lower() in text_lower:
                scores['chaos'] += score
        
        # Get dominant type
        max_score = max(scores.values())
        if max_score == 0:
            return 'neutral'
        
        for emo_type, score in scores.items():
            if score == max_score:
                return emo_type
        
        return 'neutral'
    
    def is_3am_session(self, timestamp: datetime) -> bool:
        """Check if message was sent during 3AM hours (2-5 AM)"""
        hour = timestamp.hour
        return 2 <= hour <= 5
    
    def get_node_color(self, intensity: float, emo_type: str, is_3am: bool = False) -> str:
        """
        Get color for graph node based on emotion.
        
        Args:
            intensity: 0-10 intensity score
            emo_type: emotional type
            is_3am: Was this a 3AM conversation?
            
        Returns:
            Hex color code
        """
        # 3AM sessions get special treatment
        if is_3am:
            # Pulsing purple-red gradient
            return '#FF00FF' if intensity > 5 else '#9B5DE5'
        
        # Color by emotional type + intensity
        if emo_type == 'intense':
            # Red gradient (darker = more intense)
            if intensity >= 8:
                return '#FF0000'  # PURE RED - RED ROOM
            elif intensity >= 5:
                return '#FF4444'  # Bright red
            else:
                return '#FF8888'  # Light red
        
        elif emo_type == 'technical':
            # Blue gradient
            if intensity >= 5:
                return '#0066FF'  # Deep blue
            else:
                return '#4D94FF'  # Light blue
        
        elif emo_type == 'soft':
            # Pink/purple gradient
            if intensity >= 5:
                return '#FF69B4'  # Hot pink
            else:
                return '#FFB6C1'  # Light pink
        
        elif emo_type == 'chaos':
            # Rainbow chaos (yellow-green)
            return '#FFD700' if intensity >= 5 else '#ADFF2F'
        
        else:
            # Neutral gray
            return '#888888'
    
    def analyze_conversation(self, messages: List[Dict]) -> Dict:
        """
        Analyze entire conversation for emotional metrics.
        
        Args:
            messages: List of message dicts with 'content', 'timestamp'
            
        Returns:
            {
                'avg_intensity': float,
                'peak_intensity': float,
                'dominant_emotion': str,
                'is_3am_session': bool,
                'intensity_curve': List[float]
            }
        """
        if not messages:
            return {
                'avg_intensity': 0.0,
                'peak_intensity': 0.0,
                'dominant_emotion': 'neutral',
                'is_3am_session': False,
                'intensity_curve': []
            }
        
        intensities = []
        emotions = []
        has_3am = False
        
        for msg in messages:
            content = msg.get('content', '')
            timestamp = msg.get('timestamp')
            
            intensity = self.analyze_intensity(content)
            emo_type = self.detect_emotional_type(content)
            
            intensities.append(intensity)
            emotions.append(emo_type)
            
            if timestamp and self.is_3am_session(timestamp):
                has_3am = True
        
        # Dominant emotion (most common)
        dominant = max(set(emotions), key=emotions.count) if emotions else 'neutral'
        
        return {
            'avg_intensity': sum(intensities) / len(intensities) if intensities else 0.0,
            'peak_intensity': max(intensities) if intensities else 0.0,
            'dominant_emotion': dominant,
            'is_3am_session': has_3am,
            'intensity_curve': intensities
        }


# Quick function
def analyze_text_emotion(text: str) -> Tuple[float, str, str]:
    """
    Quick analysis of text.
    
    Returns:
        (intensity, emotion_type, color_hex)
    """
    analyzer = EmotionalAnalyzer()
    intensity = analyzer.analyze_intensity(text)
    emo_type = analyzer.detect_emotional_type(text)
    color = analyzer.get_node_color(intensity, emo_type)
    return intensity, emo_type, color

