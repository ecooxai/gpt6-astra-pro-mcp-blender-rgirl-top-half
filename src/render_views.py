"""Render real multi-angle EEVEE views of the saved bust, without changing model geometry."""
import bpy, os, math, json, time
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parents[1];scene=bpy.context.scene;camera=scene.camera
revision=int(scene.get('revision',0));quality=os.environ.get('VIEW_QUALITY','review')
selected=os.environ.get('RENDER_VIEWS','detail,threequarter,side,back').split(',')
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.image_settings.file_format='PNG'
width=512 if quality=='review' else 768;height=684 if quality=='review' else 1024
samples=16 if quality=='review' else 40
jobs={
 'front':((0,-8.3,2.35),(0,-.02,2.075),3.83),
 'threequarter':((-4.7,-7.2,2.65),(0,0,2.08),3.94),
 'side':((-8.3,-.30,2.50),(0,0,2.06),3.97),
 'back':((0,8.3,2.60),(0,0,2.07),3.99),
 'detail':((0,-8.3,2.91),(.095,-.11,2.875),1.97),
}
metadata=[]
for view in selected:
 if view not in jobs:raise ValueError(view)
 position,target,scale=jobs[view];camera.location=position
 camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
 camera.data.type='ORTHO';camera.data.ortho_scale=scale
 sweep=bpy.data.objects.get('Studio seamless sweep')
 if sweep:
  normal=(camera.location-Vector(target)).normalized();sweep.location=Vector(target)-normal*3.6;sweep.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
 scene.render.resolution_x=640 if view=='detail' else width
 scene.render.resolution_y=640 if view=='detail' else height
 scene.render.resolution_percentage=100;scene.eevee.taa_render_samples=samples
 fp=root/'build'/f'gpt6_astra_pro_mcp_blender_rgirl_r{revision:02d}_{view}.png'
 scene.render.filepath=str(fp);start=time.monotonic()
 print('VIEW_START',view,flush=True);bpy.ops.render.render(write_still=True)
 row={'id':view,'absolute':str(fp),'resolution':f'{scene.render.resolution_x} × {scene.render.resolution_y}','seconds':round(time.monotonic()-start,2),'revision':revision}
 metadata.append(row);print('VIEW_COMPLETE',json.dumps(row),flush=True)
(root/'build'/f'render_views_r{revision:02d}.json').write_text(json.dumps(metadata,indent=2))
