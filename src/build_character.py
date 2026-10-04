"""Original RGirl portrait bust. Geometry and shading authored from first principles.
No image textures, pretrained character generators, imported meshes or hair assets.
The source reference is deliberately never opened by this program.
"""
import bpy, math, random, os, json, time
from mathutils import Vector
from pathlib import Path
from math import sin, cos, pi, sqrt, exp
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build'; OUT.mkdir(exist_ok=True)
REV=int(os.environ.get('ITERATION','1'))
random.seed(1094)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for block in list(bpy.data.materials): bpy.data.materials.remove(block)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples=48
scene.render.resolution_x=768; scene.render.resolution_y=1024
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=.30
scene.render.image_settings.color_mode='RGBA'
if os.environ.get('FAST_PREVIEW')=='1':
    scene.render.resolution_x=512;scene.render.resolution_y=684;scene.eevee.taa_render_samples=12
CHAR=bpy.data.collections.new('CHARACTER · handcrafted'); scene.collection.children.link(CHAR)
STAGE=bpy.data.collections.new('STUDIO · EEVEE'); scene.collection.children.link(STAGE)
FINE=bpy.data.collections.new('RENDER ONLY · fine groom'); scene.collection.children.link(FINE)
rig=bpy.data.objects.new('Head pose · 7 degree natural lean',None); CHAR.objects.link(rig)
rig.location=(0,0,2.15); rig.rotation_euler[1]=math.radians(7)

def link(obj,col=CHAR,head=False):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj)
    if head:
        obj.parent=rig
        obj.location.z-=2.15
    return obj

