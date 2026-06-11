"""
CyberWolf StealthWolf - Audio Steganography
Hides data in WAV audio files using LSB
"""

import wave
import numpy as np
import hashlib
import struct

class AudioSmuggler:
    def __init__(self, password: str):
        self.password = password
        self.key = hashlib.sha256(password.encode()).digest()
    
    def _xor_encrypt(self, data: bytes) -> bytes:
        result = bytearray()
        for i, byte in enumerate(data):
            result.append(byte ^ self.key[i % len(self.key)])
        return bytes(result)
    
    def smuggle_into_wav(self, input_wav: str, secret_data: bytes, output_wav: str) -> dict:
        """Hide data in WAV file LSB"""
        # Read WAV file
        wav = wave.open(input_wav, 'rb')
        params = wav.getparams()
        frames = wav.readframes(params.nframes)
        wav.close()
        
        # Convert to samples
        samples = np.frombuffer(frames, dtype=np.int16)
        
        # Prepare secret with markers
        marker = b'STLW'  # StealthWolf marker
        length = len(secret_data)
        payload = marker + length.to_bytes(4, 'big') + secret_data
        
        # Encrypt
        encrypted = self._xor_encrypt(payload)
        
        # Convert to bits
        bits = []
        for byte in encrypted:
            for i in range(8):
                bits.append((byte >> i) & 1)
        
        # Check capacity
        if len(bits) > len(samples):
            return {'success': False, 'error': 'Audio too short for data'}
        
        # Embed bits
        for i, bit in enumerate(bits):
            samples[i] = (samples[i] & 0xFFFE) | bit
        
        # Save
        output = wave.open(output_wav, 'wb')
        output.setparams(params)
        output.writeframes(samples.tobytes())
        output.close()
        
        return {
            'success': True,
            'bytes_hidden': len(secret_data),
            'output_path': output_wav
        }
    
    def extract_from_wav(self, wav_path: str) -> bytes:
        """Extract data from WAV file"""
        wav = wave.open(wav_path, 'rb')
        frames = wav.readframes(wav.getparams().nframes)
        wav.close()
        
        samples = np.frombuffer(frames, dtype=np.int16)
        
        # Extract bits
        extracted_bits = []
        for sample in samples[:100000]:  # Limit extraction
            extracted_bits.append(sample & 1)
        
        # Convert to bytes
        extracted_bytes = bytearray()
        for i in range(0, len(extracted_bits), 8):
            if i + 8 <= len(extracted_bits):
                byte = 0
                for j in range(8):
                    byte |= (extracted_bits[i + j] << j)
                extracted_bytes.append(byte)
        
        # Look for marker
        marker = b'STLW'
        marker_pos = extracted_bytes.find(marker)
        
        if marker_pos == -1:
            raise ValueError("No hidden data found")
        
        # Get length
        length = int.from_bytes(extracted_bytes[marker_pos+4:marker_pos+8], 'big')
        
        # Extract encrypted data
        encrypted = extracted_bytes[marker_pos+8:marker_pos+8+length]
        
        # Decrypt
        decrypted = self._xor_encrypt(encrypted)
        
        return decrypted

if __name__ == "__main__":
    print("Audio Smuggler ready - requires WAV files")
