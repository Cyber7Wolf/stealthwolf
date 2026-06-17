# 🐺 StealthWolf

**Advanced Data Smuggling & Steganography Framework**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

---

## ⚡ Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/stealthwolf.git
cd stealthwolf
pip install -r requirements.txt
python stealthwolf.py test


python stealthwolf.py smuggle -i carrier.png -d "MySecretPassword" -o stego.png -p mypass

python stealthwolf.py extract -i stego.png -p mypass

python stealthwolf.py pdf -i document.pdf -d "HiddenData" -o stego.pdf -p mypass

python stealthwolf.py detect -i suspicious.png

python stealthwolf.py exfil -w ./watch_folder -p mypass

python stealthwolf.py split -i img1.png img2.png img3.png -d "BigSecret" -o ./output -p mypass
Requirements
Pillow>=9.0.0
numpy>=1.21.0
PyPDF2>=3.0.0
reportlab>=4.0.0
watchdog>=3.0.0
scipy>=1.9.0
scikit-learn>=1.0.0
