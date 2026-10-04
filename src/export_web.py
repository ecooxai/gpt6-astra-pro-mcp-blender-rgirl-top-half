"""Export an independently inspectable reduced-groom GLB from the saved original bust."""
import bpy, json, math
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'build'
# The source .blend is not modified by this exporter.
for cname in ['STUDIO · EEVEE','RENDER ONLY · fine groom']:
    c=bpy.data.collections.get(cname)
    if c:
        for ob in list(c.all_objects):bpy.data.objects.remove(ob,do_unlink=True)
        bpy.data.collections.remove(c)
for ob in list(bpy.context.scene.objects):
    if ob.type in {'MESH','CURVE'}:
        for mod in list(ob.modifiers):
            if mod.type=='SUBSURF' and (ob.name.startswith('Face and cranium') or ob.name.startswith('Blouse · continuous')):ob.modifiers.remove(mod)
bpy.ops.object.select_all(action='DESELECT')
objects=[o for o in bpy.context.scene.objects if o.type in {'MESH','CURVE'}]
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.convert(target='MESH')
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
for ob in objects:
    world=ob.matrix_world.copy();ob.parent=None;ob.matrix_world=world
# Group compatible geometry to reduce browser draw calls without losing material identities.
groups=defaultdict(list)
for ob in objects:groups[tuple(m.name if m else '' for m in ob.data.materials)].append(ob)
for mats,obs in groups.items():
    if len(obs)>1:
        bpy.ops.object.select_all(action='DESELECT')
        for o in obs:o.select_set(True)
        bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join()
        obs[0].name='Web · '+(mats[0] if mats else 'geometry')
for ob in list(bpy.context.scene.objects):
    if ob.type!='MESH':bpy.data.objects.remove(ob,do_unlink=True)
# Simplify only the dense hair sweep surfaces, not facial features or shirt tailoring.
for ob in bpy.context.scene.objects:
    if ob.type=='MESH' and any(m and m.name.startswith('Hair · chestnut') for m in ob.data.materials):
        dec=ob.modifiers.new('Web groom optimization','DECIMATE');dec.ratio=.64
        bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=dec.name)
bpy.ops.object.select_all(action='SELECT')
triangles=0;vertices=0;bad=[]
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    ob.data.calc_loop_triangles();triangles+=len(ob.data.loop_triangles);vertices+=len(ob.data.vertices)
    if any(not math.isfinite(v) for p in ob.data.vertices for v in p.co):bad.append(ob.name)
assert not bad,('Non-finite vertices',bad)
fp=out/'gpt6_astra_pro_mcp_blender_rgirl_top_half.glb'
bpy.ops.export_scene.gltf(filepath=str(fp),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True)
stats={'triangles':triangles,'vertices':vertices,'meshObjects':sum(o.type=='MESH' for o in bpy.context.scene.objects),'bytes':fp.stat().st_size,'referenceTextures':0,'authoredImageTextures':0,'renderOnlyGroomExcluded':True,'finiteGeometry':True}
(out/'model_stats.json').write_text(json.dumps(stats,indent=2))
print('GLB_EXPORT_OK',json.dumps(stats),flush=True)
