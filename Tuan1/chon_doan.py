
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "shared/analysis_snapshot.csv"
output = ROOT / "data"

with source.open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames
    rows = list(reader)

required = {
    "image_id", "camera_id", "recording_id",
    "timestamp", "total_count", "label_status", "analysis_segment"
}
if not columns or not required.issubset(columns):
    raise ValueError(f"Thiếu cột: {required - set(columns or [])}")

# Không âm thầm loại các ID bị trùng.
duplicates = [
    image_id for image_id, count in
    Counter(r["image_id"] for r in rows).items()
    if count > 1
]
if duplicates:
    raise ValueError(f"Có image_id trùng, cần kiểm tra: {duplicates[:5]}")

selected = {}
summary = []

for segment in ("A", "B"):
    group = [r for r in rows if r["analysis_segment"] == segment]
    group.sort(key=lambda r: datetime.fromisoformat(r["timestamp"]))

    if not 80 <= len(group) <= 300:
        raise ValueError(f"{segment}: cần 80–300 quan sát.")

    for column in ("camera_id", "recording_id", "label_status"):
        values = {r[column] for r in group}
        if len(values) != 1 or not all(values):
            raise ValueError(f"{segment}: {column} thiếu hoặc không thống nhất.")

    # Kiểm tra góc nhìn nếu snapshot có khai báo.
    if "view_id" in columns:
        views = {r["view_id"] for r in group}
        if len(views) != 1:
            raise ValueError(f"{segment}: view_id không thống nhất.")
        view_note = next(iter(views)) or "Chưa có thông tin view_id"
    else:
        view_note = "Snapshot không có cột view_id"

    times = [datetime.fromisoformat(r["timestamp"]) for r in group]
    if any(t.utcoffset() is None for t in times):
        raise ValueError(f"{segment}: timestamp thiếu múi giờ.")

    counts = np.array(
        [float(r["total_count"]) for r in group],
        dtype=np.float64
    )
    if (
        not np.all(np.isfinite(counts))
        or np.any(counts < 0)
        or np.any(counts != np.floor(counts))
    ):
        raise ValueError(f"{segment}: số đếm không hợp lệ.")

    steps = np.array([
        (times[i + 1] - times[i]).total_seconds() / 60
        for i in range(len(times) - 1)
    ], dtype=np.float64)

    if np.any(steps <= 0):
        raise ValueError(f"{segment}: timestamp trùng hoặc không tăng.")

    gap_limit = 3 * np.median(steps)
    if np.any(steps > gap_limit):
        raise ValueError(f"{segment}: có gap, cần tách đoạn trước khi chọn.")

    if "is_resampled" in columns:
        if any(
            r["is_resampled"].strip().lower() not in ("false", "0")
            for r in group
        ):
            raise ValueError(
                f"{segment}: có điểm tái lấy mẫu hoặc trạng thái chưa rõ."
            )

    selected[segment] = group
    summary.append({
        "segment": segment,
        "camera_id": group[0]["camera_id"],
        "recording_id": group[0]["recording_id"],
        "view_note": view_note,
        "observations": len(group),
        "start": group[0]["timestamp"],
        "end": group[-1]["timestamp"],
        "duration_min": (times[-1] - times[0]).total_seconds() / 60,
        "median_step_min": float(np.median(steps)),
        "gap_limit_min": float(gap_limit),
        "gap_count": 0,
        "label_status": group[0]["label_status"],
        "source": "shared/analysis_snapshot.csv",
        "result_status": "PRELIMINARY_NOT_GROUND_TRUTH"
    })

if selected["A"][0]["label_status"] != selected["B"][0]["label_status"]:
    raise ValueError("A/B khác trạng thái nhãn.")

# A/B không được giao nhau về thời gian nếu cùng recording và camera.
a, b = selected["A"], selected["B"]
if (
    a[0]["camera_id"] == b[0]["camera_id"]
    and a[0]["recording_id"] == b[0]["recording_id"]
):
    a0, a1 = map(
        datetime.fromisoformat, (a[0]["timestamp"], a[-1]["timestamp"])
    )
    b0, b1 = map(
        datetime.fromisoformat, (b[0]["timestamp"], b[-1]["timestamp"])
    )
    if max(a0, b0) <= min(a1, b1):
        raise ValueError("Hai đoạn A/B giao nhau trong cùng recording.")

# Chỉ xuất khi các bước kiểm tra trên đã qua.
output.mkdir(exist_ok=True)

for segment, group in selected.items():
    path = output / f"segment_{segment}.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(group)
    print(f"Đã lưu: {path.name} — {len(group)} quan sát")

path = output / "selection_summary.csv"
with path.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(summary[0]))
    writer.writeheader()
    writer.writerows(summary)

print("Đã lưu: selection_summary.csv")
print("Giữ nguyên nhãn nguồn — kết quả SƠ BỘ / PRELABEL.")
print("Lưu ý: kiểm tra bằng CSV không thay thế đối chiếu camera/góc nhìn từ ảnh.")
