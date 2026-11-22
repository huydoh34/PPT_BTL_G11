# Bài tập lớn Phương pháp tính — Nhóm 11 | Đề tài 11

**Đề tài:** Chỉ số tải tích lũy bằng công thức hình thang ghép trên lưới thời gian không đều.  
**Mốc công việc:** Giai đoạn 2 — Tuần 47: hoàn thiện pipeline, thử nghiệm trên `analysis_snapshot.csv` và kiểm chứng các kết quả A/B.

> **Trạng thái dữ liệu:** `unreviewed_prelabel` (PRELABEL), phiên bản `student_prelabels_yolov8_manual_v1` — **chưa phải nhãn nghiệm thu (`human_verified`)**. Chỉ số tích lũy $I$ mang đơn vị **xe·phút**, không phải tổng xe đã đi qua.

## 1. Bằng chứng đã chạy trên file snapshot nguồn

Đã chạy `Tuan4/run_tuan47.py` với file **`analysis_snapshot(1).csv`** do nhóm cung cấp, **không chỉ lấy lại kết quả cũ trong `Tuan3/`**:

| Chỉ tiêu | Đoạn A | Đoạn B |
|---|---:|---:|
| Recording | `camnutgiaocaygo3_2026-07-13_R01` | `camnutgiaocaygo3_2026-07-16_R01` |
| Số bản ghi gốc trong snapshot | **100** | **100** |
| Số mốc quan sát nằm trong cửa sổ phân tích | **99** | **99** |
| Mốc cuối nằm ngoài cửa sổ 30 giây | 1 | 1 |
| Tích phân $I$ (xe·phút) | **1.418,575** | **243,891667** |
| Thời gian được phủ (phút) | **67,85** | **48,133333** |
| Số xe trung bình theo thời gian (xe) | **20,907517** | **5,067001** |
| Số khoảng thiếu ở lưới gốc | 0 | 0 |

**Tại sao chỉ có 99/100 mốc?** File nguồn có đủ 100 ảnh cho mỗi recording. Tuần 1 tạo lưới 30 giây kết thúc lúc **07:16:41** ở A và **00:48:52** ở B. Ảnh cuối tương ứng có timestamp **07:17:09** và **00:48:55**, nên nằm sau biên cuối đã chọn và không được dùng để tích phân. Không có ảnh nào bị mất khỏi file nguồn.

**Đối chiếu:** tổng `total_count` đúng bằng tổng `count_2wheel + count_bus + count_car + count_truck` ở **200/200 dòng**. Hai chuỗi $(t,y)$ được chọn khớp với CSV của Tuần 3; cả **10/10 kịch bản** (5/A + 5/B) tái tạo đúng $I$, thời gian phủ và số xe trung bình với dung sai `1e-6`. Kiểm chứng hàm $1+t^2$ có bậc hội tụ xấp xỉ 2.

- [Báo cáo kiểm chứng trực tiếp từ snapshot](Tuan4/verification_snapshot/BAO_CAO_CHAY_LAI_TUAN47.md)
- [Bảng kiểm toán nguồn, số mốc và SHA256](Tuan4/verification_snapshot/kiem_toan_snapshot.csv)
- [Đối chiếu 10 kịch bản với Tuần 3](Tuan4/verification_snapshot/doi_chieu_Tuan3.csv)
- [Bảng tích lũy có `image_id` gốc](Tuan4/verification_snapshot/chi_so_tich_luy_AB.csv)
- [Minh chứng mốc Tuần 47](Tuan4/MINH_CHUNG_TUAN47.md)

SHA256 của file snapshot đã kiểm tra: `7c285069884c59da28a571589edb2cbf273e4c559e0606c92f198dca654ab172`. File nguồn do lớp chia sẻ **không được đóng gói vào repository**; các bảng đối soát đã lưu cho phép kiểm tra kết quả mà không tự phát tán bản gốc.

## 2. Cấu trúc repository

