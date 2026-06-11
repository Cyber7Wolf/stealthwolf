"""
CyberWolf StealthWolf - PDF Steganography (FIXED WORKING VERSION)
Hides data in PDF files using EOF appending method
"""

import hashlib
import base64
import re
import os

class PDFSmuggler:
    def __init__(self, password: str):
        self.password = password
        self.key = hashlib.sha256(password.encode()).digest()
    
    def _xor_encrypt(self, data: bytes) -> bytes:
        result = bytearray()
        for i, byte in enumerate(data):
            result.append(byte ^ self.key[i % len(self.key)])
        return bytes(result)
    
    def smuggle_into_pdf(self, input_pdf: str, secret_data: bytes, output_pdf: str) -> dict:
        """Hide data in PDF by appending to end of file"""
        
        # Encrypt secret
        encrypted = self._xor_encrypt(secret_data)
        b64_secret = base64.b64encode(encrypted).decode()
        
        # Read original PDF
        with open(input_pdf, 'rb') as f:
            content = f.read()
        
        # Write output with hidden data
        with open(output_pdf, 'wb') as f:
            f.write(content)
            # Add a newline if not present
            if not content.endswith(b'\n'):
                f.write(b'\n')
            # Add hidden data with clear markers
            f.write(b'%CyberWolfStealthWolf%\n')
            f.write(b64_secret.encode())
            f.write(b'\n%CyberWolfStealthWolfEnd%\n')
        
        return {
            'success': True,
            'bytes_hidden': len(secret_data),
            'output_path': output_pdf
        }
    
    def extract_from_pdf(self, pdf_path: str) -> bytes:
        """Extract hidden data from PDF"""
        with open(pdf_path, 'rb') as f:
            content = f.read()
        
        # Look for data between markers
        start_marker = b'%CyberWolfStealthWolf%\n'
        end_marker = b'\n%CyberWolfStealthWolfEnd%\n'
        
        start_pos = content.find(start_marker)
        if start_pos == -1:
            raise ValueError("No hidden data found (start marker missing)")
        
        start_pos += len(start_marker)
        end_pos = content.find(end_marker, start_pos)
        
        if end_pos == -1:
            raise ValueError("No hidden data found (end marker missing)")
        
        b64_data = content[start_pos:end_pos].decode()
        
        try:
            encrypted = base64.b64decode(b64_data)
            decrypted = self._xor_encrypt(encrypted)
            return decrypted
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

# Test
if __name__ == "__main__":
    from reportlab.pdfgen import canvas
    
    print("Testing PDF Smuggler...")
    
    # Create test PDF
    c = canvas.Canvas("/tmp/test.pdf")
    c.drawString(100, 750, "Test PDF Document")
    c.save()
    print("✅ Created test PDF")
    
    # Test smuggling
    s = PDFSmuggler("testpass")
    secret = b"SECRET PDF DATA - Router password: admin123"
    
    result = s.smuggle_into_pdf("/tmp/test.pdf", secret, "/tmp/stego.pdf")
    print(f"✅ Smuggle: {result}")
    
    # Test extraction
    extracted = s.extract_from_pdf("/tmp/stego.pdf")
    print(f"✅ Extracted: {extracted}")
    print(f"✅ Match: {secret == extracted}")
    
    if secret == extracted:
        print("\n🎉 PDF smuggling working perfectly!")
    else:
        print("\n❌ Failed")
