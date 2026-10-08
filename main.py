"""Deterministic offline twin reducer with version deduplication and replay."""
import argparse, html, json, math
from pathlib import Path

def replay(events,until=None):
    state={}; log=[]
    for e in sorted(events,key=lambda e:(e['timestamp'],e['asset_id'],e['version'])):
        if until is not None and e['timestamp']>until: continue
        asset=e['asset_id']; old=state.get(asset)
        if old and e['version']<=old['version']: log.append({'asset':asset,'status':'duplicate_or_stale','version':e['version']}); continue
        if type(e['version']) is not int or e['version']<1: raise ValueError('positive integer version required')
        if len(e['position'])!=3 or not all(type(v) in (int,float) and math.isfinite(v) for v in e['position']): raise ValueError('3 finite position coordinates required')
        state[asset]={'version':e['version'],'timestamp':e['timestamp'],'position':e['position'],'status':e['status']}
        log.append({'asset':asset,'status':'applied','version':e['version']})
    return {'state':state,'log':log}

def render(result):
    rows=''.join('<tr><td>'+html.escape(asset)+'</td><td>'+str(s['version'])+'</td><td>'+html.escape(str(s['position']))+'</td><td>'+html.escape(s['status'])+'</td></tr>' for asset,s in result['state'].items())
    payload=json.dumps(result,ensure_ascii=False).replace('<','\u003c')
    return '<!doctype html><meta charset="utf-8"><title>디지털 트윈 이벤트 재생기</title><style>body{font:16px system-ui;max-width:1000px;margin:40px auto;background:#111e2b;color:#eff8ff}td,th{padding:15px;border-bottom:1px solid #345}pre{white-space:pre-wrap}</style><h1>디지털 트윈 이벤트 재생기</h1><p>단위: m, 오른손 좌표계, UTC 이벤트 시간. 오프라인 상태 스냅샷입니다.</p><table><tr><th>장비</th><th>버전</th><th>위치 [x,y,z]</th><th>상태</th></tr>'+rows+'</table><h2>적용 기록</h2><pre>'+html.escape(payload)+'</pre>'

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--input',default=str(Path(__file__).with_name('events.json')))
    p.add_argument('--until',help='UTC ISO-8601 timestamp, format YYYY-MM-DDTHH:MM:SSZ'); p.add_argument('--html',default='replay.html'); a=p.parse_args()
    events=json.loads(Path(a.input).read_text(encoding='utf-8')); result=replay(events,a.until)
    Path(a.html).write_text(render(result),encoding='utf-8'); print(json.dumps(result,ensure_ascii=False,indent=2))
