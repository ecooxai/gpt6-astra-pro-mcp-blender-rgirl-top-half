"""Publish only files that actually exist; retain an honest reviewed-iteration journal."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,shutil
r=Path(__file__).resolve().parents[1];b=(r/'build').resolve();p=r/'preview';a=p/'assets'
args=argparse.ArgumentParser();args.add_argument('--revision',type=int,required=True);args.add_argument('--score',type=int,required=True);args.add_argument('--title',required=True);args.add_argument('--note',required=True);q=args.parse_args()
s=json.loads((p/'status.json').read_text());now=datetime.now(timezone.utc).isoformat()
prefix='gpt6_astra_pro_mcp_blender_rgirl';front=b/f'{prefix}_r{q.revision:02d}_front.png'
assert front.is_file(), 'Do not publish a nonexistent render.'
row={'iteration':q.revision,'score':q.score,'title':q.title,'note':q.note,'reviewed':now,'assessment':'Subjective visual review; not an independent likeness score.'}
s['history']=[v for v in s.get('history',[]) if v['iteration']!=q.revision]+[row]
s['history'].sort(key=lambda x:x['iteration'])
s.update(version=f'r{q.revision:02d}-{now}',revision=q.revision,score=q.score,note=q.note,updated=now,project=str(r),build=str(b))
views=[]
for order,view in enumerate(['front','detail','threequarter','side','back']):
    f=b/f'{prefix}_r{q.revision:02d}_{view}.png'
    if f.is_file():
        dest=a/f'latest-{view}.png';shutil.copy2(f,dest)
        # PNG IHDR supplies output dimensions; the source/reference is never read here.
        data=f.read_bytes()[:24];w=int.from_bytes(data[16:20],'big');h=int.from_bytes(data[20:24],'big')
        views.append({'id':view,'path':'assets/'+dest.name,'absolute':str(f),'resolution':f'{w} × {h}','order':q.revision*10-order})
s['views']=views
name='gpt6_astra_pro_mcp_blender_rgirl_top_half'
for ext in ['blend','glb']:
    f=b/f'{name}.{ext}'
    if not f.is_file():continue
    version=q.revision if ext=='blend' else json.loads((b/'model_stats.json').read_text()).get('revision',3)
    if ext=='glb' and version!=q.revision:continue
    shutil.copy2(f,a/f.name)
    s.setdefault('files',{})[ext]={'path':'assets/'+f.name,'absolute':str(f),'version':version}
s['completedReviewedIterations']=len(s['history']);s['requestedIterations']=20000;s['targetReached']=False
if (b/'model_stats.json').is_file():
    m=json.loads((b/'model_stats.json').read_text());s['modelStats']=f"{m['triangles']:,} triangles · {m['meshObjects']} mesh groups · {m['bytes']/1e6:.1f} MB GLB · revision {m.get('revision',3)}"
tmp=p/'status.tmp.json';tmp.write_text(json.dumps(s,indent=2));tmp.replace(p/'status.json')
print('PUBLISHED',q.revision,q.score,[x['id'] for x in views],flush=True)