def material(name,color,rough=.5,metal=0,sss=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    p.inputs['Specular IOR Level'].default_value=.30
    if sss:
        p.inputs['Subsurface Weight'].default_value=sss
        p.inputs['Subsurface Radius'].default_value=(1,.48,.28)
        p.inputs['Subsurface Scale'].default_value=.045
    return m
skin=material('Skin · warm porcelain with vertex blush',(.72,.47,.37),.47,sss=.075)
nt=skin.node_tree; p=nt.nodes.get('Principled BSDF'); a=nt.nodes.new('ShaderNodeVertexColor'); a.layer_name='Complexion'; nt.links.new(a.outputs['Color'],p.inputs['Base Color'])
noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=310; noise.inputs['Detail'].default_value=2
bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.10; bump.inputs['Distance'].default_value=.003
nt.links.new(noise.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
skinplain=material('Skin · neck and ears',(.72,.47,.37),.48,sss=.08)
earinner=material('Ear · warm concha',(.51,.25,.205),.58,sss=.07)
nostril=material('Nostril · recessed warm shadow',(.105,.034,.027),.75)
water=material('Lacrimal margin · soft rose',(.52,.23,.20),.29,sss=.04)
lip=material('Lips · rose satin',(.54,.205,.205),.36,sss=.045)
seammat=material('Mouth · closed soft seam',(.18,.057,.052),.64)
sclera=material('Eyes · ivory sclera',(.84,.78,.70),.20)
pp=sclera.node_tree.nodes.get('Principled BSDF'); pp.inputs['Coat Weight'].default_value=.28; pp.inputs['Coat Roughness'].default_value=.1
pupil=material('Pupil · deep brown black',(.007,.003,.002),.12)
limbal=material('Iris · limbal ring',(.037,.016,.010),.25)
browmat=material('Eyebrows and lashes · soft umber',(.034,.015,.009),.49)
shirt=material('Shirt · white cotton weave',(.81,.83,.88),.71)
nt=shirt.node_tree; p=nt.nodes.get('Principled BSDF'); p.inputs['Sheen Weight'].default_value=.13
no=nt.nodes.new('ShaderNodeTexNoise'); no.inputs['Scale'].default_value=370; no.inputs['Detail'].default_value=1.2
bu=nt.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value=.11; bu.inputs['Distance'].default_value=.003
nt.links.new(no.outputs['Fac'],bu.inputs['Height']); nt.links.new(bu.outputs['Normal'],p.inputs['Normal'])
thread=material('Cotton seam · tonal',(.63,.65,.70),.83)
button=material('Buttons · warm mother of pearl',(.86,.84,.77),.30)
buttonhole=material('Button recesses',(.30,.29,.28),.67)
hairm=[]
for i in range(8):
    c=(.020+i*.0040,.010+i*.00225,.008+i*.00165)
    m=material('Hair · chestnut fiber %02d'%i,c,.36+(i%3)*.035)
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Anisotropic'].default_value=.37
    p.inputs['Coat Weight'].default_value=.12; p.inputs['Coat Roughness'].default_value=.3
    hairm.append(m)

def complexion(x,z):
    rosy=exp(-((abs(x)-.34)/.17)**2-((z-2.60)/.16)**2)*.23
    eye=exp(-((abs(x)-.285)/.20)**2-((z-2.83)/.13)**2)*.045
    c=(.72+rosy*.15-eye*.3,.47-rosy*.19-eye*.35,.37-rosy*.10-eye*.18)
    return (*c,1)

def mesh(name,verts,faces,mat,col=CHAR,head=False,sub=0,skincolor=False):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); ob.data.materials.append(mat)
    for p in me.polygons: p.use_smooth=True
    if skincolor:
        ca=me.color_attributes.new(name='Complexion',type='FLOAT_COLOR',domain='POINT')
        ca.data.foreach_set('color',[c for x,y,z in verts for c in complexion(x,z)])
    if sub:
        mod=ob.modifiers.new('Smooth anatomical subdivision','SUBSURF'); mod.levels=sub; mod.render_levels=sub
    if head:
        ob.parent=rig; ob.location.z=-2.15
    return ob

def uv(name,loc,scale,mat,head=False,seg=48,rings=32,col=CHAR):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(mat)
    for f in o.data.polygons:f.use_smooth=True
    return link(o,col,head)

def curve(name,paths,mat,radius=.002,head=False,col=CHAR,res=1):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=1; cu.bevel_depth=radius; cu.bevel_resolution=res
    for path in paths:
        sp=cu.splines.new('POLY'); sp.points.add(len(path)-1)
        for i,p in enumerate(path):
            sp.points[i].co=(*p[:3],1); sp.points[i].radius=p[3] if len(p)>3 else 1
    o=bpy.data.objects.new(name,cu); col.objects.link(o); cu.materials.append(mat)
    if head:o.parent=rig; o.location.z=-2.15
    return o

def catmull(points,n=80):
    out=[]; ps=[Vector(points[0])]+[Vector(p) for p in points]+[Vector(points[-1])]
    for j in range(n):
        u=j/(n-1)*(len(points)-1); k=min(int(u),len(points)-2); t=u-k
        a,b,c,d=ps[k:k+4]
        out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    return out

def interp(z,ps):
    # C1 monotone cubic interpolation: no flat derivatives at every profile ring.
    if z<=ps[0][0]:return ps[0][1]
    if z>=ps[-1][0]:return ps[-1][1]
    ds=[(ps[j+1][1]-ps[j][1])/(ps[j+1][0]-ps[j][0]) for j in range(len(ps)-1)]
    slopes=[ds[0]]
    for j in range(1,len(ps)-1):
        a,b=ds[j-1],ds[j]; slopes.append(0 if a*b<=0 else 2*a*b/(a+b))
    slopes.append(ds[-1])
    for i in range(len(ps)-1):
        if ps[i][0]<=z<=ps[i+1][0]:
            h=ps[i+1][0]-ps[i][0];t=(z-ps[i][0])/h
            return (2*t**3-3*t*t+1)*ps[i][1]+(t**3-2*t*t+t)*h*slopes[i]+(-2*t**3+3*t*t)*ps[i+1][1]+(t**3-t*t)*h*slopes[i+1]

W=[(2.035,.035),(2.08,.19),(2.16,.30),(2.28,.406),(2.44,.488),(2.62,.54),(2.82,.553),(3.04,.553),(3.24,.55),(3.42,.51),(3.58,.40),(3.70,.23),(3.765,.005)]
D=[(2.035,.255),(2.12,.375),(2.30,.438),(2.52,.460),(2.80,.470),(3.02,.485),(3.25,.470),(3.45,.425),(3.62,.30),(3.765,.003)]
B=[(2.035,.04),(2.18,.28),(2.50,.44),(2.90,.51),(3.25,.50),(3.5,.43),(3.7,.22),(3.765,.003)]

def front(x,z):
    w=max(.002,interp(z,W)); c=sqrt(max(.0,1-(x/w)**2)); y=.035-interp(z,D)*c**.67
    y-=.025*exp(-((abs(x)-.34)/.19)**2-((z-2.62)/.18)**2)
    y-=.025*exp(-(x/.22)**2-((z-2.30)/.14)**2)
    y-=.126*exp(-(x/.066)**2-((z-2.785)/.22)**2)
    y-=.207*exp(-(x/.086)**2-((z-2.567)/.080)**2)
    y-=.082*exp(-((abs(x)-.079)/.039)**2-((z-2.531)/.046)**2)
    y-=.019*exp(-(x/.040)**2-((z-2.414)/.067)**2)
    return y

# Continuous craniofacial surface with genuine eye openings; no photograph projection.
verts=[]; faces=[]; nz=178; na=256
for i in range(nz):
    z=2.035+(3.765-2.035)*i/(nz-1); w=interp(z,W)
    for j in range(na):
        a=2*pi*j/na; x=w*sin(a); c=cos(a)
        y=front(x,z) if c>=0 else .035+interp(z,B)*(-c)**.85
        verts.append((x,y,z))
for i in range(nz-1):
    for j in range(na):
        ids=(i*na+j,i*na+(j+1)%na,(i+1)*na+(j+1)%na,(i+1)*na+j)
        x=sum(verts[k][0] for k in ids)/4; y=sum(verts[k][1] for k in ids)/4; z=sum(verts[k][2] for k in ids)/4
        hole=((abs(x)-.270)/.184)**2+((z-2.875)/.082)**2<1
        if not (y<-.18 and hole):faces.append(ids)
mesh('Face and cranium · original anatomical surface',verts,faces,skin,head=True,sub=1,skincolor=True)
# Neck loft and concealed upper chest.
vs=[]; fs=[]; N=56; R=28
for i in range(R):
    t=i/(R-1); z=1.26+t*.97; rx=.33-.105*sin(t*pi*.8); ry=.245-.055*t; cy=.055+.03*t
    for j in range(N):
        a=2*pi*j/N; vs.append((rx*sin(a),cy-ry*cos(a),z))
for i in range(R-1):
    for j in range(N):fs.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
mesh('Neck · tapered sternomastoid transition',vs,fs,skinplain,sub=1)
uv('Upper chest beneath shirt',(0,.065,1.28),(.64,.28,.36),skinplain)
# Subtle paired clavicles, partly covered by the opening.
for s in [-1,1]:
    pts=catmull([(s*.04,-.21,1.40),(s*.18,-.209,1.46),(s*.34,-.18,1.48)],22)
    curve('Clavicle soft ridge',[[(*p,.65) for p in pts]],skinplain,.008)

# Anatomical ear shells and helix folds.
for s in [-1,1]:
    uv('Ear shell '+str(s),(s*.555,.025,2.765),(.116,.076,.223),skinplain,True)
    uv('Concha '+str(s),(s*.589,-.046,2.777),(.054,.014,.125),earinner,True)
    pts=[]
    for j in range(70):
        a=2*pi*j/69; pts.append((s*(.566+.083*sin(a)), -.031-.030*sin(a)**2, 2.768+.185*cos(a),.75+.25*sin(a)**2))
    curve('Helix folded cartilage '+str(s),[pts],skinplain,.014,True)
    pts=catmull([(s*.58,-.064,2.65),(s*.60,-.069,2.75),(s*.585,-.064,2.86)],30)
    curve('Antihelix '+str(s),[[(*p,.8) for p in pts]],skinplain,.012,True)
    uv('Tragus '+str(s),(s*.545,-.070,2.737),(.024,.020,.039),skinplain,True)
# Eyes: spherical sclera, radial mesh irises and concentric pupil/limbus.
EYEY=-.305; EZ=2.875; EX=.270

def eyey(dx,dz,offset=0):return EYEY-.17*sqrt(max(.004,1-(dx/.195)**2-(dz/.172)**2))-offset
iris_mats=[]
for k in range(14):
    f=k/13; iris_mats.append(material('Iris radial fiber %02d'%k,(.052+.075*f,.020+.036*f,.010+.018*f),.20))
for s in [-1,1]:
    cx=s*EX
    # Only the anatomically exposed corneal surface is outside the lids.
    # A complete unmasked sphere was protruding through the previous facial mesh.
    ev=[(cx,eyey(0,0),EZ)];ef=[];er=20;ea=128
    for ri in range(1,er+1):
        rr=ri/er
        for j in range(ea):
            a=2*pi*j/ea;dx=.166*cos(a)*rr;dz=(.067*max(0,sin(a))**.82-.045*max(0,-sin(a))**.82+s*.07*.166*cos(a))*rr
            ev.append((cx+dx,eyey(dx,dz),EZ+dz))
    for j in range(ea):ef.append((0,1+j,1+(j+1)%ea))
    for ri in range(er-1):
        for j in range(ea):
            a=1+ri*ea+j;b=1+ri*ea+(j+1)%ea;c=1+(ri+1)*ea+(j+1)%ea;d=1+(ri+1)*ea+j
            ef.append((a,d,c,b))
    mesh('Eye · anatomically masked sclera '+str(s),ev,ef,sclera,head=True)
    # Iris follows the corneal curvature; material bands are physical mesh faces.
    v=[]; f=[]; seg=160; nr=16
    random_phase=[random.random() for _ in range(seg)]
    for r in range(nr):
        rad=.027+(.069-.027)*r/(nr-1)
        for j in range(seg):
            a=2*pi*j/seg; dx=rad*cos(a); dz=rad*sin(a)
            v.append((cx+dx,eyey(dx,dz,.0025),EZ+dz))
    for r in range(nr-1):
        for j in range(seg):f.append((r*seg+j,r*seg+(j+1)%seg,(r+1)*seg+(j+1)%seg,(r+1)*seg+j))
    ob=mesh('Iris · radial brown fibers '+str(s),v,[tuple(reversed(q)) for q in f],iris_mats[0],head=True)
    for m in iris_mats[1:]:ob.data.materials.append(m)
    for poly in ob.data.polygons:
        r=poly.index//seg; j=poly.index%seg
        poly.material_index=max(0,min(13,int(3+7*random_phase[j]+2*sin(r*.72+j*.31))))
    # Pupil domed patch, rather than a flat billboard.
    v=[(cx,eyey(0,0,.0035),EZ)]; f=[]
    for j in range(seg):
        a=2*pi*j/seg; dx=.028*cos(a); dz=.028*sin(a); v.append((cx+dx,eyey(dx,dz,.0035),EZ+dz))
    for j in range(seg):f.append((0,j+1,(j+1)%seg+1))
    mesh('Pupil '+str(s),v,f,pupil,head=True)
    rings=[]
    for j in range(seg+1):
        a=2*pi*j/seg; dx=.069*cos(a); dz=.069*sin(a); rings.append((cx+dx,eyey(dx,dz,.0035),EZ+dz,1))
    curve('Limbal edge '+str(s),[rings],limbal,.002,True)
    # Fleshy eyelid annulus, blending from almond opening into facial skin.
    v=[]; f=[]; loops=11; steps=128
    inner=[]
    for r in range(loops):
        t=r/(loops-1); smooth=t*t*(3-2*t)
        for j in range(steps):
            a=2*pi*j/steps; dx=.166*cos(a); dz=.067*max(0,sin(a))**.82-.045*max(0,-sin(a))**.82+s*.07*dx
            ix=cx+dx; iz=EZ+dz; iy=eyey(dx,dz,.003)
            ox=cx+.223*cos(a); oz=EZ+.136*sin(a)+s*.06*.223*cos(a)
            x=ix*(1-smooth)+ox*smooth; z=iz*(1-smooth)+oz*smooth
            y=iy*(1-smooth)+(front(ox,oz)-.001)*smooth-.010*sin(pi*t)
            v.append((x,y,z))
            if r==0:inner.append((ix,iy-.001,iz,1))
    for r in range(loops-1):
        for j in range(steps):f.append((r*steps+j,r*steps+(j+1)%steps,(r+1)*steps+(j+1)%steps,(r+1)*steps+j))
    mesh('Orbital lids · anatomical almond '+str(s),v,[tuple(reversed(q)) for q in f],skin,head=True,sub=1,skincolor=True)
    curve('Waterline '+str(s),[inner+[inner[0]]],water,.0026,True)
    # Fine upper lid crease, not heavy eyeliner.
    pts=[]
    for j in range(55):
        a=.12+(pi-.24)*j/54; dx=.165*cos(a); dz=.097*sin(a)**.82+s*.07*dx
        pts.append((cx+dx,front(cx+dx,EZ+dz)-.017,EZ+dz, sin(pi*j/54)**.5))
    curve('Upper eyelid fold '+str(s),[pts],earinner,.0017,True)
    lashes=[]
    for j in range(38):
        a=.15+(pi-.3)*j/37; dx=.165*cos(a); dz=.067*sin(a)**.82+s*.07*dx
        x=cx+dx; y=eyey(dx,dz,.004); z=EZ+dz
        length=.017+.022*(.5+.5*s*cos(a))+.004*random.random()
        pts=catmull([(x,y,z),(x+dx*.045,y-.012,z+length*.42),(x+dx*.075,y-.022,z+length)],7)
        lashes.append([(*p,1-t/len(pts)*.96) for t,p in enumerate(pts)])
    curve('Individual upper eyelashes '+str(s),lashes,browmat,.0011,True,res=0)
    lower=[]
    for j in range(17):
        a=pi+.25+(pi-.5)*j/16; dx=.164*cos(a); dz=-.045*(-sin(a))**.82+s*.07*dx
        p=(cx+dx,eyey(dx,dz,.004),EZ+dz); q=(p[0]+dx*.04,p[1]-.012,p[2]-.012)
        lower.append([(*p,.7),(*q,.02)])
    curve('Lower lashes '+str(s),lower,browmat,.00075,True,res=0)
    brows=[]
    for j in range(180):
        t=random.random(); x=s*(.105+.381*t); z=3.035+.046*sin(pi*t*.9)-.041*t+random.uniform(-.012,.012)
        y=front(x,z)-.006; le=.023+.019*(1-t)
        brows.append([(x,y,z,.50),(x+s*.009,y-.002,z+le*.56,.75),(x+s*.021,y,z+le,.04)])
    curve('Eyebrow · 180 tapered hairs '+str(s),brows,browmat,.00105,True,res=0)
# Nose openings are small recessed warm cavities, not painted dots.
for s in [-1,1]:
    x=s*.072; z=2.508; y=front(x,z)-.004
    ob=uv('Nostril recess '+str(s),(x,y,z),(.024,.006,.0105),nostril,True,32,16)
    ob.rotation_euler[1]=s*math.radians(-14)
# Lips, cupid bow and closed mouth line.
lip.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.22
A=.178
for upper in [True,False]:
    v=[]; f=[]; cols=96; rows=16
    for i in range(rows):
        t=i/(rows-1)
        for j in range(cols):
            u=-1+2*j/(cols-1); x=A*u; amp=max(0,1-u*u)
            seam=2.281+.006*u*u-.002*cos(pi*u)
            top=seam+.038*amp**.70+.010*exp(-((abs(x)-.047)/.025)**2)-.007*exp(-(x/.021)**2)
            bottom=seam-.050*amp**.72
            z=seam*(1-t)+(top if upper else bottom)*t
            bulge=(.029 if upper else .037)*sin(pi*t)**.8*amp
            y=front(x,z)-bulge-.010*(1-t)*amp-.001
            v.append((x,y,z))
    for i in range(rows-1):
        for j in range(cols-1):f.append((i*cols+j,i*cols+j+1,(i+1)*cols+j+1,(i+1)*cols+j))
    mesh(('Upper' if upper else 'Lower')+' lip · sculpted vermilion',v,f,lip,head=True,sub=1)
pts=[]
for j in range(85):
    u=-1+2*j/84; x=A*u; z=2.281+.006*u*u-.002*cos(pi*u)
    pts.append((x,front(x,z)-.012*max(0,1-u*u)-.002,z,.8*sin(pi*j/84)**.5))
curve('Closed mouth separation',[pts],seammat,.0025,True)
# Shirt with a real open neckline, shoulder volume, fabric folds and tapered sleeves.
vs=[]; fs=[]; nr=62; ns=160
for i in range(nr):
    t=i/(nr-1)
    w=interp(t,[(0,.86),(.30,.90),(.63,.97),(.81,1.01),(.89,.86),(.96,.47),(1,.273)])
    d=interp(t,[(0,.34),(.25,.43),(.50,.48),(.70,.39),(.86,.28),(1,.223)])
    z0=interp(t,[(0,.035),(.3,.53),(.63,1.09),(.81,1.46),(.89,1.56),(1,1.74)])
    for j in range(ns):
        a=2*pi*j/ns; c=cos(a); x=w*sin(a)
        z=z0-.445*max(c,0)*(1-abs(sin(a)))*max(0,(t-.84)/.16)**1.2
        y=.055-d*c
        if c>0:
            folds=.012*sin(32*x+5*z)*exp(-((z-.55)/.60)**2)+.012*sin(16*z+12*abs(x))*abs(x)
            y-=folds*c*c
        vs.append((x,y,z))
for i in range(nr-1):
    for j in range(ns):fs.append((i*ns+j,i*ns+(j+1)%ns,(i+1)*ns+(j+1)%ns,(i+1)*ns+j))
body=mesh('Blouse · continuous woven body',vs,fs,shirt,sub=1)
solid=body.modifiers.new('Tailored cloth thickness','SOLIDIFY'); solid.thickness=.009

def tube(name,points,width,depth,mat,head=False,col=CHAR,sides=10):
    vs=[]; fs=[]; n=len(points)
    for i,p in enumerate(points):
        p=Vector(p); tangent=(Vector(points[min(n-1,i+1)])-Vector(points[max(0,i-1)])).normalized()
        ref=Vector((0,-1,0)); side=tangent.cross(ref).normalized()
        if side.length<.1:side=Vector((1,0,0))
        normal=side.cross(tangent).normalized(); t=i/(n-1)
        ww=width(t) if callable(width) else width; dd=depth(t) if callable(depth) else depth
        for j in range(sides):
            a=2*pi*j/sides; q=p+side*(cos(a)*ww)+normal*(sin(a)*dd); vs.append(tuple(q))
    for i in range(n-1):
        for j in range(sides):fs.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
    fs.append(tuple(reversed(range(sides)))); fs.append(tuple((n-1)*sides+j for j in range(sides)))
    return mesh(name,vs,fs,mat,head=head,col=col)
for s in [-1,1]:
    ps=catmull([(s*.79,.052,1.53),(s*.98,.05,1.31),(s*1.075,.04,.86),(s*1.10,.02,.42),(s*1.12,.025,.035)],50)
    tube('Sleeve · relaxed shoulder '+str(s),ps,lambda t:(.245-.032*t+.004*sin(12*pi*t))*min(1,t/.105)**.5,lambda t:(.273-.045*t)*min(1,t/.105)**.5,shirt,sides=48)
# Folded collar panels with curvature and thickness.
for s in [-1,1]:
    # corners: neck back, shoulder collar break, outer point, inner opening
    rows=[[(s*.24,.01,1.80),(s*.37,-.12,1.66),(s*.46,-.255,1.46)],[(s*.227,-.14,1.67),(s*.33,-.32,1.46),(s*.405,-.393,1.30)],[(s*.175,-.247,1.48),(s*.23,-.413,1.33),(s*.285,-.463,1.16)]]
    def bez3(q,t):return Vector(q[0])*(1-t)**2+Vector(q[1])*2*t*(1-t)+Vector(q[2])*t*t
    vs=[];fs=[];res=20
    for i in range(res):
        vv=i/(res-1)
        for j in range(res):
            uu=j/(res-1);q=[bez3(row,uu) for row in rows];vs.append(tuple(bez3(q,vv)))
    for i in range(res-1):
        for j in range(res-1):fs.append((i*res+j,i*res+j+1,(i+1)*res+j+1,(i+1)*res+j))
    ob=mesh('Collar · crisp folded point '+str(s),vs,fs,shirt)
    so=ob.modifiers.new('Collar turned edge','SOLIDIFY'); so.thickness=.012
    curve('Collar topstitch '+str(s),[[(*p,.7) for p in catmull([rows[0][2],rows[1][2],rows[2][2]],35)]],thread,.0016)
# Button placket, deliberately curved with the fabric surface.
def shirtfront(z):
    lo,hi=0,.81
    for _ in range(20):
        t=(lo+hi)/2
        zz=interp(t,[(0,.035),(.3,.53),(.63,1.09),(.81,1.46),(.89,1.56),(1,1.74)])
        if zz<z:lo=t
        else:hi=t
    t=(lo+hi)/2
    dep=interp(t,[(0,.34),(.25,.43),(.50,.48),(.70,.39),(.86,.28),(1,.223)])
    folds=.012*sin(5*z)*exp(-((z-.55)/.60)**2)
    return .055-dep-folds-.014

v=[]; f=[]; rows=60
for i in range(rows):
    t=i/(rows-1); z=.05+1.15*t; cx=-.018*sin(pi*t)
    for j in range(5):
        x=cx+(j/4-.5)*.103; y=shirtfront(z)-.012*sin(j/4*pi); v.append((x,y,z))
for i in range(rows-1):
    for j in range(4):f.append((i*5+j,i*5+j+1,(i+1)*5+j+1,(i+1)*5+j))
ob=mesh('Blouse · raised button placket',v,f,shirt,sub=1); so=ob.modifiers.new('Placket thickness','SOLIDIFY');so.thickness=.006
for x in [-.052,.052]:
    p=[(x-.018*sin(pi*i/59),shirtfront(.05+1.15*i/59)-.001,.05+1.15*i/59,.55) for i in range(60)]
    curve('Placket stitching',[p],thread,.0012)
for idx,z in enumerate([.20,.59,.985]):
    y=shirtfront(z)-.024; x=-.018*sin(pi*(z-.05)/1.15)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.031,depth=.010,location=(x,y,z),rotation=(pi/2,0,0))
    ob=bpy.context.object; ob.name='Shirt button %d · four drilled recesses'%(idx+1); ob.data.materials.append(button); link(ob)
    be=ob.modifiers.new('Rounded pearl rim','BEVEL');be.width=.005;be.segments=3
    for dx,dz in [(-.008,-.008),(.008,-.008),(-.008,.008),(.008,.008)]:uv('Button thread hole',(x+dx,y-.006,z+dz),(.0035,.002,.0035),buttonhole,seg=16,rings=8)
    curve('Button sewing thread',[[ (x-.009,y-.009,z-.008,.7),(x+.009,y-.009,z+.008,.7)],[(x-.009,y-.009,z+.008,.7),(x+.009,y-.009,z-.008,.7)]],shirt,.001)

