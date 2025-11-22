# ════════════════════════════════════════════════════════════════════════
# FILE 2: tests/conftest.py
# Configuration commune à tous les tests (fixtures pytest)
# ════════════════════════════════════════════════════════════════════════

import pytest
import pandas as pd
import tempfile
import os
import shutil
from unittest.mock import Mock

@pytest.fixture
def sample_raw_tweets():
    """Fixture : Données RAW de test"""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'created_at': ['2024-01-15 10:00:00'] * 5,
        'screen_name': ['user1', 'Free_1337', 'user2', 'spam', 'user3'],
        'name': ['Jean', 'Free Officiel', 'Marie', 'Bot', 'Paul'],
        'full_text': [
            '@Free Internet HS https://t.co/xxx #Free',
            'Réponse officielle',
            '😊😊😊',
            'asdfkjhasdf',
            'Box ne fonctionne plus'
        ],
        'in_reply_to': [None, None, None, None, None]
    })

@pytest.fixture
def sample_silver_tweets():
    """Fixture : Données SILVER de test"""
    return pd.DataFrame({
        'id': [1, 2, 3],
        'clean_text': [
            'internet hs',
            'box ne fonctionne plus',
            'problème réseau mobile'
        ]
    })

@pytest.fixture
def temp_directory():
    """Fixture : Répertoire temporaire (nettoyé automatiquement)"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_api_response_success():
    """Fixture : Mock réponse API succès"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "label": "problème avéré",
        "domaine": "fixe",
        "sous_domaine": "réseau",
        "score": 0.95
    }
    return mock_response

@pytest.fixture
def mock_api_response_error():
    """Fixture : Mock réponse API erreur"""
    mock_response = Mock()
    mock_response.status_code = 500
    return mock_response