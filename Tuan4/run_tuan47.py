#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G11 / De tai 11 / Tuan 47: replay/audit pipeline from the group's real files.

Run from anywhere: python3 Tuan4/run_tuan47.py [--snapshot /path/analysis_snapshot.csv]
No synthetic camera data. Without --snapshot, only original t,y pairs archived by Tuan3
are used; those 99-row series lack original image_id and are clearly marked derived.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import math
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "Tuan4" / "results"
TOLERANCE = 1e-6

# Dọn các biểu đồ Tuần 4 phiên bản cũ bị lặp với hình Tuần 3 (gồm cả bản tách I_k).
OBSOLETE_TUAN4_CHARTS = (
    "do_thi_dien_tich_A.png",
    "do_thi_dien_tich_B.png",
    "do_thi_do_nhay_AB.png",
    "do_thi_tich_luy_A.png",
    "do_thi_tich_luy_B.png",
)
TUAN3_REFERENCE_CHARTS = (
    ("Diện tích đoạn A (Tuần 3)", "do_thi_dien_tich_session_A.png"),
    ("Diện tích đoạn B (Tuần 3)", "do_thi_dien_tich_session_B.png"),
    ("Khảo sát độ nhạy A/B (Tuần 3)", "do_thi_khao_sat_do_nhay_AB.png"),
)


def remove_obsolete_charts(output: Path) -> list[str]:
    """Dọn đúng năm file PNG trùng do các phiên bản Tuan4 cũ đã tạo.

    Chỉ tác động trong thư mục output của Tuan4; không đụng tới Tuan3.
    """
    removed = []
    for name in OBSOLETE_TUAN4_CHARTS:
        old = output / name
        if old.is_file():
            old.unlink()
            removed.append(name)
    return removed


def chart_references(output: Path) -> list[str]:
    """Markdown links tới hình Tuan3, tính đường dẫn tương đối cho mọi --out."""
    lines = []
    for title, filename in TUAN3_REFERENCE_CHARTS:
        relative = os.path.relpath(ROOT / "Tuan3" / filename, output)
        lines.append(f"- [{title}]({Path(relative).as_posix()}) — đồ thị có sẵn; không tạo bản sao trong Tuần 4.")
    return lines


