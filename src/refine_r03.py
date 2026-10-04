from pathlib import Path
p=Path('src/build_character.py');s=p.read_text()
# Merge eyelids into the actual facial differential, avoiding oval sticker boundaries.
s=s.replace('x=ix*(1-smooth)+ox*smooth; z=iz*(1-smooth)+oz*smooth','x=ix*(1-t)+ox*t; z=iz*(1-t)+oz*t')
s=s.replace('y=iy*(1-smooth)+(front(ox,oz)-.001)*smooth-.010*sin(pi*t)','y=front(x,z)+(iy-front(ix,iz))*(1-t)**2-.004*sin(pi*t)*(1-t)-.0005')
s=s.replace("curve('Waterline '+str(s),[inner+[inner[0]]],water,.0026,True)","curve('Waterline '+str(s),[inner[steps//2:]+[inner[0]]],water,.0018,True)\n    curve('Upper lash root '+str(s),[inner[:steps//2+1]],browmat,.0019,True)")
# Radial iris faces and limbus stop at the actual palpebral aperture.
s=s.replace("iris_mats=[]",'''def inside_eye(dx,dz,side):
    u=dx/.166
    if abs(u)>1:return False
    f=max(0,1-u*u)**.41;d=dz-side*.07*dx
    return -.0448*f<=d<=.0668*f
iris_mats=[]''')
s=s.replace("ob=mesh('Iris · radial brown fibers '+str(s),v,[tuple(reversed(q)) for q in f],iris_mats[0],head=True)","f=[q for q in f if inside_eye(sum(v[k][0]-cx for k in q)/4,sum(v[k][2]-EZ for k in q)/4,s)]\n    ob=mesh('Iris · radial brown fibers '+str(s),v,[tuple(reversed(q)) for q in f],iris_mats[0],head=True)")
s=s.replace("curve('Limbal edge '+str(s),[rings],limbal,.002,True)",'''parts=[];piece=[]
    for q in rings:
        if inside_eye(q[0]-cx,q[2]-EZ,s):piece.append(q)
        elif piece:
            if len(piece)>1:parts.append(piece)
            piece=[]
    if len(piece)>1:parts.append(piece)
    if parts:curve('Limbal edge '+str(s),parts,limbal,.0015,True)''')
s=s.replace("for s in [-1,1]:\n    cx=s*EX", "for m in iris_mats+[pupil]:\n    pn=m.node_tree.nodes.get('Principled BSDF');pn.inputs['Coat Weight'].default_value=.9;pn.inputs['Coat Roughness'].default_value=.055;pn.inputs['Specular IOR Level'].default_value=.5\nfor s in [-1,1]:\n    cx=s*EX")
# Soft brow pigment plus separately modeled hairs.
s=s.replace('    brows=[]\n    for j in range(180):', '''    bv=[];bf=[];bc=[];nx=55;ny=9
    for i in range(nx):
        t=i/(nx-1);x=s*(.105+.340*t);zc=3.047+.033*sin(pi*t*.95)-.028*t;hw=.019*max(.001,sin(pi*t))**.35
        for j in range(ny):
            u=-1+2*j/(ny-1);z=zc+hw*u;bv.append((x,front(x,z)-.002,z))
            strength=.74*(1-abs(u))**.65*max(.001,sin(pi*t))**.25
            sk=complexion(x,z);dark=(.078,.036,.020)
            bc.extend([sk[k]*(1-strength)+dark[k]*strength for k in range(3)]+[1])
    for i in range(nx-1):
        for j in range(ny-1):bf.append((i*ny+j,(i+1)*ny+j,(i+1)*ny+j+1,i*ny+j+1))
    bo=mesh('Brow · softly graduated natural body '+str(s),bv,bf,skin,head=True)
    ca=bo.data.color_attributes.new(name='Complexion',type='FLOAT_COLOR',domain='POINT');ca.data.foreach_set('color',bc)
    brows=[]
    for j in range(240):''')
s=s.replace('x=s*(.105+.381*t); z=3.035+.046*sin(pi*t*.9)-.041*t+random.uniform(-.012,.012)','x=s*(.105+.340*t); z=3.041+.033*sin(pi*t*.95)-.028*t+random.uniform(-.010,.010)')
s=s.replace('le=.023+.019*(1-t)','le=.019+.012*(1-t)')
s=s.replace(".00105,True,res=0)",".00110,True,res=0)")
# Subtle facial anatomy, not a perfectly smooth mannequin ellipsoid.
s=s.replace('y-=.025*exp(-((abs(x)-.34)/.19)**2-((z-2.62)/.18)**2)','y-=.038*exp(-((abs(x)-.34)/.18)**2-((z-2.63)/.16)**2)\n    y-=.013*exp(-((abs(x)-.27)/.20)**2-((z-3.045)/.067)**2)\n    y+=.013*exp(-((abs(x)-.49)/.10)**2-((z-2.99)/.20)**2)\n    y+=.006*exp(-(x/.014)**2-((z-2.407)/.066)**2)\n    y+=.010*exp(-(x/.12)**2-((z-2.192)/.035)**2)')
# Lip color and tangent blend at the outer vermilion boundary.
s=s.replace("A=.178", "la=lip.node_tree.nodes.new('ShaderNodeVertexColor');la.layer_name='Complexion';lip.node_tree.links.new(la.outputs['Color'],lip.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])\nA=.178")
s=s.replace("sin(pi*t)**.8*amp", "sin(pi*t)**1.8*amp")
s=s.replace("y=front(x,z)-bulge-.010*(1-t)*amp-.001", "y=front(x,z)-bulge-.010*(1-t)**2*amp-.001")
s=s.replace("mesh(('Upper' if upper else 'Lower')+' lip · sculpted vermilion',v,f,lip,head=True,sub=1)",'''lob=mesh(('Upper' if upper else 'Lower')+' lip · sculpted vermilion',v,f if upper else [tuple(reversed(q)) for q in f],lip,head=True,sub=1)
    lc=[]
    for i,(x,y,z) in enumerate(v):
        t=(i//cols)/(rows-1);blend=.85*(1-t**3);sk=complexion(x,z);rose=(.54,.215,.215)
        lc.extend([sk[k]*(1-blend)+rose[k]*blend for k in range(3)]+[1])
    ca=lob.data.color_attributes.new(name='Complexion',type='FLOAT_COLOR',domain='POINT');ca.data.foreach_set('color',lc)''')
