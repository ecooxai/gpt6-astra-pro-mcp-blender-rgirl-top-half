"""Publish only actual rendered, visually reviewed iterations. No automatic quality scoring."""
import json, shutil, sys, datetime, struct
from pathlib import Path
root=Path(__file__).resolve().parents[1];r=int(sys.argv[1]);score=int(sys.argv[2]);title=sys.argv[3];note=sys.argv[4]
assert 0<=score<=100
source=root/'build'/f'gpt6_astra_pro_mcp_blender_rgirl_r{r:02d}_front.png';assert source.is_file(),source
with source.open('rb') as f:header=f.read(24)
w,h=struct.unpack('>II',header[16:24])
status=root/'preview/status.json';d=json.loads(status.read_text()) if status.exists() else {'history':[],'views':[],'files':{}}
shutil.copy2(source,root/'preview/assets/latest-front.png')
d['history']=[x for x in d.get('history',[]) if x['iteration']!=r]+[{'iteration':r,'score':score,'title':title,'note':note}]
d['history'].sort(key=lambda x:x['iteration'])
d.update(version=f'r{r:02d}-reviewed',revision=r,score=score,note=note,updated=datetime.datetime.now(datetime.timezone.utc).isoformat())
d['views']=[{'id':'front','path':'assets/latest-front.png','absolute':str(source),'resolution':f'{w} × {h}','order':r}]
blend=root/'build/gpt6_astra_pro_mcp_blender_rgirl_top_half.blend'
if blend.exists():
    shutil.copy2(blend,root/'preview/assets'/blend.name);d.setdefault('files',{})['blend']={'path':'assets/'+blend.name,'absolute':str(blend),'version':r}
tmp=status.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2));tmp.replace(status)
print(f'Published reviewed iteration {r}, subjective visual score {score}/100')
