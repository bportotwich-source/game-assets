import numpy as np, trimesh, json, os, math
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals
OUT = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(OUT+'/pieces', exist_ok=True)

COL = {
 'brick':(176,78,56),'trim':(226,212,184),'stone':(204,195,178),'glass':(160,196,214),
 'frame':(236,228,208),'iron':(46,40,38),'roof':(140,137,132),'door':(74,108,140),
 'wood':(184,110,62),'tower_roof':(76,82,96),'metal':(230,230,226),'leaf':(150,196,92),
 'trunk':(214,204,186),'pave':(224,214,194),'mat':(196,140,96),'grass':(110,170,90),
 'dark':(70,70,72),'light':(255,226,150),'plaster':(240,232,216),'floor':(196,150,104),'player':(90,140,220),'sofa':(96,124,156),'bedding':(246,242,232),'blanket':(204,124,92),'wood_light':(206,172,126),'ceramic':(250,250,247),'counter':(88,88,94),'rug':(176,96,84),'tile':(214,224,228),'plant':(108,160,90),'pot':(190,110,80),'screen':(40,44,52),
}
from PIL import Image, ImageDraw
import random
def brick_texture(px=512,rows=8,per=4,seed=7):
    # 1 m x 1 m tile: 8 courses of 0.125 m, bricks 0.25 m, running bond. Stylised toon palette.
    rnd=random.Random(seed); im=Image.new('RGB',(px,px),(214,196,170)); d=ImageDraw.Draw(im)
    rh=px/rows; bw=px/per; m=max(2,int(px*0.012))
    base=[(178,80,58),(168,72,52),(186,88,64),(160,68,50),(192,96,70)]
    for r in range(rows):
        off=(bw/2) if r%2 else 0
        for i in range(-1,per+1):
            x0=i*bw+off; y0=r*rh; c=rnd.choice(base)
            box=[x0+m/2,y0+m/2,x0+bw-m/2,y0+rh-m/2]
            for dx in (-px,0,px):
                d.rectangle([box[0]+dx,box[1],box[2]+dx,box[3]],fill=c)
                d.rectangle([box[0]+dx,box[1],box[2]+dx,box[1]+max(1,m*0.8)],fill=tuple(min(255,v+14) for v in c))
    return im.transpose(Image.FLIP_TOP_BOTTOM)
BRICK_TEX=brick_texture()
def _noise(px,cells,seed):
    # seamless value noise: random grid tiled 3x3, smooth-upscaled, centre crop
    r=np.random.RandomState(seed).rand(cells,cells); t=np.tile(r,(3,3))
    im=Image.fromarray((t*255).astype(np.uint8)).resize((px*3,px*3),Image.BICUBIC)
    return np.asarray(im,dtype=np.float32)[px:2*px,px:2*px]/255.0-0.5
def stone_texture(px=256,seed=3):
    # tile = 1.0 m wide x 0.8 m tall: two 0.4 m courses of 1.0 m ashlar blocks, running bond
    rnd=random.Random(seed); h=int(px*0.8); im=Image.new('RGB',(px,h),(168,158,142)); d=ImageDraw.Draw(im)
    base=[(206,197,180),(198,189,172),(212,204,188),(202,192,174)]; m=max(3,int(px*0.014))
    for r in range(2):
        off=px/2 if r%2 else 0; y0=r*h/2
        for i in range(-1,2):
            c=rnd.choice(base); x0=i*px+off
            for dx in (-px,0,px):
                d.rectangle([x0+dx+m/2,y0+m/2,x0+dx+px-m/2,y0+h/2-m/2],fill=c)
                d.rectangle([x0+dx+m/2,y0+m/2,x0+dx+px-m/2,y0+m/2+m*0.7],fill=tuple(min(255,v+12) for v in c))
    a=np.asarray(im,dtype=np.float32); n=_noise(px,12,seed)[:h,:]+0.5*_noise(px,40,seed+1)[:h,:]
    a=np.clip(a+n[...,None]*22,0,255).astype(np.uint8)
    return Image.fromarray(a).transpose(Image.FLIP_TOP_BOTTOM)
def plaster_texture(px=256,seed=5):
    # tile = 1 m: smooth stucco, soft blotches + fine grain, seamless
    n=_noise(px,5,seed)*0.5+_noise(px,32,seed+1)*0.5+_noise(px,128,seed+2)*0.9
    base=np.array([238,230,214],np.float32); a=base[None,None,:]+n[...,None]*16
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
STONE_TEX=stone_texture()
PLASTER_TEX=plaster_texture(); PLASTER_TEX.save(os.path.join(OUT,'plaster_texture.png'))
TEX={'brick':(BRICK_TEX,1.0,1.0),'stone':(STONE_TEX,1.0,0.8),'plaster':(PLASTER_TEX,1.0,1.0)}  # material: (image, tile width m, tile height m)
MATS = {k:PBRMaterial(name=k, baseColorFactor=[c/255 for c in v]+[1.0], metallicFactor=0.0, roughnessFactor=0.9) for k,v in COL.items()}
for k,(im,_,_) in TEX.items(): MATS[k]=PBRMaterial(name=k,baseColorTexture=im,baseColorFactor=[255,255,255,255],metallicFactor=0.0,roughnessFactor=0.9)

class Piece:
    def __init__(s): s.parts={}
    def add(s,mat,m): s.parts.setdefault(mat,[]).append(m); return s
    def box(s,mat,x0,x1,y0,y1,z0,z1):
        b=trimesh.creation.box(extents=[x1-x0,y1-y0,z1-z0]); b.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]); return s.add(mat,b)
    def cyl(s,mat,r,y0,y1,x=0,z=0,sec=16):
        c=trimesh.creation.cylinder(radius=r,height=y1-y0,sections=sec); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0])); c.apply_translation([x,(y0+y1)/2,z]); return s.add(mat,c)
    def cone(s,mat,r,y0,y1,x=0,z=0,sec=16):
        c=trimesh.creation.cone(radius=r,height=y1-y0,sections=sec); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0])); c.apply_translation([x,y0,z]); return s.add(mat,c)
    def sphere(s,mat,r,x,y,z):
        c=trimesh.creation.icosphere(subdivisions=1,radius=r); c.apply_translation([x,y,z]); return s.add(mat,c)
    def seg(s,mat,p0,p1,w):
        p0,p1=np.array(p0,float),np.array(p1,float); d=p1-p0; L=np.linalg.norm(d)
        b=trimesh.creation.box(extents=[w,w,L]); z=np.array([0,0,1.0]); v=d/L
        ax=np.cross(z,v); ang=math.acos(np.clip(np.dot(z,v),-1,1))
        if np.linalg.norm(ax)>1e-6: b.apply_transform(trimesh.transformations.rotation_matrix(ang,ax))
        b.apply_translation((p0+p1)/2); return s.add(mat,b)
    def merge(s,other,T=np.eye(4)):
        for k,ms in other.parts.items():
            for m in ms: mm=m.copy(); mm.apply_transform(T); s.add(k,mm)
        return s
    def scene(s,name):
        sc=trimesh.Scene()
        for k,ms in s.parts.items():
            m=trimesh.util.concatenate(ms); m.unmerge_vertices()
            if k in TEX:
                v=m.vertices; n=m.vertex_normals; uv=np.zeros((len(v),2))
                ax=np.argmax(np.abs(n),axis=1)
                uv[ax==0]=v[ax==0][:,[2,1]]; uv[ax==2]=v[ax==2][:,[0,1]]; uv[ax==1]=v[ax==1][:,[0,2]]
                tw,th=TEX[k][1],TEX[k][2]; uv[:,0]/=tw; uv[ax!=1,1]/=th; uv[ax==1,1]/=tw
                if k=='sign': uv=np.stack([(v[:,0]-SIGN[0])/SIGN[2],(v[:,1]-SIGN[1])/SIGN[3]],1)
                if k=='plaster': uv[ax==1]=0.37   # plain colour on horizontal plaster (wall tops, ceilings): overlapping tops at wall junctions stay identical
                m.visual=TextureVisuals(uv=uv,material=MATS[k])
            else: m.visual=TextureVisuals(material=MATS[k])
            sc.add_geometry(m,node_name=f'{name}_{k}',geom_name=f'{name}_{k}')
        return sc

