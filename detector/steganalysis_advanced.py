"""
CyberWolf StealthWolf - Advanced Steganalysis Detection
Detects hidden data using statistical analysis
"""

import numpy as np
from PIL import Image
from scipy import stats
import hashlib

class SteganalysisDetector:
    def __init__(self):
        pass
    
    def chi_square_attack(self, image_path: str) -> dict:
        """Chi-square analysis for LSB steganography"""
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        pixels = np.array(img)
        
        # Analyze each color channel
        results = []
        for channel in range(3):
            channel_data = pixels[:, :, channel].flatten()
            lsb = channel_data & 1
            
            # Count pairs of adjacent LSBs
            pairs = []
            for i in range(0, len(lsb)-1, 2):
                pairs.append((lsb[i], lsb[i+1]))
            
            # Expected distribution for random data
            expected = len(pairs) / 4
            observed = {
                (0,0): pairs.count((0,0)),
                (0,1): pairs.count((0,1)),
                (1,0): pairs.count((1,0)),
                (1,1): pairs.count((1,1))
            }
            
            # Chi-square
            chi_square = sum((observed[p] - expected)**2 / expected for p in observed)
            p_value = 1 - stats.chi2.cdf(chi_square, 3)
            
            results.append({
                'channel': ['R', 'G', 'B'][channel],
                'p_value': p_value,
                'suspicious': p_value > 0.9
            })
        
        # Overall verdict
        suspicious_channels = sum(1 for r in results if r['suspicious'])
        
        return {
            'verdict': '⚠️ HIDDEN DATA DETECTED' if suspicious_channels >= 2 else '✅ CLEAN',
            'confidence': max(r['p_value'] for r in results),
            'channels': results
        }
    
    def rs_analysis(self, image_path: str) -> dict:
        """RS (Regular/Singular) analysis"""
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        pixels = np.array(img)
        
        # Simple RS analysis
        def discrimination_function(x):
            return np.sum(np.abs(x[:-1] - x[1:]))
        
        results = []
        for channel in range(3):
            channel_data = pixels[:, :, channel].flatten()
            
            # Original groups
            groups = [channel_data[i:i+2] for i in range(0, len(channel_data)-1, 2)]
            R_orig = sum(1 for g in groups if discrimination_function(g) > 0)
            S_orig = sum(1 for g in groups if discrimination_function(g) < 0)
            
            # Flipped LSB groups
            flipped = channel_data ^ 1
            groups_f = [flipped[i:i+2] for i in range(0, len(flipped)-1, 2)]
            R_flip = sum(1 for g in groups_f if discrimination_function(g) > 0)
            S_flip = sum(1 for g in groups_f if discrimination_function(g) < 0)
            
            # Ratio
            if R_orig + S_orig > 0:
                ratio = (R_flip - R_orig) / (R_orig + S_orig)
            else:
                ratio = 0
            
            results.append({
                'channel': ['R', 'G', 'B'][channel],
                'embedding_estimate': max(0, min(1, -ratio * 2)),
                'suspicious': ratio < -0.1
            })
        
        suspicious = sum(1 for r in results if r['suspicious'])
        
        return {
            'verdict': '⚠️ POSSIBLE STEGANOGRAPHY' if suspicious >= 2 else '✅ LIKELY CLEAN',
            'embedding_estimate': np.mean([r['embedding_estimate'] for r in results]),
            'channels': results
        }
    
    def full_analysis(self, image_path: str) -> dict:
        """Run all detection methods"""
        chi2 = self.chi_square_attack(image_path)
        rs = self.rs_analysis(image_path)
        
        # Combined verdict
        if chi2['verdict'] == '⚠️ HIDDEN DATA DETECTED' or rs['verdict'] == '⚠️ POSSIBLE STEGANOGRAPHY':
            overall = '🔴 HIGH PROBABILITY OF HIDDEN DATA'
            risk_score = 85
        elif chi2['confidence'] > 0.7 or rs['embedding_estimate'] > 0.3:
            overall = '🟡 MODERATE RISK - FURTHER ANALYSIS NEEDED'
            risk_score = 50
        else:
            overall = '🟢 LOW RISK - LIKELY CLEAN'
            risk_score = 15
        
        return {
            'file': image_path,
            'overall_verdict': overall,
            'risk_score': risk_score,
            'chi_square': chi2,
            'rs_analysis': rs
        }

if __name__ == "__main__":
    detector = SteganalysisDetector()
    print("Advanced Steganalysis ready")