# Hair scalp and long layered guide locks. Every strand is a generated 3D curve.
vs=[]; fs=[]; rows=40; ns=144
for i in range(rows):
    t=i/(rows-1)
    for j in range(ns):
        th=2*pi*j/ns;c=cos(th)
        zend=3.26-.61*(1-c)/2
        z=3.813-t*(3.813-zend);zz=z-.05
        taper=min(1,max(0,(3.813-z)/.045))**.45
        w=(interp(zz,W)+.034)*taper
        x=w*sin(th)
        y=.035-(interp(zz,D)+.048)*max(c,0)**.67 if c>=0 else .035+(interp(zz,B)+.042)*(-c)**.85
        if t<.016:y=.035+(y-.035)*t/.016

        vs.append((x,y,z))
for i in range(rows-1):
    for j in range(ns):fs.append((i*ns+j,i*ns+(j+1)%ns,(i+1)*ns+(j+1)%ns,(i+1)*ns+j))
mesh('Hair · original fitted scalp shell',vs,fs,hairm[1],head=True,sub=1)
# Rear and side hair envelope, fully modeled for 360 degree viewing.
vs=[]; fs=[]; rows=66; cols=110
for i in range(rows):
    t=i/(rows-1); z=3.28-2.95*t
    w=interp(t,[(0,.55),(.20,.625),(.45,.675),(.70,.75),(.90,.70),(1,.56)])
    dep=interp(t,[(0,.46),(.24,.44),(.50,.46),(1,.40)])
    cy=interp(t,[(0,.065),(.25,.03),(.53,-.06),(.77,-.14),(1,-.10)])
    for j in range(cols):
        leftgap=.90+.68*exp(-((z-2.74)/.32)**2); th=.90+(2*pi-.90-leftgap)*j/(cols-1); wave=.014*sin(th*18+t*12)+.013*sin(th*9-t*10)
        x=(w+wave)*sin(th); y=cy-dep*cos(th); zz=z+.08*sin(th*5)*t**6
        vs.append((x,y,zz))
