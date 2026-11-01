# Nhóm 11 — Đề tài 11 — Minh chứng Tuần 1

Đề tài: Chỉ số tải tích lũy bằng công thức hình thang.

## 1. Phạm vi và trạng thái

Gói này minh chứng việc chọn hai đoạn A/B và dựng khung Python chạy thử trong Tuần 1. Không phải hồ sơ hoàn chỉnh của toàn bộ phần Phương pháp tính 6 điểm.

Dữ liệu camera hiện dùng nhãn `unreviewed_prelabel` (PRELABEL). Mọi kết quả camera là **SƠ BỘ**, không phải ground truth. Không tự đổi trạng thái nhãn thành `human_verified`.

## 2. Thành phần gói

| Đường dẫn | Nội dung |
|---|---|
| `data/segment_A.csv` | 100 quan sát nguồn của A, giữ nguyên các cột và nhãn |
| `data/segment_B.csv` | 100 quan sát nguồn của B, giữ nguyên các cột và nhãn |
| `data/selection_summary.csv` | Tóm tắt lựa chọn, thời gian, số mốc, ngưỡng gap và trạng thái |
| `data/segment_A_30s.csv` | Bản lưới 30 giây của A, xuất sau khi chạy script tái lấy mẫu |
| `data/segment_B_30s.csv` | Bản lưới 30 giây của B, xuất sau khi chạy script tái lấy mẫu |
| `nhom11_hinh_thang_chay_thu.py` | Tự tính hình thang, tích lũy và trung bình theo thời gian từ CSV nguồn |
| `src/chon_doan.py` | Kiểm tra và xuất A/B từ snapshot chung |
| `src/tai_lay_mau.py` | Nội suy tuyến tính trên lưới 30 giây trong từng đoạn liên tục |
| `README.md` | Hướng dẫn và giới hạn sử dụng |

Các CSV kết quả `A_tich_luy.csv`, `A_tong_hop.csv`, `B_tich_luy.csv`, `B_tong_hop.csv` được tạo khi chạy tính thử. Kiểm tra đủ các file đầu vào trong bảng trước khi nén; README không tự tạo các file đó.

## 3. Nguồn và lựa chọn dữ liệu

Nguồn: `shared/analysis_snapshot.csv` trong gói Traffic_BTL do giảng viên cung cấp, không tự đếm lại từ batch ảnh riêng của nhóm để thay snapshot.

| Đoạn | Recording | Số quan sát gốc | Thời điểm đầu (+07:00) | Thời điểm cuối (+07:00) |
|---|---|---:|---|---|
| A | camnutgiaocaygo3_2026-07-13_R01 | 100 | 2026-07-13 06:08:41 | 2026-07-13 07:17:09 |
| B | camnutgiaocaygo3_2026-07-16_R01 | 100 | 2026-07-16 00:00:22 | 2026-07-16 00:48:55 |

Hai đoạn được xử lý riêng. Thông tin truy vết giữ trong CSV nguồn. Kiểm tra tự động không thay thế đối chiếu camera/góc nhìn từ ảnh; không coi việc xuất file thành công là nhãn đã nghiệm thu.

## 4. Dữ liệu gốc và lưới 30 giây

- `segment_A.csv` và `segment_B.csv` là đầu vào tính hình thang chính, dùng timestamp thật và số đếm nguồn.
- `segment_A_30s.csv` và `segment_B_30s.csv` là dữ liệu dẫn xuất để minh chứng tái lấy mẫu.
- Bước cơ sở: h0 = 30 giây = 0,5 phút, không phải 0,5 giây.
- Lưới bắt đầu tại đầu từng đoạn liên tục, kết thúc ở mốc 30 giây cuối còn trong miền. Không ép thêm điểm cuối ngoài lưới, không ngoại suy, không nội suy qua gap.
- `count_value` là giá trị trên lưới; có thể là số thập phân do nội suy, không phải số xe quan sát nguyên mới.
- `is_resampled=True` đánh dấu điểm nội suy; `False` khi mốc trùng quan sát nguồn. `source_image_ids` lưu ID ảnh nguồn dùng cho giá trị đó.
- Số mốc lưới không phải số quan sát thật độc lập. Không đổi bản nội suy thành nhãn đã kiểm định.
- Code hình thang hiện đọc schema nguồn, không đọc trực tiếp schema `count_value` của các file 30s. Các file 30s không được tự động đưa vào phép tính chính.

