import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def resample(segment):
    source = ROOT / "data" / f"segment_{segment}.csv"

    with source.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    rows.sort(key=lambda r: datetime.fromisoformat(r["timestamp"]))
    if len(rows) < 2:
        raise ValueError(f"{segment}: cần ít nhất hai quan sát.")

    for col in ("camera_id", "recording_id", "label_status"):
        values = {r[col] for r in rows}
        if len(values) != 1 or not all(values):
            raise ValueError(f"{segment}: {col} không thống nhất.")

    dates = [datetime.fromisoformat(r["timestamp"]) for r in rows]
    if any(d.utcoffset() is None for d in dates):
        raise ValueError("Timestamp thiếu múi giờ.")

    t = np.array(
        [(d - dates[0]).total_seconds() for d in dates],
        dtype=np.float64
    )
    y = np.array(
        [float(r["total_count"]) for r in rows],
        dtype=np.float64
    )

    steps = np.diff(t)
    if np.any(steps <= 0):
        raise ValueError("Timestamp trùng hoặc không tăng.")
    if not np.all(np.isfinite(y)) or np.any(y < 0):
        raise ValueError("Số đếm không hợp lệ.")

    gap_limit = 3 * np.median(steps)
    cuts = np.r_[0, np.flatnonzero(steps > gap_limit) + 1, len(rows)]
    output = []

    for part, (left, right) in enumerate(zip(cuts[:-1], cuts[1:]), 1):
        # Lưới bắt đầu tại đầu từng đoạn liên tục.
        # Chỉ lấy mốc còn nằm trong miền, không ngoại suy.
        duration = t[right - 1] - t[left]
        grid = t[left] + 30 * np.arange(
            int(np.floor(duration / 30)) + 1,
            dtype=np.float64
        )

        for target in grid:
            pos = int(np.searchsorted(t[left:right], target)) + left
            exact = (
                pos < right
                and abs(t[pos] - target) < 1e-9
            )

            if exact:
                value = y[pos]
                ids = [rows[pos]["image_id"]]
            else:
                lo, hi = pos - 1, pos
                weight = (target - t[lo]) / (t[hi] - t[lo])
                value = y[lo] + weight * (y[hi] - y[lo])
                ids = [rows[lo]["image_id"], rows[hi]["image_id"]]

            output.append({
                "analysis_segment": segment,
                "continuous_part": part,
                "camera_id": rows[left]["camera_id"],
                "recording_id": rows[left]["recording_id"],
                "timestamp": (
                    dates[0] + timedelta(seconds=float(target))
                ).isoformat(),
                "time_from_part_start_min": float(
                    (target - t[left]) / 60
                ),
                "count_value": float(value),
                "is_resampled": not exact,
                "source_image_ids": json.dumps(ids),
                "label_status": rows[left]["label_status"],
                "method": "observed" if exact else "linear_interpolation",
                "step_seconds": 30,
                "result_status": "PRELIMINARY_NOT_GROUND_TRUTH"
            })

    path = ROOT / "data" / f"segment_{segment}_30s.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)

    print(f"Đã lưu {path.name}: {len(output)} mốc lưới")
    print("Các mốc nội suy không phải quan sát thật mới.")


if __name__ == "__main__":
    for segment in ("A", "B"):
        resample(segment)
