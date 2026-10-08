import importlib.util, json, threading, unittest, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("app",ROOT/"main.py")
replay=importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)

class ReplayTests(unittest.TestCase):
    def setUp(self): self.events=json.loads((ROOT/'events.json').read_text())
    def test_duplicate_and_shuffle(self):
        a=replay.replay(self.events); b=replay.replay(self.events[::-1]); self.assertEqual(a,b)
        self.assertEqual(a['state']['oht-01']['position'],[3,0,2]); self.assertEqual(a['log'][-1]['status'],'duplicate_or_stale')
    def test_time_cutoff(self): self.assertEqual(replay.replay(self.events,'2026-10-08T06:00:01Z')['state']['oht-01']['version'],1)
    def test_html_escape(self):
        out=replay.render({'state':{'<script>':{'version':1,'position':[0,0,0],'status':'<img>'}},'log':[]})
        self.assertNotIn('<script>',out); self.assertIn('&lt;script&gt;',out)

if __name__=="__main__": unittest.main()