W=2.0; T=0.3; H=3.0; HG=3.2   # module width, wall thickness, floor heights

from shapely.geometry import Polygon, box as sbox
def grid_solid(xs,ys,zs,cell):
    """Watertight mesh on a rectilinear grid. cell(i,j,k) -> material or None.
    Every face is split on the same grid lines, so neighbouring faces share vertices:
    no T-junctions, no slivers, no pixel cracks."""
    out={}
    nx,ny,nz=len(xs)-1,len(ys)-1,len(zs)-1
    def get(i,j,k):
        if 0<=i<nx and 0<=j<ny and 0<=k<nz: return cell(i,j,k)
        return None
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                m=get(i,j,k)
                if m is None: continue
                x0,x1,y0,y1,z0,z1=xs[i],xs[i+1],ys[j],ys[j+1],zs[k],zs[k+1]
                quads=[]
                if get(i-1,j,k) is None: quads.append([(x0,y0,z0),(x0,y0,z1),(x0,y1,z1),(x0,y1,z0)])
                if get(i+1,j,k) is None: quads.append([(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)])
                if get(i,j-1,k) is None: quads.append([(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)])
                if get(i,j+1,k) is None: quads.append([(x0,y1,z0),(x0,y1,z1),(x1,y1,z1),(x1,y1,z0)])
                if get(i,j,k-1) is None: quads.append([(x0,y0,z0),(x0,y1,z0),(x1,y1,z0),(x1,y0,z0)])
                if get(i,j,k+1) is None: quads.append([(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
                for q in quads: out.setdefault(m,[]).append(q)
    meshes={}
    for m,qs in out.items():
        v=[];f=[]
        for q in qs:
            b=len(v); v+=q; f+=[[b,b+1,b+2],[b,b+2,b+3]]
        mm=trimesh.Trimesh(vertices=np.array(v,float),faces=np.array(f),process=False); mm.merge_vertices(); meshes[m]=mm
    return meshes
def wall_with_opening(p,mat,ow,oy0,oy1,h,inner='plaster',t=T,centered=False):
    x=ow/2; z0=-t/2 if centered else -t
    zs=[z0,z0+0.02,z0+t]
    if ow>0:
        xs=[-W/2,-x,x,W/2]; ys=sorted(set([0.0,max(oy0,0.0),oy1,h]))
        def cell(i,j,k):
            if i==1 and ys[j]>=max(oy0,0.0)-1e-9 and ys[j+1]<=oy1+1e-9: return None
            return inner if k==0 else mat
    else:
        xs=[-W/2,W/2]; ys=[0.0,h]
        def cell(i,j,k): return inner if k==0 else mat
    for m,mesh in grid_solid(xs,ys,zs,cell).items(): p.add(m,mesh)

def window(p,ow,oy0,oy1,lintel='trim',mull=True,sill_top=None,glass=True):
    x=ow/2; f=0.07
    if glass: p.box('glass',-x,x,oy0,oy1,-0.16,-0.14)
    p.box('frame',-x,-x+f,oy0,oy1,-0.18,-0.06); p.box('frame',x-f,x,oy0,oy1,-0.18,-0.06)
    p.box('frame',-x,x,oy1-f,oy1,-0.18,-0.06); p.box('frame',-x,x,oy0,oy0+f,-0.18,-0.06)
    if mull:
        p.box('frame',-0.025,0.025,oy0,oy1,-0.17,-0.1)
        m=oy0+(oy1-oy0)*0.55; p.box('frame',-x,x,m-0.025,m+0.025,-0.17,-0.1)
    st=oy0+0.015 if sill_top is None else sill_top   # never level with the opening floor
    p.box('trim',-x-0.08,x+0.08,st-0.08,st,-0.05,0.08)      # sill
    if lintel: p.box(lintel,-x-0.06,x+0.06,oy1+0.01,oy1+0.15,-0.02,0.04)

def ledge(p,h,mat='trim',th=0.1,d=0.06):
    p.box(mat,-W/2,W/2,h-th+0.015,h+0.015,0.0,d)   # rises 1.5 cm above the module top: hides the slab edge, never level with the wall top

P={}
def wall_brick_window():
    p=Piece(); wall_with_opening(p,'brick',0.9,0.85,2.3,H); window(p,0.9,0.85,2.3); ledge(p,H,th=0.08,d=0.04); return p
def wall_brick_plain():
    p=Piece(); wall_with_opening(p,'brick',0,0,0,H); ledge(p,H,th=0.08,d=0.04); return p
def wall_brick_balcony_door():
    p=Piece(); wall_with_opening(p,'brick',0.9,0.05,2.35,H); window(p,0.9,0.05,2.35,sill_top=0.015,glass=False,mull=False); ledge(p,H,th=0.08,d=0.04); return p
def wall_ground_window():
    p=Piece(); wall_with_opening(p,'stone',0.9,0.9,2.3,HG); window(p,0.9,0.9,2.3,lintel='stone')
    p.box('dark',-W/2,W/2,0,0.12,0.0,0.03); ledge(p,HG,th=0.2,d=0.08); return p
def wall_ground_door():
    p=Piece(); ow=1.1; wall_with_opening(p,'stone',ow,0,2.4,HG)
    x=ow/2
    p.box('frame',-x,-x+0.07,0,2.4,-0.22,0.02); p.box('frame',x-0.07,x,0,2.4,-0.22,0.02); p.box('frame',-x,x,2.33,2.4,-0.22,0.02)
    p.box('stone',-0.75,0.75,0,0.15,0,0.45)  # step
    p.box('dark',-W/2,-x,0,0.12,0.0,0.03); p.box('dark',x,W/2,0,0.12,0.0,0.03)
    ledge(p,HG,th=0.2,d=0.08); return p
def corner(mat,h,ledge_th,ledge_d,plinth=False):
    p=Piece(); e=0.03; p.box(mat,-T-0.01,e,0,h,-T-0.01,e)
    p.box('trim',-T,e+ledge_d,h-ledge_th+0.015,h+0.015,-T,e+ledge_d)
    if plinth: p.box('dark',-T,e+0.03,0,0.12,-T,e+0.03)
    return p
def cornice(corner_=False,gap=0.0):
    p=Piece(); x0,x1=(-T,0.03) if corner_ else (-W/2,W/2)
    def bx(mat,y0,y1,d,back=-T):
        if corner_: p.box(mat,-T,0.03+d,y0,y1,-T,0.03+d)
        elif gap: p.box(mat,-W/2,-gap/2,y0,y1,back,d); p.box(mat,gap/2,W/2,y0,y1,back,d)
        else: p.box(mat,-W/2,W/2,y0,y1,back,d)
    bx('brick',0,0.6,0.03); bx('trim',0.6,0.72,0.12); bx('trim',0.72,0.82,0.2)
    bx('brick',0.82,1.3,0.0); bx('trim',1.3,1.4,0.06)
    if not corner_:
        for i in range(6):
            cx=-W/2+W/12+i*W/6
            if abs(cx)>gap/2+0.07: p.box('trim',cx-0.07,cx+0.07,0.2,0.42,0,0.12)
        if gap: p.box('trim',-W/2,-gap/2,1.3,1.4,-T-0.06,-T); p.box('trim',gap/2,W/2,1.3,1.4,-T-0.06,-T)
        else: p.box('trim',-W/2,W/2,1.3,1.4,-T-0.06,-T)  # inner cap lip
        if gap: p.box('roof',-gap/2,gap/2,-0.04,0.02,-T,0.04)  # threshold (2 cm sill hides the wall top + roof edge)
    return p
def roof_tile():
    p=Piece(); p.box('roof',-W/2,W/2,-0.04,0.0,-W/2,W/2); p.box('plaster',-W/2+0.02,W/2-0.02,-0.2,-0.04,-W/2+0.02,W/2-0.02); return p
def roof_stair_hut():
    p=Piece(); s=1.0; h=2.6
    p.box('brick',-s,s,0,h,-s,s); p.box('roof',-s-0.12,s+0.12,h,h+0.14,-s-0.12,s+0.12)
    p.box('trim',-s-0.04,s+0.04,h-0.12,h,-s-0.04,s+0.04)
    p.box('dark',-0.45,0.45,0,2.1,s,s+0.03); p.box('frame',-0.5,0.5,2.1,2.18,s,s+0.05)
    p.box('frame',-0.5,-0.45,0,2.1,s,s+0.05); p.box('frame',0.45,0.5,0,2.1,s,s+0.05)
    p.box('metal',0.28,0.36,1.0,1.08,s+0.03,s+0.07); return p
def water_tower():
    p=Piece(); r=0.8; leg=1.6
    for sx in (-1,1):
        for sz in (-1,1): p.cyl('iron',0.05,0,leg,sx*0.55,sz*0.55,8)
    p.seg('iron',(-0.55,0.5,0.55),(0.55,1.2,0.55),0.04); p.seg('iron',(-0.55,0.5,-0.55),(0.55,1.2,-0.55),0.04)
    p.box('iron',-0.95,0.95,leg,leg+0.1,-0.95,0.95)
    p.cyl('wood',r,leg+0.1,leg+1.9,sec=20)
    for y in (leg+0.5,leg+1.1,leg+1.7): p.cyl('iron',r+0.02,y,y+0.05,sec=20)
    p.cone('tower_roof',r+0.12,leg+1.9,leg+2.7,sec=20); p.sphere('tower_roof',0.06,0,leg+2.72,0); return p
def ac_unit():
    p=Piece(); p.box('metal',-0.45,0.45,0,0.6,-0.3,0.3); p.cyl('dark',0.2,0.3,0.31,0,0,20)
    p.add('dark',p.parts['dark'].pop().apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0],[0,0.3,0])).apply_translation([0.08,0,0.3]))
    p.box('dark',-0.42,-0.38,0,0.05,-0.27,0.27); p.box('dark',0.38,0.42,0,0.05,-0.27,0.27); return p