for i in range(rows-1):
    for j in range(cols-1):fs.append((i*cols+j,i*cols+j+1,(i+1)*cols+j+1,(i+1)*cols+j))
mesh('Hair · continuous rear silhouette',vs,fs,hairm[1],head=True,sub=1)
# Flowing side guide locks. Flattened elliptical geometry, tapered tips, mild waves.
locks=[]
for side in [-1,1]:
    for k in range(46):
        u=k/45; yy=-.24+.65*u; root=(.10+side*.027,yy,3.80-.31*abs(yy)**1.5)
        endz=.26+random.random()*.37
        xx=side*(.52+.17*random.random())
        ps=[root,(side*.30,yy-.03,3.74-.12*u),(side*.56,yy-.03,3.38),(side*(.59+.06*u),yy+.02,2.91),(side*(.60+.08*u),yy-.01,2.28),(side*(.63+.09*u),yy-.34,1.55),(side*(.75-.03*u),yy-.37,.82),(xx,yy-.30,endz)]
        
        if side<0:
            ps[3]=(ps[3][0],max(.095,ps[3][1]),ps[3][2]);ps[4]=(ps[4][0],max(.02,ps[4][1]),ps[4][2])
        locks.append((catmull(ps,105),side,u))
    # Front shoulder cascades, asymmetrical side part framing the face.
    for k in range(17):
        u=k/16; yy=-.09-u*.17
        ps=[(.105+side*.024,-.19,3.80),(side*.36,-.40-u*.025,3.56),(side*(.55+.035*u),-.33,3.04),(side*(.58+.075*u),-.24,2.48),(side*(.54+.15*u),-.39,1.95),(side*(.58+.20*u),-.59,1.30),(side*(.60+.23*u),-.64,.72),(side*(.46+.18*u),-.53,.27+.21*u)]
        
        if side<0:
            ps[2]=(ps[2][0],.04,ps[2][2]);ps[3]=(ps[3][0],.075,ps[3][2])
        locks.append((catmull(ps,105),side,u))