| Thư mục | Nội dung |
|---|---|
| [`Tuan1/`](Tuan1/) | Chọn A/B, thông tin recording, khung thời gian và lưới tái lấy mẫu 30 giây |
| [`Tuan2/`](Tuan2/) | Code hình thang tự cài và kiểm chứng giải tích; có script chạy lại |
| [`Tuan3/`](Tuan3/) | Hai chuỗi tích lũy A/B, bảng 10 kịch bản, **ba biểu đồ gốc** |
| [`Tuan4/`](Tuan4/) | **Tuần 47:** pipeline độc lập, kiểm thử, đối chiếu dữ liệu nguồn, các bảng kết quả và báo cáo; **không tạo hình trùng Tuần 3** |

**Biểu đồ gốc đã có ở Tuần 3:** [Diện tích và chỉ số tích lũy A](Tuan3/do_thi_dien_tich_session_A.png) · [Diện tích và chỉ số tích lũy B](Tuan3/do_thi_dien_tich_session_B.png) · [Độ nhạy lấy mẫu A/B](Tuan3/do_thi_khao_sat_do_nhay_AB.png). Tuần 4 chỉ liên kết đến các hình này, không xuất lại PNG.

## 3. Hướng dẫn chạy lại

### Yêu cầu

- Python 3.10 trở lên và `numpy>=1.24`.
- Từ thư mục **gốc repository** `PPT_BTL_G11`, cài môi trường rồi chạy kiểm thử:

```bash
python3 -m pip install -r Tuan4/requirements.txt
python3 -m unittest discover -s Tuan4/tests -v
```

**A. Tái tạo từ dữ liệu 99 mốc đã lưu trong GitHub** (không cần file dữ liệu lớp):

```bash
python3 Tuan4/run_tuan47.py
```

Đầu ra: `Tuan4/results/`.

**B. Đối chiếu trực tiếp với `analysis_snapshot.csv` của lớp** (có `image_id` gốc):

```bash
python3 Tuan4/run_tuan47.py \
  --snapshot "/duong/dan/analysis_snapshot.csv" \
  --out Tuan4/verification_snapshot
```

Đường dẫn trên chỉ là **ví dụ**; thay bằng vị trí file của bạn. Dùng dấu ngoặc kép nếu tên file có dấu cách hoặc là `analysis_snapshot(1).csv`. Đầu ra: `Tuan4/verification_snapshot/`; các bảng Tuần 3 và kết quả lưu sẵn không bị ghi đè.

**C. Kiểm chứng riêng Tuần 2** (chạy từ gốc repository):

```bash
python3 Tuan2/src/nhom11_kiem_chung.py
```

Đầu ra của lệnh này là `Tuan2/results/`.

## 4. Giới hạn của kết luận

1. Hai đoạn A/B đều là **PRELABEL**; việc khớp số học **không** chứng minh nhãn xe đã được nghiệm thu hoặc phân loại đúng 100%.
2. `total_count` là **số xe hiện diện tại thời điểm chụp**, không phải lưu lượng xe đi qua. $I$ đo tải tích lũy theo thời gian (xe·phút).
3. So sánh giữ mỗi 2/4 mốc hoặc mất ngẫu nhiên 10%/20% mốc với `seed=2026` là **khảo sát độ nhạy lấy mẫu**, không phải sai số với nghiệm đúng.
4. Ngưỡng khoảng thiếu bằng **3 lần trung vị bước thời gian**, được tính **lại cho từng kịch bản**; không tính tích phân bắc cầu qua khoảng thiếu.
5. Kết quả nghiệm thu cuối cùng cần chạy lại khi có snapshot mới mang `human_verified` và xác nhận phiên bản nhãn.

Chi tiết: [Tuan4/README.md](Tuan4/README.md) và [báo cáo kiểm chứng nguồn](Tuan4/verification_snapshot/BAO_CAO_CHAY_LAI_TUAN47.md).
