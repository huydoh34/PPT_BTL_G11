# Minh chứng GĐ2 — Tuần 47 | Nhóm 11

**Đề tài 11:** Chỉ số tải tích lũy bằng công thức hình thang ghép trên lưới thời gian không đều.  
**Mốc Tuần 47:** hoàn tất pipeline, chạy được trên dữ liệu chung, có bảng và đồ thị nháp; có kết quả kiểm thử đối chiếu.

## Phân biệt phần đã có và phần bổ sung

| Nội dung | Nguồn | Tình trạng |
|---|---|---|
| Chọn A/B và mốc thời gian | [`Tuan1/`](../Tuan1/) | Đã có; tái sử dụng |
| Thuật toán, kiểm chứng trên `1+t²` | [`Tuan2/`](../Tuan2/) | Đã có; chạy lại và kiểm tra |
| Tích phân A/B, 10 kịch bản | [`Tuan3/`](../Tuan3/) | Đã có; đối chiếu 10/10 |
| Ba biểu đồ diện tích/tích lũy/độ nhạy | [A](../Tuan3/do_thi_dien_tich_session_A.png), [B](../Tuan3/do_thi_dien_tich_session_B.png), [độ nhạy](../Tuan3/do_thi_khao_sat_do_nhay_AB.png) | **Chỉ tham chiếu; không vẽ lại** |
| Pipeline chạy lại bằng một lệnh | [`run_tuan47.py`](run_tuan47.py) | **Bổ sung ở Tuần 47** |
| Đối chiếu từ **snapshot nguồn** có `image_id` | [`verification_snapshot/`](verification_snapshot/) | **Đã chạy thực tế trên 200 dòng nguồn** |
| Kiểm toán khoảng thiếu và ngưỡng gap từng kịch bản | [`verification_snapshot/bang_theo_doan.csv`](verification_snapshot/bang_theo_doan.csv), [`bang_tong_hop_AB.csv`](verification_snapshot/bang_tong_hop_AB.csv) | **Bổ sung ở Tuần 47** |
| Kiểm thử tự động và kiểm tra nguồn | [`tests/`](tests/), [`kiem_toan_snapshot.csv`](verification_snapshot/kiem_toan_snapshot.csv) | **Bổ sung ở Tuần 47** |

## Kết quả trên file gốc `analysis_snapshot(1).csv`

- File snapshot: **200 dòng**, hai recording A/B, mỗi recording **100 ảnh**, toàn bộ là `unreviewed_prelabel`.
- Cửa sổ 30 giây Tuần 1 chỉ bao gồm **99 ảnh/đoạn**. Mỗi recording có đúng **1 ảnh cuối nằm sau biên thời gian** (A: 07:17:09 sau 07:16:41; B: 00:48:55 sau 00:48:52).
- **0/200** dòng sai phép cộng `total_count = count_2wheel + count_bus + count_car + count_truck`.
- **198/198** cặp quan sát `(t,y)` trong cửa sổ khớp với chuỗi đã lưu ở Tuần 3; ghi lại `image_id` để truy vết.
- **10/10** kịch bản thí nghiệm khớp giá trị lưu trong bảng Tuần 3 (dung sai `1e-6`).

| Session | Ảnh nguồn | Mốc trong cửa sổ | I (xe·phút) | Thời gian phủ (phút) | Xe TB (xe) |
|---|---:|---:|---:|---:|---:|
| A | 100 | 99 | 1.418,575 | 67,850000 | 20,907517 |
| B | 100 | 99 | 243,891667 | 48,133333 | 5,067001 |

**SHA256 file nguồn đã dùng:** `7c285069884c59da28a571589edb2cbf273e4c559e0606c92f198dca654ab172`. File snapshot gốc không tự động được phát hành lên repository; dữ liệu kiểm toán và báo cáo đầu ra nằm ở [`verification_snapshot/`](verification_snapshot/).

## Kết luận phạm vi Tuần 47

Pipeline và bằng chứng số học đã hoàn thiện trên bản PRELABEL. **Chưa được coi là kết quả từ nhãn nghiệm thu**; cần chạy lại với dữ liệu `human_verified` khi có. Độ nhạy lấy mẫu không phải sai số so với nghiệm tích phân thực. Chỉ số $I$ có đơn vị **xe·phút**, không được gọi là số lượt xe đi qua.