def read_csv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def save_csv(path: Path, rows: list[dict[str, Any]], columns: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"Không có bản ghi để xuất: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = columns or list(rows[0])
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def verify_series(t: np.ndarray, y: np.ndarray, session: str) -> None:
    if t.ndim != 1 or y.ndim != 1 or len(t) != len(y) or len(t) < 2:
        raise ValueError(f"{session}: cần ít nhất 2 mốc, t và y cùng độ dài.")
    if not np.all(np.isfinite(t)) or not np.all(np.isfinite(y)):
        raise ValueError(f"{session}: t, y chứa NaN/Inf.")
    if np.any(np.diff(t) <= 0):
        raise ValueError(f"{session}: timestamp không tăng nghiêm ngặt hoặc trùng.")
    if np.any(y < 0):
        raise ValueError(f"{session}: total_count âm.")


def trap(t: np.ndarray, y: np.ndarray) -> float:
    """Tự cài hình thang trên lưới không đều; không dùng np.trapezoid để tính."""
    verify_series(t, y, "verify")
    acc = np.float64(0)
    for i in range(1, len(t)):
        acc += (t[i] - t[i - 1]) * (y[i] + y[i - 1]) / np.float64(2)
    return float(acc)


def verify_analytical() -> list[dict[str, Any]]:
    exact = 4 / 3
    out = []
    prev_error = None
    for n in (10, 20, 40):
        t = np.linspace(0, 1, n + 1, dtype=np.float64)
        estimate = trap(t, 1 + t * t)
        err = abs(estimate - exact)
        order = math.log2(prev_error / err) if prev_error and err else ""
        out.append({"grid": f"uniform_{n}", "intervals": n, "estimate": estimate,
                    "exact": exact, "abs_error": err,
                    "relative_error_pct": err / exact * 100, "order_p": order})
        prev_error = err
    t = (np.arange(21, dtype=np.float64) / 20) ** 2
    estimate = trap(t, 1 + t*t)
    out.append({"grid": "nonuniform_t=j^2/20^2", "intervals": 20,
                "estimate": estimate, "exact": exact,
                "abs_error": abs(estimate - exact),
                "relative_error_pct": abs(estimate-exact)/exact*100, "order_p": ""})
    return out


@dataclass
class SessionData:
    name: str
    recording_id: str
    camera_id: str
    label_status: str
    provenance: str
    t: np.ndarray
    y: np.ndarray
    timestamps: list[str]
    image_ids: list[str]


def load_selection() -> dict[str, dict[str, str]]:
    selection = read_csv(ROOT / "Tuan1" / "selection_summary.csv")
    if set(r["segment"] for r in selection) != {"A", "B"}:
        raise ValueError("Tuan1/selection_summary.csv cần đúng A và B.")
    return {r["segment"]: r for r in selection}


def from_archived(selection: dict[str, dict[str, str]]) -> dict[str, SessionData]:
    sessions = {}
    for name in ("A", "B"):
        path = ROOT / "Tuan3" / f"chi_so_tich_luy_session_{name}.csv"
        rows = read_csv(path)
        t = np.asarray([float(r["t_phut"]) for r in rows], dtype=np.float64)
        y = np.asarray([float(r["y_total_count"]) for r in rows], dtype=np.float64)
        verify_series(t, y, name)
        start = datetime.fromisoformat(selection[name]["start"])
        timestamps = [(start + timedelta(seconds=float(x) * 60)).isoformat() for x in t]
        sessions[name] = SessionData(name, selection[name]["recording_id"],
            selection[name]["camera_id"], selection[name]["label_status"],
            "Tuan3 archived original t,y (derived CSV; image_id not stored)",
            t, y, timestamps, [""] * len(t))
    return sessions


def is_yes(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def from_snapshot(snapshot: Path, selection: dict[str, dict[str, str]]) -> dict[str, SessionData]:
    """Use the group's exact two recordings and Tuan1's saved 30-second window boundaries."""
    rows = read_csv(snapshot)
    if not rows:
        raise ValueError(f"Snapshot rỗng: {snapshot}")
    needed = {"image_id", "camera_id", "recording_id", "timestamp", "total_count", "label_status"}
    missing = needed - rows[0].keys()
    if missing:
        raise ValueError(f"Snapshot thiếu các cột: {sorted(missing)}")
    sessions = {}
    for name in ("A", "B"):
        boundary = read_csv(ROOT / "Tuan1" / "result" / f"segment_{name}_30s.csv")
        if not boundary:
            raise ValueError(f"Thiếu biên A/B của Tuần 1: {name}")
        begin = datetime.fromisoformat(boundary[0]["timestamp"])
        end = datetime.fromisoformat(boundary[-1]["timestamp"])
        target_camera = selection[name]["camera_id"]
        target_recording = selection[name]["recording_id"]
        picks = []
        for row in rows:
            if row["camera_id"] != target_camera or row["recording_id"] != target_recording:
                continue
            dt = datetime.fromisoformat(row["timestamp"])
            if not (begin <= dt <= end):
                continue
            if "is_resampled" in row and is_yes(row.get("is_resampled", "")):
                continue
            picks.append((dt, row))
        picks.sort(key=lambda x: x[0])
        if len(picks) < 80 or len(picks) > 300:
            raise ValueError(f"{name}: tìm được {len(picks)} quan sát, cần 80–300. Kiểm tra snapshot và biên Tuần 1.")
        ids = [row["image_id"] for _, row in picks]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{name}: image_id trùng trong bản snapshot.")
        status = {row["label_status"] for _, row in picks}
        if len(status) != 1 or not all(status):
            raise ValueError(f"{name}: label_status không đồng nhất hoặc bị thiếu.")
        t = np.asarray([(dt-begin).total_seconds()/60 for dt, _ in picks], dtype=np.float64)
        y = np.asarray([float(row["total_count"]) for _, row in picks], dtype=np.float64)
        verify_series(t, y, name)
        sessions[name] = SessionData(name, target_recording, target_camera,
            next(iter(status)), f"snapshot raw: {snapshot.name}", t, y,
            [dt.isoformat() for dt, _ in picks], ids)
    if sessions["A"].label_status != sessions["B"].label_status:
        raise ValueError("Hai session A/B không cùng label_status; không được gộp.")
    return sessions



def audit_snapshot(snapshot: Path, selection: dict[str, dict[str, str]],
                   sessions: dict[str, SessionData]) -> tuple[str, list[dict[str, Any]]]:
    """Đối soát file nguồn với đúng các cửa sổ A/B đã lưu tại Tuần 1.

    Không đưa ảnh, nhãn cá nhân hay toàn bộ snapshot vào đầu ra. Hash dùng để xác
    định phiên bản snapshot trong báo cáo; CSV kiểm toán chỉ lưu thống kê A/B.
    """
    digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    data = read_csv(snapshot)
    counts = ("count_2wheel", "count_bus", "count_car", "count_truck")
    have_components = bool(data) and all(c in data[0] for c in counts)
    audit = []
    for name in ("A", "B"):
        target = selection[name]
        source_rows = [r for r in data if r["camera_id"] == target["camera_id"]
                       and r["recording_id"] == target["recording_id"]]
        boundary = read_csv(ROOT / "Tuan1" / "result" / f"segment_{name}_30s.csv")
        begin = datetime.fromisoformat(boundary[0]["timestamp"])
        end = datetime.fromisoformat(boundary[-1]["timestamp"])
        inside = [r for r in source_rows if begin <= datetime.fromisoformat(r["timestamp"]) <= end]
        selected = [r for r in inside if not is_yes(r.get("is_resampled", ""))]
        selected.sort(key=lambda r: datetime.fromisoformat(r["timestamp"]))
        if [r["image_id"] for r in selected] != sessions[name].image_ids:
            raise ValueError(f"{name}: truy vết image_id không khớp pipeline.")
        duplicate_ids = len(source_rows)-len({r["image_id"] for r in source_rows})
        if duplicate_ids:
            raise ValueError(f"{name}: snapshot chứa {duplicate_ids} image_id trùng.")
        inconsistent_total = ""
        if have_components:
            inconsistent_total = sum(
                not math.isclose(float(r["total_count"]),sum(float(r[c]) for c in counts),abs_tol=1e-9)
                for r in source_rows)
            if inconsistent_total:
                raise ValueError(f"{name}: {inconsistent_total} dòng có total_count không khớp tổng bốn lớp xe.")
        outside_end = sorted((r["timestamp"] for r in source_rows
            if datetime.fromisoformat(r["timestamp"]) > end))
        outside_begin = sorted((r["timestamp"] for r in source_rows
            if datetime.fromisoformat(r["timestamp"]) < begin))
        archived = read_csv(ROOT / "Tuan3" / f"chi_so_tich_luy_session_{name}.csv")
        archived_t = np.asarray([float(r["t_phut"]) for r in archived], dtype=np.float64)
        archived_y = np.asarray([float(r["y_total_count"]) for r in archived], dtype=np.float64)
        matches_archive = (len(archived_t) == len(sessions[name].t)
            and np.allclose(archived_t,sessions[name].t,rtol=0,atol=1e-9)
            and np.array_equal(archived_y,sessions[name].y))
        if not matches_archive and sessions[name].label_status == "unreviewed_prelabel":
            raise ValueError(f"{name}: snapshot PRELABEL không trùng chuỗi quan sát lưu ở Tuần 3.")
        # Snapshot human_verified có thể đổi giá trị y; không ép khớp với PRELABEL cũ.
        status = sorted({r.get("label_status", "") for r in source_rows})
        versions = sorted({r.get("label_version", "") for r in source_rows})
        audit.append({
            "session":name,"camera_id":target["camera_id"],"recording_id":target["recording_id"],
            "raw_records":len(source_rows),"within_window":len(inside),
            "selected_nonresampled":len(selected),
            "excluded_before_window":len(outside_begin),
            "excluded_after_window":len(outside_end),
            "excluded_resampled_inside_window":len(inside)-len(selected),
            "resampled_window_end":end.isoformat(),
            "excluded_after_window_timestamps":"; ".join(outside_end),
            "label_status":";".join(status),"label_version":";".join(versions),
            "total_count_mismatch_rows":inconsistent_total,
            "matched_archived_t_y":matches_archive,
            "image_ids_present":sum(bool(r["image_id"]) for r in selected),
            "snapshot_sha256":digest,
        })
    return digest,audit


def evaluate(t: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    """Gap cutoff recomputed on *each* scenario after sampling, as the Tuan3 code did."""
    verify_series(t, y, "evaluate")
    steps = np.diff(t)
    limit = float(3 * np.median(steps))
    gap_mask = steps > limit
    accumulated = np.float64(0)
    covered = np.float64(0)
    acc_part = np.float64(0)
    part = 1
    per_point = []
    for k in range(len(t)):
        if k == 0:
            h, area, gap = 0.0, 0.0, False
        else:
            h = float(steps[k-1])
            gap = bool(gap_mask[k-1])
            if gap:
                area = 0.0
                part += 1
                acc_part = np.float64(0)
            else:
                area = float((y[k-1] + y[k]) * h / np.float64(2))
                covered += h
                accumulated += area
                acc_part += area
        per_point.append({"part": part, "t_min": float(t[k]), "y_count": float(y[k]),
                "h_from_previous_min": h, "gap_before": gap, "interval_area_veh_min": area,
                "I_k_since_part_start_veh_min": float(acc_part),
                "I_cumulative_session_veh_min": float(accumulated)})
    parts = []
    start = 0
    breaks = list(np.where(gap_mask)[0] + 1) + [len(t)]
    for part_no, stop in enumerate(breaks, start=1):
        subset = per_point[start:stop]
        if len(subset) >= 2:
            integral = subset[-1]["I_k_since_part_start_veh_min"]
            duration = subset[-1]["t_min"]-subset[0]["t_min"]
        else:
            integral = duration = 0.0
        parts.append({"part": part_no, "observations": len(subset), "first_t_min": subset[0]["t_min"],
            "last_t_min": subset[-1]["t_min"], "integral_veh_min": integral,
            "covered_min": duration,
            "mean_count": integral/duration if duration>0 else ""})
        start = stop
    return {"I": float(accumulated), "covered": float(covered),
            "mean": float(accumulated/covered) if covered>0 else None,
            "threshold": limit, "gap_count": int(np.sum(gap_mask)),
            "parts": parts, "points": per_point}


def scenarios(n: int) -> list[tuple[str, np.ndarray, str]]:
    if n < 2:
        raise ValueError("Ít hơn hai điểm")
    all_indices = np.arange(n, dtype=np.int64)
    plan = [("full", all_indices, "Dữ liệu gốc trong cửa sổ, không nội suy")]
    for step in (2, 4):
        idx = np.arange(0, n, step, dtype=np.int64)
        idx = np.unique(np.r_[idx, n-1])
        plan.append((f"every_{step}", idx, f"Giữ mỗi {step} mốc và hai đầu"))
    rng = np.random.default_rng(2026)
    inner = np.arange(1, n-1, dtype=np.int64)
    for p in (10, 20):
        keep_count = int(np.round(len(inner) * (1-p/100)))
        chosen = np.sort(rng.choice(inner, size=keep_count, replace=False))
        idx = np.r_[0, chosen, n-1]
        plan.append((f"drop_{p}pct", idx, f"Mất {p}% mốc nội bộ; seed=2026"))
    return plan


def replay_archive(summary: list[dict[str, Any]], archive: Path) -> list[dict[str, Any]]:
    expected = read_csv(archive)
    aliases = {"full": "1. Gốc", "every_2": "2. Giữ mỗi 2", "every_4": "2. Giữ mỗi 4",
               "drop_10pct": "3. Mất 10%", "drop_20pct": "3. Mất 20%"}
    out = []
    for s in summary:
        matches = [r for r in expected if r["Session"] == s["session"]
            and r["Kich_ban"].startswith(aliases[s["scenario"]])]
        if len(matches) != 1:
            raise ValueError(f"Tuan3: không tìm đúng kịch bản {s['session']} {s['scenario']}")
        prev = matches[0]
        diffs = {
            "integral": abs(float(prev["Chi_so_I (xe.phut)"])-float(s["I_veh_min"])),
            "covered": abs(float(prev["Thoi_gian_phu (phut)"])-float(s["covered_min"])),
            "mean": abs(float(prev["Trung_binh_y_bar (xe)"])-float(s["mean_count"])),
        }
        out.append({"session": s["session"], "scenario": s["scenario"],
                    "max_abs_diff": max(diffs.values()),
                    "reproduced": max(diffs.values()) < TOLERANCE,
                    "note": "Đối chiếu Tuan3 PRELABEL; không phải gold truth"})
    return out


def run(snapshot: Path | None = None, out: Path = DEFAULT_OUT) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    select = load_selection()
    sessions = from_snapshot(snapshot, select) if snapshot else from_archived(select)
    if len({s.label_status for s in sessions.values()}) != 1:
        raise ValueError("Hai session A/B không có cùng trạng thái nhãn.")
    snapshot_audit = None
    digest = None
    if snapshot is not None:
        digest, snapshot_audit = audit_snapshot(snapshot, select, sessions)
        save_csv(out/"kiem_toan_snapshot.csv", snapshot_audit)
        print(f"[SOURCE] SHA256={digest}; " + "; ".join(
            f"{r['session']}: {r['raw_records']} ảnh nguồn → {r['selected_nonresampled']} mốc, "
            f"loại {r['excluded_after_window']} mốc sau cửa sổ"
            for r in snapshot_audit))
    verify = verify_analytical()
    save_csv(out/"kiem_chung_hinh_thang.csv", verify)
    print("[CHECK] f(t)=1+t², I thật=4/3; p hội tụ:", [round(float(r["order_p"]),6) for r in verify if r["order_p"]!=""])
    row_summaries, row_points, row_parts = [], [], []
    evals = {}
    for name, sess in sessions.items():
        original = evaluate(sess.t, sess.y)
        evals[name] = original
        for scenario, idx, note in scenarios(len(sess.t)):
            evaluation = evaluate(sess.t[idx], sess.y[idx])
            ratio = evaluation["I"]/original["I"]*100 if original["I"]>0 else None
            covered_ratio = evaluation["covered"]/original["covered"]*100 if original["covered"]>0 else None
            stat = {"session": name, "camera_id": sess.camera_id,
                    "recording_id": sess.recording_id, "scenario": scenario,
                    "observations": len(idx), "span_min": float(sess.t[-1] - sess.t[0]),
                    "gap_threshold_min": evaluation["threshold"],
                    "gap_count": evaluation["gap_count"], "parts_count": len(evaluation["parts"]),
                    "covered_min": evaluation["covered"], "I_veh_min": evaluation["I"],
                    "mean_count": evaluation["mean"], "I_pct_of_full": ratio,
                    "covered_pct_of_full": covered_ratio,
                    "I_change_pct": ratio - 100 if ratio is not None else "",
                    "label_status": sess.label_status,
                    "result_status": "HUMAN_VERIFIED_SOURCE_UNAUDITED" if sess.label_status=="human_verified"
                      else "PRELIMINARY_NOT_GROUND_TRUTH",
                    "provenance": sess.provenance, "method_note": note}
            row_summaries.append(stat)
            for point_i, point in zip(idx, evaluation["points"]):
                row_points.append({"session":name,"scenario":scenario, "image_id":sess.image_ids[point_i],
                    "timestamp":sess.timestamps[point_i], **point})
            for part in evaluation["parts"]:
                row_parts.append({"session":name,"scenario":scenario,"gap_threshold_min":evaluation["threshold"], **part})
        print(f"[DATA] {name}: {len(sess.t)} mốc; I={original['I']:.6f} xe·phút; "
            f"T phủ={original['covered']:.6f} phút; ȳ={original['mean']:.6f} xe; status={sess.label_status}")
    save_csv(out/"bang_tong_hop_AB.csv", row_summaries)
    save_csv(out/"bang_theo_doan.csv", row_parts)
    save_csv(out/"chi_so_tich_luy_AB.csv", row_points)
    replayed = None
    archive = ROOT/"Tuan3"/"bang_tich_phan_tuan3_AB.csv"
    # Compare only when using archived PRELABEL source or the matching prelabel raw snapshot.
    if archive.exists() and all(s.label_status=="unreviewed_prelabel" for s in sessions.values()):
        replayed = replay_archive(row_summaries, archive)
        save_csv(out/"doi_chieu_Tuan3.csv", replayed)
        print("[AUDIT] Tuan3:",sum(x["reproduced"] for x in replayed),"/",len(replayed),"kịch bản tái tạo (I, thời gian phủ, trung bình).")
        if not all(x["reproduced"] for x in replayed):
            raise RuntimeError("Bảng A/B mới không khớp Tuan3, xem Tuan4/results/doi_chieu_Tuan3.csv")
    obsolete = remove_obsolete_charts(out)
    if obsolete:
        print("[CLEAN] Đã bỏ hình lặp của Tuần 4:", ", ".join(obsolete))
    provenance = "Tuan3/chi_so_tich_luy_session_{A,B}.csv" if snapshot is None else snapshot.name
    summary = [
        "# G11 | Báo cáo kiểm tra pipeline - Tuần 47",
        "", "Đề tài 11: Chỉ số tải tích lũy bằng công thức hình thang trên bước thời gian không đều.",
        "", f"**Nguồn dữ liệu:** `{provenance}`.",
        "", f"**Nguồn nhãn:** {sessions['A'].label_status} (A và B đồng nhất).",
        "", "**Phân biệt dữ liệu:** I có đơn vị xe·phút, ȳ có đơn vị xe; "
        "không được gọi I là tổng số xe đi qua.",
        "", "## Kết quả chạy lại", "",
        "| Đoạn | Recording | Mốc gốc | I (xe·phút) | T phủ (phút) | ȳ (xe) |",
        "|:--|:--|--:|--:|--:|--:|",
    ]
    for name, sess in sessions.items():
        v = evals[name]
        summary.append(f"| {name} | `{sess.recording_id}` | {len(sess.t)} | {v['I']:.6f} | {v['covered']:.6f} | {v['mean']:.6f} |")
    if snapshot_audit is not None:
        summary.extend(["", "## Kiểm toán snapshot gốc đã cung cấp", "",
            f"SHA256 của file nguồn: `{digest}`. File nguồn không được tự động đóng gói/đưa lên GitHub.",
            "", "| Đoạn | Số ảnh nguồn | Đã chọn | Ngoài cửa sổ (sau cuối) | "
            "Khớp chuỗi Tuần 3 | Sai tổng bốn lớp |",
            "|:--|--:|--:|--:|:--:|--:|"])
        for r in snapshot_audit:
            summary.append(f"| {r['session']} | {r['raw_records']} | {r['selected_nonresampled']} | "
                f"{r['excluded_after_window']} | {r['matched_archived_t_y']} | {r['total_count_mismatch_rows']} |")
        summary.extend(["", "Mỗi recording có 100 ảnh trong snapshot. Khi giới hạn đến mốc cuối "
            "của lưới 30 giây ở Tuần 1, một ảnh cuối của A và một ảnh cuối của B nằm sau "
            "cửa sổ nên không đưa vào tích phân. Đây không phải mất dữ liệu nguồn.",
            "", "Chuỗi `chi_so_tich_luy_AB.csv` của lần chạy này ghi `image_id` gốc "
            "cho từng mốc đã sử dụng; bảng `kiem_toan_snapshot.csv` lưu thông tin đối chiếu."])
    summary += ["", "## Kiểm chứng công thức", "",
        "f(t) = 1 + t², t ∈ [0,1]; tích phân thật I=4/3. Bậc hội tụ thực nghiệm p≈2 khi h giảm một nửa.",
        "", "## Kiểm tra chéo với Tuần 3", "",
        (f"Tái tạo **{sum(x['reproduced'] for x in replayed)}/{len(replayed)}** kịch bản "
        "từ CSV đã lưu của nhóm (dung sai 1e-6)." if replayed is not None
         else "Bỏ qua kiểm tra số học với bản prelabel Tuần 3 vì dữ liệu có trạng thái khác."),
        "", "**Điểm chỉnh so với báo cáo cũ:** Ngưỡng gap (3×median(h)) thay đổi theo từng "
        "kịch bản lấy mẫu; cột `gap_threshold_min` báo đúng ngưỡng đã áp dụng. "
        "Đặc biệt mỗi 2 mốc và mỗi 4 mốc có ngưỡng lớn hơn bản gốc.",
        "", "## Giới hạn / các việc còn lại", "",
        ("- Không tự đưa snapshot gốc vào GitHub; lần chạy này đã dùng snapshot và "
         "truy vết `image_id` gốc trong `chi_so_tich_luy_AB.csv`."
         if snapshot is not None else
         "- Không dùng snapshot gốc ở lần chạy này, nên các `image_id` không có "
         "trong CSV Tuần 3; muốn truy vết nguồn hãy chạy `--snapshot`."),
        ("- Cần snapshot `human_verified` chính thức để cập nhật các kết quả trên nhãn đã nghiệm thu."
         if snapshot is not None else
         "- Có thể chạy `--snapshot` trỏ tới file nguồn của giảng viên để đối soát ảnh; "
         "phần nhãn nghiệm thu cần xác nhận riêng."),
        "- Đối chiếu số học không đồng nghĩa với nghiệm thu nhãn; kết quả chỉ dựa "
        "trên `unreviewed_prelabel` khi dữ liệu nguồn còn ở trạng thái này.",
        "- Các kịch bản mất mốc và giữ thưa đo độ nhạy, chênh lệch so với lưới đầy đủ "
        "không phải sai số so với tích phân thật.",
        "- Session Tuần 1 ghi 100 ảnh mỗi đoạn, nhưng bản ranh giới 30 giây "
        "giới hạn cửa sổ thí nghiệm chỉ còn 99 mốc nguồn ở Tuần 3; cần nêu rõ để tránh "
        "nhầm thành thiếu một ảnh trong batch.",
        "", "## Tệp xuất", "",
        "- `kiem_chung_hinh_thang.csv`: lưới 10/20/40 và lưới không đều", 
        "- `bang_tong_hop_AB.csv`: 10 kịch bản A/B, gap thực tế và chênh lệch so với gốc", 
        "- `bang_theo_doan.csv`: thời gian phủ, tích phân từng đoạn", 
        "- `chi_so_tich_luy_AB.csv`: chuỗi tích lũy theo từng điểm và mỗi kịch bản", 
        "- `doi_chieu_Tuan3.csv`: đối chiếu 10 kịch bản đã lưu của nhóm",
        *( ["- `kiem_toan_snapshot.csv`: số ảnh nguồn, số mốc chọn, mốc nằm ngoài cửa sổ, "
            "kiểm tra tổng xe và hash file nguồn"] if snapshot is not None else []), 
        "- Không xuất PNG ở Tuần 4: các hình số xe/diện tích/I_k/độ nhạy đều đã có trong Tuần 3.",
        "", "## Đồ thị đã có ở Tuần 3 — tham chiếu, không xuất lại", "",
        *chart_references(out),
        "", "Tuần 4 không tạo lại biểu đồ. Phần bổ sung là code tái lập, kiểm thử, "
        "đối chiếu số học và CSV kiểm toán khoảng thiếu.",
    ]
    (out/"BAO_CAO_CHAY_LAI_TUAN47.md").write_text("\n".join(summary)+"\n",encoding="utf-8")
    return {"out":out,"scenarios":len(row_summaries),"reproduced":replayed,"sessions":sessions}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--snapshot",type=Path,help="analysis_snapshot.csv từ thầy (không có trong repo ZIP)")
    ap.add_argument("--out",type=Path,default=DEFAULT_OUT)
    ap.add_argument("--no-charts", action="store_true", help=argparse.SUPPRESS)  # Tương thích lệnh V2
    args = ap.parse_args()
    run(args.snapshot,args.out)
    print("[DONE] Kết quả tại:",args.out.resolve())


if __name__=="__main__":
    main()
