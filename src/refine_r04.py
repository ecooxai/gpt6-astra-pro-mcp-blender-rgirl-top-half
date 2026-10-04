from pathlib import Path
p=Path('src/build_character.py');s=p.read_text()
s=s.replace("rig.rotation_euler[1]=math.radians(7)","rig.rotation_euler[1]=math.radians(7);rig.rotation_euler[2]=math.radians(-2.5)")
s=s.replace("(.84,.78,.70),.20)","(.70,.66,.60),.17)")
s=s.replace(".027+(.069-.027)",".026+(.076-.026)").replace("dx=.028*cos(a); dz=.028*sin(a)","dx=.026*cos(a); dz=.026*sin(a)").replace("dx=.069*cos(a); dz=.069*sin(a)","dx=.076*cos(a); dz=.076*sin(a)")
s=s.replace("y-=.013*exp(-((abs(x)-.27)/.20)**2-((z-3.045)/.067)**2)","y-=.024*exp(-((abs(x)-.27)/.20)**2-((z-3.045)/.080)**2)\n    y-=.016*exp(-((abs(x)-.29)/.185)**2-((z-2.765)/.074)**2)\n    y-=.014*exp(-(x/.145)**2-((z-2.142)/.07)**2)")
s=s.replace(".126*exp(-(x/.066)**2", ".112*exp(-(x/.080)**2")
s=s.replace(".207*exp(-(x/.086)**2", ".176*exp(-(x/.093)**2")
s=s.replace("y-=.082*exp(-((abs(x)-.079)/.039)**2-((z-2.531)/.046)**2)","y-=.070*exp(-((abs(x)-.083)/.041)**2-((z-2.533)/.044)**2)\n    y-=.025*exp(-(x/.026)**2-((z-2.512)/.031)**2)")
s=s.replace("(.024,.006,.0105),nostril", "(.019,.0045,.008),nostril")
s=s.replace("skinplain,.014,True)","skinplain,.0095,True)")
s=s.replace("skinplain,.012,True)","skinplain,.009,True)")
s=s.replace("2.281+.006*u*u", "2.281-.004*u*u")
s=s.replace("bottom=seam-.050*amp**.72", "bottom=seam-.055*amp**.72")
s=s.replace("y=front(x,z)-bulge-.010*(1-t)**2*amp-.001", "y=front(x,z)-bulge-.010*(1-t)**2*amp-.001+.00065*sin(540*x+3*sin(180*x))*sin(pi*t)*amp")
# A single continuous neck-to-upper-chest surface removes the exposed intersection ridge.
a=s.index('# Neck loft and concealed upper chest.');b=s.index('# Subtle paired clavicles',a)
s=s[:a]+'''# Continuous neck and upper chest; no intersecting ellipsoid at the neckline.
vs=[];fs=[];N=80;R=72
for i in range(R):
    z=.93+(2.23-.93)*i/(R-1)
    rx=interp(z,[(.93,.73),(1.12,.61),(1.28,.45),(1.42,.32),(1.65,.253),(1.91,.216),(2.23,.223)])
    ry=interp(z,[(.93,.32),(1.12,.29),(1.28,.255),(1.45,.219),(1.70,.193),(2.0,.184),(2.23,.181)])
    cy=.055+.03*max(0,(z-1.6)/.63)
    for j in range(N):
        a=2*pi*j/N;x=rx*sin(a);y=cy-ry*cos(a)
        if cos(a)>0:
            y-=.011*exp(-((abs(x)-.115)/.055)**2-((z-1.66)/.27)**2)
            y+=.012*exp(-(x/.074)**2-((z-1.36)/.11)**2)
        vs.append((x,y,z))
for i in range(R-1):
    for j in range(N):fs.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
mesh('Neck and upper chest · continuous anatomy',vs,fs,skinplain,sub=1)
''' +s[b:]
# Original tailoring displacement, reused for the center placket.
s=s.replace("folds=.012*sin(32*x+5*z)*exp(-((z-.55)/.60)**2)+.012*sin(16*z+12*abs(x))*abs(x)","folds=.009*sin(32*x+5*z)*exp(-((z-.55)/.60)**2)+.012*sin(16*z+12*abs(x))*abs(x)\n            folds+=.047*exp(-((abs(x)-.34)/.24)**2-((z-.88)/.36)**2)\n            folds+=.018*sin(21*(z-.62)+9*abs(x))*exp(-(x/.44)**2-((z-.62)/.36)**2)\n            folds+=.012*sin(38*(z-.98)-18*abs(x))*exp(-(x/.25)**2-((z-.98)/.12)**2)")
s=s.replace("folds=.012*sin(5*z)*exp(-((z-.55)/.60)**2)","folds=.009*sin(5*z)*exp(-((z-.55)/.60)**2)\n    folds+=.047*exp(-(.34/.24)**2-((z-.88)/.36)**2)\n    folds+=.018*sin(21*(z-.62))*exp(-((z-.62)/.36)**2)\n    folds+=.012*sin(38*(z-.98))*exp(-((z-.98)/.12)**2)")
s=s.replace("(s*.285,-.463,1.16)","(s*.285,-.400,1.16)")
# Graduated lock width and a rounded cross-section create depth instead of flat panels.
s=s.replace("width=.032+random.random()*.023", "width=.026+random.random()*.027")
s=s.replace("w*(.22+.78*sin(pi*min(t,.999))**.40)*(1-t**12)", "w*(.30+.70*sin(pi*min(t,.999))**.45)*(1-t**5)")
s=s.replace("lambda t:.014*(.25+.75*sin(pi*t)**.45)*(1-t**12)", "lambda t:.024*(.25+.75*sin(pi*t)**.45)*(1-t**5)")
needle="    width=.026+random.random()*.027"
s=s.replace(needle,'''    # Guide-specific motion is shared by its tube and every associated filament.
    phase=1.4+u*5.8+(k%7)*.15
    for i,pt in enumerate(ps):
        t=i/(len(ps)-1);flow=max(0,(t-.36)/.64)
        pt.x+=side*.041*sin(flow*2.3*pi+phase)*flow**1.1
        pt.y+=.060*sin(flow*1.9*pi+phase)*flow**1.1
        if k>=92:
            pt.y-=.04*sin(u*pi)*flow
            pt.z+=.065*sin(phase)*flow**5
    width=.026+random.random()*.027''')
