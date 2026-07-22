import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("API Key tidak ditemukan. Pastikan GEMINI_API_KEY terisi di .env")
    exit(1)

try:
    # Karena kita sudah beralih ke SDK baru, kita menggunakan google-genai
    client = genai.Client(api_key=API_KEY)
    
    print("\nMemeriksa daftar model Gemini yang tersedia untuk API Key Anda...")
    print("-" * 50)
    
    models = client.models.list()
    
    count = 0
    for m in models:
        name = m.name
        # Kita hanya mencari model yang berawalan gemini dan (flash atau pro)
        if 'gemini' in name.lower():
            # SDK baru biasanya meletakkan method pendukung dalam supported_generation_methods
            methods = getattr(m, 'supported_generation_methods', [])
            
            # Jika property tidak ada, tetap print (berjaga-jaga)
            if not methods or 'generateContent' in methods:
                print(f"✅ {name}")
                count += 1
                
    print("-" * 50)
    print(f"Total model ditemukan: {count}")

except Exception as e:
    print(f"Gagal mengambil daftar model. Error: {e}")