def railing(p,x0,x1,z0,z1,y,h=0.9,sides=(True,True,True),n=None):
    def run(a,b):
        L=np.linalg.norm(np.subtract(b,a)); k=n or max(2,int(L/0.12))
        for i in range(k+1):
            t=i/k; q=np.add(a,np.multiply(t,np.subtract(b,a))); p.box('iron',q[0]-0.015,q[0]+0.015,y,y+h,q[1]-0.015,q[1]+0.015)
        p.seg('iron',(a[0],y+h,a[1]),(b[0],y+h,b[1]),0.05); p.seg('iron',(a[0],y+0.1,a[1]),(b[0],y+0.1,b[1]),0.035)
    if sides[0]: run((x0,z1),(x1,z1))
    if sides[1]: run((x0,z0),(x0,z1))
    if sides[2]: run((x1,z0),(x1,z1))
def balcony():
    p=Piece(); x=0.75; d=0.8
    p.box('dark',-x,x,-0.08,0.0,0,d); p.box('iron',-x,x,-0.16,-0.08,d-0.05,d)
    railing(p,-x+0.02,x-0.02,0.02,d-0.02,0); return p
def fire_escape_platform():
    p=Piece(); x=1.0; d=0.9
    for i in range(10): p.box('iron',-x+i*0.2+0.02,-x+i*0.2+0.16,-0.05,0,0,d)
    p.box('iron',-x,x,-0.12,0,d-0.04,d); p.box('iron',-x,x,-0.12,0,0,0.04)
    railing(p,-x+0.02,x-0.02,0.02,d-0.02,0)
    p.seg('iron',(-x+0.1,-0.1,0.02),(-x+0.1,-0.7,0.02),0.06); p.seg('iron',(-x+0.1,-0.7,0.02),(-x+0.1,-0.1,d-0.1),0.05)
    p.seg('iron',(x-0.1,-0.1,0.02),(x-0.1,-0.7,0.02),0.06); p.seg('iron',(x-0.1,-0.7,0.02),(x-0.1,-0.1,d-0.1),0.05)
    return p
def fire_escape_stairs():
    p=Piece(); run=1.7; rise=H; w=0.6; z0=0.15; z1=z0+w
    for z in (z0,z1): p.seg('iron',(-run/2,0,z),(run/2,rise,z),0.06)
    n=14
    for i in range(1,n):
        t=i/n; xx=-run/2+t*run; yy=t*rise; p.box('iron',xx-0.06,xx+0.06,yy-0.02,yy+0.01,z0,z1)
    p.seg('iron',(-run/2,0.9,z1),(run/2,rise+0.9,z1),0.04)
    return p
FE_D=2.0; FE_W=1.0   # platform depth (1 m walkway + 1 m stair strip)
def fe_rail_run(p,a,b,y=0,h=1.0,step=0.12):
    L=np.linalg.norm(np.subtract(b,a)); k=max(2,int(L/step))
    for i in range(k+1):
        t=i/k; q=np.add(a,np.multiply(t,np.subtract(b,a))); p.box('iron',q[0]-0.015,q[0]+0.015,y,y+h,q[1]-0.015,q[1]+0.015)
    p.seg('iron',(a[0],y+h,a[1]),(b[0],y+h,b[1]),0.05); p.seg('iron',(a[0],y+0.1,a[1]),(b[0],y+0.1,b[1]),0.035)
def fe_deck(p,z0,z1):
    p.box('iron',-W/2,W/2,-0.06,-0.02,z0,z1)
    n=int((z1-z0)/0.1)
    for i in range(n): zz=z0+0.03+i*0.1; p.box('iron',-W/2,W/2,-0.02,0,zz,zz+0.05)
    p.box('iron',-W/2,W/2,-0.16,-0.06,z1-0.05,z1); p.box('iron',-W/2,W/2,-0.16,-0.06,z0,z0+0.05)
def fe_brackets(p,d=FE_D):
    for xx in (-W/2+0.08,W/2-0.08):
        p.box('iron',xx-0.03,xx+0.03,-0.16,-0.06,0,d); p.seg('iron',(xx,-0.7,0.02),(xx,-0.14,d*0.8),0.05)
def fire_escape_platform():
    p=Piece(); fe_deck(p,0,FE_D); fe_brackets(p); fe_rail_run(p,(-W/2,FE_D-0.02),(W/2,FE_D-0.02)); return p
def fire_escape_platform_stairwell():
    p=Piece(); fe_deck(p,0,FE_W); fe_brackets(p,FE_W); p.box('iron',-W/2,W/2,-0.16,-0.02,FE_D-0.05,FE_D); return p
def fire_escape_end_rail():
    p=Piece(); fe_rail_run(p,(0,0.05),(0,FE_D-0.02)); return p
def fire_escape_stairs(rise=H,run=4.0,w=0.9):
    p=Piece(); n=round(rise/0.18); tr=run/n; st=rise/n; z0=FE_W+0.05; z1=z0+w
    for i in range(n):
        x0=i*tr; top=(i+1)*st; p.box('iron',x0,x0+tr,top-0.04,top,z0,z1)
        for k in range(1,3): p.box('dark',x0+0.02,x0+tr-0.02,top-0.005,top+0.003,z0+k*w/3-0.01,z0+k*w/3+0.01)
    for z in (z0,z1): p.seg('iron',(0,0,z),(run,rise,z),0.07)
    p.seg('iron',(0,1.0,z1),(run,rise+1.0,z1),0.05)
    for i in range(0,n+1,3): xx=i*tr; yy=i*st; p.box('iron',xx-0.02,xx+0.02,yy,yy+1.0,z1-0.02,z1+0.02)
    return p
