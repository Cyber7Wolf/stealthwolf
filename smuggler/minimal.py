"""
ULTRA SIMPLE - Guaranteed working steganography
No encryption, just proof of concept
"""

from PIL import Image
import numpy as np

def hide_text(image_path, text, output_path):
    """Hide text in image - simple version"""
    # Load image
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixels = np.array(img)
    
    # Convert text to binary with clear markers
    # Format: "START" + text + "END"
    full_text = "START" + text + "END"
    binary = ''.join(format(ord(c), '016b') for c in full_text)  # 16 bits per char
    
    # Flatten pixels
    flat = pixels.flatten()
    
    # Check capacity
    if len(binary) > len(flat):
        return f"Error: Need {len(binary)} bits, only {len(flat)} available"
    
    # Embed
    for i in range(len(binary)):
        flat[i] = (flat[i] & 0xFE) | int(binary[i])
    
    # Save
    new_pixels = flat.reshape(pixels.shape)
    Image.fromarray(new_pixels).save(output_path, 'PNG')
    
    return f"Hidden {len(text)} chars in {output_path}"

def extract_text(image_path):
    """Extract text from image"""
    # Load image
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixels = np.array(img)
    
    # Extract bits
    flat = pixels.flatten()
    bits = ''.join(str(pixel & 1) for pixel in flat[:50000])  # First 50000 bits
    
    # Convert bits to text (16 bits per char)
    text = ''
    for i in range(0, len(bits), 16):
        if i + 16 <= len(bits):
            char_code = int(bits[i:i+16], 2)
            char = chr(char_code)
            text += char
            
            # Stop if we find END marker
            if text.endswith("END"):
                # Remove START and END
                if "START" in text:
                    text = text.replace("START", "").replace("END", "")
                    return text
    
    return "No text found"

# Test
if __name__ == "__main__":
    from PIL import Image
    import numpy as np
    
    print("=" * 50)
    print("MINIMAL STEGANOGRAPHY TEST")
    print("=" * 50)
    
    # Create test image
    img = Image.fromarray(np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8))
    img.save("/tmp/test_carrier.png", format='PNG')
    print("✅ Created carrier image")
    
    # Test text
    test_text = "MySecretPassword123"
    print(f"Original text: {test_text}")
    
    # Hide
    result = hide_text("/tmp/test_carrier.png", test_text, "/tmp/test_stego.png")
    print(f"Hide: {result}")
    
    # Extract
    extracted = extract_text("/tmp/test_stego.png")
    print(f"Extracted: {extracted}")
    
    # Verify
    if extracted == test_text:
        print("\n🎉 SUCCESS! Minimal version works!")
        print("   Now we can add encryption and features.")
    else:
        print(f"\n❌ Failed: Expected '{test_text}', got '{extracted}'")
