import csv
from pathlib import Path
import numpy as np


def hinh_thang(t, y):
    """Tự tính tích phân hình thang ghép bằng float64, hỗ trợ lưới không đều."""
    t = np.asarray(t, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if t.ndim != 1 or y.ndim != 1 or len(t) != len(y) or len(t) < 2:
        raise ValueError("t và y phải là mảng 1 chiều cùng độ dài >= 2")
    if not np.all(np.diff(t) > 0):
        raise ValueError("Các mốc thời gian phải tăng nghiêm ngặt")
    tong = np.float64(0.0)
    for i in range(len(t) - 1):
        tong += (t[i + 1] - t[i]) * (y[i] + y[i + 1]) / np.float64(2.0)
    return tong


def tao_ban_ghi(grid, n, t, exact, previous_error=None):
    y = np.float64(1.0) + t**2
    result = hinh_thang(t, y)
    signed_error = np.float64(result - exact)
    ae = np.abs(signed_error)
    re_percent = np.float64(100.0) * ae / np.abs(exact) if exact != 0 else np.nan
    p = (np.log2(previous_error / ae)
         if previous_error is not None and previous_error > 0 and ae > 0 else "")
    return {
        "grid": grid,
        "intervals": n,
        "integral": float(result),
        "exact": float(exact),
        "signed_error": float(signed_error),
        "absolute_error_AE": float(ae),
        "relative_error_RE_percent": float(re_percent),
        "MAE_uniform_3_tests": "",
        "MSE_uniform_3_tests": "",
        "RMSE_uniform_3_tests": "",
        "convergence_order_p": float(p) if p != "" else "",
        "difference_from_numpy": float(np.abs(result - np.trapezoid(y, x=t))),
    }


def ghi_csv(path, rows, columns):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main():
    # Kết quả luôn nằm trong thư mục results cạnh file .py.
    output = Path(__file__).resolve().parent / "results"
    output.mkdir(parents=True, exist_ok=True)
    exact = np.float64(4.0) / np.float64(3.0)
    records = []
    previous_error = None

    for n in (10, 20, 40):
        t = np.linspace(0.0, 1.0, n + 1, dtype=np.float64)
        row = tao_ban_ghi("uniform", n, t, exact, previous_error)
        records.append(row)
        previous_error = np.float64(row["absolute_error_AE"])

    # Tổng hợp thống kê cho đúng 3 phép thử lưới đều (không gộp lưới không đều).
    errors = np.array([r["signed_error"] for r in records], dtype=np.float64)
    mae = np.mean(np.abs(errors), dtype=np.float64)
    mse = np.mean(errors**2, dtype=np.float64)
    rmse = np.sqrt(mse)
    for row in records:
        row["MAE_uniform_3_tests"] = float(mae)
        row["MSE_uniform_3_tests"] = float(mse)
        row["RMSE_uniform_3_tests"] = float(rmse)

    t = np.linspace(0.0, 1.0, 21, dtype=np.float64)**2
    records.append(tao_ban_ghi("nonuniform_t=s^2", 20, t, exact))

    path = output / "nhom11_kiem_chung.csv"
    ghi_csv(path, records, list(records[0].keys()))

    summary_path = output / "nhom11_tong_ket_sai_so.csv"
    summary = [{
        "scope": "uniform_N=10_20_40",
        "sample_count": len(errors),
        "MAE": float(mae),
        "MSE": float(mse),
        "RMSE": float(rmse),
        "max_AE": float(np.max(np.abs(errors))),
        "mean_RE_percent": float(np.mean([r["relative_error_RE_percent"] for r in records[:3]])),
    }]
    ghi_csv(summary_path, summary, list(summary[0].keys()))

    for row in records:
        print(f'{row["grid"]:18} N={row["intervals"]:2} '
              f'AE={row["absolute_error_AE"]:.10g} '
              f'RE={row["relative_error_RE_percent"]:.8g}% '
              f'p={row["convergence_order_p"]} '
              f'DeltaNumPy={row["difference_from_numpy"]:.3g}')
    print(f'MAE={mae:.12g}; MSE={mse:.12g}; RMSE={rmse:.12g}')
    print('Đã lưu:', path)
    print('Đã lưu:', summary_path)


if __name__ == "__main__":
    main()