for k,(ps,side,u) in enumerate(locks):
    for i,pt in enumerate(ps):
        t=i/(len(ps)-1);f=max(0,(t-.43)/.57)**1.3
        pt.x+=side*f*(.043*sin(12*t+u*4)+.027*sin(18*t+u*2))
        pt.y+=f*.025*sin(13*t+u*4)
    width=.032+random.random()*.023
    tube('Hair lock %03d · swept and tapered'%k,ps,lambda t,w=width:w*(.22+.78*sin(pi*min(t,.999))**.40)*(1-t**12),lambda t:.014*(.25+.75*sin(pi*t)**.45)*(1-t**12),hairm[k%4],True,sides=8)
# Thousands of explicitly modeled fine filaments, plus a reduced export groom.
fine=[[] for _ in range(8)]; lod=[[] for _ in range(8)]
for k,(ps,side,u) in enumerate(locks):
    for j in range(26):
        phase=random.random()*pi*2; off=(j/25-.5)*.088; d=random.uniform(-.009,.010)
        path=[]
        for i,p in enumerate(ps):
            t=i/(len(ps)-1); dx=off*sin(pi*t)**.45+.003*sin(phase+t*15); dy=-.017+d+.0018*sin(phase+t*19)
            path.append((p.x+dx,p.y+dy,p.z+.003*sin(phase+t*11),(.15+.85*sin(pi*min(t,.999))**.22)*(1-t**14)))
        fine[(j+k)%8].append(path)
        if j in [3,10,17,24]:lod[(j+k)%8].append(path[::2]+[path[-1]])
