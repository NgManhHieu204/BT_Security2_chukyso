import os
import sys
import pypdf

# --- Đảm bảo hiển thị Unicode trên Windows ---
sys.stdout.reconfigure(encoding="utf-8")

# --- Cấu hình Đường dẫn (Đã cập nhật cho SecurityChukyso) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Các file trong thư mục "pdf"
SIGNED_PDF = os.path.join(BASE_DIR, "pdf", "signed.pdf")
TAMPERED_PDF = os.path.join(BASE_DIR, "pdf", "tampered.pdf")

def tamper_pdf():
    """Sửa đổi tệp PDF đã ký để kiểm tra tính toàn vẹn."""
    
    print(f"⏳ Đang tải tệp đã ký: {SIGNED_PDF}...")
    
    try:
        # Mở tệp đã ký
        reader = pypdf.PdfReader(SIGNED_PDF)
        writer = pypdf.PdfWriter()

        # Thêm tất cả các trang gốc vào writer
        for page in reader.pages:
            writer.add_page(page)

        # Bất kỳ thay đổi nào (thêm văn bản, sửa metadata, thêm JS) sẽ phá vỡ chữ ký.
        writer.add_js("app.alert('Tài liệu đã bị thay đổi sau khi ký! (Lỗi kiểm tra tính toàn vvẹn)');")
        
        # Thay đổi một thuộc tính metadata
        writer.add_metadata({
            "/Title": "Tài liệu ĐÃ BỊ SỬA ĐỔI (TEST TAMPER)",
            "/Author": "Kẻ Xâm Nhập"
        })


        # Ghi tệp đã bị sửa đổi
        with open(TAMPERED_PDF, "wb") as out_file:
            writer.write(out_file)
            
        print(f"\n✅ Hoàn tất. Tệp đã ký đã bị sửa đổi và lưu tại: {TAMPERED_PDF}")
        print("💡 Tệp này (tampered.pdf) sẽ được dùng để kiểm tra tính năng xác minh thất bại.")

    except FileNotFoundError:
        print(f"\n❌ LỖI: Không tìm thấy tệp đã ký tại {SIGNED_PDF}. Hãy chạy sign_document.py trước.")
    except Exception as e:
        print(f"\n❌ LỖI KHÔNG XÁC ĐỊNH trong quá trình sửa đổi: {e}")

if __name__ == '__main__':
    tamper_pdf()