def entrance_canopy():
    p=Piece(); x=0.9; d=1.0
    p.box('dark',-x,x,0,0.14,0,d); p.box('iron',-x-0.02,x+0.02,0.14,0.18,-0.02,d+0.02)
    p.seg('iron',(-x+0.1,0.07,d-0.05),(-x+0.1,0.9,0.02),0.03); p.seg('iron',(x-0.1,0.07,d-0.05),(x-0.1,0.9,0.02),0.03); return p
def wall_lamp():
    p=Piece(); p.box('iron',-0.04,0.04,0,0.06,0,0.25); p.box('iron',-0.1,0.1,-0.35,-0.3,0.15,0.35)
    p.box('light',-0.08,0.08,-0.3,-0.05,0.17,0.33); p.box('iron',-0.11,0.11,-0.05,0.0,0.14,0.36); return p
def street_lamp():
    p=Piece(); p.cyl('iron',0.05,0,2.6,sec=8); p.box('iron',-0.14,0.14,2.6,2.65,-0.14,0.14)
    p.box('light',-0.11,0.11,2.65,2.95,-0.11,0.11); p.cone('iron',0.18,2.95,3.15,sec=4); return p
def tree():
    p=Piece(); p.cyl('trunk',0.07,0,1.2,sec=8)
    for (x,y,z,r) in [(0,1.6,0,0.5),(0.28,1.25,0.15,0.38),(-0.22,1.3,-0.1,0.36),(0.05,2.0,0.05,0.35)]: p.sphere('leaf',r,x,y,z)
    p.box('dark',-0.3,0.3,0,0.06,-0.3,0.3); return p
def sidewalk_tile():
    p=Piece(); p.box('pave',-W/2,W/2,-0.12,0,-W/2,W/2); return p
def sidewalk_curb():
    p=Piece(); p.box('stone',-W/2,W/2,-0.15,0.0,-0.15,0.0); return p
def grass_strip():
    p=Piece(); p.box('grass',-W/2,W/2,0,0.04,-0.2,0.0); return p
def doormat():
    p=Piece(); p.box('mat',-0.4,0.4,0,0.02,-0.25,0.25); return p

SLAB=0.2
def floor_tile():
    p=Piece(); p.box('floor',-W/2,W/2,-0.03,0,-W/2,W/2); p.box('plaster',-W/2+0.02,W/2-0.02,-SLAB,-0.03,-W/2+0.02,W/2-0.02); return p
def floor_tile_bath():
    p=Piece(); p.box('tile',-W/2,W/2,-0.03,0,-W/2,W/2); p.box('plaster',-W/2+0.02,W/2-0.02,-SLAB,-0.03,-W/2+0.02,W/2-0.02); return p
CORE=4.0; HOLE=1.35
def stair_core_slab(top='floor'):
    """4x4 m slab with the stair hole (x in [-1.35,1.35], full depth). Pivot: centre."""
    p=Piece(); h=CORE/2
    for (a,b) in ((-h,-HOLE),(HOLE,h)):
        p.box(top,a,b,-0.03 if top!='roof' else -0.04,0,-h,h); p.box('plaster',a+0.02,b-0.02,-SLAB,-0.03 if top!='roof' else -0.04,-h+0.02,h-0.02)
    return p
def stairs_u(rise,run=2.0,w=1.2,gap=0.1,land=1.7):
    """U-shaped stair: flight A goes up toward -Z on the left, landing at the back, flight B returns on the right.
    Pivot: centre of the core's open (front) edge, at the lower floor level."""
    p=Piece(); n=math.ceil(rise/0.18-1e-9); n+=n%2; k=n//2; st=rise/n; tr=run/k
    xa0,xa1=-gap/2-w,-gap/2; xb0,xb1=gap/2,gap/2+w
    for i in range(k-1):
        top=(i+1)*st; p.box('floor',xa0,xa1,top-0.04,top,-(i+1)*tr,-i*tr); p.box('plaster',xa0,xa1,top-0.26,top-0.04,-(i+1)*tr,-i*tr)
    mid=k*st
    p.box('floor',xa0,xb1,mid-0.04,mid,-run-land,-run+tr); p.box('plaster',xa0,xb1,mid-0.24,mid-0.04,-run-land,-run+tr)
    for j in range(1,k):
        top=mid+j*st
        p.box('floor',xb0,xb1,top-0.04,top,-run+(j)*tr,-run+(j+1)*tr); p.box('plaster',xb0,xb1,top-0.26,top-0.04,-run+(j)*tr,-run+(j+1)*tr)
    # handrails (inner pair + outer pair)
    for x in (xa0+0.04,xa1-0.04):
        p.seg('iron',(x,0.9,0),(x,mid+0.9,-run),0.05)
    for x in (xb0+0.04,xb1-0.04):
        p.seg('iron',(x,mid+0.9,-run+tr),(x,rise+0.9,0),0.05)
    for i in range(0,k+1,2):
        z=-i*tr; ya=i*st; yb=rise-i*st
        p.box('iron',xa1-0.06,xa1-0.02,ya,ya+0.9,z-0.02,z+0.02); p.box('iron',xb0+0.02,xb0+0.06,yb,yb+0.9,z-0.02,z+0.02)
    return p
def door_leaf_balcony(w=0.76,h=2.16):
    """Glazed leaf for the balcony / fire-escape door. Pivot: hinge, bottom. Closed = along +X."""
    p=Piece(); f=0.06
    p.box('frame',0,f,0,h,-0.02,0.02); p.box('frame',w-f,w,0,h,-0.02,0.02)
    p.box('frame',f,w-f,0,0.25,-0.02,0.02); p.box('frame',f,w-f,h-f,h,-0.02,0.02); p.box('frame',f,w-f,1.2,1.25,-0.02,0.02)
    p.box('glass',f,w-f,0.25,h-f,-0.008,0.008); p.box('metal',w-0.12,w-0.08,1.0,1.06,-0.05,0.05); return p
def door_leaf(w=0.96,h=2.32,glass=True,mat='door'):
    p=Piece(); p.box(mat,0,w,0,h,-0.025,0.025)
    if glass: p.box('glass',w*0.2,w*0.8,h*0.62,h*0.9,-0.03,0.03)
    p.box('metal',w-0.14,w-0.06,1.0,1.06,-0.06,0.06); return p
def interior_wall(doorway,h=H-SLAB,ow=0.9):
    p=Piece(); t=0.12; ow=ow if doorway else 0
    wall_with_opening(p,'plaster',ow,0,2.1,h,inner='plaster',t=t,centered=True)
    if doorway:
        for xx in (-ow/2,ow/2): p.box('frame',xx-0.04,xx+0.04,0,2.14,-t/2-0.02,t/2+0.02)
        p.box('frame',-ow/2-0.04,ow/2+0.04,2.08,2.18,-t/2-0.02,t/2+0.02)
    segs=[(-W/2,-ow/2-0.04),(ow/2+0.04,W/2)] if doorway else [(-W/2,W/2)]  # rodapé para na porta
    for a,b in segs: p.box('trim',a,b,0,0.1,t/2,t/2+0.015); p.box('trim',a,b,0,0.1,-t/2-0.015,-t/2)
    return p
def interior_wall_end(h=H-SLAB):
    # plain interior wall that stops at the inner face of an exterior wall (+X end shortened by T)
    p=Piece(); t=0.12; L=W-T
    m=trimesh.creation.box(extents=[L,h,t]); m.apply_translation([-W/2+L/2,h/2,0]); p.add('plaster',m)
    p.box('trim',-W/2,-W/2+L,0,0.1,t/2,t/2+0.015); p.box('trim',-W/2,-W/2+L,0,0.1,-t/2-0.015,-t/2); return p
