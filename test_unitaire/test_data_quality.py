
# ════════════════════════════════════════════════════════════════════════
# FILE 6: tests/test_quality.py
# Tests de qualité des données
# ════════════════════════════════════════════════════════════════════════

import pytest
import pandas as pd

class TestDataQuality:
    """Tests qualité des données GOLD"""
    
    @pytest.fixture
    def sample_gold_data(self):
        """Données GOLD de test"""
        return pd.DataFrame({
            'id': [1, 2, 3, 4],
            'label': ['problème avéré', 'problème non avéré', 'problème avéré', 'inconnu'],
            'domaine': ['fixe', 'aucun', 'mobile', 'inconnu'],
            'sous_domaine': ['réseau', 'aucun', 'wifi', 'aucun'],
            'score': [0.95, 0.88, 0.92, 0.50]
        })
    
    def test_no_missing_critical_fields(self, sample_gold_data):
        """Test : Pas de NaN dans champs critiques"""
        critical_fields = ['id', 'label', 'domaine']
        
        for field in critical_fields:
            assert sample_gold_data[field].isna().sum() == 0, \
                f"Champ {field} contient des NaN"
    
    def test_label_vocabulary(self, sample_gold_data):
        """Test : Labels conformes au vocabulaire"""
        valid_labels = ['problème avéré', 'problème non avéré', 'inconnu']
        
        invalid = sample_gold_data[~sample_gold_data['label'].isin(valid_labels)]
        
        assert len(invalid) == 0, \
            f"Labels invalides: {invalid['label'].unique()}"
    
    def test_domaine_vocabulary(self, sample_gold_data):
        """Test : Domaines conformes au vocabulaire"""
        valid_domaines = ['mobile', 'fixe', 'facture', 'contact', 'aucun', 'inconnu']
        
        invalid = sample_gold_data[~sample_gold_data['domaine'].isin(valid_domaines)]
        
        assert len(invalid) == 0, \
            f"Domaines invalides: {invalid['domaine'].unique()}"
    
    def test_score_range(self, sample_gold_data):
        """Test : Score entre 0 et 1"""
        scores = sample_gold_data['score'].dropna()
        
        assert all(scores >= 0.0), "Scores négatifs trouvés"
        assert all(scores <= 1.0), "Scores > 1.0 trouvés"
    
    def test_consistency_rules(self, sample_gold_data):
        """Test : Règle métier - Si 'non avéré' alors domaine='aucun'"""
        df_non_avere = sample_gold_data[
            sample_gold_data['label'] == 'problème non avéré'
        ]
        
        invalid = df_non_avere[df_non_avere['domaine'] != 'aucun']
        
        assert len(invalid) == 0, \
            "Incohérence: 'non avéré' mais domaine != 'aucun'"
    
    def test_no_duplicates(self, sample_gold_data):
        """Test : Pas de doublons par ID"""
        duplicates = sample_gold_data[sample_gold_data.duplicated(subset=['id'])]
        
        assert len(duplicates) == 0, f"{len(duplicates)} doublons trouvés"
