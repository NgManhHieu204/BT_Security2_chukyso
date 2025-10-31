import os
import sys
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

# --- Đảm bảo hiển thị Unicode trên Windows ---
sys.stdout.reconfigure(encoding="utf-8")

# --- Thư mục lưu key/cert ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# Đảm bảo thư mục "keys" là thư mục con của thư mục dự án
key_folder = os.path.join(current_dir, "keys")
os.makedirs(key_folder, exist_ok=True)

priv_key_file = os.path.join(key_folder, "signer_key.pem")
cert_file = os.path.join(key_folder, "signer_cert.pem")

# --- Tạo khóa RSA 2048 ---
print("🛠️ Khởi tạo khóa RSA 2048-bit...")
rsa_private = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# --- Chuẩn bị dữ liệu chứng chỉ ---
print("🧾 Chuẩn bị thông tin chứng chỉ tự ký...")
name_info = [
    x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Thai Nguyen"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Thai Nguyen"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "K58KTP"),
    x509.NameAttribute(NameOID.COMMON_NAME, "Nguyen Manh Hieu")
]
subject_data = x509.Name(name_info)

# --- Xây dựng và ký chứng chỉ ---
print("🔏 Đang tạo và ký chứng chỉ...")
builder = x509.CertificateBuilder()
builder = builder.subject_name(subject_data)
builder = builder.issuer_name(subject_data)
builder = builder.public_key(rsa_private.public_key())
builder = builder.serial_number(x509.random_serial_number())
builder = builder.not_valid_before(datetime.utcnow())
builder = builder.not_valid_after(datetime.utcnow() + timedelta(days=365))
builder = builder.add_extension(
    x509.BasicConstraints(ca=True, path_length=None),
    critical=True
)
certificate = builder.sign(private_key=rsa_private, algorithm=hashes.SHA256())

# --- Ghi khóa riêng ra file ---
with open(priv_key_file, "wb") as out_key:
    pem_key = rsa_private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    out_key.write(pem_key)
print(f"📁 Private key đã được ghi vào: {priv_key_file}")

# --- Ghi chứng chỉ ra file ---
with open(cert_file, "wb") as out_cert:
    pem_cert = certificate.public_bytes(serialization.Encoding.PEM)
    out_cert.write(pem_cert)
print(f"📂 Chứng chỉ đã lưu tại: {cert_file}")

print("\n✅ Hoàn tất — cặp khóa và chứng chỉ đã sẵn sàng.")