# ════════════════════════════════════════════════════════════════════════
# FILE 4: tests/test_integration.py
# Tests d'intégration du pipeline complet
# ════════════════════════════════════════════════════════════════════════

import pytest
import pandas as pd
import os
from unittest.mock import patch, Mock
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from ETL import clean_text, normalize_text
from call_api_classify import classify_text

class TestIntegrationPipeline:
    """Tests d'intégration : Pipeline RAW → SILVER → GOLD"""
    
    def test_raw_to_silver(self, sample_raw_tweets, temp_directory):
        """
        Test intégration RAW → SILVER
        
        Étapes testées:
        1. Nettoyage texte
        2. Normalisation noms
        3. Filtrage comptes officiels
        4. Export SILVER
        """
        df = sample_raw_tweets.copy()
        
        # Nettoyage
        df['clean_text'] = df['full_text'].apply(clean_text)
        
        # Vérifications nettoyage
        assert not any('@' in str(t) for t in df['clean_text'])
        assert not any('#' in str(t) for t in df['clean_text'])
        
        # Normalisation
        df['screen_name_clean'] = df['screen_name'].apply(normalize_text)
        
        # Filtrage
        excluded = ['free_1337']
        df_clean = df[~df['screen_name_clean'].isin(excluded)]
        
        # Filtrage tweets courts
        df_clean = df_clean[df_clean['clean_text'].str.len() > 5]
        
        # Export
        silver_path = os.path.join(temp_directory, "silver.csv")
        df_clean.to_csv(silver_path, index=False)
        
        # Assertions
        assert os.path.exists(silver_path)
        assert len(df_clean) < len(df)
        assert 'free_1337' not in df_clean['screen_name_clean'].values
    
    @patch('requests.post')
    def test_silver_to_gold(self, mock_post, sample_silver_tweets, 
                        mock_api_response_success, temp_directory):
        """
        Test intégration SILVER → GOLD
        
        Étapes testées:
        1. Classification via API
        2. Merge résultats
        3. Export GOLD
        """
        mock_post.return_value = mock_api_response_success
        
        df = sample_silver_tweets.copy()
        
        # Classification
        results = []
        for _, row in df.iterrows():
            result = classify_text(row, retries=1)
            results.append(result)
        
        # Merge
        df_gold = pd.merge(df, pd.DataFrame(results), on='id', how='left')
        
        # Export
        gold_path = os.path.join(temp_directory, "gold.csv")
        df_gold.to_csv(gold_path, index=False)
        
        # Assertions
        assert len(results) == len(df)
        assert 'label' in df_gold.columns
        assert 'domaine' in df_gold.columns
        assert os.path.exists(gold_path)
        assert mock_post.call_count == len(df)