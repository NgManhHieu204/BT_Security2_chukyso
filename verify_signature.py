import os
import sys
from pyhanko.pdf_utils.reader import PdfReader
from pyhanko.sign import validation, signers
from pyhanko.sign.validation import SignatureCoverageStatus, RevocationInfoValidationType
from pyhanko_certvalidator import ValidationContext

# --- Đảm bảo hiển thị Unicode trên Windows ---
sys.stdout.reconfigure(encoding="utf-8")

# --- Cấu hình Đường dẫn (Đã cập nhật cho SecurityChukyso) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# !!! CẦN THAY ĐỔI BIẾN NÀY ĐỂ CHỌN FILE KIỂM TRA !!!
# 1. Để kiểm tra file nguyên vẹn (signed.pdf):
PDF_PATH = os.path.join(BASE_DIR, "pdf", "signed.pdf") 
# 2. Để kiểm tra file bị sửa đổi (tampered.pdf), bạn cần thay đổi dòng trên thành:
# PDF_PATH = os.path.join(BASE_DIR, "pdf", "tampered.pdf") 

# Chứng chỉ công khai dùng để xác minh
CERT_PEM = os.path.join(BASE_DIR, "keys", "signer_cert.pem")
# File báo cáo kết quả
LOG_FILE = os.path.join(BASE_DIR, "pdf", "bao_cao_kiem_tra.txt")

# --- Chức năng xác minh chữ ký ---
def verify_signature(pdf_path, trusted_cert_path):
    """Xác minh chữ ký số trong tệp PDF."""
    
    print(f"\n⏳ Đang xác minh chữ ký trong tệp: {os.path.basename(pdf_path)}...")

    try:
        # Tải chứng chỉ tin cậy
        with open(trusted_cert_path, 'rb') as f:
            trusted_cert = signers.load_cert_from_pemder(f.read())
        
        # Tạo Context Xác minh (chỉ tin tưởng chứng chỉ tự ký của người ký)
        validation_context = ValidationContext(
            trust_roots=[trusted_cert],
            # Không kiểm tra thu hồi (CRL/OCSP) cho chứng chỉ tự ký (Tự tạo)
            revinfo_validation_type=RevocationInfoValidationType.NONE, 
        )

        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            
            # Lấy thông tin về chữ ký
            signatures = reader.get_signatures()
            if not signatures:
                return "❌ KHÔNG CÓ CHỮ KÝ NÀO được tìm thấy.", None

            # Chỉ kiểm tra chữ ký đầu tiên (tên là 'Signature1' đã được ký)
            sig_obj = signatures[0]

            # Thực hiện xác minh
            status = validation.validate_pdf_signature(
                sig_obj,
                validation_context
            )
            
            return status, sig_obj.field_name

    except FileNotFoundError:
        return f"❌ LỖI: Không tìm thấy tệp PDF tại {pdf_path} hoặc chứng chỉ tại {trusted_cert_path}.", None
    except Exception as e:
        return f"❌ LỖI KHÔNG XÁC ĐỊNH: {e}", None


# --- Chức năng ghi báo cáo ---
def write_report(status, field_name):
    """Ghi kết quả xác minh vào file báo cáo."""
    
    # Chuẩn bị nội dung báo cáo
    report_content = f"----- BÁO CÁO KIỂM TRA CHỮ KÝ SỐ ({os.path.basename(PDF_PATH)}) -----\n"
    report_content += f"Thời gian kiểm tra: {validation.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report_content += f"Tệp PDF: {PDF_PATH}\n"
    report_content += f"Chứng chỉ xác minh: {CERT_PEM}\n\n"
    
    # Xử lý lỗi
    if isinstance(status, str):
        report_content += f"KẾT QUẢ CHUNG: {status}\n"
        print(report_content)
        return

    # Thông tin chi tiết chữ ký
    report_content += f"Tên trường chữ ký: {field_name}\n"
    report_content += f"Người ký: {status.signing_cert.subject.human_friendly}\n"
    
    # 1. Kiểm tra tính toàn vẹn của file (chữ ký có khớp với nội dung không)
    data_integrity = "❌ File có thay đổi sau khi ký hoặc không xác định rõ."
    if status.coverage == SignatureCoverageStatus.ENTIRE_FILE:
        data_integrity = "✅ Chữ ký bao phủ toàn bộ file."
    elif status.modification_level == validation.ModificationLevel.NONE:
        data_integrity = "✅ Không có thay đổi nào sau khi ký."
        
    report_content += f"\n--- KIỂM TRA TÍNH TOÀN VẸN (INTEGRITY) ---\n"
    report_content += f"Mức độ bao phủ chữ ký: {status.coverage.name}\n"
    report_content += f"Mức độ sửa đổi: {status.modification_level.name}\n"
    report_content += f"Tóm tắt toàn vẹn: {data_integrity}\n"
    
    # 2. Kiểm tra chuỗi chứng chỉ (đối với chứng chỉ tự ký thì chỉ cần check tính hợp lệ của chính nó)
    cert_validity = "❌ CHỨNG CHỈ KHÔNG HỢP LỆ HOẶC KHÔNG ĐƯỢC TIN CẬY."
    if status.validity and status.validity.signing_cert_valid:
        cert_validity = "✅ Chứng chỉ người ký HỢP LỆ và được TIN CẬY (theo cert cung cấp)."
        
    report_content += f"\n--- KIỂM TRA CHỨNG CHỈ (CERTIFICATE VALIDATION) ---\n"
    report_content += f"Tình trạng chứng chỉ: {cert_validity}\n"
    report_content += f"Ngày hết hạn: {status.signing_cert.not_valid_after.strftime('%Y-%m-%d')}\n"
    
    # 3. Kết luận cuối cùng
    overall_result = ""
    # Chữ ký hợp lệ khi: không có sửa đổi sau khi ký VÀ chứng chỉ hợp lệ
    if status.modification_level == validation.ModificationLevel.NONE and status.validity.valid:
        overall_result = "✅ CHỮ KÝ HỢP LỆ — FILE VẪN NGUYÊN VẸN."
    else:
        overall_result = "❌ CHỮ KÝ KHÔNG HỢP LỆ HOẶC FILE ĐÃ BỊ CAN THIỆP."

    report_content += f"\n--- KẾT LUẬN CHUNG ---\n"
    report_content += overall_result

    # Ghi vào file báo cáo (chế độ 'a' để thêm vào cuối file)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(report_content + "\n\n")

    print(report_content)
    print(f"\n📝 Báo cáo đã được ghi/cập nhật vào: {LOG_FILE}")


if __name__ == '__main__':
    # THAY ĐỔI BIẾN PDF_PATH Ở ĐẦU FILE NÀY ĐỂ CHUYỂN GIỮA 2 CHẾ ĐỘ KIỂM TRA
    # 1. Kiểm tra file signed.pdf (PHẢI THÀNH CÔNG)
    # 2. Kiểm tra file tampered.pdf (PHẢI THẤT BẠI)
    
    status, field_name = verify_signature(PDF_PATH, CERT_PEM)
    write_report(status, field_name)