Đề tài 11 cho phép bước thời gian không đều; bản 30s được nộp bổ sung theo checklist chuẩn bị dữ liệu.

## 5. Phương pháp tính thử

Với t tính bằng phút, y là `total_count`:

    h_i = t_(i+1) - t_i
    I = tổng [h_i * (y_i + y_(i+1)) / 2]

Ngưỡng gap bằng 3 lần trung vị bước thời gian dương. Khoảng vượt ngưỡng không được tích phân. Tổng thời gian phủ chỉ gồm các khoảng được chấp nhận.

    Trung bình theo thời gian = I / tổng thời gian phủ

Đơn vị: h và thời gian phủ là phút; I và chỉ số tích lũy là xe·phút; trung bình là xe. Số xe hiện diện không phải lưu lượng; I không phải tổng số xe duy nhất đi qua.

Script tính thử dùng `float` Python (độ chính xác kép trên môi trường chạy hiện tại). Script tái lấy mẫu dùng `numpy.float64`. Không dùng bộ tích phân thư viện thay công thức chủ đạo. Chọn đoạn, hình thang và nội suy là các bước xác định, không phát sinh số ngẫu nhiên; seed quy ước của dự án là 2026 khi chạy thí nghiệm ngẫu nhiên.

## 6. Chạy tính thử trong gói nộp

Mở Terminal tại thư mục chứa README này. Dùng Python 3.10 trở lên:

```bash
python3 nhom11_hinh_thang_chay_thu.py data/segment_A.csv --output-prefix A
python3 nhom11_hinh_thang_chay_thu.py data/segment_B.csv --output-prefix B
```

Hai lệnh trên chỉ dùng thư viện chuẩn Python, không cần NumPy hay snapshot bên ngoài vì đã có hai CSV nguồn trong gói.

Kết quả đối chiếu của lần chạy sơ bộ trên dữ liệu hiện tại:

| Đoạn | Thời gian phủ (phút) | Gap | Tích phân (xe·phút) | Trung bình (xe) |
|---|---:|---:|---:|---:|
| A | 68.466666667 | 0 | 1438.925000000 | 21.016431353 |
| B | 48.550000000 | 0 | 246.391666667 | 5.075008582 |

Đây là kết quả từ PRELABEL; có thể thay đổi sau khi cập nhật nhãn nghiệm thu.

## 7. Tạo lại hai file lưới 30 giây trong gói

Script đọc `data/segment_A.csv` và `data/segment_B.csv` tương đối với thư mục gốc của gói, nên có thể chạy ngay trong gói nộp:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install numpy
python src/tai_lay_mau.py
```

Lệnh ghi hai file `data/segment_A_30s.csv` và `data/segment_B_30s.csv`. Nếu cần khóa chính xác phiên bản môi trường, kèm thêm `requirements.txt` từ môi trường đã chạy. Không nộp thư mục `.venv`.

## 8. Tạo lại lựa chọn A/B từ snapshot

`src/chon_doan.py` cần NumPy và cần dự án Traffic_BTL gốc có `shared/analysis_snapshot.csv`. Chạy tại gốc Traffic_BTL:

```bash
python3 src/chon_doan.py
```

Trong gói nộp tách riêng không có thư mục `shared`, không chạy script chọn đoạn trực tiếp trừ khi bổ sung đúng snapshot nguồn vào đường dẫn tương ứng. Không cần chạy bước này để tái lập phép tính trên A/B đã đóng gói.

## 9. ROI và cập nhật sau nghiệm thu

Đề tài 11 dùng `total_count` trên toàn ảnh, không dùng số đo ROI. Giữ nguyên `roi_valid=False` và các số đo ROI trống khi chưa được xác nhận; không thay bằng 0.

Tuần 5–6 sử dụng snapshot chính thức do giảng viên cung cấp sau nghiệm thu để chạy lại. Nếu được giao tạo lại snapshot từ nhãn đã sửa, dùng công cụ `rebuild_analysis.py` của giảng viên theo hướng dẫn và quyết định nghiệm thu thực tế. Công cụ không tự biến nhãn đã sửa thành `human_verified` khi chưa có xác nhận.

Cập nhật dữ liệu, trạng thái kết quả và minh chứng trước khi dùng kết quả chính thức. Không dùng hai phân bố/ảnh chung làm lý do phát sinh nhiệm vụ review toàn batch cho nhóm khác.
