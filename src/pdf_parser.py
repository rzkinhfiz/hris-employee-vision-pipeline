import pdfplumber
import pytesseract
from src.config import TESSERACT_CMD_PATH

# Jika TESSERACT_CMD_PATH diisi di .env (misal pada OS Windows), gunakan path tersebut
if TESSERACT_CMD_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH

def extract_text_from_pdf(pdf_path: str) -> tuple[str, bool]:
    """
    Mengekstrak teks dari file PDF.
    
    Args:
        pdf_path (str): Path absolut atau relatif ke file PDF.
        
    Returns:
        tuple[str, bool]: (teks_hasil_ekstraksi, status_apakah_menggunakan_ocr)
    """
    full_text = ""
    is_scanned = False
    
    try:
        # Buka dokumen PDF menggunakan pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            
            # Tahap 1: Ekstraksi Teks Digital (Primary)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            
            # Tahap 2: Evaluasi hasil teks
            # Jika teks hasil ekstraksi kurang dari 50 karakter, asumsikan sebagai dokumen scan (gambar)
            if len(full_text.strip()) < 50:
                is_scanned = True
                full_text = ""  # Bersihkan variabel karena kita akan menimpanya dengan hasil OCR
                
                # Tahap 3: Fallback OCR
                for page in pdf.pages:
                    # Render halaman PDF menjadi objek gambar (Pillow Image)
                    # Resolusi diset ke 300 DPI agar kualitas teks cukup baik untuk dibaca oleh Tesseract OCR
                    pil_image = page.to_image(resolution=300).original
                    
                    # Jalankan OCR pada gambar
                    ocr_text = pytesseract.image_to_string(pil_image, lang='ind+eng')
                    if ocr_text:
                        full_text += ocr_text + "\n"
                        
        return full_text.strip(), is_scanned

    except Exception as e:
        raise Exception(f"Gagal mengekstrak teks dari PDF: {str(e)}")


# Blok pengujian sederhana
if __name__ == "__main__":
    import os
    print("=== Testing Modul PDF Parser (src/pdf_parser.py) ===")
    
    # Tentukan path file dummy (silakan ubah jika ada file PDF sungguhan)
    test_pdf_path = "dummy_test.pdf"
    
    print(f"Target file uji: {test_pdf_path}")
    if os.path.exists(test_pdf_path):
        try:
            print("Memulai ekstraksi...")
            extracted_text, used_ocr = extract_text_from_pdf(test_pdf_path)
            print("-" * 40)
            print(f"Status Ekstraksi : Sukses")
            print(f"Metode Digunakan : {'OCR (Dokumen Scan)' if used_ocr else 'Digital (Teks Asli)'}")
            print(f"Jumlah Karakter  : {len(extracted_text)}")
            print(f"Pratinjau Teks   :\n{extracted_text[:200]}...")
            print("-" * 40)
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Peringatan: File '{test_pdf_path}' tidak ditemukan di direktori eksekusi.")
        print("Silakan buat atau salin file PDF ke lokasi tersebut untuk melakukan pengetesan riil.")
        print("Fungsi 'extract_text_from_pdf' secara sintaks siap digunakan.")
