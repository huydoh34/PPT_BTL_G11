# GĐ2 — Tuần 47 | Tích hợp, kiểm thử và đối chiếu dữ liệu nguồn

Mục tiêu tuần này là **chạy được pipeline từ đầu đến cuối** trên hai đoạn A/B của Đề tài 11, kiểm chứng công thức và đối chiếu với kết quả lưu ở Tuần 3; không trình bày các biểu đồ cũ như sản phẩm mới.

## Dữ liệu sử dụng

- Tuần 1: [`selection_summary.csv`](../Tuan1/selection_summary.csv) xác định recording A/B, mỗi recording 100 ảnh.
- Tuần 1: [`result/segment_A_30s.csv`](../Tuan1/result/segment_A_30s.csv) và [`result/segment_B_30s.csv`](../Tuan1/result/segment_B_30s.csv) cung cấp **cửa sổ thời gian phân tích**. Mốc tái lấy mẫu không được xem là ảnh quan sát thực.
- Tuần 2: [`nhom11_kiem_chung.py`](../Tuan2/src/nhom11_kiem_chung.py) kiểm chứng hàm có nghiệm đúng `1+t²`.
- Tuần 3: [`chi_so_tich_luy_session_A.csv`](../Tuan3/chi_so_tich_luy_session_A.csv), [`chi_so_tich_luy_session_B.csv`](../Tuan3/chi_so_tich_luy_session_B.csv) và [`bang_tich_phan_tuan3_AB.csv`](../Tuan3/bang_tich_phan_tuan3_AB.csv) làm tham chiếu.
- **Snapshot kiểm chứng:** `analysis_snapshot(1).csv` do nhóm cung cấp, SHA256 `7c285069884c59da28a571589edb2cbf273e4c559e0606c92f198dca654ab172`. File gồm **200 ảnh nguồn = 100 A + 100 B**, đều `unreviewed_prelabel`; `is_resampled=False` ở cả 200 hàng.

Sau khi giới hạn theo thời điểm cuối của lưới 30 giây Tuần 1, **A và B mỗi đoạn còn 99 điểm thực**. Cụ thể:

| Đoạn | Kết thúc cửa sổ 30s | Ảnh cuối của snapshot | Xử lý |
|---|---|---|---|
| A | `2026-07-13 07:16:41+07:00` | `2026-07-13 07:17:09+07:00` | Không tích phân qua mốc cuối nằm ngoài cửa sổ |
| B | `2026-07-16 00:48:52+07:00` | `2026-07-16 00:48:55+07:00` | Không tích phân qua mốc cuối nằm ngoài cửa sổ |

**Đã kiểm chứng:** cả 198 điểm được chọn khớp `(timestamp, total_count)` với hai CSV Tuần 3, có `image_id` nguyên gốc trong lần chạy snapshot. **200/200** hàng trong snapshot có `total_count` bằng tổng 4 lớp, **10/10** kịch bản đối chiếu Tuần 3 đạt dung sai `1e-6`.

## Hai chế độ chạy lại

Từ thư mục gốc repository:

```bash
python3 -m pip install -r Tuan4/requirements.txt
python3 -m unittest discover -s Tuan4/tests -v
```

**(1) Chạy từ dữ liệu đã lưu ở GitHub:**

```bash
python3 Tuan4/run_tuan47.py
```

Tạo báo cáo và CSV ở `Tuan4/results/`, chỉ có `(t,y)` từ Tuần 3 và **không có `image_id`** gốc.

**(2) Chạy kiểm toán lại snapshot nguồn:**

```bash
python3 Tuan4/run_tuan47.py \
  --snapshot "/duong/dan/analysis_snapshot.csv" \
  --out Tuan4/verification_snapshot
```

Tạo báo cáo và CSV ở `Tuan4/verification_snapshot/`, gồm `image_id` gốc và hash SHA256. File snapshot **không được đóng gói vào GitHub**; thầy có thể dùng file lớp cung cấp để tái chạy và so sánh hash. Thay `--snapshot` bằng đường dẫn thực tế.

## Các sản phẩm kiểm toán Tuần 47

| File | Công dụng |
|---|---|
| [`run_tuan47.py`](run_tuan47.py) | Tích phân hình thang trên lưới không đều, ngắt gap, tích lũy, 5 kịch bản/đoạn |
| [`tests/test_tuan47.py`](tests/test_tuan47.py) | Kiểm chứng lý thuyết, số học, mốc thời gian và không trùng ảnh |
| [`verification_snapshot/kiem_toan_snapshot.csv`](verification_snapshot/kiem_toan_snapshot.csv) | Kiểm ảnh gốc, mốc bị loại, nguồn nhãn, SHA256 và tính nhất quán bốn lớp |
| [`verification_snapshot/bang_tong_hop_AB.csv`](verification_snapshot/bang_tong_hop_AB.csv) | I, thời gian phủ, trung bình xe, ngưỡng gap cho đủ 10 kịch bản |
| [`verification_snapshot/bang_theo_doan.csv`](verification_snapshot/bang_theo_doan.csv) | Tích phân và thời gian phủ theo đoạn liên tục |
| [`verification_snapshot/chi_so_tich_luy_AB.csv`](verification_snapshot/chi_so_tich_luy_AB.csv) | Tích lũy ở từng mốc và `image_id` nguồn cho 5 kịch bản/đoạn |
| [`verification_snapshot/doi_chieu_Tuan3.csv`](verification_snapshot/doi_chieu_Tuan3.csv) | Đối chiếu 10/10 kịch bản với Tuần 3 |
| [`verification_snapshot/BAO_CAO_CHAY_LAI_TUAN47.md`](verification_snapshot/BAO_CAO_CHAY_LAI_TUAN47.md) | Báo cáo chạy từ snapshot nguồn và kết quả kiểm chứng |
| [`results/`](results/) | Bản tái tạo từ CSV đã lưu, chạy được khi không có snapshot |

**Biểu đồ:** dùng nguyên ba hình Tuần 3 — [diện tích A](../Tuan3/do_thi_dien_tich_session_A.png), [diện tích B](../Tuan3/do_thi_dien_tich_session_B.png), [độ nhạy A/B](../Tuan3/do_thi_khao_sat_do_nhay_AB.png). Tuần 4 **không sinh PNG**.

## Giới hạn

- Toàn bộ 200 ảnh ở snapshot kiểm chứng là `unreviewed_prelabel` (`student_prelabels_yolov8_manual_v1`), **chưa phải human_verified**.
- Sai khác của các kịch bản lấy thưa/xóa mốc so với lưới gốc chỉ là **độ nhạy lấy mẫu**; lưới gốc không được mặc định là tích phân thật.
- `I` (xe·phút) phản ánh tải tích lũy; không phải tổng số lượt xe đi qua.
- Ngưỡng gap `3×median(h)` được tính **riêng cho mỗi lưới**; diện tích không bắc cầu qua gap.
- Kết quả snapshot hiện tại chỉ chứng minh **quy trình có thể tái lập và khớp với nguồn**. Để có kết quả từ nhãn đã nghiệm thu, cần dùng snapshot phiên bản mới sau nghiệm thu.