def player_ref():
    p=Piece(); c=trimesh.creation.capsule(height=1.8-0.6,radius=0.3,count=[8,8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0])); c.apply_translation([0,0.9,0]); p.add('player',c)
    p.box('dark',-0.15,0.15,1.5,1.6,0.22,0.32); return p
def roof_stair_hut(wx=4.0,dz=5.4,h=2.8):
    """Walk-in hut over the stair core. Pivot: centre of footprint on the roof. Door on +Z."""
    p=Piece(); x=wx/2; z=dz/2; t=0.2
    p.box('brick',-x,x,0,h,-z,-z+t); p.box('brick',-x,-x+t,0,h,-z,z); p.box('brick',x-t,x,0,h,-z,z)
    p.box('brick',-x,-0.6,0,h,z-t,z); p.box('brick',0.6,x,0,h,z-t,z); p.box('brick',-0.6,0.6,2.3,h,z-t,z)
    for (a,b,c,d) in ((-x+t,x-t,-z+t,-z+t+0.02),):
        p.box('plaster',a,b,0,h,c,d)
    p.box('plaster',-x+t,-x+t+0.02,0,h,-z+t,z-t); p.box('plaster',x-t-0.02,x-t,0,h,-z+t,z-t)
    p.box('roof',-x-0.12,x+0.12,h,h+0.14,-z-0.12,z+0.12); p.box('trim',-x-0.04,x+0.04,h-0.12,h,-z-0.04,z+0.04)
    for xx in (-0.6,0.6): p.box('frame',xx-0.05,xx+0.05,0,2.3,z-0.02,z+0.03)
    p.box('frame',-0.65,0.65,2.28,2.36,z-0.02,z+0.03); p.box('light',-0.12,0.12,2.45,2.6,z,z+0.08)
    return p
# =====================================================================================
# KIT 7: single-storey bungalow (green clapboard, brick base, hipped roof, gabled front porch)
# =====================================================================================
from shapely.ops import unary_union
COL.update({'siding':(126,150,108),'shingles':(70,72,80),'ridge':(54,56,62),'trim':(242,236,220),'frame':(242,236,220),
            'door':(146,58,46),'deck':(150,104,70),'brick':(166,80,60),'cap':(198,192,180),'iron':(50,50,54),'ceiling':(206,226,224)})
def siding_texture(px=256,seed=71):
    # tile 1 x 1 m: five 0.2 m clapboards, shadow line under each lap, faint grain
    im=Image.new('RGB',(px,px),COL['siding']); d=ImageDraw.Draw(im); bh=px/5
    for i in range(5):
        y0=i*bh; d.rectangle([0,y0,px,y0+bh*0.16],fill=tuple(int(v*0.8) for v in COL['siding']))
        d.rectangle([0,y0+bh*0.16,px,y0+bh*0.3],fill=tuple(int(v*0.92) for v in COL['siding']))
    a=np.asarray(im,dtype=np.float32); n=_noise(px,8,seed)*0.6+_noise(px,64,seed+1)*0.5
    return Image.fromarray(np.clip(a+n[...,None]*10,0,255).astype(np.uint8))
def shingles_texture(px=256,seed=73):
    # tile 1 x 1 m: 5 courses of 0.2 m asphalt shingles, tabs 0.33 m, staggered
    rnd=random.Random(seed); im=Image.new('RGB',(px,px),(46,48,54)); d=ImageDraw.Draw(im); rh=px/5; tw=px/3
    base=[(72,74,82),(66,68,76),(78,80,88),(62,64,72)]
    for r in range(5):
        off=tw/2 if r%2 else 0
        for i in range(-1,4):
            c=rnd.choice(base); x0=i*tw+off
            for dx in (-px,0,px): d.rectangle([x0+dx+1,r*rh+1,x0+dx+tw-2,r*rh+rh-2],fill=c)
        d.rectangle([0,r*rh+rh*0.78,px,r*rh+rh-1],fill=(50,52,58))
    return im
SIDING_TEX=siding_texture(); SHINGLES_TEX=shingles_texture(); BRICK2_TEX=brick_texture(px=256)
for nm,im in (('siding',SIDING_TEX),('shingles',SHINGLES_TEX),('brick',BRICK2_TEX)): im.save(os.path.join(OUT,nm+'_texture.png'))
TEX={'siding':(SIDING_TEX,1.0,1.0),'shingles':(SHINGLES_TEX,1.0,1.0),'brick':(BRICK2_TEX,1.0,1.0),'plaster':(PLASTER_TEX,1.0,1.0)}
SIGN=(0,0,1,1)
MATS = {k:PBRMaterial(name=k, baseColorFactor=[c/255 for c in v]+[1.0], metallicFactor=0.0, roughnessFactor=0.9) for k,v in COL.items()}
for k,(im,_,_) in TEX.items(): MATS[k]=PBRMaterial(name=k,baseColorTexture=im,baseColorFactor=[255,255,255,255],metallicFactor=0.0,roughnessFactor=0.9)

RAISE=0.45  # floor raised on a brick base (3 risers of 15 cm)
def lvl(fl): return RAISE+fl*H
def ext(p,mat,poly,z0,z1):
    for g in getattr(poly,'geoms',[poly]):
        if g.geom_type!='Polygon' or g.area<1e-6: continue
        m=trimesh.creation.extrude_polygon(g,z1-z0); m.apply_translation([0,0,z0]); p.add(mat,m)
def hull(p,mat,pts): p.add(mat,trimesh.convex.convex_hull(np.array(pts,float)))
def rect(x0,y0,x1,y1): return sbox(x0,y0,x1,y1)
def sheared(p,mat,poly,t0,t1,f):
    """Extrude a plan polygon (x, z) between t0 and t1 and lift it onto a plane: y = f(x, z) + t."""
    for g in getattr(poly,'geoms',[poly]):
        if g.geom_type!='Polygon' or g.area<1e-6: continue
        m=trimesh.creation.extrude_polygon(g,t1-t0); v=m.vertices.copy()
        a,b,c=v[:,0].copy(),v[:,1].copy(),v[:,2]+t0
        m.vertices=np.stack([a,f(a,b)+c,b],1); m.invert(); p.add(mat,m)
# ---------- walls (3.0 m, ceiling at the top, brick base below the floor) ----------
FRIEZE=2.72; HW=H+0.18; FT=H+0.05   # exterior walls rise into the roof slab; frieze board top
def base_and_water_table(p,x0=-W/2,x1=W/2):
    p.box('brick',x0,x1,-RAISE,0.0,-T,0.0)
    p.box('trim',x0,x1,-0.1,0.14,0.0,0.05)                     # water table: hides the floor slab edge
    p.box('trim',x0,x1,FRIEZE,FT,0.0,0.03)                      # frieze board under the eaves: hides the ceiling edge
def casing(p,ow,oy0,oy1):
    x=ow/2; w=0.12
    for (a,b) in ((-x-w,-x),(x,x+w)): p.box('trim',a,b,oy0-0.02,oy1+0.02,0.0,0.03)
    p.box('trim',-x-w-0.03,x+w+0.03,oy1+0.02,oy1+0.22,0.0,0.045)
def wall_siding_window():
    p=Piece(); wall_with_opening(p,'siding',1.1,0.8,2.3,HW); window(p,1.1,0.8,2.3,lintel=None); casing(p,1.1,0.8,2.3); base_and_water_table(p); return p
def wall_siding_small_window():
    p=Piece(); wall_with_opening(p,'siding',0.6,1.5,2.3,HW); window(p,0.6,1.5,2.3,mull=False,lintel=None); casing(p,0.6,1.5,2.3); base_and_water_table(p); return p
def wall_siding_plain():
    p=Piece(); wall_with_opening(p,'siding',0,0,0,HW); base_and_water_table(p); return p