s=s.replace("d=random.uniform(-.009,.010)", "d=random.uniform(-.009,.009)")
s=s.replace("dy=-.017+d+.0018", "dy=-.028+d+.0018")
# More individual forehead wisps; retain the deliberate asymmetric sweep.
idx=s.index('# A few airy flyaways')
s=s[:idx]+'''# Individually separated short hairs soften the fringe boundary and side part.
wisps=[]
for k in range(85):
    g=fringes[k%4];ps=catmull(g,58);off=random.uniform(-.027,.030);end=random.uniform(.84,1.02)
    path=[]
    for i,p in enumerate(ps):
        t=i/(len(ps)-1)
        if t>end:break
        path.append((p.x+off*sin(t*pi/2),p.y-.010-.003*sin(t*pi),p.z+.018*sin(k*.65)*t*t,(.35+.5*sin(pi*t))*(1-(t/end)**6)))
    if len(path)>2:wisps.append(path)
curve('Fringe · separated fine baby hairs',wisps,hairm[3],.00065,True,CHAR,0)

''' +s[idx:]
s=s.replace("default_value=.32\nback=", "default_value=.18\nback=")
s=s.replace("520,(1.0,.88,.80),4.0", "610,(1.0,.88,.82),3.8")
s=s.replace("210,(.81,.87,1),3", "90,(.81,.87,1),3.3")
s=s.replace("da.ortho_scale=3.98", "da.ortho_scale=3.83").replace("target=Vector((0,-.02,2.015))", "target=Vector((0,-.02,2.075))")
s=s.replace("scene.eevee.taa_render_samples=12", "scene.eevee.taa_render_samples=16")
p.write_text(s)
