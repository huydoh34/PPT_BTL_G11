# Tuần 3 - Đề tài 11: Tính chỉ số tải tích lũy và khảo sát độ nhạy

Thư mục lưu trữ mã nguồn, dữ liệu kết quả và biểu đồ trực quan hóa cho giai đoạn chạy thử nghiệm trên hai đoạn dữ liệu thực tế A, B và khảo sát độ nhạy lấy mẫu (Bước 4 và Bước 5 của đề tài).

## 1. Danh sách tệp trong thư mục

```text
Tuan3/
├── nhom11_tuan3.py                   # Mã nguồn chính tính tích phân hình thang (float64) và khảo sát độ nhạy
├── bang_tich_phan_tuan3_AB.csv       # Bảng tổng hợp chỉ số tải I, thời gian phủ và số xe trung bình qua các kịch bản
├── chi_so_tich_luy_session_A.csv     # Chuỗi giá trị tích lũy I_k theo thời gian của đoạn A
├── chi_so_tich_luy_session_B.csv     # Chuỗi giá trị tích lũy I_k theo thời gian của đoạn B
├── do_thi_dien_tich_session_A.png    # Đồ thị diện tích và đường tích lũy đoạn A
├── do_thi_dien_tich_session_B.png    # Đồ thị diện tích và đường tích lũy đoạn B
├── do_thi_khao_sat_do_nhay_AB.png    # Biểu đồ so sánh chỉ số tải I giữa các kịch bản khảo sát
└── README.md                         # Tài liệu mô tả thư mục
```

## 2. Yêu cầu kỹ thuật và quy trình xử lý

* **Dữ liệu đầu vào:** Đọc trực tiếp từ bảng dữ liệu chung `shared/analysis_snapshot.csv`, lọc theo `recording_id` và khung thời gian của hai đoạn A, B đã xác định ở Tuần 1.
* **Thuật toán:** Tự lập trình quy tắc hình thang trên lưới không đều sử dụng kiểu dữ liệu bắt buộc `np.float64` (không dùng các hàm tích phân có sẵn của thư viện).
* **Quy tắc ngắt đoạn (Gap):** Tự động chia thành các đoạn liên tục khi khoảng cách thời gian $h_i > 3 \times \text{median}(h)$, không tính tích phân bắc cầu qua các khoảng thiếu dữ liệu.
* **Kịch bản khảo sát độ nhạy:**
  1. Tính trên lưới gốc đầy đủ ($h_0$).
  2. Làm thưa lưới đều: giữ lại mỗi 2 mốc ($2h_0$) và mỗi 4 mốc ($4h_0$), cố định hai mốc đầu/cuối.
  3. Mất dữ liệu ngẫu nhiên: loại bỏ ngẫu nhiên 10% và 20% số mốc nội bộ với `seed=2026` (giữ hai mốc đầu/cuối và áp dụng lại quy tắc ngắt đoạn qua gap).

## 3. Tóm tắt kết quả thực nghiệm

Đơn vị tính: thời gian tính bằng **phút**, chỉ số tải tích lũy $I$ tính bằng **xe·phút**, và mật độ trung bình theo thời gian $\bar{y}_t$ tính bằng **xe** (số xe trung bình).

| Session | Kịch bản | Số mốc | Ngưỡng gap (phút) | Chỉ số $I$ (xe·phút) | Thời gian phủ (phút) | Số xe trung bình $\bar{y}_t$ (xe) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **A** | 1. Gốc (Full) | 99 | 1.85 | 1418.58 | 67.85 | 20.91 |
| **A** | 2. Giữ mỗi 2 mốc | 50 | 1.85 | 1497.76 | 67.85 | 22.07 |
| **A** | 2. Giữ mỗi 4 mốc | 26 | 1.85 | 1718.85 | 67.85 | 25.33 |
| **A** | 3. Mất 10% mốc nội bộ | 89 | 1.85 | 1296.54 | 63.55 | 20.40 |
| **A** | 3. Mất 20% mốc nội bộ | 80 | 1.85 | 1320.98 | 63.57 | 20.78 |
| **B** | 1. Gốc (Full) | 99 | 1.25 | 243.89 | 48.13 | 5.07 |
| **B** | 2. Giữ mỗi 2 mốc | 50 | 1.25 | 258.00 | 48.13 | 5.36 |
| **B** | 2. Giữ mỗi 4 mốc | 26 | 1.25 | 252.44 | 48.13 | 5.24 |
| **B** | 3. Mất 10% mốc nội bộ | 89 | 1.25 | 226.24 | 45.23 | 5.00 |
| **B** | 3. Mất 20% mốc nội bộ | 80 | 1.25 | 204.83 | 41.93 | 4.88 |

**Nhận xét chính:**
* Khi làm thưa lưới đều (giữ mỗi 2 hoặc 4 mốc), tổng thời gian bao phủ không đổi nhưng sai số xấp xỉ hình thang tăng lên do bỏ qua các biến động cục bộ của lưu lượng xe.
* Khi mất ngẫu nhiên 10%–20% mốc nội bộ, một số khoảng cách vượt ngưỡng gap làm ngắt đoạn và giảm tổng thời gian phủ thực tế; tuy nhiên chỉ số số xe trung bình $\bar{y}_t$ vẫn duy trì tính ổn định cao quanh mức ~20.4–20.9 xe (đoạn A) và ~4.9–5.1 xe (đoạn B).

## 4. Hướng dẫn chạy lại mã nguồn

Đặt tệp dữ liệu chung `analysis_snapshot.csv` (hoặc `shared/analysis_snapshot.csv`) cùng hai tệp ranh giới `segment_A_30s.csv`, `segment_B_30s.csv` ở thư mục làm việc hiện tại, sau đó chạy lệnh:

```bash
python nhom11_tuan3.py
```
