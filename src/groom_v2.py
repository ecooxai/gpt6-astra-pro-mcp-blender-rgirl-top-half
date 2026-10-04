"""Original strand groom v2. Executed in the procedural builder's namespace.
No image, external mesh, hair card, or downloaded material is used.
Separated crown, tucked temple, shoulder cascades, rear volume and flyaways.
"""
# Simple fiber shaders avoid nonexistent UV tangents on curve primitives.
fiber_mats=[]
for k in range(8):
    f=k/7
    m=material('Hair fibers · natural chestnut %02d'%k,(.014+.012*f,.0075+.006*f,.0065+.005*f),.34+.055*(k%3)/2)
    pn=m.node_tree.nodes.get('Principled BSDF')
    pn.inputs['Specular IOR Level'].default_value=.37
    pn.inputs['Coat Weight'].default_value=.025
    fiber_mats.append(m)
# A scalp-following, closed foundation. Fine strands soften its hairline.
vs=[];fs=[];rows=48;ns=160
for i in range(rows):
    t=i/(rows-1)
    for j in range(ns):
        th=2*pi*j/ns;c=cos(th)
        zend=3.405-.79*(1-c)/2+.017*sin(5*th)
        z=3.807-t*(3.807-zend);zz=z-.04
        taper=min(1,max(0,(3.807-z)/.035))**.48
        w=(interp(zz,W)+.038)*taper
        x=w*sin(th)
        y=.035-(interp(zz,D)+.052)*max(c,0)**.67 if c>=0 else .035+(interp(zz,B)+.060)*(-c)**.85
        if t<.012:y=.035+(y-.035)*t/.012
        vs.append((x,y,z))
for i in range(rows-1):
    for j in range(ns):fs.append((i*ns+j,(i+1)*ns+j,(i+1)*ns+(j+1)%ns,i*ns+(j+1)%ns))
cap=mesh('Hair · scalp-following foundation v2',vs,fs,fiber_mats[0],head=True,sub=1)
# Swept fibers radiate from a modest off-center part. These are curves, not texture pixels.
crown=[[] for _ in range(8)]; crown_web=[[] for _ in range(8)]
for k in range(2350):
    side=-1 if k<1490 else 1;u=random.random();theta=side*(.035+1.56*u)
    zend=3.405-.79*(1-cos(theta))/2+random.uniform(-.033,.006)
    xe=(interp(zend-.04,W)+.038)*sin(theta)
    xr=.095+random.uniform(-.012,.012);zr=3.77+random.uniform(-.009,.008)
    path=[];phase=random.random()*6.28
    for j in range(62):
        t=j/61;sn=sin(t*pi/2)
        z=zr-(zr-zend)*sn**1.02;x=xr+(xe-xr)*sn**.87
        w=interp(z-.04,W)+.038;c=sqrt(max(.008,1-(x/w)**2))
        y=.035-(interp(z-.04,D)+.055)*c**.67-.008
        path.append((x+.0008*sin(phase+t*19),y-.001*sin(phase+t*11),z,(.25+.65*sin(pi*t)**.32)*(1-.90*t**11)))
    crown[k%8].append(path)
    if k%10==0:crown_web[k%8].append(path[::2]+[path[-1]])
for k in range(8):
    curve('Hair crown · dense swept fibers %d'%k,crown[k],fiber_mats[k],.00078,True,FINE,0)
    if crown_web[k]:curve('Hair crown · web fibers %d'%k,crown_web[k],fiber_mats[k],.00092,True,CHAR,0)
# Full rear curtain follows the back of the head and stays outside the blouse.
def rear_shape(t,th):
    z=3.27-2.95*t
    w=interp(t,[(0,.579),(.18,.624),(.42,.678),(.70,.80),(.89,.80),(1,.65)])
    dep=interp(t,[(0,.485),(.22,.495),(.50,.53),(.8,.535),(1,.46)])
    wave=(.012*sin(th*17+t*11)+.012*sin(th*8-t*9))*sin(pi*t)**.5
    return Vector(((w+wave)*sin(th),.050-dep*cos(th),z+.075*sin(th*5)*t**6))
