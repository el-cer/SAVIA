
# ════════════════════════════════════════════════════════════════════════
# FILE 5: tests/test_performance.py
# Tests de performance et stabilité
# ════════════════════════════════════════════════════════════════════════

import pytest
import time
import pandas as pd
from unittest.mock import patch, Mock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from ETL import clean_text
from call_api_classify import classify_text

class TestPerformance:
    """Tests de performance"""
    
    def test_etl_throughput(self):
        """
        Test : Débit nettoyage ETL > 100 tweets/sec
        """
        # Générer 1000 tweets
        tweets = [f"@Free Internet HS tweet {i}" for i in range(1000)]
        
        start = time.time()
        cleaned = [clean_text(t) for t in tweets]
        duration = time.time() - start
        
        throughput = len(tweets) / duration
        
        print(f"\n📊 Débit ETL: {throughput:.0f} tweets/sec")
        
        assert throughput > 100, f"Débit trop faible: {throughput:.0f} tweets/sec"
    
    @patch('requests.post')
    def test_api_response_time(self, mock_post, mock_api_response_success):
        """
        Test : Temps réponse API < 2s en moyenne
        """
        mock_post.return_value = mock_api_response_success
        
        # 50 appels API
        response_times = []
        for i in range(50):
            row = pd.Series({'id': i, 'clean_text': f'Tweet {i}'})
            result = classify_text(row, retries=1)
            response_times.append(result.get('duration_seconds', 0))
        
        avg_time = sum(response_times) / len(response_times)
        
        print(f"\n📊 Temps moyen API: {avg_time:.3f}s")
        
        assert avg_time < 2.0, f"Temps moyen trop élevé: {avg_time:.3f}s"
    
    @patch('requests.post')
    def test_stress_api_calls(self, mock_post, mock_api_response_success):
        """
        Test : Taux erreur < 1% sur 200 appels
        """
        mock_post.return_value = mock_api_response_success
        
        errors = 0
        total = 200
        
        for i in range(total):
            try:
                row = pd.Series({'id': i, 'clean_text': f'Tweet {i}'})
                classify_text(row, retries=1)
            except Exception:
                errors += 1
        
        error_rate = errors / total
        
        print(f"\n📊 Taux erreur: {error_rate*100:.1f}%")
        
        assert error_rate < 0.01, f"Taux erreur trop élevé: {error_rate*100:.1f}%"