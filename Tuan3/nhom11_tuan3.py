import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

import numpy as np
import pandas as pd
import os

# ==============================================================================
# PHẦN 1: CÁC HÀM LÕI (BƯỚC 1 & BƯỚC 2 - BẮT BUỘC FLOAT64, KHÔNG DÙNG HÀM THƯ VIỆN)
# ==============================================================================
def tach_doan_lien_tuc(t, y, he_so_gap=3.0):
    """Bước 1: Chia thành các đoạn liên tục dựa trên ngưỡng khoảng thiếu (gap)"""
    t = np.asarray(t, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    idx = np.argsort(t)
    t, y = t[idx], y[idx]
    
    if len(t) < 2:
        return [], np.float64(0.0)
        
    h = np.diff(t)
    nguong_gap = he_so_gap * np.median(h)
    
    vi_tri_ngat = np.where(h > nguong_gap)[0] + 1
    cac_doan_t = np.split(t, vi_tri_ngat)
    cac_doan_y = np.split(y, vi_tri_ngat)
    
    cac_doan_hop_le = [(dt, dy) for dt, dy in zip(cac_doan_t, cac_doan_y) if len(dt) >= 2]
    return cac_doan_hop_le, nguong_gap

def tinh_hinh_thang_tich_luy(t, y):
    """Bước 2: Tự tính I = sum(h_i * (y_i + y_{i+1}) / 2) và chuỗi tích lũy I_k"""
    t = np.asarray(t, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    n = len(t)
    I_k = np.zeros(n, dtype=np.float64)
    tong_I = np.float64(0.0)
    
    for i in range(n - 1):
        h_i = t[i+1] - t[i]
        dien_tich = np.float64(0.5) * (y[i] + y[i+1]) * h_i
        tong_I += dien_tich
        I_k[i+1] = tong_I
        
    thoi_gian_phu = t[-1] - t[0]
    return tong_I, I_k, thoi_gian_phu

def danh_gia_session(t, y, he_so_gap=3.0):
    """Bước 2 & Bước 4: Tính tổng I, tổng thời gian phủ và trung bình y_bar_t"""
    cac_doan, nguong_gap = tach_doan_lien_tuc(t, y, he_so_gap)
    tong_I_session = np.float64(0.0)
    tong_thoi_gian_phu = np.float64(0.0)
    du_lieu_tich_luy = []
    
    for id_doan, (dt, dy) in enumerate(cac_doan, start=1):
        I_doan, I_k, dt_phu = tinh_hinh_thang_tich_luy(dt, dy)
        tong_I_session += I_doan
        tong_thoi_gian_phu += dt_phu
        
        for k in range(len(dt)):
            du_lieu_tich_luy.append({
                'doan_lien_tuc': id_doan,
                't_phut': dt[k],
                'y_total_count': dy[k],
                'I_k_tich_luy': I_k[k]
            })
            
    y_bar_t = tong_I_session / tong_thoi_gian_phu if tong_thoi_gian_phu > 0 else np.float64(0.0)
    return tong_I_session, tong_thoi_gian_phu, y_bar_t, nguong_gap, pd.DataFrame(du_lieu_tich_luy)

# ==============================================================================
# PHẦN 2: ĐỌC TRỰC TIẾP TỪ analysis_snapshot.csv VÀ CHẠY BƯỚC 4 & BƯỚC 5
# ==============================================================================
file_snapshot = 'shared/analysis_snapshot.csv' if os.path.exists('shared/analysis_snapshot.csv') else 'analysis_snapshot.csv'
df_snapshot = pd.read_csv(file_snapshot)

# Chuyển cột timestamp sang định dạng datetime để so sánh và tính thời gian chính xác
df_snapshot['dt_parsed'] = pd.to_datetime(df_snapshot['timestamp'])

files_mau = {'A': 'segment_A_30s.csv', 'B': 'segment_B_30s.csv'}
ket_qua_tong_hop = []

for ten_session, file_seg in files_mau.items():
    df_seg = pd.read_csv(file_seg)
    df_seg['dt_parsed'] = pd.to_datetime(df_seg['timestamp'])
    
    # Lấy đúng recording_id và khung thời gian đầu/cuối của đoạn A/B
    rec_id = df_seg['recording_id'].iloc[0]
    t_start = df_seg['dt_parsed'].min()
    t_end = df_seg['dt_parsed'].max()
    
    # Lọc dữ liệu gốc trực tiếp trên analysis_snapshot.csv
    df_sub = df_snapshot[
        (df_snapshot['recording_id'] == rec_id) &
        (df_snapshot['dt_parsed'] >= t_start) &
        (df_snapshot['dt_parsed'] <= t_end)
    ].sort_values(by='dt_parsed').drop_duplicates(subset=['dt_parsed'])
    
    # Tính thời gian t bằng phút (float64) tính từ mốc bắt đầu đoạn
    t_full = ((df_sub['dt_parsed'] - t_start).dt.total_seconds() / 60.0).to_numpy(dtype=np.float64)
    y_full = df_sub['total_count'].to_numpy(dtype=np.float64)
    
    # --- BƯỚC 4: Tính trên lưới đầy đủ (Full) ---
    I_full, T_full, ybar_full, nguong_gap, df_tich_luy = danh_gia_session(t_full, y_full)
    df_tich_luy.to_csv(f"chi_so_tich_luy_session_{ten_session}.csv", index=False)
    
    ket_qua_tong_hop.append({
        'Session': ten_session,
        'Recording_ID': rec_id,
        'Kich_ban': '1. Gốc (Full - analysis_snapshot)',
        'So_moc': len(t_full),
        'Nguong_gap_phut': nguong_gap,
        'Chi_so_I (xe.phut)': I_full,
        'Thoi_gian_phu (phut)': T_full,
        'Trung_binh_y_bar (xe)': ybar_full
    })
    
    # --- BƯỚC 5: Khảo sát độ nhạy lấy mẫu ---
    # 5a. Giữ mỗi 2 mốc và 4 mốc, cùng hai đầu
    for step in [2, 4]:
        idx_sub = list(range(0, len(t_full), step))
        if idx_sub[-1] != len(t_full) - 1:
            idx_sub.append(len(t_full) - 1)
            
        I_sub, T_sub, ybar_sub, _, _ = danh_gia_session(t_full[idx_sub], y_full[idx_sub])
        ket_qua_tong_hop.append({
            'Session': ten_session,
            'Recording_ID': rec_id,
            'Kich_ban': f'2. Giữ mỗi {step} mốc (+2 đầu)',
            'So_moc': len(idx_sub),
            'Nguong_gap_phut': nguong_gap,
            'Chi_so_I (xe.phut)': I_sub,
            'Thoi_gian_phu (phut)': T_sub,
            'Trung_binh_y_bar (xe)': ybar_sub
        })
        
    # 5b. Tạo hai bản mất 10%, 20% mốc nội bộ với seed 2026, giữ hai đầu
    rng = np.random.default_rng(2026)
    cac_moc_noi_bo = np.arange(1, len(t_full) - 1)
    
    for ty_le_mat in [0.10, 0.20]:
        so_moc_giu = int(np.round(len(cac_moc_noi_bo) * (1 - ty_le_mat)))
        moc_noi_bo_giu = np.sort(rng.choice(cac_moc_noi_bo, size=so_moc_giu, replace=False))
        idx_drop = np.concatenate(([0], moc_noi_bo_giu, [len(t_full) - 1]))
        
        I_drop, T_drop, ybar_drop, _, _ = danh_gia_session(t_full[idx_drop], y_full[idx_drop])
        ket_qua_tong_hop.append({
            'Session': ten_session,
            'Recording_ID': rec_id,
            'Kich_ban': f'3. Mất {int(ty_le_mat*100)}% mốc nội bộ (seed=2026)',
            'So_moc': len(idx_drop),
            'Nguong_gap_phut': nguong_gap,
            'Chi_so_I (xe.phut)': I_drop,
            'Thoi_gian_phu (phut)': T_drop,
            'Trung_binh_y_bar (xe)': ybar_drop
        })

# Xuất Bảng tích phân tổng hợp (Sản phẩm bắt buộc Tuần 3)
df_ket_qua = pd.DataFrame(ket_qua_tong_hop)
df_ket_qua.to_csv("bang_tich_phan_tuan3_AB.csv", index=False)

print("=== BẢNG KẾT QUẢ TỔNG HỢP TUẦN 3 ===")
print(df_ket_qua.to_string(index=False))
