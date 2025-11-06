# BT_Security2_Chữ Ký Số: Nguyễn Mạnh Hiếu - K225480106020 - Môn An Toàn Và Bảo Mật Thông Tin
## I. MÔ TẢ CHUNG
- Sinh viên thực hiện báo cáo và thực hành: phân tích và hiện thực việc nhúng, xác thực chữ ký số trong file PDF.
- Phải nêu rõ chuẩn tham chiếu (PDF 1.7 / PDF 2.0, PAdES/ETSI) và sử dụng công cụ thực thi (ví dụ iText7, OpenSSL, PyPDF, pdf-lib).
## II. CÁC YÊU CẦU CỤ THỂ
- Cấu trúc PDF liên quan chữ ký (Nghiên cứu)
- Thời gian ký được lưu ở đâu?
- Các bước tạo và lưu chữ ký trong PDF (đã có private RSA)
- Các bước xác thực chữ ký trên PDF đã ký
## III. YÊU CẦU NỘP BÀI
- Báo cáo PDF ≤ 6 trang: mô tả cấu trúc, thời gian ký, rủi ro bảo mật.
- Code + README (Git repo hoặc zip).
- Demo files: original.pdf, signed.pdf, tampered.pdf.
- (Tuỳ chọn) Video 3–5 phút demo kết quả.
## IV. TIÊU CHÍ CHẤM
- Lý thuyết & cấu trúc PDF/chữ ký: 25%
- Quy trình tạo chữ ký đúng kỹ thuật: 30%
- Xác thực đầy đủ (chain, OCSP, timestamp): 25%
- Code & demo rõ ràng: 15%
- Sáng tạo mở rộng (LTV, PAdES): 5%
## V. GHI CHÚ AN TOÀN
- Vẫn lưu private key (sinh random) trong repo. Tránh dùng private key thương mại.
- Dùng RSA ≥ 2048-bit và SHA-256 hoặc mạnh hơn.
- Có thể dùng RSA-PSS thay cho PKCS#1 v1.5.
- Khuyến khích giải thích rủi ro: padding oracle, replay, key leak.
## VI. GỢI Ý CÔNG CỤ
- OpenSSL, iText7/BouncyCastle, pypdf/PyPDF2.
- Tham khảo chuẩn PDF: ISO 32000-2 (PDF 2.0) và ETSI EN 319 142 (PAdES).
_____

1. Chuẩn bị:

- Chuẩn bị 1 file pdf gốc:

<img width="448" height="82" alt="image" src="https://github.com/user-attachments/assets/77dcb272-78af-41a1-bb49-55bad1497468" />

- Chuẩn bị 1 ảnh chữ ký:

<img width="1036" height="627" alt="image" src="https://github.com/user-attachments/assets/0e70ced5-c650-43b1-96da-d53386dbdb41" />

- Cài đặt các thư viện cần thiết

<img width="869" height="400" alt="image" src="https://github.com/user-attachments/assets/169cd4ff-3351-42c2-810f-db1ad3aa8fa6" />

2. Các bước thực hiện:

- Tạo chứng chỉ và khóa:

<img width="1409" height="969" alt="image" src="https://github.com/user-attachments/assets/3b566219-d3af-4fd4-9b8f-986c19e1c128" />

--> Tạo thành công:

<img width="454" height="107" alt="image" src="https://github.com/user-attachments/assets/d31114fd-3d84-494c-b641-51649fdaf21c" />

- Chạy sign_document để ký:

<img width="1392" height="748" alt="image" src="https://github.com/user-attachments/assets/22afc14e-2fed-47b4-b6bc-fac317e16143" />

--> Ký thành công:

<img width="1871" height="984" alt="image" src="https://github.com/user-attachments/assets/a5f533d8-0052-49a2-a1fa-02478e7037b7" />

- Tạo file giả mạo: chạy tamper_document.py để tạo file giả mạo là tampered.pdf

<img width="1919" height="991" alt="image" src="https://github.com/user-attachments/assets/65e4875c-8176-4110-be59-6f80837805be" />

- Xác minh: chạy verify_signature.py để kiểm tra:

