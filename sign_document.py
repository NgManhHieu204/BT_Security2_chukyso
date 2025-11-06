import os
import sys
import traceback
from datetime import datetime

from pyhanko.sign import signers, fields
from pyhanko.sign.signers.pdf_signer import PdfSignatureMetadata, PdfSigner
from pyhanko.sign.fields import SigFieldSpec
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils import images
from pyhanko.pdf_utils.layout import SimpleBoxLayoutRule, AxisAlignment, Margins
from pyhanko.pdf_utils.text import TextBoxStyle
from pyhanko.stamp.text import TextStampStyle
from pyhanko.keys import load_private_key_from_pemder, load_cert_from_pemder

# --- Hiển thị Unicode ---
sys.stdout.reconfigure(encoding="utf-8")

# === Cấu hình đường dẫn ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PDF = os.path.join(BASE_DIR, "pdf", "original.pdf")
SIGNED_PDF = os.path.join(BASE_DIR, "pdf", "signed.pdf")
PRIVATE_KEY = os.path.join(BASE_DIR, "keys", "signer_key.pem")
CERT_PEM = os.path.join(BASE_DIR, "keys", "signer_cert.pem")
STAMP_IMG = os.path.join(BASE_DIR, "picture", "sign.jpg")

# BƯỚC 1: TẢI KEY VÀ CHỨNG CHỈ

print("🔑 Đang tải khóa cá nhân và chứng chỉ...")
try:
    signer_obj = signers.SimpleSigner(
        signing_cert=load_cert_from_pemder(CERT_PEM),
        signing_key=load_private_key_from_pemder(
            PRIVATE_KEY,
            passphrase=None
        ),
        cert_registry=[]
    )
except FileNotFoundError:
    print("❌ Lỗi: Không tìm thấy file key/cert.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Lỗi khi tải key: {e}")
    traceback.print_exc()
    sys.exit(1)

# BƯỚC 2: KÝ TÀI LIỆU

print(f"📖 Đang đọc file: {SRC_PDF}")
try:
    with open(SRC_PDF, "rb") as infile:
        pdf_writer = IncrementalPdfFileWriter(infile)

        # === Xác định trang cuối ===
        try:
            page_tree = pdf_writer.root["/Pages"]
            total_pages = int(page_tree.get("/Count", 1))
        except Exception:
            total_pages = 1
        last_page_index = total_pages - 1
        print(f"📝 Tệp có {total_pages} trang, thêm chữ ký vào trang cuối ({last_page_index + 1}).")

        # === Tạo trường chữ ký ===
        fields.append_signature_field(
            pdf_writer,
            SigFieldSpec(
                sig_field_name="DigitalSignField",
                box=(150, 50, 550, 150),
                on_page=last_page_index
            ),
        )
        print("🔖 Đã thêm vùng chữ ký vào PDF (AcroForm).")


        # === Tạo con dấu (Stamp) ===
        img = images.PdfImage(STAMP_IMG)
        layout_img = SimpleBoxLayoutRule(
            x_align=AxisAlignment.ALIGN_MIN,
            y_align=AxisAlignment.ALIGN_MID,
            margins=Margins(right=15)
        )
        layout_text = SimpleBoxLayoutRule(
            x_align=AxisAlignment.ALIGN_MIN,
            y_align=AxisAlignment.ALIGN_MID,
            margins=Margins(left=200)
        )
        style_text = TextBoxStyle(font_size=11)

        today = datetime.now().strftime("%d/%m/%Y %H:%M")
        signer_info = (
            "Nguyen Manh Hieu\n"
            "Lớp: K58KTP\n"
            "MSSV: K225480106020\n"
            f"Ngày ký: {today}"
        )

        style_stamp = TextStampStyle(
            stamp_text=signer_info,
            background=img,
            background_layout=layout_img,
            inner_content_layout=layout_text,
            text_box_style=style_text,
            border_width=1
        )

        # === Metadata chữ ký ===
        meta_data = PdfSignatureMetadata(
            field_name="DigitalSignField",
            reason="Bài tập Chữ ký số - An toàn bảo mật thông tin",
            location="Thái Nguyên, Việt Nam",
            md_algorithm="sha256"
        )

        # === Thực hiện ký (truyền đúng kiểu writer) ===
        pdf_signer = PdfSigner(
            signature_meta=meta_data,
            signer=signer_obj,
            stamp_style=style_stamp
        )
        
        print("✍️ Đang thực hiện ký...")
        try:
            with open(SIGNED_PDF, "wb") as outfile:
                pdf_signer.sign_pdf(pdf_writer, output=outfile)
            print("✅ Hoàn tất ký số!")
            print(f"Tệp đã lưu tại: {SIGNED_PDF}")
        
        except Exception as e:
            print(f"\n❌ Lỗi chi tiết khi ký PDF: {e}")
            print("--- FULL TRACEBACK ---")
            traceback.print_exc()
            print("----------------------")

except FileNotFoundError:
    print(f"❌ Lỗi: Không tìm thấy file PDF gốc tại: {SRC_PDF}")
    print("Vui lòng kiểm tra lại đường dẫn và đảm bảo file không bị khóa.")
except Exception as e:
    print(f"❌ Lỗi không xác định khi đọc file PDF: {e}")
    traceback.print_exc()