vs=[];fs=[];rows=72;ns=128
for i in range(rows):
    t=i/(rows-1);z=3.27-2.95*t
    leftgap=1.03+.49*exp(-((z-2.8)/.32)**2)
    for j in range(ns):
        th=1.03+(2*pi-leftgap-1.03)*j/(ns-1)
        vs.append(tuple(rear_shape(t,th)))
for i in range(rows-1):
    for j in range(ns-1):fs.append((i*ns+j,(i+1)*ns+j,(i+1)*ns+j+1,i*ns+j+1))
mesh('Hair · complete rear volume v2',vs,fs,fiber_mats[0],head=True,sub=1)
# Each guide controls both a narrow volume core and circumferential physical fibers.
guides=[]
for k in range(138):
    u=k/137;th=1.07+(2*pi-2.14)*u;rooty=-.035+.43*random.random()
    rootz=3.13+.69*sqrt(max(.1,1-(.10/.59)**2-((rooty-.035)/.54)**2))+.025
    points=[(.10+random.uniform(-.009,.009),rooty,rootz),(.46*sin(th),.04-.40*cos(th),3.61)]
    for t in [0,.17,.36,.55,.73,.87,1.0]:
        q=rear_shape(t,th)
        q.x+=.025*sin(k*.27+t*9)*t;q.y+=.018*sin(k*.31+t*8)*t
        q.z+=random.uniform(-.012,.012)*t
        points.append(tuple(q))
    guides.append((catmull(points,94),.025+random.random()*.009,.018,k))
for side in [-1,1]:
    for k in range(52):
        u=k/51;phase=random.random()*pi*2
        yy=-.21+.20*u;rz=3.13+.69*sqrt(max(.1,1-(.11/.59)**2-((yy-.035)/.54)**2))+.034
        root=(.10+random.uniform(-.018,.018),yy,rz)
        if side<0:
            points=[root,(-.28,-.27+.18*u,3.64),(-.51,.085+.05*u,3.25),(-.58-.026*u,.11,2.85),(-.565-.052*u,-.015,2.32),(-.59-.12*u,-.30,1.83),(-.69-.16*u,-.50,1.30),(-.88-.045*u,-.57,.82),(-.82+.105*u,-.585,.50),(-.57-.04*u,-.56,.28+.18*u)]
        else:
            points=[root,(.37,-.36+.10*u,3.58),(.558+.025*u,-.31,3.12),(.608+.035*u,-.24,2.60),(.614+.13*u,-.40,2.12),(.76+.18*u,-.55,1.60),(.89+.16*u,-.62,1.17),(.99+.10*u,-.63,.81),(.88+.12*u,-.63,.51),(.66+.16*u,-.55,.29+.18*u)]
        # Alternating curl phase gives softly staggered ends, never a single cut-off ribbon.
        for i in range(4,len(points)):
            x,y,z=points[i];f=(i-3)/(len(points)-4)
            x+=side*.035*sin(phase+f*5)*f;y+=.034*cos(phase+f*5)*f;z+=.07*sin(phase)*f**3
            points[i]=(x,y,z)
        if k%4==1:
            x,y,z=points[-1];points.append((x-side*.05,y+.03,z+.10))
        guides.append((catmull(points,104),.022+random.random()*.016,.016,k+200+(side+1)*100))
