from pathlib import Path
p=Path('src/build_character.py');s=p.read_text()
start=s.index('def interp(z,ps):');end=s.index('\nW=[',start)
s=s[:start]+'''def interp(z,ps):
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
''' +s[end:]
s=s.replace('scene.eevee.taa_render_samples=32','scene.eevee.taa_render_samples=48')
s=s.replace("hole=((abs(x)-.285)/.198)**2+((z-2.875)/.094)**2<1", "hole=((abs(x)-.270)/.184)**2+((z-2.875)/.082)**2<1")
s=s.replace('EYEY=-.320; EZ=2.875; EX=.285','EYEY=-.305; EZ=2.875; EX=.270')
s=s.replace("uv('Eyeball '+str(s),(cx,EYEY,EZ),(.195,.17,.172),sclera,True,64,40)",'''# Only the anatomically exposed corneal surface is outside the lids.
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
    mesh('Eye · anatomically masked sclera '+str(s),ev,ef,sclera,head=True)''')
s=s.replace('rad=.030+(.079-.030)*r/(nr-1)','rad=.027+(.069-.027)*r/(nr-1)')
s=s.replace("v,f,iris_mats[0],head=True)","v,[tuple(reversed(q)) for q in f],iris_mats[0],head=True)")
s=s.replace('dx=.0315*cos(a); dz=.0315*sin(a)','dx=.028*cos(a); dz=.028*sin(a)')
s=s.replace('dx=.079*cos(a); dz=.079*sin(a)','dx=.069*cos(a); dz=.069*sin(a)')
s=s.replace('dx=.18*cos(a); dz=.076*max(0,sin(a))**.82-.052*max(0,-sin(a))**.82+s*.07*dx','dx=.166*cos(a); dz=.067*max(0,sin(a))**.82-.045*max(0,-sin(a))**.82+s*.07*dx')
s=s.replace('ox=cx+.240*cos(a); oz=EZ+.153*sin(a)+s*.06*.24*cos(a)','ox=cx+.223*cos(a); oz=EZ+.136*sin(a)+s*.06*.223*cos(a)')
s=s.replace("v,f,skin,head=True,sub=1,skincolor=True)\n    curve('Waterline", "v,[tuple(reversed(q)) for q in f],skin,head=True,sub=1,skincolor=True)\n    curve('Waterline")
s=s.replace('dx=.179*cos(a); dz=.103*sin(a)**.82','dx=.165*cos(a); dz=.097*sin(a)**.82')
s=s.replace('dx=.179*cos(a); dz=.076*sin(a)**.82','dx=.165*cos(a); dz=.067*sin(a)**.82')
s=s.replace('dx=.177*cos(a); dz=-.052*(-sin(a))**.82','dx=.164*cos(a); dz=-.045*(-sin(a))**.82')
s=s.replace(".010+.018*f),.25))", ".010+.018*f),.20))")
s=s.replace('# Lips, cupid bow and closed mouth line.','# Lips, cupid bow and closed mouth line.\nlip.node_tree.nodes.get(\'Principled BSDF\').inputs[\'Coat Weight\'].default_value=.22')
s=s.replace('A=.185','A=.178').replace('top=seam+.044*amp**.70','top=seam+.038*amp**.70').replace('bottom=seam-.056*amp**.72','bottom=seam-.050*amp**.72')
# Curvature-matched cap, always outside the actual cranium, removes z-fighting.
a=s.index('        th=2*pi*j/ns; c=cos(th); maxph=1.38')
b=s.index('\n        vs.append((x,y,z))',a)
s=s[:a]+'''        th=2*pi*j/ns;c=cos(th)
        zend=3.26-.61*(1-c)/2
        z=3.813-t*(3.813-zend);zz=z-.05
        taper=min(1,max(0,(3.813-z)/.045))**.45
        w=(interp(zz,W)+.034)*taper
        x=w*sin(th)
        y=.035-(interp(zz,D)+.048)*max(c,0)**.67 if c>=0 else .035+(interp(zz,B)+.042)*(-c)**.85
        if t<.016:y=.035+(y-.035)*t/.016
''' +s[b:]
# Ear-side tuck and flowing, non-parallel lower guide curves.
s=s.replace("th=.90+(2*pi-1.8)*j/(cols-1); wave=", "leftgap=.90+.68*exp(-((z-2.74)/.32)**2); th=.90+(2*pi-.90-leftgap)*j/(cols-1); wave=")
s=s.replace("locks.append((catmull(ps,88),side,u))", "\n        if side<0:\n            ps[3]=(ps[3][0],max(.095,ps[3][1]),ps[3][2]);ps[4]=(ps[4][0],max(.02,ps[4][1]),ps[4][2])\n        locks.append((catmull(ps,105),side,u))")
s=s.replace("locks.append((catmull(ps,90),side,u))", "\n        if side<0:\n            ps[2]=(ps[2][0],.04,ps[2][2]);ps[3]=(ps[3][0],.075,ps[3][2])\n        locks.append((catmull(ps,105),side,u))")
s=s.replace("for k,(ps,side,u) in enumerate(locks):\n    width=", "for k,(ps,side,u) in enumerate(locks):\n    for i,pt in enumerate(ps):\n        t=i/(len(ps)-1);f=max(0,(t-.43)/.57)**1.3\n        pt.x+=side*f*(.043*sin(12*t+u*4)+.027*sin(18*t+u*2))\n        pt.y+=f*.025*sin(13*t+u*4)\n    width=")
s=s.replace("lambda t:.022*(.25+.75*sin(pi*t)**.5)*(1-t**5),lambda t:.0045", "lambda t:.012*(.25+.75*sin(pi*t)**.5)*(1-t**5),lambda t:.0028")
# A true V opening and smooth shoulder caps.
s=s.replace('.445*max(c,0)**8*max(0,(t-.84)/.16)**1.2','.445*max(c,0)*(1-abs(sin(a)))*max(0,(t-.84)/.16)**1.2')
s=s.replace('lambda t:.245-.032*t+.010*sin(12*pi*t),lambda t:.273-.045*t','lambda t:(.245-.032*t+.004*sin(12*pi*t))*min(1,t/.105)**.5,lambda t:(.273-.045*t)*min(1,t/.105)**.5')
# Tessellated quadratic collar preserves the pointed silhouette instead of shrinking into a teardrop.
a=s.index('    vs=[p for row in rows for p in row]; fs=[]');b=s.index("    so=ob.modifiers.new('Collar turned edge'",a)
s=s[:a]+'''    def bez3(q,t):return Vector(q[0])*(1-t)**2+Vector(q[1])*2*t*(1-t)+Vector(q[2])*t*t
    vs=[];fs=[];res=20
    for i in range(res):
        vv=i/(res-1)
        for j in range(res):
            uu=j/(res-1);q=[bez3(row,uu) for row in rows];vs.append(tuple(bez3(q,vv)))
    for i in range(res-1):
        for j in range(res-1):fs.append((i*res+j,i*res+j+1,(i+1)*res+j+1,(i+1)*res+j))
    ob=mesh('Collar · crisp folded point '+str(s),vs,fs,shirt)
''' +s[b:]
a=s.index('def shirtfront(z):');b=s.index('\nv=[]; f=[]; rows=60',a)
s=s[:a]+'''def shirtfront(z):
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
''' +s[b:]
s=s.replace("da.ortho_scale=4.10", "da.ortho_scale=3.98").replace("target=Vector((0,-.02,1.94))", "target=Vector((0,-.02,2.015))")
p.write_text(s)
