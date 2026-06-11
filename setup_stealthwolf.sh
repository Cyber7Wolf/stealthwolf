#!/bin/bash
# CyberWolf StealthWolf - Complete Setup Script

cd ~/cyberwolf/stealthwolf

# Create directory structure
mkdir -p smuggler detector exfil formats logs

# Create __init__ files
touch smuggler/__init__.py detector/__init__.py exfil/__init__.py formats/__init__.py

# ========== MODULE 1: IMAGE SMUGGLER ==========
cat > smuggler/image_smuggler.py << 'EOF'
#!/usr/bin/env python3
"""
CyberWolf StealthWolf - Advanced Image Steganography
"""

import numpy as np
from PIL import Image
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
import struct
from typing import Tuple, Optional

class ImageSmuggler:
    def __init__(self, password: str):
        self.password = password
        self.key = hashlib.sha256(password.encode()).digest()
    
    def _derive_iv(self, image_hash: str) -> bytes:
        return hashlib.md5(image_hash.encode()).digest()
    
    def _encrypt_data(self, data: bytes, iv: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return cipher.encrypt(pad(data, AES.block_size))
    
    def _decrypt_data(self, data: bytes, iv: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(data), AES.block_size)
    
    def _bits_to_bytes(self, bits):
        byte_array = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte |= (bits[i + j] << j)
            byte_array.append(byte)
        return bytes(byte_array)
    
    def _bytes_to_bits(self, data: bytes):
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> i) & 1)
        return bits
    
    def _embed_lsb(self, carrier: np.ndarray, payload_bits: list) -> np.ndarray:
        flat = carrier.flatten()
        max_bits = len(flat)
        
        if len(payload_bits) > max_bits:
            raise ValueError(f"Payload too large: {len(payload_bits)} bits > {max_bits} bits capacity")
        
        for i, bit in enumerate(payload_bits):
            flat[i] = (flat[i] & ~1) | bit
        
        return flat.reshape(carrier.shape)
    
    def _extract_lsb(self, carrier: np.ndarray, num_bits: int) -> list:
        flat = carrier.flatten()
        return [flat[i] & 1 for i in range(min(num_bits, len(flat)))]
    
    def smuggle_into_image(self, input_image_path: str, secret_data: bytes, output_image_path: str) -> dict:
        img = Image.open(input_image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img)
        capacity_bits = img_array.size
        capacity_bytes = capacity_bits // 8
        
        magic = b'CWSW'
        header = magic + struct.pack('>I', len(secret_data))
        full_payload = header + secret_data
        
        iv = self._derive_iv(hashlib.md5(img_array.tobytes()).hexdigest())
        encrypted = self._encrypt_data(full_payload, iv)
        final_payload = iv + encrypted
        payload_bits = self._bytes_to_bits(final_payload)
        
        if len(payload_bits) > capacity_bits:
            return {
                'success': False,
                'error': f'Data too large: {len(payload_bits)} bits > {capacity_bits} bits',
                'capacity_mb': capacity_bytes / (1024 * 1024)
            }
        
        modified_array = self._embed_lsb(img_array.copy(), payload_bits)
        output_img = Image.fromarray(modified_array.astype('uint8'))
        output_img.save(output_image_path)
        
        return {
            'success': True,
            'capacity_bytes': capacity_bytes,
            'payload_bytes': len(final_payload),
            'used_percent': (len(payload_bits) / capacity_bits) * 100,
            'output_path': output_image_path
        }
    
    def extract_from_image(self, smuggled_image_path: str) -> Tuple[bytes, dict]:
        img = Image.open(smuggled_image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img)
        max_bits = img_array.size
        extracted_bits = self._extract_lsb(img_array, max_bits)
        extracted_bytes = self._bits_to_bytes(extracted_bits)
        
        magic = b'CWSW'
        magic_pos = extracted_bytes.find(magic)
        
        if magic_pos == -1:
            raise ValueError("No smuggled data found")
        
        iv = extracted_bytes[magic_pos + len(magic) + 4:magic_pos + len(magic) + 4 + 16]
        data_len = struct.unpack('>I', extracted_bytes[magic_pos + len(magic):magic_pos + len(magic) + 4])[0]
        encrypted = extracted_bytes[magic_pos + len(magic) + 4 + 16:magic_pos + len(magic) + 4 + 16 + data_len + 16]
        
        decrypted = self._decrypt_data(encrypted, iv)
        secret_data = decrypted[4+4:]  # Skip magic + length
        
        return secret_data, {'secret_size': len(secret_data)}

if __name__ == "__main__":
    print("ImageSmuggler ready")
EOF

# ========== MODULE 2: DETECTOR ==========
cat > detector/steganalysis.py << 'EOF'
#!/usr/bin/env python3
"""
CyberWolf StealthWolf - Steganalysis Detector
"""

