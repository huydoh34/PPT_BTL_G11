"""Validation for integrated week 47 pipeline. Run: python3 -m unittest discover -s Tuan4/tests -v"""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Tuan4'))
import run_tuan47 as t4


class TestTrapezoidTuan47(unittest.TestCase):
    def test_uniform_convergence(self):
        rows=t4.verify_analytical()
        self.assertEqual([x['intervals'] for x in rows[:3]],[10,20,40])
        self.assertAlmostEqual(rows[1]['order_p'],2,places=8)
        self.assertAlmostEqual(rows[2]['order_p'],2,places=8)

    def test_irregular_grid(self):
        t=np.array([0,.1,.42,1],dtype=np.float64)
        y=2*t+1
        self.assertAlmostEqual(t4.trap(t,y),2,places=12)

    def test_nonuniform_regression_tuan2(self):
        self.assertAlmostEqual(t4.verify_analytical()[-1]['estimate'],1.334165625,places=11)

    def test_gap_not_integrated(self):
        t=np.array([0,1,2,3,20,21,22,23],dtype=np.float64)
        y=np.full(len(t),5,dtype=np.float64)
        v=t4.evaluate(t,y)
        self.assertEqual(v['gap_count'],1)
        self.assertAlmostEqual(v['covered'],6,places=10)
        self.assertAlmostEqual(v['I'],30,places=10)
        self.assertEqual(len(v['parts']),2)
        self.assertAlmostEqual(v['points'][4]['interval_area_veh_min'],0)
        self.assertAlmostEqual(v['points'][4]['I_k_since_part_start_veh_min'],0)

    def test_bad_data_rejected(self):
        with self.assertRaises(ValueError):
            t4.evaluate(np.array([0,0,1.]),np.array([1,2,3.]))
        with self.assertRaises(ValueError):
            t4.evaluate(np.array([0,1]),np.array([1,-2]))
        with self.assertRaises(ValueError):
            t4.evaluate(np.array([0,1]),np.array([1,np.nan]))

    def test_same_endpoints_and_fixed_seed(self):
        a=t4.scenarios(99)
        b=t4.scenarios(99)
        self.assertEqual([n for n,_,_ in a], ['full','every_2','every_4','drop_10pct','drop_20pct'])
        for (na,ia,_),(nb,ib,_) in zip(a,b):
            self.assertEqual(na,nb)
            np.testing.assert_array_equal(ia,ib)
            self.assertEqual(ia[0],0)
            self.assertEqual(ia[-1],98)
        self.assertEqual([len(ia) for _,ia,_ in a],[99,50,26,89,80])

    def test_archive_crosscheck(self):
        selection=t4.load_selection()
        sessions=t4.from_archived(selection)
        summaries=[]
        for name,s in sessions.items():
            self.assertEqual(len(s.t),99)
            for scenario,idx,_ in t4.scenarios(len(s.t)):
                values=t4.evaluate(s.t[idx],s.y[idx])
                summaries.append(dict(session=name,scenario=scenario,
                    I_veh_min=values['I'],covered_min=values['covered'],mean_count=values['mean']))
        audit=t4.replay_archive(summaries,ROOT/'Tuan3/bang_tich_phan_tuan3_AB.csv')
        self.assertEqual(len(audit),10)
        self.assertTrue(all(x['reproduced'] for x in audit))

    def test_full_local_run_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            result=t4.run(out=Path(d))
            self.assertEqual(result['scenarios'],10)
            self.assertTrue((Path(d)/'BAO_CAO_CHAY_LAI_TUAN47.md').exists())
            self.assertEqual(len(t4.read_csv(Path(d)/'chi_so_tich_luy_AB.csv')),99*(1+1)+50*2+26*2+89*2+80*2)

    def test_no_duplicate_plots_and_tuan3_unchanged(self):
        """Tuan4 không có PNG trùng; dọn 5 tên cũ và bảo toàn biểu đồ Tuan3."""
        original = {filename: (ROOT / 'Tuan3' / filename).read_bytes()
                    for _, filename in t4.TUAN3_REFERENCE_CHARTS}
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            for name in t4.OBSOLETE_TUAN4_CHARTS:
                (out / name).write_bytes(b'previous-week4-output')
            (out / 'hinh_minh_hoa_khac.png').write_bytes(b'keep')
            t4.run(out=out)
            actual = {p.name for p in out.glob('*.png')}
            self.assertEqual(actual, {'hinh_minh_hoa_khac.png'})
            generated_report = (out / 'BAO_CAO_CHAY_LAI_TUAN47.md').read_text(encoding='utf-8')
            for _, filename in t4.TUAN3_REFERENCE_CHARTS:
                self.assertIn(filename, generated_report)
                self.assertEqual((ROOT / 'Tuan3' / filename).read_bytes(), original[filename])

    def test_snapshot_ingest_matches_archived_when_recovered(self):
        """Test snapshot mode with same original observed points, preserving camera and time."""
        selection=t4.load_selection()
        original=t4.from_archived(selection)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'analysis_snapshot.csv'
            rows=[]
            for name,s in original.items():
                for i,(ts,y) in enumerate(zip(s.timestamps,s.y)):
                    rows.append(dict(image_id=f'{name}{i:03}',camera_id=s.camera_id,
                                     recording_id=s.recording_id,timestamp=ts,total_count=str(y),
                                     label_status=s.label_status,is_resampled='false'))
            t4.save_csv(p,rows)
            parsed=t4.from_snapshot(p,selection)
            for name in 'AB':
                self.assertEqual(len(parsed[name].t),len(original[name].t))
                np.testing.assert_allclose(parsed[name].y,original[name].y)
                np.testing.assert_allclose(parsed[name].t,original[name].t,atol=1e-9)


    def test_snapshot_source_audit_records_excluded_endpoints(self):
        """Kiểm tra 100 ảnh nguồn/đoạn, 99 được chọn và hash nguồn trên fixture tạm."""
        import hashlib
        from datetime import datetime, timedelta
        selection=t4.load_selection()
        archived=t4.from_archived(selection)
        with tempfile.TemporaryDirectory() as d:
            snapshot=Path(d)/"analysis_snapshot.csv"
            rows=[]
            for name,s in archived.items():
                for i,(ts,y) in enumerate(zip(s.timestamps,s.y)):
                    rows.append(dict(image_id=f"{name}-{i:03d}", camera_id=s.camera_id,
                        recording_id=s.recording_id, timestamp=ts, total_count=str(int(y)),
                        count_2wheel=str(int(y)), count_bus="0", count_car="0", count_truck="0",
                        label_status=s.label_status,label_version="test_fixture",is_resampled="false"))
                rows.append(dict(image_id=f"{name}-last",camera_id=s.camera_id,
                    recording_id=s.recording_id,timestamp=selection[name]["end"],total_count="1",
                    count_2wheel="1",count_bus="0",count_car="0",count_truck="0",
                    label_status=s.label_status,label_version="test_fixture",is_resampled="false"))
            t4.save_csv(snapshot,rows)
            parsed=t4.from_snapshot(snapshot,selection)
            sha,audit=t4.audit_snapshot(snapshot,selection,parsed)
            self.assertEqual(sha,hashlib.sha256(snapshot.read_bytes()).hexdigest())
            for row in audit:
                self.assertEqual(row['raw_records'],100)
                self.assertEqual(row['within_window'],99)
                self.assertEqual(row['selected_nonresampled'],99)
                self.assertEqual(row['excluded_after_window'],1)
                self.assertEqual(row['total_count_mismatch_rows'],0)
                self.assertTrue(row['matched_archived_t_y'])
                self.assertEqual(row['image_ids_present'],99)

if __name__=='__main__':unittest.main()