for i,paths in enumerate(fine):curve('Fine hair · render groom %d'%i,paths,hairm[i],.00085,True,FINE,0)
for i,paths in enumerate(lod):curve('Hair filaments · web groom %d'%i,paths,hairm[i],.0010,True,CHAR,0)
# Short side-swept fringe is independent of the long-hair guides.
fringes=[[(.11,-.22,3.80),(-.13,-.46,3.57),(-.32,-.49,3.25),(-.42,-.48,2.98),(-.48,-.42,2.65)],[(.12,-.22,3.78),(-.02,-.49,3.48),(-.14,-.51,3.22),(-.24,-.49,2.99)],[(.14,-.23,3.77),(.11,-.49,3.48),(.06,-.53,3.20),(-.025,-.50,2.998)],[(.16,-.23,3.78),(.21,-.50,3.45),(.21,-.53,3.20),(.12,-.50,3.035)]]
for k,guide in enumerate(fringes):
    ps=catmull(guide,65)
    tube('Fringe · wispy cluster %d'%k,ps,lambda t:.012*(.25+.75*sin(pi*t)**.5)*(1-t**5),lambda t:.0028*(1-t**6),hairm[2],True,sides=8)
    paths=[]
    for j in range(30):
        off=(j/29-.5)*(.067 if k==0 else .045); path=[]
        for i,p in enumerate(ps):
            t=i/(len(ps)-1); path.append((p.x+off*t**.5,p.y-.007-random.random()*.001,p.z+.006*sin(t*pi+j),(.55+.45*sin(pi*t))*(1-t**9)))
        paths.append(path)
    curve('Fringe filaments %d'%k,paths,hairm[4],.00085,True,res=0)