# Prevent the front shirt loft from doubling back and hiding its own V opening.
s=s.replace('.445*max(c,0)*(1-abs(sin(a)))*max(0,(t-.84)/.16)**1.2','.445*max(c,0)*(1-abs(sin(a)))*t**3')
s=s.replace('lo,hi=0,.81','lo,hi=0,1.0')
s=s.replace("zz=interp(t,[(0,.035),(.3,.53),(.63,1.09),(.81,1.46),(.89,1.56),(1,1.74)])", "zz=interp(t,[(0,.035),(.3,.53),(.63,1.09),(.81,1.46),(.89,1.56),(1,1.74)])-.445*t**3")
# Raise the hairline, soften scalp sheen, and add a dense surface-following front groom.
s=s.replace('zend=3.26-.61*(1-c)/2','zend=3.39-.74*(1-c)/2')
s=s.replace("mesh('Hair · original fitted scalp shell',vs,fs,hairm[1],head=True,sub=1)",'''capmat=hairm[0].copy();capmat.name='Hair scalp · matte fiber foundation'
cp=capmat.node_tree.nodes.get('Principled BSDF');cp.inputs['Roughness'].default_value=.64;cp.inputs['Coat Weight'].default_value=0
nn=capmat.node_tree.nodes.new('ShaderNodeTexNoise');nn.inputs['Scale'].default_value=290;nn.inputs['Detail'].default_value=2
bb=capmat.node_tree.nodes.new('ShaderNodeBump');bb.inputs['Strength'].default_value=.28;bb.inputs['Distance'].default_value=.007
capmat.node_tree.links.new(nn.outputs['Fac'],bb.inputs['Height']);capmat.node_tree.links.new(bb.outputs['Normal'],cp.inputs['Normal'])
mesh('Hair · original fitted scalp shell',vs,fs,capmat,head=True,sub=1)
frontfibers=[[] for _ in range(8)];frontlod=[[] for _ in range(8)]
for k in range(1500):
    side=-1 if k<970 else 1;u=random.random();theta=side*(.035+1.55*u)
    zend=3.39-.74*(1-cos(theta))/2+random.uniform(-.025,.01)
    we=interp(zend-.05,W)+.034;xe=we*sin(theta)
    xr=.11+random.uniform(-.016,.018);zr=3.784+random.uniform(-.006,.011)
    path=[]
    for j in range(55):
        t=j/54;z=zr-(zr-zend)*sin(t*pi/2)**.86
        x=xr+(xe-xr)*sin(t*pi/2)**1.12
        w=interp(z-.05,W)+.034;c=sqrt(max(0,1-(x/w)**2))
        y=.035-(interp(z-.05,D)+.048)*c**.67-.008-random.random()*.001
        path.append((x,y,z,(.35+.65*sin(pi*t)**.3)*(1-.75*t**12)))
    frontfibers[k%8].append(path)
    if k%8==0:frontlod[k%8].append(path[::2]+[path[-1]])
for k in range(8):
    curve('Crown swept fibers · render '+str(k),frontfibers[k],hairm[k],.0009,True,FINE,0)
    if frontlod[k]:curve('Crown swept fibers · web '+str(k),frontlod[k],hairm[k],.00115,True,CHAR,0)''')
# More substantial chest cascades, with heterogeneous end lengths and broad waves.
s=s.replace('for k in range(17):\n        u=k/16;', 'for k in range(36):\n        u=k/35;')
s=s.replace("(side*(.54+.15*u),-.39,1.95),(side*(.58+.20*u),-.59,1.30),(side*(.60+.23*u),-.64,.72),(side*(.46+.18*u),-.53,.27+.21*u)","(side*(.54+.26*u),-.42,1.95),(side*(.53+.44*u),-.59-.055*u,1.30),(side*(.59+.42*u),-.64-.04*u,.77),(side*(.43+.35*u),-.55,.27+.34*u)")
s=s.replace("c=(.020+i*.0040,.010+i*.00225,.008+i*.00165)","c=(.014+i*.0035,.007+i*.0018,.0055+i*.0014)")
s=s.replace("c,.36+(i%3)*.035", "c,.43+(i%3)*.035")
s=s.replace("p.inputs['Coat Weight'].default_value=.12", "p.inputs['Coat Weight'].default_value=.05")
s=s.replace("480,(1,.83,.72),2.8", "300,(1,.83,.72),3.0")
s=s.replace("scene.view_settings.exposure=.30", "scene.view_settings.exposure=.22")
p.write_text(s)