# Curve materials remain deliberately simple; volume cores use authored longitudinal UV shading.
fine=[[] for _ in range(8)];web=[[] for _ in range(8)]
for gi,(ps,width,depth,key) in enumerate(guides):
    phase=(key*.137)%6.28
    for i,p in enumerate(ps):
        t=i/(len(ps)-1);f=max(0,(t-.34)/.66)
        p.x+=.015*sin(t*15+phase)*f;p.y+=.019*sin(t*12+phase)*f
    def breadth(t,w=width):return w*(.43+.57*sin(pi*t)**.4)*(1-t**7)
    def thickness(t,d=depth):return d*(.40+.60*sin(pi*t)**.4)*(1-t**7)
    tube('Hair · flowing volume core %03d'%gi,ps,breadth,thickness,hairm[gi%3],True,sides=10)
    # A parallel transport approximation distributes fibers around the guide, including its rear.
    frames=[]
    for i,p in enumerate(ps):
        tangent=(ps[min(len(ps)-1,i+1)]-ps[max(0,i-1)]).normalized()
        cross=tangent.cross(Vector((0,-1,0)))
        if cross.length<.02:cross=Vector((1,0,0))
        cross.normalize();normal=cross.cross(tangent).normalized();frames.append((cross,normal))
    count=34 if gi<138 else 46
    for j in range(count):
        angle=2*pi*j/count+random.uniform(-.05,.05);end=random.uniform(.91,1.0)
        offset=1.01+random.random()*.22;shift=random.random()*6.28;path=[]
        for i,p in enumerate(ps):
            t=i/(len(ps)-1)
            if t>end:break
            cross,normal=frames[i];taper=(.4+.6*sin(pi*t)**.35)*(1-t**8)
            q=p+cross*(cos(angle)*width*offset*taper)+normal*(sin(angle)*depth*offset*taper)
            q.x+=.0015*sin(shift+t*23)*sin(pi*t);q.y+=.0013*sin(shift+t*19)*sin(pi*t)
            q.z+=.018*sin(shift)*t**8
            path.append((*q,(.32+.65*sin(pi*t)**.35)*max(0,1-(t/end)**12)))
        if len(path)>2:
            fine[(j+gi)%8].append(path)
            if j%10==0:web[(j+gi)%8].append(path[::2]+[path[-1]])
for i in range(8):
    curve('Hair · all-side fine render groom %d'%i,fine[i],fiber_mats[i],.00072,True,FINE,0)
    curve('Hair · web groom %d'%i,web[i],fiber_mats[i],.00090,True,CHAR,0)
# Sparse, staggered fringe. Only small fiber bundles, no opaque broad bang cards.
fringes=[[(.095,-.215,3.78),(-.12,-.46,3.54),(-.31,-.51,3.22),(-.43,-.475,2.91),(-.47,-.40,2.60)],[(.10,-.215,3.78),(-.015,-.49,3.49),(-.15,-.525,3.20),(-.25,-.50,2.995)],[(.125,-.225,3.78),(.11,-.495,3.48),(.055,-.535,3.20),(-.045,-.51,3.015)],[(.15,-.225,3.77),(.205,-.505,3.46),(.19,-.535,3.21),(.10,-.51,3.045)],[(.17,-.23,3.76),(.28,-.475,3.45),(.28,-.51,3.21),(.215,-.50,3.11)]]
for k,g in enumerate(fringes):
    ps=catmull(g,76);paths=[]
    for j in range(70 if k<4 else 28):
        off=random.uniform(-.027,.027)*(1 if k<4 else .40);end=random.uniform(.86,1.01);path=[]
        for i,p in enumerate(ps):
            t=i/(len(ps)-1)
            if t>end:break
            x=p.x+off*sin(t*pi/2);y=p.y-.004-.0008*sin(j*.9+t*16);z=p.z+.018*sin(j*.77)*t*t
            path.append((x,y,z,(.36+.50*sin(pi*t))*max(.005,1-(t/end)**9)))
        if len(path)>2:paths.append(path)
    curve('Hair fringe · individual wisps %d'%k,paths,fiber_mats[2+k%4],.00086,True,CHAR,0)
# Flyaways remain understated, with tapering actual geometry.
paths=[]
for k in range(140):
    ps,width,depth,key=random.choice(guides);phase=random.random()*6.28;path=[]
    for i in range(0,len(ps),2):
        p=ps[i];t=i/(len(ps)-1);side=-1 if p.x<0 else 1
        path.append((p.x+side*(.012+.024*sin(pi*t))*sin(pi*t)**.4,p.y-.021+.018*sin(phase+t*7),p.z+.013*sin(phase+t*8),(.15+.6*sin(pi*t)**.5)*(1-t**8)))
    paths.append(path)
curve('Hair · separated airy flyaways',paths,fiber_mats[5],.00055,True,FINE,0)
print('GROOM_V2_READY',len(guides),sum(len(p) for p in fine),flush=True)
