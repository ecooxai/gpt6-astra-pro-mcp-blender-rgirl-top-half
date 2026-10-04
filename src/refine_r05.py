from pathlib import Path
p=Path('src/build_character.py');s=p.read_text()
# Reference-like open almond proportions, with iris and limbus still clipped anatomically.
s=s.replace("((z-2.875)/.082)**2<1", "((z-2.875)/.096)**2<1")
s=s.replace(".067*max(0,sin(a))**.82-.045*max(0,-sin(a))**.82", ".082*max(0,sin(a))**.82-.054*max(0,-sin(a))**.82")
s=s.replace("return -.0448*f<=d<=.0668*f", "return -.0538*f<=d<=.0818*f")
s=s.replace("dz=.067*sin(a)**.82", "dz=.082*sin(a)**.82")
s=s.replace("dz=-.045*(-sin(a))**.82", "dz=-.054*(-sin(a))**.82")
s=s.replace("dz=.097*sin(a)**.82", "dz=.111*sin(a)**.82")
s=s.replace("oz=EZ+.136*sin(a)", "oz=EZ+.157*sin(a)")
# A fuller vermilion silhouette, not merely a painted mouth line.
s=s.replace("top=seam+.038*amp**.70", "top=seam+.052*amp**.70")
s=s.replace("bottom=seam-.055*amp**.72", "bottom=seam-.072*amp**.72")
s=s.replace("(.029 if upper else .037)", "(.040 if upper else .052)")
# Give the hair mass a true longitudinal UV field for anisotropic flow and procedural fibers.
s=s.replace("return mesh(name,vs,fs,mat,head=head,col=col)","""ob=mesh(name,vs,fs,mat,head=head,col=col)
    uv=ob.data.uv_layers.new(name='Flow')
    for poly in ob.data.polygons:
        for li in poly.loop_indices:
            index=ob.data.loops[li].vertex_index
            uv.data[li].uv=(index//sides/(n-1),(index%sides)/sides)
    return ob""")
# Each hair material's generated flow texture is authored here, not sourced from an image.
s=s.replace("hairm.append(m)","""nt=m.node_tree
    tangent=nt.nodes.new('ShaderNodeTangent');tangent.direction_type='UV_MAP';tangent.uv_map='Flow'
    nt.links.new(tangent.outputs['Tangent'],p.inputs['Tangent'])
    p.inputs['Anisotropic'].default_value=.58
    uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='Flow'
    mul=nt.nodes.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=(4,680,1)
    nt.links.new(uv.outputs[0],mul.inputs[0])
    no=nt.nodes.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=1;no.inputs['Detail'].default_value=1.6
    nt.links.new(mul.outputs[0],no.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(*(v*.67 for v in c),1)
    ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=(*(v*1.36 for v in c),1)
    nt.links.new(no.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.0012
    nt.links.new(no.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
    hairm.append(m)""")
# Looser inward curling ends, with some tips turning upward rather than all pointing down.
s=s.replace("ps[2]=(ps[2][0],.04,ps[2][2]);ps[3]=(ps[3][0],.075,ps[3][2])\n        locks.append", "ps[2]=(ps[2][0],.04,ps[2][2]);ps[3]=(ps[3][0],.075,ps[3][2])\n        if k%3!=0:\n            last=ps[-1];ps.append((last[0]-side*(.085+.055*u),last[1]-.025,last[2]+.045+.035*sin(k*.9)))\n        locks.append")
# More controlled eye catchlights; diffuse softness and specular highlight size are independent.
s=s.replace("area('Key · large soft window',(-3.5,-4.5,5.4),610,(1.0,.88,.82),3.8)", "key=area('Key · large soft window',(-3.5,-4.5,5.4),610,(1.0,.88,.82),3.8);key.data.specular_factor=.18")
s=s.replace("area('Fill · cool bounce',(3,-2.8,3.2),90,(.81,.87,1),3.3)", "fill=area('Fill · cool bounce',(3,-2.8,3.2),90,(.81,.87,1),3.3);fill.data.specular_factor=.08")
s=s.replace("area('Eye catchlight',(-.8,-4.0,3.6),35,(1,1,1),1.4)", "catch=area('Eye catchlight',(-.8,-4.0,3.6),22,(1,1,1),.48);catch.data.shape='RECTANGLE';catch.data.size_y=.72;catch.data.diffuse_factor=.05")
# A self-authored emissive studio sweep removes the distant floor/world horizon.
marker="da=bpy.data.cameras.new('Portrait camera')"
idx=s.index(marker)
s=s[:idx]+'''# Procedural seamless photographic backdrop; no HDRI or background photograph.
mat=bpy.data.materials.new('Studio sweep · original radial gradient');mat.use_nodes=True
nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission')
uv=nt.nodes.new('ShaderNodeTexCoord');dist=nt.nodes.new('ShaderNodeVectorMath');dist.operation='DISTANCE';dist.inputs[1].default_value=(.5,.51,0)
nt.links.new(uv.outputs['UV'],dist.inputs[0]);ramp=nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.01;ramp.color_ramp.elements[0].color=(.060,.043,.048,1)
ramp.color_ramp.elements[1].position=.31;ramp.color_ramp.elements[1].color=(.009,.007,.010,1)
nt.links.new(dist.outputs['Value'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],em.inputs[0]);em.inputs[1].default_value=.8;nt.links.new(em.outputs[0],out.inputs[0])
bpy.ops.mesh.primitive_plane_add(size=12,location=(0,3.6,2.10),rotation=(pi/2,0,0));sweep=bpy.context.object;sweep.name='Studio seamless sweep';sweep.data.materials.append(mat);link(sweep,STAGE)
''' +s[idx:]
s=s.replace("da.type='ORTHO';da.ortho_scale=3.83;da.lens=80", "da.type='PERSP';da.ortho_scale=3.83;da.lens=78;da.sensor_fit='VERTICAL';da.sensor_height=36")
p.write_text(s)
# Keep the seamless stage behind the subject for every camera direction.
p=Path('src/render_views.py');s=p.read_text();s=s.replace("camera.data.type='ORTHO';camera.data.ortho_scale=scale", "camera.data.type='ORTHO';camera.data.ortho_scale=scale\n sweep=bpy.data.objects.get('Studio seamless sweep')\n if sweep:\n  normal=(camera.location-Vector(target)).normalized();sweep.location=Vector(target)-normal*3.6;sweep.rotation_euler=normal.to_track_quat('Z','Y').to_euler()")
p.write_text(s)
