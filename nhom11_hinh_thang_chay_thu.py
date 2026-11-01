#!/usr/bin/env python3
"""Phần tính thử nhóm 11 - dữ liệu chưa nghiệm thu, chỉ dùng để chạy thử."""
import argparse
import csv
from collections import defaultdict
from datetime import datetime
from statistics import median
from pathlib import Path

def to_number(value):
    return int(value)

def run(source, output_prefix):
    with open(source, newline="", encoding="utf-8-sig") as f:
        records = list(csv.DictReader(f))
    if not records:
        raise ValueError("CSV không chứa bản ghi.")
    groups = defaultdict(list)
    for r in records:
        for col in ("image_id", "camera_id", "recording_id", "timestamp",
                    "total_count", "label_status", "analysis_segment"):
            if not r.get(col):
                raise ValueError(f"Thiếu {col} tại image_id={r.get('image_id', '?')}")
        timestamp = datetime.fromisoformat(r["timestamp"])
        if timestamp.tzinfo is None:
            raise ValueError("Timestamp phải có múi giờ.")
        groups[(r["analysis_segment"], r["recording_id"])].append(r)
    detailed = []
    summary = []
    for (segment, recording), group in sorted(groups.items()):
        group.sort(key=lambda r: datetime.fromisoformat(r["timestamp"]))
        times = [datetime.fromisoformat(r["timestamp"]) for r in group]
        counts = [to_number(r["total_count"]) for r in group]
        if any(x < 0 for x in counts):
            raise ValueError(f"Số lượng xe âm trong {recording}")
        steps = [(times[i] - times[i-1]).total_seconds() / 60
                 for i in range(1, len(times))]
        if any(step <= 0 for step in steps):
            raise ValueError(f"Timestamp trùng hoặc không tăng trong {recording}")
        gap_limit = 3 * median(steps) if steps else 0
        integral, covered_minutes, num_breaks = 0.0, 0.0, 0
        for i, r in enumerate(group):
            dt = steps[i-1] if i else 0.0
            is_gap = bool(i and dt > gap_limit)
            area = 0.0 if is_gap or i == 0 else dt * (counts[i-1]+counts[i])/2
            if is_gap:
                num_breaks += 1
            else:
                covered_minutes += dt
            integral += area
            detailed.append({
                "segment": segment, "recording_id": recording,
                "image_id": r["image_id"], "timestamp": r["timestamp"],
                "label_status": r["label_status"],
                "total_count": counts[i], "delta_t_min": f"{dt:.9f}",
                "gap_detected": str(is_gap),
                "interval_vehicles_min": f"{area:.9f}",
                "cumulative_vehicles_min": f"{integral:.9f}"
            })
        unique_status = "|".join(sorted({r["label_status"] for r in group}))
        summary.append({
            "segment": segment, "recording_id": recording,
            "start": times[0].isoformat(), "end": times[-1].isoformat(),
            "observations": len(group),
            "gap_limit_min": f"{gap_limit:.9f}",
            "gap_count": num_breaks,
            "covered_minutes": f"{covered_minutes:.9f}",
            "integral_vehicles_min": f"{integral:.9f}",
            "time_weighted_mean_vehicles": f"{integral/covered_minutes:.9f}" if covered_minutes else "",
            "label_status": unique_status,
            "result_status": "PRELIMINARY_NOT_GROUND_TRUTH" if unique_status != "human_verified" else "SOURCE_STATUS_HUMAN_VERIFIED"
        })
    def write(path, data):
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)
    prefix = Path(output_prefix)
    write(str(prefix) + "_tich_luy.csv", detailed)
    write(str(prefix) + "_tong_hop.csv", summary)
    print("Đã xuất", len(detailed), "quan sát,", len(summary), "đoạn.")
    for r in summary:
        print(r["segment"], "I =", r["integral_vehicles_min"], "xe·phút",
              "mean =", r["time_weighted_mean_vehicles"], "xe",
              "gap =", r["gap_count"])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="Đường dẫn analysis_snapshot.csv")
    ap.add_argument("--output-prefix", default="nhom11_chay_thu")
    args = ap.parse_args()
    run(args.source, args.output_prefix)
