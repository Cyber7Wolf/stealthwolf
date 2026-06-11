"""
CyberWolf StealthWolf - Multi-Image Split Smuggler
Splits large data across multiple images
"""

from PIL import Image
import numpy as np
import hashlib
import os
import json

class SplitSmuggler:
    def __init__(self, password: str):
        self.password = password
        self.key = hashlib.sha256(password.encode()).digest()
    
    def _xor_encrypt(self, data: bytes) -> bytes:
        result = bytearray()
        for i, byte in enumerate(data):
            result.append(byte ^ self.key[i % len(self.key)])
        return bytes(result)
    
    def smuggle_split(self, image_paths: list, secret_data: bytes, output_dir: str) -> dict:
        """Split and hide data across multiple images"""
        # Prepare data
        encrypted = self._xor_encrypt(secret_data)
        
        # Calculate chunks
        num_images = len(image_paths)
        chunk_size = len(encrypted) // num_images + 1
        
        chunks = []
        for i in range(num_images):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(encrypted))
            chunks.append(encrypted[start:end])
        
        # Hide chunks in each image
        results = []
        for i, (img_path, chunk) in enumerate(zip(image_paths, chunks)):
            # Add header to chunk
            header = f"CHUNK:{i}:{num_images}:".encode()
            full_chunk = header + chunk + b"END"
            
            # Load image
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = np.array(img)
            
            # Convert to bits
            bits = []
            for byte in full_chunk:
                for j in range(8):
                    bits.append((byte >> j) & 1)
            
            # Embed
            flat = pixels.flatten()
            for j, bit in enumerate(bits[:len(flat)]):
                flat[j] = (flat[j] & 0xFE) | bit
            
            # Save
            output_path = os.path.join(output_dir, f"stego_part_{i}.png")
            new_pixels = flat.reshape(pixels.shape)
            Image.fromarray(new_pixels).save(output_path, 'PNG')
            results.append(output_path)
        
        return {
            'success': True,
            'num_images': num_images,
            'output_paths': results,
            'bytes_hidden': len(secret_data)
        }
    
    def extract_split(self, image_paths: list) -> bytes:
        """Extract data from multiple images"""
        chunks = []
        
        for img_path in image_paths:
            # Load image
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = np.array(img)
            
            # Extract bits
            flat = pixels.flatten()
            bits = [str(pixel & 1) for pixel in flat[:500000]]
            bits_str = ''.join(bits)
            
            # Convert to bytes
            bytes_data = bytearray()
            for i in range(0, len(bits_str), 8):
                if i + 8 <= len(bits_str):
                    byte = int(bits_str[i:i+8], 2)
                    bytes_data.append(byte)
            
            # Extract chunk (between header and END)
            bytes_str = bytes_data
            if b'END' in bytes_str:
                chunk_data = bytes_str.split(b'END')[0]
                # Find where chunk starts
                if b'CHUNK:' in chunk_data:
                    chunk_start = chunk_data.find(b'CHUNK:')
                    data_start = chunk_data.find(b':', chunk_start + 6)
                    data_start = chunk_data.find(b':', data_start + 1)
                    if data_start != -1:
                        chunks.append(chunk_data[data_start + 1:])
        
        # Reconstruct
        full_data = b''.join(chunks)
        decrypted = self._xor_encrypt(full_data)
        
        return decrypted

if __name__ == "__main__":
    print("Split Smuggler ready")