def wall_siding_window_hood():
    """Window module with a small shingled hood on two brackets (side facade)."""
    p=wall_siding_window(); x=0.85; y0=2.64; y1=2.36; d=0.7
    hull(p,'shingles',[(xx,y,z) for xx in (-x,x) for (z,y) in ((0.04,y0),(0.04,y0+0.1),(d,y1),(d,y1+0.1))])
    p.box('trim',-x+0.01,x-0.01,y1-0.12,y1+0.02,d-0.03,d+0.02)
    for s in (-1,1):
        xa,xb=sorted((s*(x-0.12),s*(x-0.04)))
        hull(p,'trim',[(xx,y,z) for xx in (xa,xb) for (z,y) in ((0.045,1.95),(0.045,y0+0.02),(d-0.05,y1+0.02),(0.12,y0-0.1))])
    return p
def wall_siding_door():
    p=Piece(); ow=1.0; x=ow/2; oy0=0.015; wall_with_opening(p,'siding',ow,oy0,2.3,HW)
    p.box('frame',-x,-x+0.07,oy0,2.3,-0.24,0.0); p.box('frame',x-0.07,x,oy0,2.3,-0.24,0.0); p.box('frame',-x,x,2.23,2.3,-0.24,0.0)
    casing(p,ow,oy0,2.3); p.box('trim',-x+0.07,x-0.07,0.0,0.02,-0.24,0.04)
    p.box('brick',-W/2,W/2,-RAISE,0.0,-T,0.0)
    for (a,b) in ((-W/2,-x-0.12),(x+0.12,W/2)): p.box('trim',a,b,-0.1,0.14,0.0,0.05)
    p.box('trim',-x-0.12,x+0.12,-0.1,0.0,0.0,0.05); p.box('trim',-W/2,W/2,FRIEZE,FT,0.0,0.03)
    return p
def corner_siding():
    p=Piece(); e=0.04; p.box('trim',-T-0.01,e,0,FT,-T-0.01,e); p.box('brick',-T-0.01,0.01,-RAISE,0,-T-0.01,0.01); p.box('trim',-T,e+0.06,-0.1,0.14,-T,e+0.06); return p
def ceiling_tile():
    """2 x 2 m flat ceiling (top at the wall plate, 3.0 m above the floor). Pivot: centre, top face."""
    p=Piece(); p.box('plaster',-W/2,W/2,-SLAB,0,-W/2,W/2); return p
def brick_steps(w=1.36,rise=0.15,run=0.3,n=2):
    """Brick steps with stone treads, down from the floor (n treads, then grade). Pivot: top edge, centre; goes toward +Z."""
    p=Piece()
    for i in range(n):
        top=-(i+1)*rise; p.box('brick',-w/2,w/2,-RAISE,top-0.04,i*run,(i+1)*run)
        p.box('cap',-w/2-0.02,w/2+0.02,top-0.04,top,i*run,(i+1)*run+0.03)
    return p
def fireplace():
    """Brick fireplace against the side wall. Pivot: back-centre on the floor, mouth toward +Z."""
    p=Piece(); w=0.8; d=0.5
    p.box('brick',-w,w,0,1.2,0,d); p.box('cap',-w-0.08,w+0.08,1.2,1.28,0,d+0.1)
    p.box('dark',-0.45,0.45,0.12,0.8,d,d+0.01); p.box('brick',-w-0.1,w+0.1,0,0.08,d,d+0.45)
    p.box('brick',-0.5,0.5,1.28,H-SLAB,0,0.4); return p
def chimney(h):
    """Outside brick chimney: wide breast, sloped shoulders, stack through the eaves. Pivot: centre of the wall face at grade."""
    p=Piece(); d0=0.7; w0=0.8; ws=0.36; ys=RAISE+1.4
    p.box('brick',-w0,w0,0,ys,0.0,d0)
    hull(p,'brick',[(x,y,z) for (x,y) in ((-w0,ys),(w0,ys),(-ws,ys+0.8),(ws,ys+0.8)) for z in (0.0,d0)])
    p.box('brick',-ws,ws,ys+0.8,h,0.04,0.66); p.box('cap',-ws-0.06,ws+0.06,h,h+0.1,-0.02,0.72)
    p.box('dark',-ws+0.1,ws-0.1,h+0.1,h+0.12,0.14,0.56); return p
# ---------- hipped roof, 30 degrees, built from 2 m strips ----------
KR=math.tan(math.radians(30)); TV=0.25; OVER=0.5; YE=H-0.03   # roof underside meets the wall face at YE
AXR,AZR=7.0+OVER,6.0+OVER    # half sizes of the roof outline (house 14 x 12 m)
def roof_strip(E,P,u,x0=-W/2,x1=W/2,fascia_ext=0.0):
    """One 2 m strip of a hipped slope. Eave along local X at z=OVER (pivot: wall face, floor level), slope rises toward -Z.
    E = half length of this eave (outer), P = distance from the eave to the ridge; u = module centre along the eave."""
    p=Piece()
    top=P if P<E else E
    slope=Polygon([(-E,0),(E,0),(E-top,top),(-(E-top),top)]) if P<E else Polygon([(-E,0),(E,0),(0,E)])
    s=rect(u+x0,0,u+x1,top+1).intersection(slope)
    poly=Polygon([(x-u,OVER-d) for x,d in s.exterior.coords])
    f=lambda a,b:YE-KR*b
    sheared(p,'plaster',poly,0.0,0.02,f); sheared(p,'shingles',poly,0.02,TV,f)
    yb=YE-KR*OVER; a,b=x0,x1
    a=a+fascia_ext if fascia_ext<0 else a+0.001
    b=b+fascia_ext if fascia_ext>0 else b-0.001
    p.box('trim',a,b,yb-0.15,yb+0.05,OVER-0.02,OVER+0.03)
    return p
def hip_cap():
    """Hip ridge cap from the eave corner to the ridge end. Pivot: outer corner of the walls, floor level."""
    p=Piece(); t0,t1=OVER+0.02,-(AZR-OVER)
    yt=lambda t:YE+TV-KR*t
    pts=[]
    for t in (t0,t1):
        c=np.array([t,0,t]); n=np.array([1,0,-1])/math.sqrt(2)
        for (off,dy) in ((0,0.07),(0.13,-0.04),(-0.13,-0.04),(0,-0.12)):
            q=c+n*off; pts.append((q[0],yt(t)+dy,q[2]))
    hull(p,'ridge',pts); return p
def ridge_cap(x0=-1.0,x1=1.0):
    p=Piece(); y=YE+TV+KR*(AZR-OVER); d=0.16
    hull(p,'ridge',[(x,yy,z) for x in (x0-0.05,x1+0.05) for (yy,z) in ((y-d*KR-0.04,d),(y-d*KR-0.04,-d),(y+0.07,0.0),(y-0.12,0.0))]); return p
# ---------- porch: brick piers, tapered columns, low walls, gabled roof ----------
PD=2.5; LW=0.9; PB=2.35; PBT=2.65; PX=5.15; PXO=5.45   # depth, low wall height, beam bottom/top, beam outer face, porch eave
def porch_deck():
    """2 m deck module from the house wall (z=0) to the low wall (z=PD-0.25), top at floor level."""
    p=Piece(); p.box('deck',-W/2,W/2,-0.05,0,0,PD-0.25)
    for i in range(1,10): xx=-W/2+i*0.2; p.box('dark',xx-0.006,xx+0.006,-0.002,0.001,0.01,PD-0.26)
    return p
def porch_front_wall():
    """Low clapboard wall between the piers, on a brick foundation. Pivot: centre, outer face, floor level."""
    p=Piece(); t=0.25
    p.box('brick',-W/2,W/2,-RAISE,-0.05,-t,0); p.box('siding',-W/2,W/2,-0.05,LW,-t,0)
    p.box('cap',-W/2,W/2,LW,LW+0.06,-t-0.04,0.04); return p
def porch_base_steps():
    """Front edge of the porch where the steps arrive: brick foundation, deck boards, fascia. Pivot like porch_front_wall."""
    p=Piece(); t=0.25
    p.box('brick',-W/2,W/2,-RAISE,-0.05,-t,0); p.box('deck',-W/2,W/2,-0.05,0,-t,0); p.box('trim',-W/2,W/2,-0.15,0,0,0.03); return p
