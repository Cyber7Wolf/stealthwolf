#!/usr/bin/env python3
"""
CyberWolf StealthWolf - Simple Steganalysis Detector
"""

import numpy as np
from PIL import Image

class SteganalysisDetector:
    def chi_square_attack(self, image_path: str) -> dict:
        """Simple LSB distribution analysis"""
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Collect LSBs
        lsb_values = []
        flat = img_array.flatten()
        for val in flat[:10000]:  # Sample first 10000 pixels
            lsb_values.append(val & 1)
        
        if not lsb_values:
            return {'verdict': 'No data', 'probability': 0}
        
        zero_count = lsb_values.count(0)
        one_count = lsb_values.count(1)
        total = zero_count + one_count
        
        if total == 0:
            return {'verdict': 'No data', 'probability': 0}
        
        # Calculate deviation from 50/50
        expected = total / 2
        deviation = abs(zero_count - expected) / expected
        
        # Higher deviation = more suspicious (but LSB stego actually makes it MORE uniform)
        # So lower deviation = more suspicious for LSB stego
        if deviation < 0.05:
            verdict = '⚠️ POSSIBLE HIDDEN DATA'
            prob = 0.8
        elif deviation < 0.1:
            verdict = '⚠️ LOW CONFIDENCE'
            prob = 0.5
        else:
            verdict = '✅ LIKELY CLEAN'
            prob = 0.1
        
        return {
            'verdict': verdict,
            'probability': prob,
            'zero_one_ratio': f"{zero_count}/{one_count}",
            'deviation': f"{deviation:.3f}"
        }
    
    def full_analysis(self, file_path: str) -> dict:
        results = {
            'file': file_path,
            'chi_square': self.chi_square_attack(file_path)
        }
        return results

if __name__ == "__main__":
    print("SteganalysisDetector ready")
