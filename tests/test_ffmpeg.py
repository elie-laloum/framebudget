import os
from pathlib import Path
import shutil
import tempfile
import unittest
from framebudget.core import search, encode, run, BudgetError
from framebudget.cli import main


FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')
FFPROBE = os.environ.get('FFPROBE', 'ffprobe')


@unittest.skipUnless(shutil.which(FFMPEG) and shutil.which(FFPROBE), 'FFmpeg and ffprobe required')
class FFmpegTests(unittest.TestCase):
    def test_search_encode_audio_and_no_clobber(self):
        with tempfile.TemporaryDirectory() as d:
            source, output = Path(d)/'input.mkv', Path(d)/'output.mkv'
            run([FFMPEG, '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=size=160x90:rate=12', '-f', 'lavfi', '-i',
                 'sine=frequency=440:sample_rate=48000', '-t', '2', '-c:v', 'ffv1', '-c:a', 'pcm_s16le', str(source)])
            report = search(source, ffmpeg=FFMPEG, ffprobe=FFPROBE, metric='psnr', min_quality=25,
                            crfs=[18, 35], presets=['ultrafast'], samples=2, sample_seconds=.5, budget=30)
            self.assertEqual(len(report['candidates']), 2)
            self.assertIsNotNone(report['selected'])
            encode(report, output, ffmpeg=FFMPEG, ffprobe=FFPROBE, verify_quality=True)
            self.assertTrue(output.exists())
            self.assertGreaterEqual(report['final_quality'], 25)
            before = output.read_bytes()
            with self.assertRaises(BudgetError):
                encode(report, output, ffmpeg=FFMPEG, ffprobe=FFPROBE)
            self.assertEqual(output.read_bytes(), before)
            self.assertEqual(main([str(source), '--report', str(source)]), 2)

    def test_impossible_quality_never_claims_success(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d)/'input.mkv'
            run([FFMPEG, '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=size=160x90:rate=12', '-t', '1', '-c:v', 'ffv1', str(source)])
            report = search(source, ffmpeg=FFMPEG, ffprobe=FFPROBE, metric='psnr', min_quality=99,
                            crfs=[45], presets=['ultrafast'], samples=1, sample_seconds=.5, budget=20)
            self.assertIsNone(report['selected'])
            self.assertEqual(report['status'], 'no_feasible_candidate')

    def test_budget_exhaustion_returns_report(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d)/'input.mkv'
            run([FFMPEG, '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=size=160x90:rate=12', '-t', '1', '-c:v', 'ffv1', str(source)])
            report = search(source, ffmpeg=FFMPEG, ffprobe=FFPROBE, metric='psnr', min_quality=30, budget=.001)
            self.assertTrue(report['budget_exhausted'])
            self.assertEqual(report['status'], 'no_feasible_candidate')


if __name__ == '__main__':
    unittest.main()
