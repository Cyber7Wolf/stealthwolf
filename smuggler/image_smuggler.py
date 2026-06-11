"""
CyberWolf StealthWolf - Full Featured Steganography
Built on top of working minimal version
"""

from PIL import Image
import numpy as np
import hashlib
import base64

class ImageSmuggler:
    def __init__(self, password: str):
        self.password = password
        self.key = hashlib.sha256(password.encode()).digest()
    
    def _xor_encrypt(self, data: bytes) -> bytes:
        """Simple XOR encryption"""
        result = bytearray()
        for i, byte in enumerate(data):
            result.append(byte ^ self.key[i % len(self.key)])
        return bytes(result)
    
    def _text_to_bits(self, text: str) -> str:
        """Convert text to binary (16 bits per char)"""
        return ''.join(format(ord(c), '016b') for c in text)
    
    def _bits_to_text(self, bits: str) -> str:
        """Convert binary to text"""
        chars = []
        for i in range(0, len(bits), 16):
            if i + 16 <= len(bits):
                chars.append(chr(int(bits[i:i+16], 2)))
        return ''.join(chars)
    
    def smuggle_into_image(self, input_path: str, secret_data: bytes, output_path: str) -> dict:
        """Hide secret data in image"""
        try:
            # Load image
            img = Image.open(input_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = np.array(img, dtype=np.uint8)
            
            # Convert secret to string (handle bytes)
            if isinstance(secret_data, bytes):
                try:
                    secret_str = secret_data.decode('utf-8')
                except:
                    secret_str = base64.b64encode(secret_data).decode('ascii')
            else:
                secret_str = str(secret_data)
            
            # Encrypt
            encrypted = self._xor_encrypt(secret_str.encode())
            encrypted_str = encrypted.decode('latin1')
            
            # Create payload with markers
            full_text = "START" + encrypted_str + "END"
            binary = self._text_to_bits(full_text)
            
            # Flatten pixels
            flat = pixels.flatten()
            
            # Check capacity
            if len(binary) > len(flat):
                return {
                    'success': False,
                    'error': f'Need {len(binary)} bits, only {len(flat)} available',
                    'capacity_bytes': len(flat) // 8,
                    'data_bytes': len(secret_data)
                }
            
            # Embed bits
            for i in range(len(binary)):
                flat[i] = (flat[i] & 0xFE) | int(binary[i])
            
            # Save
            new_pixels = flat.reshape(pixels.shape)
            Image.fromarray(new_pixels).save(output_path, 'PNG')
            
            return {
                'success': True,
                'capacity_bytes': len(flat) // 8,
                'data_bytes': len(secret_data),
                'output_path': output_path
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def extract_from_image(self, input_path: str):
        """Extract hidden data from image"""
        try:
            # Load image
            img = Image.open(input_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = np.array(img, dtype=np.uint8)
            
            # Extract bits
            flat = pixels.flatten()
            bits = ''.join(str(pixel & 1) for pixel in flat[:100000])
            
            # Convert to text
            text = ''
            for i in range(0, len(bits), 16):
                if i + 16 <= len(bits):
                    char_code = int(bits[i:i+16], 2)
                    text += chr(char_code)
                    
                    # Look for END marker
                    if text.endswith("END"):
                        # Extract between START and END
                        if "START" in text:
                            start_pos = text.find("START") + 5
                            end_pos = text.find("END")
                            encrypted_str = text[start_pos:end_pos]
                            
                            # Decrypt
                            decrypted = self._xor_encrypt(encrypted_str.encode('latin1'))
                            
                            # Try to decode as bytes
                            try:
                                result = decrypted.decode('utf-8')
                                # If it's base64 encoded bytes
                                try:
                                    result_bytes = base64.b64decode(result)
                                    return result_bytes, {'secret_size': len(result_bytes)}
                                except:
                                    return result.encode(), {'secret_size': len(result)}
                            except:
                                return decrypted, {'secret_size': len(decrypted)}
            
            raise ValueError("No hidden data found")
            
        except Exception as e:
            raise ValueError(f"Extraction failed: {str(e)}")

# Test
if __name__ == "__main__":
    from PIL import Image
    import numpy as np
    
    print("=" * 50)
    print("FULL FEATURED STEGANOGRAPHY TEST")
    print("=" * 50)
    
    # Create test image
    img = Image.fromarray(np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8))
    img.save("/tmp/test.png", format='PNG')
    
    # Test
    smuggler = ImageSmuggler("mypass123")
    secret = b"TOP SECRET: Router admin password is admin123!"
    
    print(f"Secret: {secret}")
    
    # Hide
    result = smuggler.smuggle_into_image("/tmp/test.png", secret, "/tmp/stego.png")
    print(f"Hide result: {result}")
    
    if result['success']:
        # Extract
        extracted, meta = smuggler.extract_from_image("/tmp/stego.png")
        print(f"Extracted: {extracted}")
        print(f"Match: {secret == extracted}")
        
        if secret == extracted:
            print("\n✅✅✅ SUCCESS! Working perfectly! ✅✅✅")
        else:
            print("\n❌ Failed - mismatch")
    else:
        print(f"\n❌ Failed - {result.get('error')}")