def porch_side_wall(L=PD-0.125):
    """Low wall from the house wall to the corner pier. Pivot: end at the house wall, centre line, floor level; runs along +X."""
    p=Piece(); t=0.25
    p.box('brick',0,L,-RAISE,-0.05,-t/2,t/2); p.box('siding',0,L,-0.05,LW,-t/2,t/2)
    p.box('cap',0.05,L,LW,LW+0.06,-t/2-0.04,t/2+0.04); return p
def porch_pier():
    """Brick pier with a stone cap and a tapered square column up to the beam. Pivot: centre, floor level."""
    p=Piece(); a=0.3
    p.box('brick',-a,a,-RAISE,LW+0.05,-a,a); p.box('cap',-a-0.05,a+0.05,LW+0.05,LW+0.15,-a-0.05,a+0.05)
    y0,y1=LW+0.15,PB-0.1; b0,b1=0.21,0.14
    hull(p,'trim',[(sx*b,y,sz*b) for (b,y) in ((b0,y0),(b1,y1)) for sx in (-1,1) for sz in (-1,1)])
    p.box('trim',-0.2,0.2,PB-0.1,PB,-0.2,0.2); p.box('trim',-0.25,0.25,y0,y0+0.12,-0.25,0.25); return p
def porch_beam_side(L=PD-0.275):
    p=Piece(); p.box('trim',0,L,PB,PBT,-0.15,0.15); return p
def porch_ceiling():
    """Flat painted porch ceiling between the beams. Pivot: house wall face, centre of the porch, floor level."""
    p=Piece(); p.box('ceiling',-PX+0.3,PX-0.3,PBT-0.03,PBT,0,PD-0.275); return p
ZF=PD+0.45
def porch_y(x): return PBT+KR*(PX-np.abs(x))          # underside of the porch roof
def porch_gable():
    """Front beam + clapboard pediment with a louvred vent + rake boards. Pivot: house wall face, centre of the porch, floor level."""
    p=Piece(); zc=PD-0.125
    p.box('trim',-PX,PX,PB,PBT,zc-0.15,zc+0.15)
    tri=Polygon([(-PX,PBT),(PX,PBT),(0,float(porch_y(0))+0.02)])
    ext(p,'siding',tri,PD-0.1,PD+0.05)
    p.box('trim',-PX,PX,PBT,PBT+0.16,PD+0.05,PD+0.08)
    vy=PBT+1.25; p.box('trim',-0.5,0.5,vy-0.05,vy+0.75,PD+0.05,PD+0.08)
    p.box('dark',-0.4,0.4,vy+0.05,vy+0.65,PD+0.08,PD+0.085)
    for i in range(5): yy=vy+0.1+i*0.12; p.box('trim',-0.4,0.4,yy,yy+0.04,PD+0.085,PD+0.12)
    for s in (-1,1):
        a=np.array([s*PX,PBT]); b=np.array([0,float(porch_y(0))]); d=b-a; n=np.array([-d[1],d[0]])/np.linalg.norm(d)*0.12
        q=Polygon([a+n,b+n,b-n,a-n]).intersection(tri.buffer(0))
        ext(p,'trim',q,PD+0.05,PD+0.08)
    return p
def porch_roof():
    """Gabled porch roof; at the back it dies into the hipped main roof along two valleys. Pivot: house wall face, porch centre, floor level."""
    p=Piece(); zv=(TV-TV+YE+TV-PBT-TV)/KR       # valley: porch top = main roof top  ->  z = |x| - PX + zv
    zb=lambda ax:min(ax-PX+zv,OVER+0.05)
    for s in (-1,1):
        xs=np.linspace(0,PX,12); pts=[(s*x,zb(x)) for x in xs]+[(s*PX,OVER+0.05),(s*PXO,OVER+0.05),(s*PXO,ZF),(0,ZF)]
        poly=Polygon(pts).buffer(0); f=lambda a,b:PBT+KR*(PX-np.abs(a))
        sheared(p,'plaster',poly,0.0,0.02,f); sheared(p,'shingles',poly,0.02,TV,f)
        p.box('trim',*sorted((s*(PXO-0.02),s*(PXO+0.03))),float(porch_y(PXO))-0.15,float(porch_y(PXO))+0.05,OVER+0.06,ZF+0.03)
        a=(s*(PXO+0.03),float(porch_y(PXO))); b=(0,float(porch_y(0)))
        hull(p,'trim',[(x,y+dy,z) for (x,y) in (a,b) for dy in (-0.15,0.05) for z in (ZF-0.02,ZF+0.03)])
    y=float(porch_y(0))+TV; d=0.16; z0=zb(0.0)
    hull(p,'ridge',[(x,yy,z) for z in (z0,ZF+0.05) for (yy,x) in ((y-d*KR-0.04,d),(y-d*KR-0.04,-d),(y+0.07,0.0),(y-0.12,0.0))])
    return p
# ---------- interior ----------
def interior_wall_end_doorway(h=H-SLAB):
    p=Piece(); t=0.12; e=W/2-T
    xs=[-W/2,-0.45,0.45,e]; ys=[0.0,2.1,h]; zs=[-t/2,t/2]
    def cell(i,j,k): return None if (i==1 and j==0) else 'plaster'
    for m,mesh in grid_solid(xs,ys,zs,cell).items(): p.add(m,mesh)
    for xx in (-0.45,0.45): p.box('frame',xx-0.04,xx+0.04,0,2.14,-t/2-0.02,t/2+0.02)
    p.box('frame',-0.49,0.49,2.08,2.18,-t/2-0.02,t/2+0.02)
    for (a,b) in ((-W/2,-0.49),(0.49,e)): p.box('trim',a,b,0,0.1,t/2,t/2+0.015); p.box('trim',a,b,0,0.1,-t/2-0.015,-t/2)
    return p
def player_ref():
    p=Piece(); c=trimesh.creation.capsule(height=1.8-0.6,radius=0.3,count=[8,8]); c.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0])); c.apply_translation([0,0.9,0]); p.add('player',c)
    p.box('dark',-0.15,0.15,1.5,1.6,0.22,0.32); return p
CHIM_H=round(RAISE+5.1,2)
FB=[-6,-4,-2,0,2,4,6]; SB=[-5,-3,-1,1,3,5]
def roof_name(kind,u): return f'roof_{kind}_{abs(u)}'+('_l' if u<0 else '')
pieces={'floor_tile':floor_tile(),'floor_tile_bath':floor_tile_bath(),'ceiling_tile':ceiling_tile(),
 'door_leaf_front':door_leaf(0.94,2.26,True,'door'),'door_leaf_back':door_leaf(0.94,2.26,False,'door'),'door_leaf_interior':door_leaf(0.86,2.08,False,'frame'),
 'interior_wall_plain':interior_wall(False),'interior_wall_doorway':interior_wall(True),'interior_wall_end':interior_wall_end(),'interior_wall_end_doorway':interior_wall_end_doorway(),
 'wall_siding_window':wall_siding_window(),'wall_siding_small_window':wall_siding_small_window(),'wall_siding_plain':wall_siding_plain(),'wall_siding_door':wall_siding_door(),
 'wall_siding_window_hood':wall_siding_window_hood(),'corner_siding':corner_siding(),'fireplace':fireplace(),'chimney':chimney(CHIM_H),'brick_steps':brick_steps(),
 'hip_cap':hip_cap(),'ridge_cap':ridge_cap(),
 'porch_deck':porch_deck(),'porch_front_wall':porch_front_wall(),'porch_base_steps':porch_base_steps(),'porch_side_wall':porch_side_wall(),'porch_pier':porch_pier(),
 'porch_beam_side':porch_beam_side(),'porch_ceiling':porch_ceiling(),'porch_gable':porch_gable(),'porch_roof':porch_roof(),
 'player_scale_ref':player_ref(),
}
for u in FB:
    pieces.setdefault(roof_name('main',u),roof_strip(AXR,AZR,u,-W/2-(OVER if u==-6 else 0),W/2+(OVER if u==6 else 0),fascia_ext=0.03 if u==6 else -0.03 if u==-6 else 0))
