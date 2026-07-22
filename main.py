import time
from src.config import TARGET_DIR, EXCEL_TEMPLATE_PATH, DELAY_BETWEEN_FILES
from src.folder_scanner import scan_employee_folders
from src.vision_extractor import extract_employee_data
from src.excel_manager import append_to_excel, get_processed_employees

def main():
    print("==========================================================")
    print("   Multi-Modal Employee Data Pipeline (Vertex AI Core)   ")
    print("==========================================================")
    print(f"Target Direktori: {TARGET_DIR}")
    
    # 1. Scanning Folders (Phase 3)
    print("\nMemindai folder karyawan...")
    employee_folders = scan_employee_folders(str(TARGET_DIR))
    
    total_folders = len(employee_folders)
    if total_folders == 0:
        print("Tidak ada folder karyawan yang ditemukan untuk diproses. Selesai.")
        return
        
    print(f"Ditemukan {total_folders} folder karyawan untuk diproses.\n")
    
    # Membaca data yang sudah diproses sebelumnya untuk fitur Resume (menghindari duplikasi & kuota API)
    processed_ids, processed_names = get_processed_employees(str(EXCEL_TEMPLATE_PATH))
    if processed_ids or processed_names:
        print(f"[Resume Mode] Ditemukan {max(len(processed_ids), len(processed_names))} baris data di Excel. Sistem akan melewati data tersebut.\n")
    
    # 2. Main Looping (Phase 5 Orkestrasi)
    for index, emp_meta in enumerate(employee_folders, start=1):
        emp_id = str(emp_meta.get("id", "")).strip()
        emp_name = str(emp_meta.get("nama", "")).strip()
        file_paths = emp_meta.get("file_paths", [])
        
        # Logika skip jika ID sudah ada (dan bukan ID fallback 'UNKNOWN')
        if emp_id and emp_id != "UNKNOWN" and emp_id in processed_ids:
            print(f"[{index}/{total_folders}] Melewati '{emp_name}' (ID {emp_id} sudah tersimpan di Excel).")
            continue
            
        # Logika skip jika ID UNKNOWN namun Namanya cocok persis dengan yang ada di Excel
        if emp_name.lower() in processed_names:
            print(f"[{index}/{total_folders}] Melewati '{emp_name}' (Nama '{emp_name}' sudah tersimpan di Excel).")
            continue
            
        print(f"[{index}/{total_folders}] Memproses: '{emp_name}' ({len(file_paths)} file media)...")

        
        try:
            # 3. Ekstraksi AI (Phase 2)
            # Jika file kosong, fungsi ini sudah menangani fallback gracefully
            extracted_data, final_note = extract_employee_data(file_paths)
            
            # Pastikan catatan (Lapis 1/Lapis 2) tersinkronisasi
            extracted_data["catatan_dokumen"] = final_note
            
            # 4. Pemetaan Excel (Phase 4)
            append_to_excel(str(EXCEL_TEMPLATE_PATH), emp_meta, extracted_data)
            
        except Exception as e:
            # Isolasi robust: Jangan biarkan 1 folder buruk mematikan program
            print(f"  -> [FATAL ERROR] Kegagalan sistemik mendadak pada '{emp_name}': {e}")
            
        finally:
            # 5. Rate Limiting Vertex AI
            # Terapkan jeda kecuali pada folder terakhir
            if index < total_folders:
                print(f"  -> Menunggu jeda {DELAY_BETWEEN_FILES} detik...\n")
                time.sleep(DELAY_BETWEEN_FILES)
                
    print("\n==========================================================")
    print(f"Proses Ekstraksi Selesai!")
    print(f"Semua data telah disuntikkan dengan aman ke: {EXCEL_TEMPLATE_PATH.name}")
    print("==========================================================")

if __name__ == "__main__":
    main()
