import os
import sys
import pypdf

# --- Hiển thị Unicode ---
sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNED_PDF = os.path.join(BASE_DIR, "pdf", "signed.pdf")
TAMPERED_PDF = os.path.join(BASE_DIR, "pdf", "tampered.pdf")


def tamper_pdf():
    """Sửa đổi PDF đã ký để test phát hiện"""
    print(f"🧪 Đang sửa đổi file: {SIGNED_PDF}")

    try:
        reader = pypdf.PdfReader(SIGNED_PDF)
        writer = pypdf.PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.add_js("app.alert('Tài liệu này đã bị chỉnh sửa!');")
        writer.add_metadata({
            "/Title": "Tài liệu ĐÃ BỊ SỬA (TEST)",
            "/Author": "Kẻ xâm nhập"
        })

        with open(TAMPERED_PDF, "wb") as f:
            writer.write(f)

        print(f"✅ Tệp giả mạo lưu tại: {TAMPERED_PDF}")

    except Exception as e:
        print(f"❌ Lỗi khi sửa file: {e}")


if __name__ == '__main__':
    tamper_pdf()
