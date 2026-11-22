# G11 | Báo cáo kiểm tra pipeline - Tuần 47

Đề tài 11: Chỉ số tải tích lũy bằng công thức hình thang trên bước thời gian không đều.

**Nguồn dữ liệu:** `analysis_snapshot(1).csv`.

**Nguồn nhãn:** unreviewed_prelabel (A và B đồng nhất).

**Phân biệt dữ liệu:** I có đơn vị xe·phút, ȳ có đơn vị xe; không được gọi I là tổng số xe đi qua.

## Kết quả chạy lại

| Đoạn | Recording | Mốc gốc | I (xe·phút) | T phủ (phút) | ȳ (xe) |
|:--|:--|--:|--:|--:|--:|
| A | `camnutgiaocaygo3_2026-07-13_R01` | 99 | 1418.575000 | 67.850000 | 20.907517 |
| B | `camnutgiaocaygo3_2026-07-16_R01` | 99 | 243.891667 | 48.133333 | 5.067001 |

## Kiểm toán snapshot gốc đã cung cấp

SHA256 của file nguồn: `7c285069884c59da28a571589edb2cbf273e4c559e0606c92f198dca654ab172`. File nguồn không được tự động đóng gói/đưa lên GitHub.

| Đoạn | Số ảnh nguồn | Đã chọn | Ngoài cửa sổ (sau cuối) | Khớp chuỗi Tuần 3 | Sai tổng bốn lớp |
|:--|--:|--:|--:|:--:|--:|
| A | 100 | 99 | 1 | True | 0 |
| B | 100 | 99 | 1 | True | 0 |

Mỗi recording có 100 ảnh trong snapshot. Khi giới hạn đến mốc cuối của lưới 30 giây ở Tuần 1, một ảnh cuối của A và một ảnh cuối của B nằm sau cửa sổ nên không đưa vào tích phân. Đây không phải mất dữ liệu nguồn.

Chuỗi `chi_so_tich_luy_AB.csv` của lần chạy này ghi `image_id` gốc cho từng mốc đã sử dụng; bảng `kiem_toan_snapshot.csv` lưu thông tin đối chiếu.

## Kiểm chứng công thức

f(t) = 1 + t², t ∈ [0,1]; tích phân thật I=4/3. Bậc hội tụ thực nghiệm p≈2 khi h giảm một nửa.

## Kiểm tra chéo với Tuần 3

Tái tạo **10/10** kịch bản từ CSV đã lưu của nhóm (dung sai 1e-6).

**Điểm chỉnh so với báo cáo cũ:** Ngưỡng gap (3×median(h)) thay đổi theo từng kịch bản lấy mẫu; cột `gap_threshold_min` báo đúng ngưỡng đã áp dụng. Đặc biệt mỗi 2 mốc và mỗi 4 mốc có ngưỡng lớn hơn bản gốc.

## Giới hạn / các việc còn lại

- Không tự đưa snapshot gốc vào GitHub; lần chạy này đã dùng snapshot và truy vết `image_id` gốc trong `chi_so_tich_luy_AB.csv`.
- Cần snapshot `human_verified` chính thức để cập nhật các kết quả trên nhãn đã nghiệm thu.
- Đối chiếu số học không đồng nghĩa với nghiệm thu nhãn; kết quả chỉ dựa trên `unreviewed_prelabel` khi dữ liệu nguồn còn ở trạng thái này.
- Các kịch bản mất mốc và giữ thưa đo độ nhạy, chênh lệch so với lưới đầy đủ không phải sai số so với tích phân thật.
- Session Tuần 1 ghi 100 ảnh mỗi đoạn, nhưng bản ranh giới 30 giây giới hạn cửa sổ thí nghiệm chỉ còn 99 mốc nguồn ở Tuần 3; cần nêu rõ để tránh nhầm thành thiếu một ảnh trong batch.

## Tệp xuất

- `kiem_chung_hinh_thang.csv`: lưới 10/20/40 và lưới không đều
- `bang_tong_hop_AB.csv`: 10 kịch bản A/B, gap thực tế và chênh lệch so với gốc
- `bang_theo_doan.csv`: thời gian phủ, tích phân từng đoạn
- `chi_so_tich_luy_AB.csv`: chuỗi tích lũy theo từng điểm và mỗi kịch bản
- `doi_chieu_Tuan3.csv`: đối chiếu 10 kịch bản đã lưu của nhóm
- `kiem_toan_snapshot.csv`: số ảnh nguồn, số mốc chọn, mốc nằm ngoài cửa sổ, kiểm tra tổng xe và hash file nguồn
- Không xuất PNG ở Tuần 4: các hình số xe/diện tích/I_k/độ nhạy đều đã có trong Tuần 3.

## Đồ thị đã có ở Tuần 3 — tham chiếu, không xuất lại

- [Diện tích đoạn A (Tuần 3)](../../Tuan3/do_thi_dien_tich_session_A.png) — đồ thị có sẵn; không tạo bản sao trong Tuần 4.
- [Diện tích đoạn B (Tuần 3)](../../Tuan3/do_thi_dien_tich_session_B.png) — đồ thị có sẵn; không tạo bản sao trong Tuần 4.
- [Khảo sát độ nhạy A/B (Tuần 3)](../../Tuan3/do_thi_khao_sat_do_nhay_AB.png) — đồ thị có sẵn; không tạo bản sao trong Tuần 4.

Tuần 4 không tạo lại biểu đồ. Phần bổ sung là code tái lập, kiểm thử, đối chiếu số học và CSV kiểm toán khoảng thiếu.
