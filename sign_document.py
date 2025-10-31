import os
import sys
# !!! ĐÃ SỬA LỖI IMPORT cho pyhanko 0.20.0 - DEFAULT_MD được import từ pyhanko.sign !!!
from pyhanko.sign import signers, fields
# !!! CẦN SỬA LẠI: CertificateStore được import từ pyhanko_certvalidator.registry trong 0.20.0 !!!
# Thay thế: from pyhanko.keys import CertificateStore 
from pyhanko_certvalidator.registry import CertificateStore
from pyhanko.sign.fields import SigFieldSpec
from pyhanko.sign import DEFAULT_MD # <--- ĐÃ SỬA VỀ VỊ TRÍ MỚI CHO BẢN 0.20.0
# !!! ĐÃ SỬA LỖI IMPORT CHO VisibleSigSettings (Di chuyển từ models sang fields) !!!
from pyhanko.sign.fields import VisibleSigSettings 
from pyhanko.stamp import TextStamp
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# --- Ensure Unicode is displayed correctly on Windows ---
sys.stdout.reconfigure(encoding="utf-8")

# --- Path Configuration (Updated for SecurityChukyso) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Files in the "pdf" directory
ORIGINAL_PDF = os.path.join(BASE_DIR, "pdf", "original.pdf")
SIGNED_PDF = os.path.join(BASE_DIR, "pdf", "signed.pdf")
# Files in the "keys" directory
KEY_FILE = os.path.join(BASE_DIR, "keys", "signer_key.pem")
CERT_FILE = os.path.join(BASE_DIR, "keys", "signer_cert.pem")
# Signature image in the "picture" directory
SIGNATURE_IMAGE = os.path.join(BASE_DIR, "picture", "sign.jpg")

# --- Signing Configuration Information ---
SIGNER_NAME = "Nguyen Manh Hieu - K58KTP"
REASON = "Đã xem xét và phê duyệt tài liệu"
LOCATION = "Thai Nguyen, Viet Nam"

def create_visible_signature_box():
    """Create the visible signature box using ReportLab."""
    # Kích thước hộp chữ ký: 2 inches x 1.5 inches
    c = canvas.Canvas("signature_box.pdf", pagesize=(2 * inch, 1.5 * inch))
    
    width = 2 * inch
    height = 1.5 * inch

    # Draw border (optional)
    c.rect(1, 1, width - 2, height - 2, stroke=1)
    
    # Insert signature image (customize position)
    try:
        # Giả sử hình ảnh chữ ký chiếm 80% chiều rộng và 70% chiều cao
        img_w = width * 0.8
        img_h = height * 0.7
        # Căn giữa hình ảnh
        img_x = (width - img_w) / 2
        img_y = height * 0.3 
        # The 'mask=auto' attempts to use transparency information
        c.drawImage(SIGNATURE_IMAGE, img_x, img_y, img_w, img_h, mask='auto')
    except Exception as e:
        print(f"⚠️ Could not load signature image: {e}. Continuing without image.")

    # Add signing information (TextStamp will add details)
    # Signer name at the bottom
    c.setFont("Helvetica", 6)
    c.drawString(width * 0.1, height * 0.1, f"Ký bởi: {SIGNER_NAME}")

    c.save()
    return "signature_box.pdf"

def sign_pdf_document():
    """Perform digital signing of the PDF document."""
    
    # 1. Create the visible signature box
    sig_box_path = create_visible_signature_box()

    # 2. Create the signer object
    try:
        # Khởi tạo một kho lưu trữ chứng chỉ trống (bắt buộc cho pyhanko 0.20.0)
        cert_store = CertificateStore() 
        
        # !!! ĐÃ SỬA: Thêm cert_registry vào constructor SimpleSigner
        signer = signers.SimpleSigner(
            signing_cert=CERT_FILE, 
            signing_key=KEY_FILE,
            cert_registry=cert_store 
        )
    except FileNotFoundError:
        print("\n❌ ERROR: Key or certificate not found. Run generate_keys.py first.")
        # Xóa file tạm nếu có lỗi
        if os.path.exists(sig_box_path): os.remove(sig_box_path)
        return

    # 3. Configure the display position (on page 0 - the first page)
    # Position: lower right corner (50pt margin, box size 144x108 pt - equivalent to 2in x 1.5in)
    # !!! ĐÃ SỬA LỖI: Bỏ keyword 'box_rect=' và 'page=' để tương thích với pyhanko 0.20.0
    sig_field_spec = SigFieldSpec(
        'Signature1',
        # PDF coordinates (bottom-left x, bottom-left y, top-right x, top-right y)
        (400, 50, 544, 158), 
        # Page index (tham số vị trí thứ 3)
        0 
    )

    # 4. Configure Visual Appearance (V/A)
    # Load the small PDF file containing the signature box created by ReportLab
    with open(sig_box_path, 'rb') as f:
        signature_appearance_pdf = f.read()

    # !!! ĐÃ SỬA LỖI: Đổi stamp_text thành text, và text_box_width thành box_width (cho pyhanko 0.20.0)
    sig_settings = VisibleSigSettings(
        sig_field_spec=sig_field_spec,
        stamp_style=TextStamp(
            text='Chữ ký số hợp lệ',
            # SỬA: Dùng None thay vì opentype_font_loader để tránh lỗi
            font=None, 
            box_width=100
        ),
        # Use the generated PDF as the visual content for the signature
        widget_content=signature_appearance_pdf
    )

    # 5. Perform signing
    try:
        print(f"⏳ Starting to sign file: {ORIGINAL_PDF}...")
        with open(ORIGINAL_PDF, 'rb') as inf:
            # Sử dụng signers.PdfFileWriter thay cho SigningStamper/PdfFileWriter
            w = signers.PdfFileWriter(inf) 
            signer.sign(
                pdf_writer=w,
                sig_field_spec=sig_field_spec, # Dùng sig_field_spec đã được cấu hình ở bước 3
                signature_meta=signers.SignatureMeta(
                    field_name='Signature1',
                    md_algorithm=DEFAULT_MD,
                    location=LOCATION,
                    reason=REASON,
                ),
                signer_setup=signers.PdfSignatureBase(
                    sig_appearance_settings=sig_settings
                )
            )

            with open(SIGNED_PDF, 'wb') as outf:
                w.write(outf)
        
        print(f"\n✅ Complete. Signed file saved at: {SIGNED_PDF}")
    except FileNotFoundError:
        print(f"\n❌ ERROR: Original PDF file not found at {ORIGINAL_PDF}. Check the path.")
    except Exception as e:
        print(f"\n❌ UNKNOWN ERROR during signing: {e}")
    finally:
        # Delete the temporary signature_box file
        if os.path.exists(sig_box_path):
            os.remove(sig_box_path)


if __name__ == '__main__':
    sign_pdf_document()
