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
    if ob.type=='CURVE' and ('web groom' in ob.name or 'Crown swept fibers · web' in ob.name):
        for index,spline in enumerate(list(ob.data.splines)):
            if index%2:ob.data.splines.remove(spline)
    if ob.type in {'MESH','CURVE'}:
        for mod in list(ob.modifiers):
            if mod.type=='SUBSURF' and (ob.name.startswith('Face and cranium') or ob.name.startswith('Blouse · continuous') or ob.name.startswith('Neck') or ob.name.startswith('Hair · original fitted scalp')):ob.modifiers.remove(mod)
bpy.ops.object.select_all(action='DESELECT')
objects=[o for o in bpy.context.scene.objects if o.type in {'MESH','CURVE'}]
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.object.convert(target='MESH')
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
# Replace fourteen iris draw-call materials with equivalent authored corner colors.
iris_material=None
for ob in objects:
    if ob.name.startswith('Iris · radial'):
        colors=[tuple(m.diffuse_color) for m in ob.data.materials]
        ca=ob.data.color_attributes.new(name='IrisFiber',type='BYTE_COLOR',domain='CORNER')
        for poly in ob.data.polygons:
            color=colors[poly.material_index]
            for li in poly.loop_indices:ca.data[li].color=color
            poly.material_index=0
        ob.data.color_attributes.active_color=ca
        if iris_material is None:
            iris_material=ob.data.materials[0].copy();iris_material.name='Iris · single-draw-call radial color'
            nt=iris_material.node_tree;vc=nt.nodes.new('ShaderNodeVertexColor');vc.layer_name='IrisFiber'
            nt.links.new(vc.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color'])
            iris_material.diffuse_color=(1,1,1,1)
        ob.data.materials.clear();ob.data.materials.append(iris_material)
# Retain full physical hair shading in the Blender source, use cheaper PBR in the web LOD.
for mat in bpy.data.materials:
    if mat.use_nodes and mat.name.startswith('Hair'):
        p=mat.node_tree.nodes.get('Principled BSDF')
        if p:
            p.inputs['Anisotropic'].default_value=0;p.inputs['Coat Weight'].default_value=0

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
        dec=ob.modifiers.new('Web groom optimization','DECIMATE');dec.ratio=.34
        bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=dec.name)
bpy.ops.object.select_all(action='SELECT')
triangles=0;vertices=0;bad=[]
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    ob.data.calc_loop_triangles();triangles+=len(ob.data.loop_triangles);vertices+=len(ob.data.vertices)
    if any(not math.isfinite(v) for p in ob.data.vertices for v in p.co):bad.append(ob.name)
assert not bad,('Non-finite vertices',bad)
fp=out/'gpt6_astra_pro_mcp_blender_rgirl_top_half.glb'
bpy.ops.export_scene.gltf(filepath=str(fp),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=14,export_draco_normal_quantization=10,export_draco_color_quantization=8)
stats={'triangles':triangles,'vertices':vertices,'meshObjects':sum(o.type=='MESH' for o in bpy.context.scene.objects),'bytes':fp.stat().st_size,'referenceTextures':0,'authoredImageTextures':0,'renderOnlyGroomExcluded':True,'finiteGeometry':True,'compression':'KHR_draco_mesh_compression','revision':int(bpy.context.scene.get('revision',0))}
(out/'model_stats.json').write_text(json.dumps(stats,indent=2))
print('GLB_EXPORT_OK',json.dumps(stats),flush=True)