for u in SB:
    pieces.setdefault(roof_name('hip',u),roof_strip(AZR,AXR,u,-W/2-(OVER if u==-5 else 0),W/2+(OVER if u==5 else 0)))
import shutil; shutil.rmtree(f'{OUT}/pieces',ignore_errors=True); os.makedirs(f'{OUT}/pieces')
for n,p in pieces.items(): p.scene(n).export(f'{OUT}/pieces/{n}.glb',include_normals=True)

# ================= assembly: 14 x 12 m bungalow, front (porch) on +Z, hipped roof (ridge along X), chimney on the left =================
SX,SZ=7.0,6.0
L=[]
def put(n,x,y,z,ry=0,tags=(),door=None):
    e={'piece':n,'pos':[round(x,3),round(y,3),round(z,3)],'rotY':ry,'tags':list(tags)}
    if door is not None: e['door']={'closed':ry,'open':ry+door}; e['tags'].append('door')
    L.append(e)
def hinge(x,z,ry,lx,lz):
    r=math.radians(ry); return x+lx*math.cos(r)+lz*math.sin(r), z-lx*math.sin(r)+lz*math.cos(r)
def ftag(fl): return f'floor{fl}'
faces=[(0,FB,lambda u:(u,SZ),'front'),(90,SB,lambda u:(SX,-u),'right'),(180,FB,lambda u:(-u,-SZ),'back'),(-90,SB,lambda u:(-SX,u),'left')]
SW,SS,SP,SD,SH='wall_siding_window','wall_siding_small_window','wall_siding_plain','wall_siding_door','wall_siding_window_hood'
G={'front':{-6:SW,-4:SW,-2:SW,0:SD,2:SW,4:SP,6:SW},
   'back':{-6:SW,-4:SW,-2:SD,0:SS,2:SP,4:SW,6:SW},
   'left':{5:SW,3:SP,1:SW,-1:SW,-3:SW,-5:SP},       # chimney breast at z=3
   'right':{5:SW,3:SH,1:SS,-1:SW,-3:SP,-5:SW}}
for ry,bays,f,tag in faces:
    for u in bays:
        x,z=f(u); wk=x if tag in ('front','back') else z
        put(G[tag][wk],x,lvl(0),z,ry,[tag,'ext',ftag(0)])
        put(roof_name('main' if tag in ('front','back') else 'hip',u),x,lvl(0),z,ry,[tag,'roof'])
for ry,x,z,tg in [(0,SX,SZ,('front','right')),(90,SX,-SZ,('right','back')),(180,-SX,-SZ,('back','left')),(-90,-SX,SZ,('left','front'))]:
    put('corner_siding',x,lvl(0),z,ry,tg+('ext',ftag(0))); put('hip_cap',x,lvl(0),z,ry,tg+('roof',))
put('ridge_cap',0,lvl(0),0,0,['roof'])
put('chimney',-SX,0,3,-90,['left','ext']); put('fireplace',-SX+T,lvl(0),3,90,[ftag(0)])
# porch: x in [-5,5], z in [6,8.5]; piers at -5,-1,1,5; steps in the middle bay
for x in (-4,-2,0,2,4):
    put('porch_deck',x,lvl(0),SZ,0,['front','porch'])
    put('porch_base_steps' if x==0 else 'porch_front_wall',x,lvl(0),SZ+PD,0,['front','porch'])
for x in (-5,-1,1,5): put('porch_pier',x,lvl(0),SZ+PD-0.125,0,['front','porch'])
for x in (-5,5): put('porch_side_wall',x,lvl(0),SZ,-90,['front','porch']); put('porch_beam_side',x,lvl(0),SZ,-90,['front','porch'])
put('porch_ceiling',0,lvl(0),SZ,0,['front','porch']); put('porch_gable',0,lvl(0),SZ,0,['front','porch'])
put('porch_roof',0,lvl(0),SZ,0,['front','porch','roof'])
put('brick_steps',0,lvl(0),SZ+PD,0,['front','porch'])
put('brick_steps',-2,lvl(0),-SZ,180,['back','ext'])
# floor + ceiling
TILE={(2,-3),(2,-1),(-2,-5),(-2,-3),(-2,-1),(0,-5),(0,-3),(0,-1),(2,-5)}
for a in FB:
    for b in SB:
        put('floor_tile_bath' if (a,b) in TILE else 'floor_tile',a,lvl(0),b,0,[ftag(0)])
        put('ceiling_tile',a,lvl(0)+H-0.01,b,0,['roof','ceiling'])
def wl(fl,x0,z0,x1,z1,doors=()):
    y=lvl(fl)
    if z0==z1:
        for c in range(int(min(x0,x1))+1,int(max(x0,x1)),2):
            end=abs(c)+1>=SX; d=c in doors
            put(('interior_wall_end' if end else 'interior_wall_'+('doorway' if d else 'plain'))+('_doorway' if end and d else ''),c,y,z0,(0 if c>0 else 180) if end else 0,[ftag(fl)])
            if d: hx,hz=hinge(c,z0,0,-0.43,0); put('door_leaf_interior',hx,y,hz,0,[ftag(fl)],door=70)
    else:
        for c in range(int(min(z0,z1))+1,int(max(z0,z1)),2):
            end=abs(c)+1>=SZ; d=c in doors
            put(('interior_wall_end' if end else 'interior_wall_'+('doorway' if d else 'plain'))+('_doorway' if end and d else ''),x0,y,c,(-90 if c>0 else 90) if end else 90,[ftag(fl)])
            if d: hx,hz=hinge(x0,c,90,-0.43,0); put('door_leaf_interior',hx,y,hz,90,[ftag(fl)],door=70)
# living (front left, fireplace) | dining (back left) | kitchen + pantry | corridor, bathroom, two bedrooms on the right
wl(0,-7,0,1,0,doors=(-4,0)); wl(0,1,-6,1,6,doors=(1,-5)); wl(0,1,0,7,0,doors=(2,4)); wl(0,1,2,7,2,doors=(4,))
wl(0,3,-6,3,0); wl(0,1,-4,3,-4); wl(0,-3,-6,-3,0,doors=(-3,))
put('door_leaf_front',-0.47,lvl(0)+0.015,SZ-0.18,0,['front','ext',ftag(0)],door=85)
hx,hz=hinge(-2,-SZ,180,-0.47,-0.18); put('door_leaf_back',hx,lvl(0)+0.015,hz,180,['back','ext',ftag(0)],door=85)
put('player_scale_ref',2.0,0,SZ+PD+1.4); put('player_scale_ref',-4,lvl(0),3,0,[ftag(0)]); put('player_scale_ref',3,lvl(0),SZ+1.2,0,['porch'])
json.dump({'grid':{'module_width':W,'floor_height':H,'wall_thickness':T,'slab':SLAB,'floor_raise':RAISE,'footprint':[2*SX,2*SZ],'porch':{'x':[-5,5],'z':[SZ,SZ+PD]},
  'roof':'hipped, 30 deg, ridge along X (x in [-1,1]) at z=0, eave overhang 0.5 m'},'placements':L},open(f'{OUT}/building_layout.json','w'),indent=1)
asm=Piece()
for e in L:
    if e['piece']=='player_scale_ref': continue
    Tm=trimesh.transformations.rotation_matrix(math.radians(e['rotY']),[0,1,0]); Tm[:3,3]=e['pos']
    asm.merge(pieces[e['piece']],Tm)
asm.scene('building').export(f'{OUT}/building_assembled.glb',include_normals=True)
print(len(pieces),'pieces',len(L),'placements',sum(1 for e in L if 'door' in e),'doors')