# A few airy flyaways; no opaque cards or alpha texture shortcuts.
paths=[]
for k in range(90):
    ps,side,u=random.choice(locks); phase=random.random()*2*pi
    path=[]
    for i in range(0,len(ps),2):
        p=ps[i]; t=i/(len(ps)-1); off=.006+.015*sin(pi*t)
        path.append((p.x+side*off,p.y-.024-.008*sin(phase+8*t),p.z+.013*sin(phase+7*t),(.1+.8*sin(pi*t)**.6)*(1-t**7)))
    paths.append(path)
curve('Hair · airy flyaway strands',paths,hairm[5],.0006,True,FINE,0)

# Neutral portrait atelier lighting, with no downloaded HDR environment.
world=bpy.data.worlds.new('Studio · neutral ambient'); scene.world=world; world.use_nodes=True
world.node_tree.nodes.get('Background').inputs[0].default_value=(.28,.30,.34,1)
world.node_tree.nodes.get('Background').inputs[1].default_value=.32
back=material('Backdrop · slate taupe',(.075,.071,.077),.87)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.035)); floor=bpy.context.object; floor.name='Studio floor';floor.data.materials.append(back);link(floor,STAGE)

def area(name,loc,power,color,size,target=(0,0,2.3)):
    da=bpy.data.lights.new(name,'AREA'); da.energy=power; da.color=color;da.shape='DISK'; da.size=size
    ob=bpy.data.objects.new(name,da); STAGE.objects.link(ob);ob.location=loc; ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();return ob