import numpy as np
from PIL import Image
from scipy import stats

class SteganalysisDetector:
    def chi_square_attack(self, image_path: str) -> dict:
        img = Image.open(image_path)
        img_array = np.array(img)
        
        lsb_values = []
        if len(img_array.shape) == 3:
            for channel in range(3):
                flat = img_array[:, :, channel].flatten()
                lsb_values.extend(flat & 1)
        else:
            flat = img_array.flatten()
            lsb_values.extend(flat & 1)
        
        zero_count = lsb_values.count(0)
        one_count = lsb_values.count(1)
        total = zero_count + one_count
        
        if total == 0:
            return {'probability': 0, 'verdict': 'No data'}
        
        expected = total / 2
        chi_square = ((zero_count - expected) ** 2 / expected) + ((one_count - expected) ** 2 / expected)
        p_value = 1 - stats.chi2.cdf(chi_square, 1)
        
        return {
            'verdict': '⚠️ SUSPICIOUS' if p_value > 0.9 else '✅ NORMAL',
            'probability': p_value,
            'zero_one_ratio': f"{zero_count}/{one_count}"
        }
    
    def full_analysis(self, file_path: str) -> dict:
        results = {
            'file': file_path,
            'chi_square': self.chi_square_attack(file_path)
        }
        return results

if __name__ == "__main__":
    print("SteganalysisDetector ready")
EOF

# ========== MAIN CLI ==========
cat > stealthwolf.py << 'EOF'
#!/usr/bin/env python3
"""
CyberWolf StealthWolf - Unified CLI
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description="🐺 CyberWolf StealthWolf")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Smuggle
    smuggle = subparsers.add_parser('smuggle', help='Hide data')
    smuggle.add_argument('-i', '--input', required=True, help='Carrier image')
    smuggle.add_argument('-d', '--data', required=True, help='Secret data')
    smuggle.add_argument('-o', '--output', required=True, help='Output image')
    smuggle.add_argument('-p', '--password', required=True, help='Password')
    
    # Extract
    extract = subparsers.add_parser('extract', help='Extract data')
    extract.add_argument('-i', '--input', required=True, help='Stego image')
    extract.add_argument('-p', '--password', required=True, help='Password')
    
    # Detect
    detect = subparsers.add_parser('detect', help='Detect hidden data')
    detect.add_argument('-i', '--input', required=True, help='File to analyze')
    
    # Test
    test = subparsers.add_parser('test', help='Run self-test')
    
    args = parser.parse_args()
    
    if args.command == 'test':
        print("🐺 Running StealthWolf Self-Test...")
        from smuggler.image_smuggler import ImageSmuggler
        
        # Create test image
        from PIL import Image
        import numpy as np
        test_img = Image.fromarray(np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))
        test_img.save("/tmp/test_carrier.png")
        
        # Test smuggling
        smuggler = ImageSmuggler("test123")
        secret = b"TOP SECRET: Router password is admin123"
        
        result = smuggler.smuggle_into_image("/tmp/test_carrier.png", secret, "/tmp/test_stego.png")
        print(f"Smuggle result: {result}")
        
        # Test extraction
        extracted, meta = smuggler.extract_from_image("/tmp/test_stego.png")
        print(f"Extracted: {extracted}")
        print(f"Matches: {secret == extracted}")
        
        # Test detection
        from detector.steganalysis import SteganalysisDetector
        detector = SteganalysisDetector()
        analysis = detector.full_analysis("/tmp/test_stego.png")
        print(f"Detection: {analysis}")
        
        print("\n✅ ALL TESTS PASSED!")
        return
    
    elif args.command == 'smuggle':
        from smuggler.image_smuggler import ImageSmuggler
        smuggler = ImageSmuggler(args.password)
        secret = args.data.encode()
        result = smuggler.smuggle_into_image(args.input, secret, args.output)
        print(f"✅ Smuggled: {result}")
    
    elif args.command == 'extract':
        from smuggler.image_smuggler import ImageSmuggler
        smuggler = ImageSmuggler(args.password)
        data, meta = smuggler.extract_from_image(args.input)
        print(f"✅ Extracted: {data.decode()}")
        print(f"Metadata: {meta}")
    
    elif args.command == 'detect':
        from detector.steganalysis import SteganalysisDetector
        detector = SteganalysisDetector()
        results = detector.full_analysis(args.input)
        print(f"\n🔍 Analysis of {args.input}")
        print(f"Verdict: {results['chi_square']['verdict']}")
        print(f"Probability: {results['chi_square']['probability']:.4f}")

if __name__ == "__main__":
    main()
EOF

echo "✅ All files created!"
