import os
import sys
from pyhanko.pdf_utils.reader import PdfReader
from pyhanko.sign import validation, signers
from pyhanko.sign.validation import SignatureCoverageStatus, RevocationInfoValidationType
from pyhanko_certvalidator import ValidationContext

# --- Hiển thị Unicode ---
sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🔧 Chọn file cần kiểm tra
PDF_PATH = os.path.join(BASE_DIR, "pdf", "signed.pdf")
# PDF_PATH = os.path.join(BASE_DIR, "pdf", "tampered.pdf")

CERT_PEM = os.path.join(BASE_DIR, "keys", "signer_cert.pem")
LOG_FILE = os.path.join(BASE_DIR, "pdf", "bao_cao_kiem_tra.txt")


def verify_signature(pdf_path, trusted_cert_path):
    """Xác minh chữ ký số trong tệp PDF"""
    print(f"\n🔍 Đang xác minh chữ ký trong: {os.path.basename(pdf_path)}")

    try:
        with open(trusted_cert_path, 'rb') as f:
            trusted_cert = signers.load_cert_from_pemder(f.read())

        validation_context = ValidationContext(
            trust_roots=[trusted_cert],
            revinfo_validation_type=RevocationInfoValidationType.NONE
        )

        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            signatures = reader.get_signatures()
            if not signatures:
                return "❌ Không có chữ ký nào.", None

            sig_obj = signatures[0]
            status = validation.validate_pdf_signature(sig_obj, validation_context)
            return status, sig_obj.field_name

    except FileNotFoundError:
        return f"❌ Không tìm thấy file hoặc chứng chỉ.", None
    except Exception as e:
        return f"❌ Lỗi xác minh: {e}", None


def write_report(status, field_name):
    """Ghi kết quả xác minh vào file"""
    report = f"----- BÁO CÁO XÁC MINH ({os.path.basename(PDF_PATH)}) -----\n"

    if isinstance(status, str):
        report += f"{status}\n"
        print(report)
        return

    report += f"Tên trường chữ ký: {field_name}\n"
    report += f"Người ký: {status.signing_cert.subject.human_friendly}\n"

    # Kiểm tra toàn vẹn
    if status.coverage == SignatureCoverageStatus.ENTIRE_FILE:
        report += "✅ File còn nguyên vẹn.\n"
    else:
        report += "❌ File đã bị thay đổi sau khi ký.\n"

    # Kiểm tra chứng chỉ
    if status.validity and status.validity.signing_cert_valid:
        report += "✅ Chứng chỉ hợp lệ.\n"
    else:
        report += "❌ Chứng chỉ không hợp lệ.\n"

    print(report)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(report + "\n")


if __name__ == '__main__':
    status, field = verify_signature(PDF_PATH, CERT_PEM)
    write_report(status, field)