area('Key · large soft window',(-3.5,-4.5,5.4),520,(1.0,.88,.80),4.0)
area('Fill · cool bounce',(3,-2.8,3.2),210,(.81,.87,1),3)
area('Hair rim · broad strip',(1.8,1.4,4.6),480,(1,.83,.72),2.8)
area('Eye catchlight',(-.8,-4.0,3.6),35,(1,1,1),1.4)
da=bpy.data.cameras.new('Portrait camera');cam=bpy.data.objects.new('Portrait camera',da);STAGE.objects.link(cam);scene.camera=cam
cam.location=(0,-8.3,2.35);target=Vector((0,-.02,2.015));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();da.type='ORTHO';da.ortho_scale=3.98;da.lens=80
scene.render.filepath=str(OUT/f'gpt6_astra_pro_mcp_blender_rgirl_r{REV:02d}_front.png')
scene['authorship']='GPT-6 Astra Pro · MCP Colabdev · Blender 4.2 EEVEE'
scene['asset_provenance']='All character meshes, curves and material definitions are original code. No imported character assets or image textures.'
scene['reference_usage']='Visual comparison only; reference pixels are never processed by this builder.'
scene['revision']=REV
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'gpt6_astra_pro_mcp_blender_rgirl_top_half.blend'),compress=True)
print('BUILD_READY',len(bpy.data.objects),flush=True)
bpy.ops.render.render(write_still=True)
print('RENDER_COMPLETE',scene.render.filepath,flush=True)
