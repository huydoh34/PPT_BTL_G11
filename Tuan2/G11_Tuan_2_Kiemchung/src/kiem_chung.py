import csv
from pathlib import Path
import numpy as np


def hinh_thang(t, y):
    tong = np.float64(0.0)
    for i in range(len(t) - 1):
        tong += (t[i + 1] - t[i]) * (y[i] + y[i + 1]) / 2
    return tong


def main():
    output = Path(__file__).resolve().parents[1] / "results"
    output.mkdir(exist_ok=True)
    exact = np.float64(4 / 3)
    records = []
    previous_error = None

    for n in (10, 20, 40):
        t = np.linspace(0, 1, n + 1, dtype=np.float64)
        y = 1 + t**2
        result = hinh_thang(t, y)
        error = abs(result - exact)
        order = (
            np.log2(previous_error / error)
            if previous_error is not None and error > 0
            else ""
        )
        records.append({
            "grid": "uniform",
            "intervals": n,
            "integral": float(result),
            "exact": float(exact),
            "absolute_error": float(error),
            "convergence_order": float(order) if order != "" else "",
            "difference_from_numpy": float(
                abs(result - np.trapezoid(y, x=t))
            )
        })
        previous_error = error

    t = np.linspace(0, 1, 21, dtype=np.float64)**2
    y = 1 + t**2
    result = hinh_thang(t, y)
    records.append({
        "grid": "nonuniform_t=s^2",
        "intervals": 20,
        "integral": float(result),
        "exact": float(exact),
        "absolute_error": float(abs(result - exact)),
        "convergence_order": "",
        "difference_from_numpy": float(
            abs(result - np.trapezoid(y, x=t))
        )
    })

    path = output / "nhom11_kiem_chung.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    for row in records:
        print(
            row["grid"], row["intervals"],
            "sai số =", row["absolute_error"],
            "chênh NumPy =", row["difference_from_numpy"]
        )
    print("Đã lưu:", path)


if __name__ == "__main__":
    main()