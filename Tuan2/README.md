## Tuần 2 – Cài đặt thuật toán và kiểm chứng

### 1. Cài đặt thuật toán chính

**File:** `nhom11_hinh_thang_chay_thu.py`

- Tự cài đặt phương pháp hình thang ghép cho dữ liệu có bước thời gian không đều.
- Sử dụng `timestamp` và `total_count` từ dữ liệu phân tích.
- Phát hiện khoảng thiếu dữ liệu bằng ngưỡng 3 lần trung vị bước thời gian.
- Không tích phân qua các khoảng thiếu bị loại.
- Tính tích phân, chỉ số tải tích lũy và số xe trung bình theo thời gian.

Kết quả chạy thử trên hai đoạn A/B sử dụng nhãn PRELABEL, chưa được xem là ground truth.

### 2. Kiểm chứng thuật toán

**Script:** `src/kiem_chung.py`

**Kết quả:** `results/nhom11_kiem_chung.csv`

Kiểm chứng bằng hàm:

\(f(t)=1+t^2\), trên đoạn \([0,1]\).

Tích phân chính xác: \(I=4/3\).

Các cấu hình kiểm chứng:
- Lưới đều: 10, 20 và 40 khoảng.
- Lưới không đều: \(t_j=(j/20)^2\), với \(j=0,\ldots,20\).

Kết quả gồm tích phân xấp xỉ, sai số tuyệt đối, bậc hội tụ và đối chứng với `numpy.trapezoid`.

**Nhận xét:** Sai số giảm khoảng 4 lần khi số khoảng tăng gấp đôi; bậc hội tụ thực nghiệm xấp xỉ 2, phù hợp với tính chất của phương pháp hình thang trên hàm kiểm chứng.

### 3. Cách chạy kiểm chứng

Tại thư mục gốc của repository:

```bash
pip install numpy
python src/kiem_chung.py
```

Kết quả được xuất vào `results/nhom11_kiem_chung.csv`.

### 4. Trạng thái

Đã cài đặt thuật toán chính và có kết quả kiểm chứng trên bài toán biết nghiệm đúng. Kết quả ứng dụng trên dữ liệu camera vẫn là sơ bộ (PRELABEL).
