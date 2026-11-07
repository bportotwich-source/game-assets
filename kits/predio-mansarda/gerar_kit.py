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
def stair_core_slab(top='floor',xl=None,xr=None,back=0.0):
    """4x4 m slab with the stair hole (x in [-1.35,1.35], full depth). Pivot: centre."""
    p=Piece(); h=CORE/2
    xl=-HOLE if xl is None else xl; xr=HOLE if xr is None else xr; p._sargs=(top,)
    for (a,b) in ((-h,xl),(xr,h)):
        p.box(top,a,b,-0.03 if top!='roof' else -0.04,0,-h,h); p.box('plaster',a+0.02,b-0.02,-SLAB,-0.03 if top!='roof' else -0.04,-h+0.02,h-0.02)
    if back>0.02:
        p.box(top,xl,xr,-0.03 if top!='roof' else -0.04,0,-h,-h+back); p.box('plaster',xl-0.02,xr+0.02,-SLAB,-0.03 if top!='roof' else -0.04,-h+0.02,-h+back)
    return p
def stairs_u(rise,run=2.0,w=1.2,gap=0.1,land=1.7,xl=None,xr=None):
    """U-shaped stair: flight A goes up toward -Z on the left, landing at the back, flight B returns on the right.
    Pivot: centre of the core's open (front) edge, at the lower floor level."""
    p=Piece(); n=round(rise/0.18); n+=n%2; k=n//2; st=rise/n; tr=run/k
    xa0,xa1=-gap/2-w,-gap/2; xb0,xb1=gap/2,gap/2+w
    p._uargs=dict(rise=rise,run=run,w=w,gap=gap,land=land); ow=0.04
    if xl is not None: xa0,xb1,ow=xl,xr,0.08   # flights run wall to wall
    for i in range(k-1):
        top=(i+1)*st; p.box('floor',xa0,xa1,top-0.04,top,-(i+1)*tr,-i*tr); p.box('plaster',xa0,xa1,top-0.26,top-0.04,-(i+1)*tr,-i*tr)
    mid=k*st
    p.box('floor',xa0,xb1,mid-0.04,mid,-run-land,-run+tr); p.box('plaster',xa0,xb1,mid-0.24,mid-0.04,-run-land,-run+tr)
    for j in range(1,k):
        top=mid+j*st
        p.box('floor',xb0,xb1,top-0.04,top,-run+(j)*tr,-run+(j+1)*tr); p.box('plaster',xb0,xb1,top-0.26,top-0.04,-run+(j)*tr,-run+(j+1)*tr)
    # handrails (inner pair + outer pair)
    for x in (xa0+ow,xa1-0.04):
        p.seg('iron',(x,0.9,0),(x,mid+0.9,-run),0.05)
    for x in (xb0+0.04,xb1-ow):
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
# KIT 2: classic stone townhouses with mansard roof (two attached houses, A and B)
# =====================================================================================
COL.update({'ashlar':(232,216,182),'rustic':(222,204,170),'zinc':(108,120,138),'trim':(242,232,206),
            'door':(46,62,96),'door_b':(132,44,40),'pot':(190,104,74),'iron':(40,38,40)})
def ashlar_texture(px=256,seed=11):
    # tile 1 x 1 m: two 0.5 m courses of 1.0 m blocks, running bond, fine joints
    rnd=random.Random(seed); im=Image.new('RGB',(px,px),(206,188,152)); d=ImageDraw.Draw(im); m=max(2,int(px*0.008))
    base=[(234,218,184),(228,211,176),(238,223,190),(230,214,180)]
    for r in range(2):
        off=px/2 if r%2 else 0; y0=r*px/2
        for i in range(-1,2):
            c=rnd.choice(base); x0=i*px+off
            for dx in (-px,0,px): d.rectangle([x0+dx+m/2,y0+m/2,x0+dx+px-m/2,y0+px/2-m/2],fill=c)
    a=np.asarray(im,dtype=np.float32); n=_noise(px,10,seed)+0.6*_noise(px,48,seed+1)
    return Image.fromarray(np.clip(a+n[...,None]*14,0,255).astype(np.uint8)).transpose(Image.FLIP_TOP_BOTTOM)
def rustic_texture(px=256,seed=13):
    # tile 1.0 x 0.8 m: rusticated base, deep horizontal grooves every 0.4 m, staggered vertical joints
    h=int(px*0.8); im=Image.new('RGB',(px,h),(150,134,108)); d=ImageDraw.Draw(im); g=max(4,int(px*0.03)); m=max(2,int(px*0.01))
    rnd=random.Random(seed); base=[(224,206,172),(218,200,166),(228,211,178)]
    for r in range(2):
        off=px/2 if r%2 else 0; y0=r*h/2
        for i in range(-1,2):
            c=rnd.choice(base); x0=i*px+off
            for dx in (-px,0,px):
                d.rectangle([x0+dx+m/2,y0+g/2,x0+dx+px-m/2,y0+h/2-g/2],fill=c)
                d.rectangle([x0+dx+m/2,y0+h/2-g/2-max(2,g*0.4),x0+dx+px-m/2,y0+h/2-g/2],fill=tuple(int(v*0.9) for v in c))
    a=np.asarray(im,dtype=np.float32); n=_noise(px,10,seed)[:h]+0.6*_noise(px,48,seed+1)[:h]
    return Image.fromarray(np.clip(a+n[...,None]*14,0,255).astype(np.uint8)).transpose(Image.FLIP_TOP_BOTTOM)
def zinc_texture(px=256,seed=17):
    # tile 1 x 1 m: standing seams every 0.5 m (vertical in the texture)
    n=_noise(px,8,seed)*0.6+_noise(px,64,seed+1)*0.3
    a=np.array([108,120,138],np.float32)[None,None,:]+n[...,None]*14
    for s in (0,px//2):
        a[:,max(0,s-2):s+2]=[86,96,112]; a[:,s+2:s+4]=[150,162,178]
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
ASHLAR_TEX=ashlar_texture(); RUSTIC_TEX=rustic_texture(); ZINC_TEX=zinc_texture()
for nm,im in (('ashlar',ASHLAR_TEX),('rustic',RUSTIC_TEX),('zinc',ZINC_TEX)): im.save(os.path.join(OUT,nm+'_texture.png'))
TEX={'ashlar':(ASHLAR_TEX,1.0,1.0),'rustic':(RUSTIC_TEX,1.0,0.8),'zinc':(ZINC_TEX,1.0,1.0),'plaster':(PLASTER_TEX,1.0,1.0)}
MATS = {k:PBRMaterial(name=k, baseColorFactor=[c/255 for c in v]+[1.0], metallicFactor=0.0, roughnessFactor=0.9) for k,v in COL.items()}
for k,(im,_,_) in TEX.items(): MATS[k]=PBRMaterial(name=k,baseColorTexture=im,baseColorFactor=[255,255,255,255],metallicFactor=0.0,roughnessFactor=0.9)

from shapely.geometry import Point
from shapely.ops import unary_union
RAISE=0.54            # ground floor 3 steps above the street
HW=RAISE+HG           # ground facade module height (street to first floor)
K=1/3.0               # mansard slope: 1 m inset for 3 m of height
MH=3.03               # mansard module height (3 cm zinc lip above the roof deck)
def lvl(fl): return RAISE if fl==0 else RAISE+HG+(fl-1)*H
def ext(p,mat,poly,z0,z1):
    for g in getattr(poly,'geoms',[poly]):
        if g.area<1e-6: continue
        m=trimesh.creation.extrude_polygon(g,z1-z0); m.apply_translation([0,0,z0]); p.add(mat,m)
def hull(p,mat,pts): p.add(mat,trimesh.convex.convex_hull(np.array(pts,float)))
def arch_half(cx,cy,r0,r1,n=24):
    a=np.linspace(0,math.pi,n); o=[(cx+r1*math.cos(t),cy+r1*math.sin(t)) for t in a]; i=[(cx+r0*math.cos(t),cy+r0*math.sin(t)) for t in a[::-1]]
    return Polygon(o+i)
def half_disc(cx,cy,r,n=24):
    a=np.linspace(0,math.pi,n); return Polygon([(cx+r*math.cos(t),cy+r*math.sin(t)) for t in a])
def arch_opening(p,mat,ow,oy0,spring,h):
    """Wall module with a round-arched opening (rect up to spring + half circle). Spandrels fill the corners."""
    r=ow/2; wall_with_opening(p,mat,ow,oy0,spring+r,h)
    sp=sbox(-r,spring,r,spring+r).difference(Point(0,spring).buffer(r,resolution=24))
    ext(p,mat,sp,-T+0.02,0.0); ext(p,'plaster',sp,-T,-T+0.02)
    ext(p,'trim',arch_half(0,spring,r,r+0.12),0.0,0.03); p.box('trim',-0.09,0.09,spring+r-0.04,spring+r+0.2,0.0,0.06)  # moulding + keystone
def arch_glazing(p,ow,spring,glass=True,gy=0.0):
    r=ow/2
    ext(p,'frame',arch_half(0,spring,r-0.07,r),-0.18,-0.06)
    if glass: ext(p,'glass',half_disc(0,spring,r-0.07).intersection(sbox(-r,spring+gy,r,spring+r)),-0.16,-0.14)
def wall_ground_arch_window():
    p=Piece(); sill=RAISE+0.9; spring=RAISE+2.3
    arch_opening(p,'rustic',0.9,sill,spring,HW); window(p,0.9,sill,spring,lintel=None); arch_glazing(p,0.9,spring)
    ledge(p,HW,th=0.2,d=0.08); water_table(p); return p
def wall_ground_rect_window():
    p=Piece(); sill=RAISE+0.9; top=RAISE+2.4
    wall_with_opening(p,'rustic',0.9,sill,top,HW); window(p,0.9,sill,top,lintel='trim')
    p.box('trim',-0.09,0.09,top+0.01,top+0.24,0.0,0.06); ledge(p,HW,th=0.2,d=0.08); water_table(p); return p
def wall_ground_plain():
    p=Piece(); wall_with_opening(p,'rustic',0,0,0,HW); ledge(p,HW,th=0.2,d=0.08); water_table(p); return p
def water_table(p,gap=0.0):
    """Stone band at floor level (hides the raised ground slab edge)."""
    if gap: p.box('trim',-W/2,-gap/2,0.25,0.57,0,0.03); p.box('trim',gap/2,W/2,0.25,0.57,0,0.03)
    else: p.box('trim',-W/2,W/2,0.25,0.57,0,0.03)
def stoop(p,w=1.6):
    for i,(y,d) in enumerate(((0.18,0.9),(0.36,0.6),(0.54,0.3))): p.box('trim',-w/2,w/2,y-0.18 if i==0 else 0,y,0,d)
def wall_ground_arch_door():
    p=Piece(); ow=1.1; x=ow/2; oy0=RAISE+0.015; spring=RAISE+2.3
    arch_opening(p,'rustic',ow,oy0,spring,HW)
    p.box('frame',-x,-x+0.07,oy0,spring,-0.22,0.02); p.box('frame',x-0.07,x,oy0,spring,-0.22,0.02); p.box('frame',-x,x,spring,spring+0.07,-0.22,0.02)
    arch_glazing(p,ow,spring,gy=0.07); stoop(p); ledge(p,HW,th=0.2,d=0.08); water_table(p,1.6); return p
def wall_ground_rect_door():
    p=Piece(); ow=1.1; x=ow/2; oy0=RAISE+0.015; top=RAISE+2.42
    wall_with_opening(p,'rustic',ow,oy0,top,HW)
    p.box('frame',-x,-x+0.07,oy0,top,-0.22,0.02); p.box('frame',x-0.07,x,oy0,top,-0.22,0.02); p.box('frame',-x,x,top-0.07,top,-0.22,0.02)
    p.box('trim',-x-0.12,x+0.12,top+0.01,top+0.16,-0.02,0.05); p.box('trim',-x-0.18,x+0.18,top+0.16,top+0.24,-0.02,0.12)  # door hood
    stoop(p); ledge(p,HW,th=0.2,d=0.08); water_table(p,1.6); return p
def hood(p,ow,oy1):
    p.box('trim',-ow/2-0.14,ow/2+0.14,oy1+0.15,oy1+0.24,-0.02,0.12)
def wall_ashlar_window():
    p=Piece(); wall_with_opening(p,'ashlar',0.9,0.85,2.3,H); window(p,0.9,0.85,2.3); hood(p,0.9,2.3); ledge(p,H,th=0.08,d=0.04); return p
def wall_ashlar_plain():
    p=Piece(); wall_with_opening(p,'ashlar',0,0,0,H); ledge(p,H,th=0.08,d=0.04); return p
def wall_ashlar_balconette():
    p=Piece(); wall_with_opening(p,'ashlar',0.9,0.3,2.4,H); window(p,0.9,0.3,2.4); hood(p,0.9,2.4)
    railing(p,-0.5,0.5,0.0,0.07,0.33,h=0.8,sides=(True,False,False),n=8); ledge(p,H,th=0.08,d=0.04); return p
def wall_ashlar_french():
    p=Piece(); wall_with_opening(p,'ashlar',0.9,0.05,2.35,H); window(p,0.9,0.05,2.35,sill_top=0.015,glass=False,mull=False); hood(p,0.9,2.35)
    ledge(p,H,th=0.08,d=0.04); return p
def balcony_band():
    """2 m of continuous stone balcony with iron railing on the front edge. Pivot: bottom-centre at the facade."""
    p=Piece(); d=0.6
    p.box('trim',-W/2,W/2,-0.12,0.0,0,d); p.box('trim',-W/2,W/2,-0.2,-0.12,0,d-0.08)
    for xx in (-0.5,0.5): p.box('trim',xx-0.06,xx+0.06,-0.45,-0.2,0,0.35)   # brackets
    railing(p,-W/2+0.02,W/2-0.02,0.02,d-0.03,0.0,h=1.0,sides=(True,False,False),n=16); return p
def balcony_side_rail():
    p=Piece(); railing(p,-0.02,0.02,0.02,0.57,0.0,h=1.0,sides=(False,True,False),n=5); return p
def cornice_mansard(corner_=False):
    p=Piece()
    if corner_:
        p.box('trim',-T,0.32,-0.3,0.0,-T,0.32); p.box('trim',-T,0.18,-0.42,-0.3,-T,0.18)
    else:
        p.box('trim',-W/2,W/2,-0.3,0.0,0,0.32); p.box('trim',-W/2,W/2,-0.42,-0.3,0,0.18)
        for i in range(8):
            cx=-W/2+W/16+i*W/8; p.box('trim',cx-0.04,cx+0.04,-0.3,-0.2,0.32,0.36)  # dentils under the drip edge
    return p
def _shear(mesh):
    v=mesh.vertices.copy(); v[:,2]=v[:,2]-v[:,1]*K; mesh.vertices=v; return mesh
def mansard_panel(p,x0,x1,hole=None,miter=False):
    """Sloped zinc panel 0.3 m thick (horizontal), outer face from z=0 at the bottom to z=-1 at 3 m.
    hole=(hx,y0,y1) cuts a dormer opening. miter=True tapers the +x end along the hip (corner piece)."""
    ws=[-T,-T+0.02,0.0]
    if hole:
        hx,y0,y1=hole; xs=[x0,-hx,hx,x1]; ys=[0.0,y0,y1,MH]
        def cell(i,j,k): return None if (i==1 and j==1) else ('plaster' if k==0 else 'zinc')
    else:
        xs=[x0,x1]; ys=[0.0,MH]
        def cell(i,j,k): return 'plaster' if k==0 else 'zinc'
    for m,mesh in grid_solid(xs,ys,ws,cell).items():
        mesh=_shear(mesh)
        if miter:
            v=mesh.vertices.copy(); e=np.isclose(v[:,0],x1); v[e,0]=x1+v[e,2]; mesh.vertices=v
        p.add(m,mesh)
def mansard_plain():
    p=Piece(); mansard_panel(p,-W/2,W/2); return p
def mansard_corner():
    """Hip corner: two mitred 2 m panels meeting at the building corner (pivot), faces +Z and +X."""
    p=Piece(); q=Piece(); mansard_panel(q,-2.0,0.0,miter=True)
    for k,ms in q.parts.items():
        for m in ms:
            p.add(k,m.copy())
            s=m.copy(); v=s.vertices.copy(); s.vertices=v[:,[2,1,0]]; s.invert(); p.add(k,s)
    return p
def mansard_dormer():
    """Mansard module with a dormer: vertical stone front with window, zinc cheeks, segmental zinc cap."""
    p=Piece(); hx=0.6; mansard_panel(p,-W/2,W/2,hole=(hx,0.35,2.3))
    fz0,fz1=-0.25,-0.1; top=2.45
    xs=[-0.8,-0.45,0.45,0.8]; ys=[0.3,0.9,2.15,top]; zs=[fz0,fz0+0.02,fz1]
    def cell(i,j,k): return None if (i==1 and j==1) else ('plaster' if k==0 else 'ashlar')
    for m,mesh in grid_solid(xs,ys,zs,cell).items(): p.add(m,mesh)
    w=Piece(); window(w,0.9,0.9,2.15)
    for k,ms in w.parts.items():
        for m in ms: mm=m.copy(); mm.apply_translation([0,0,-0.07]); p.add(k,mm)
    ct=2.55
    for sx in (-1,1):
        for (a,b,mat) in ((hx-0.01,0.67,'plaster'),(0.67,0.75,'zinc')):
            xa,xb=sorted((sx*a,sx*b))
            pts=[(x,y,z) for x in (xa,xb) for (z,y) in ((-0.2,0.3),(-0.2,ct),(-0.2-(ct-0.3)*K,ct))]
            hull(p,mat,pts)
    # segmental cap + tympanum
    c=0.9; sag=0.35; R=(c*c+sag*sag)/(2*sag); cy=top+sag-R; a0=math.asin(c/R)
    ang=np.linspace(math.pi/2+a0,math.pi/2-a0,20)
    outer=[(R*math.cos(t)*1.0,cy+(R+0.08)*math.sin(t)) for t in ang]
    outer=[(x*(R+0.08)/R,y) for (x,y) in outer]
    inner=[(R*math.cos(t),cy+R*math.sin(t)) for t in ang[::-1]]
    ext(p,'zinc',Polygon(outer+inner).buffer(0),-1.05,0.02)
    tym=Polygon([(R*math.cos(t),cy+R*math.sin(t)) for t in ang]).intersection(sbox(-0.8,top,0.8,top+sag+0.01))
    ext(p,'ashlar',tym,fz0+0.02,fz1); ext(p,'plaster',tym,fz0,fz0+0.02)
    p.box('trim',-0.86,0.86,top-0.06,top,fz1,fz1+0.06)   # cornice line under the cap
    return p
def interior_wall_end_attic(h=H-SLAB):
    """End wall for the mansard floor: its outer edge follows the sloped roof (1 cm clear)."""
    p=Piece(); t=0.12; e=W/2-T-0.01
    ext(p,'plaster',Polygon([(-W/2,0),(e,0),(e-h*K,h),(-W/2,h)]),-t/2,t/2)
    p.box('trim',-W/2,e-0.04,0,0.1,t/2,t/2+0.015); p.box('trim',-W/2,e-0.04,0,0.1,-t/2-0.015,-t/2); return p
def roof_cap(wx,dz,h=1.0):
    """Low hipped zinc cap over one house. Pivot: centre of base on the roof deck."""
    p=Piece(); x=wx/2; z=dz/2; r=max(0.0,z-x)
    hull(p,'zinc',[(-x,0,-z),(x,0,-z),(-x,0,z),(x,0,z),(0,h,-r),(0,h,r)]); return p
def chimney():
    p=Piece(); p.box('ashlar',-0.4,0.4,0,2.4,-0.8,0.8); p.box('trim',-0.48,0.48,2.4,2.55,-0.88,0.88)
    for zz in (-0.5,0,0.5): p.cyl('pot',0.11,2.55,2.9,0,zz,10)
    return p

def stair_core_rail(z0=-1.98):
    p=Piece(); railing(p,-0.02,0.02,z0,1.98,0,sides=(False,True,False),n=int((1.98-z0)/0.165)); return p
def corner_ground():
    p=corner('rustic',HW,0.2,0.08,True); e=0.03; p.box('trim',-T,e+0.03,0.25,0.57,-T,e+0.03); return p
import sys as _s; _s.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts', 'detalhe'))
import retrofit
retrofit.aplicar(globals(), {'ashlar': 'stone', 'rustic': 'stone', 'zinc': None, 'plaster': 'plaster'})
pieces={'floor_tile':floor_tile(),'floor_tile_bath':floor_tile_bath(),'stair_core_slab':stair_core_slab(),'stair_core_rail':stair_core_rail(),'stair_core_rail_attic':stair_core_rail(-1.2),
 'stairs_u_3m':stairs_u(H),'stairs_u_3m2':stairs_u(HG),
 'door_leaf_entrance':door_leaf(0.96,2.28),'door_leaf_entrance_b':door_leaf(0.96,2.32,True,'door_b'),'door_leaf_interior':door_leaf(0.86,2.08,False,'frame'),'door_leaf_balcony':door_leaf_balcony(),
 'interior_wall_plain':interior_wall(False),'interior_wall_doorway':interior_wall(True),'interior_wall_end':interior_wall_end(),'interior_wall_end_attic':interior_wall_end_attic(),
 'interior_wall_plain_ground':interior_wall(False,HG-SLAB),'interior_wall_doorway_ground':interior_wall(True,HG-SLAB),'interior_wall_end_ground':interior_wall_end(HG-SLAB),
 'wall_ground_arch_window':wall_ground_arch_window(),'wall_ground_rect_window':wall_ground_rect_window(),'wall_ground_plain':wall_ground_plain(),
 'wall_ground_arch_door':wall_ground_arch_door(),'wall_ground_rect_door':wall_ground_rect_door(),'corner_ground':corner_ground(),
 'wall_ashlar_window':wall_ashlar_window(),'wall_ashlar_plain':wall_ashlar_plain(),'wall_ashlar_balconette':wall_ashlar_balconette(),'wall_ashlar_french':wall_ashlar_french(),
 'corner_ashlar':corner('ashlar',H,0.08,0.04),'balcony_band':balcony_band(),'balcony_side_rail':balcony_side_rail(),
 'cornice_mansard':cornice_mansard(),'cornice_mansard_corner':cornice_mansard(True),
 'mansard_plain':mansard_plain(),'mansard_dormer':mansard_dormer(),'mansard_corner':mansard_corner(),
 'roof_tile':roof_tile(),'roof_cap_a':roof_cap(9.0,10.0),'roof_cap_b':roof_cap(7.0,10.0),'chimney':chimney(),'player_scale_ref':player_ref(),
}
import shutil; shutil.rmtree(f'{OUT}/pieces',ignore_errors=True); os.makedirs(f'{OUT}/pieces')
for n,p in pieces.items(): p.scene(n).export(f'{OUT}/pieces/{n}.glb',include_normals=True)

# ================= assembly: 18 x 12 m, house A x in [-9,1] (corner), house B x in [1,9] =================
SX,SZ=9.0,6.0
L=[]
def put(n,x,y,z,ry=0,tags=(),door=None):
    e={'piece':n,'pos':[round(x,3),round(y,3),round(z,3)],'rotY':ry,'tags':list(tags)}
    if door is not None: e['door']={'closed':ry,'open':ry+door}; e['tags'].append('door')
    L.append(e)
def hinge(x,z,ry,lx,lz):
    r=math.radians(ry); return x+lx*math.cos(r)+lz*math.sin(r), z-lx*math.sin(r)+lz*math.cos(r)
def ftag(fl): return f'floor{fl}'
FB=[-8,-6,-4,-2,0,2,4,6,8]; SB=[-5,-3,-1,1,3,5]
CORE_BAYS={('back',-4),('back',-2),('back',6),('right',-3)}   # facade bays in front of the two stair cores
faces=[(0,FB,lambda u:(u,SZ),'front'),(90,SB,lambda u:(SX,-u),'right'),(180,FB,lambda u:(-u,-SZ),'back'),(-90,SB,lambda u:(-SX,u),'left')]
for ry,bays,f,tag in faces:
    for u in bays:
        x,z=f(u); wpos=x if tag in ('front','back') else z
        core=(tag,wpos) in CORE_BAYS; houseA=(x<1) if tag in ('front','back') else tag=='left'
        # ground
        if tag=='front' and x==0: n='wall_ground_arch_door'
        elif tag=='front' and x==6: n='wall_ground_rect_door'
        elif core: n='wall_ground_plain'
        else: n='wall_ground_arch_window' if houseA else 'wall_ground_rect_window'
        put(n,x,0,z,ry,[tag,'ext',ftag(0)])
        put('wall_ashlar_plain' if core else ('wall_ashlar_balconette' if tag=='front' else 'wall_ashlar_window'),x,lvl(1),z,ry,[tag,'ext',ftag(1)])
        put('wall_ashlar_plain' if core else ('wall_ashlar_french' if tag=='front' else 'wall_ashlar_window'),x,lvl(2),z,ry,[tag,'ext',ftag(2)])
        put('cornice_mansard',x,lvl(3),z,ry,[tag,'ext',ftag(2)])
        if abs(u)<(8 if tag in ('front','back') else 5):
            put('mansard_plain' if core else 'mansard_dormer',x,lvl(3),z,ry,[tag,'ext',ftag(3)])
for ry,x,z,tg in [(0,SX,SZ,('front','right')),(90,SX,-SZ,('right','back')),(180,-SX,-SZ,('back','left')),(-90,-SX,SZ,('left','front'))]:
    put('corner_ground',x,0,z,ry,tg+('ext',ftag(0)))
    for fl in (1,2): put('corner_ashlar',x,lvl(fl),z,ry,tg+('ext',ftag(fl)))
    put('cornice_mansard_corner',x,lvl(3),z,ry,tg+('ext',ftag(2)))
    put('mansard_corner',x,lvl(3),z,ry,tg+('ext',ftag(3)))
# continuous balcony on the second floor front
for x in FB: put('balcony_band',x,lvl(2)+0.05,SZ,0,['front','ext',ftag(2)])
for x in (-SX+0.03,SX-0.03): put('balcony_side_rail',x,lvl(2)+0.05,SZ,0,['front','ext',ftag(2)])
# french-door leaves
for e in [e for e in L if e['piece']=='wall_ashlar_french']:
    hx,hz=hinge(e['pos'][0],e['pos'][2],e['rotY'],-0.38,-0.12)
    put('door_leaf_balcony',hx,e['pos'][1]+0.12,hz,e['rotY'],[t for t in e['tags'] if t!='door'],door=80)
# slabs; stair cores: A x in [-5,-1], B x in [5,9], both z in [-6,-2]
CORES={(-4,-5),(-2,-5),(-4,-3),(-2,-3),(6,-5),(8,-5),(6,-3),(8,-3)}
BATH={0:{(-2,3),(-2,5),(2,-1)},1:{(-8,-1),(2,-1)},2:{(-8,-1),(2,-1)},3:{(-8,-1),(2,-1)}}
for fl in range(0,4):
    y=lvl(fl)
    for a in FB:
        for b in SB:
            if fl>0 and (a,b) in CORES: continue
            put('floor_tile_bath' if (a,b) in BATH[fl] else 'floor_tile',a,y,b,0,[ftag(fl)])
    if fl>0:
        for cx in (-3,7):
            put('stair_core_slab',cx,y,-4,0,[ftag(fl)]); rn='stair_core_rail_attic' if fl==3 else 'stair_core_rail'; put(rn,cx-1.4,y,-4,0,[ftag(fl)]); put(rn,cx+1.4,y,-4,0,[ftag(fl)])
for cx in (-3,7):
    put('stairs_u_3m2',cx,lvl(0),-2,0,[ftag(0)])
    for fl in (1,2): put('stairs_u_3m',cx,lvl(fl),-2,0,[ftag(fl)])
# roof deck (inset 1 m by the mansard), caps and chimneys
for a in range(-7,8,2):
    for b in range(-4,5,2): put('roof_tile',a,lvl(4),b,0,['roof'])
put('roof_cap_a',-3.5,lvl(4),0,0,['roof']); put('roof_cap_b',4.5,lvl(4),0,0,['roof'])
for (x,z) in ((1,3),(1,-3),(-6.5,0),(6.5,0)): put('chimney',x,lvl(4),z,0,['roof'])
# interior walls
def wl(fl,x0,z0,x1,z1,doors=()):
    y=lvl(fl); g='_ground' if fl==0 else ''; endn='interior_wall_end_attic' if fl==3 else 'interior_wall_end'+g
    if z0==z1:
        for c in range(int(min(x0,x1))+1,int(max(x0,x1)),2):
            if c not in doors and abs(c)+1>=SX: put(endn,c,y,z0,0 if c>0 else 180,[ftag(fl)]); continue
            put(('interior_wall_doorway' if c in doors else 'interior_wall_plain')+g,c,y,z0,0,[ftag(fl)])
    else:
        for c in range(int(min(z0,z1))+1,int(max(z0,z1)),2):
            if c not in doors and abs(c)+1>=SZ: put(endn,x0,y,c,-90 if c>0 else 90,[ftag(fl)]); continue
            put(('interior_wall_doorway' if c in doors else 'interior_wall_plain')+g,x0,y,c,90,[ftag(fl)])
def door(fl,x,z,ry,ang=70):
    hx,hz=hinge(x,z,ry,-0.43,0); put('door_leaf_interior',hx,lvl(fl),hz,ry,[ftag(fl)],door=ang)
for fl in range(4): wl(fl,1,-6,1,6)          # party wall between the houses
# ---- house A, ground: lobby + hall, studio (front), storage, bike room
wl(0,-9,0,-1,0); wl(0,-1,0,-1,6,doors=(1,)); wl(0,-3,2,-1,2,doors=(-2,)); wl(0,-3,2,-3,6)
wl(0,-5,-6,-5,0,doors=(-1,)); wl(0,-1,-6,-1,-2); wl(0,-1,-2,1,-2,doors=(0,))
door(0,-1,1,90); door(0,-2,2,0); door(0,-5,-1,90,-70); door(0,0,-2,0)
# ---- house A, floors 1-2: 3-bedroom flat; attic: two studios
for fl in (1,2,3):
    attic=fl==3
    wl(fl,-9,0,-1,0,doors=(-6,-4,-2) if attic else (-6,-2)); wl(fl,-3,0,-3,6,doors=() if attic else (1,))
    wl(fl,-3,2,1,2,doors=(-2,0)); wl(fl,-1,2,-1,6); wl(fl,-9,-2,-5,-2,doors=(-6,)); wl(fl,-7,-2,-7,0,doors=(-1,))
    wl(fl,-5,-6,-5,0); wl(fl,-1,-6,-1,0); wl(fl,-1,-2,1,-2,doors=(0,))
    door(fl,-6,0,0); door(fl,-2,0,0); door(fl,-2,2,0); door(fl,0,2,0); door(fl,-6,-2,0); door(fl,-7,-1,90); door(fl,0,-2,0)
    if attic: door(fl,-4,0,0)
    else: door(fl,-3,1,90)
# ---- house B, ground: hall, 1-bedroom flat, storage room
wl(0,7,0,7,6,doors=(3,)); wl(0,7,0,9,0); wl(0,5,0,5,6); wl(0,5,-2,5,0,doors=(-1,)); wl(0,5,-6,5,-2)
wl(0,1,2,5,2,doors=(2,4)); wl(0,3,-2,3,2,doors=(-1,1)); wl(0,1,0,3,0); wl(0,1,-2,5,-2,doors=(4,))
door(0,7,3,90,-70); door(0,5,-1,90,-70); door(0,2,2,0); door(0,4,2,0); door(0,3,-1,90); door(0,3,1,90); door(0,4,-2,0)
# ---- house B, floors 1-3: 2-bedroom flat (living on the corner)
for fl in (1,2,3):
    wl(fl,5,0,9,0,doors=(6,)); wl(fl,5,0,5,6,doors=(1,3)); wl(fl,5,-2,5,0); wl(fl,5,-6,5,-2)
    wl(fl,3,2,5,2); wl(fl,3,-2,3,6,doors=(-1,1)); wl(fl,1,0,3,0); wl(fl,1,-2,5,-2,doors=(4,))
    door(fl,6,0,0); door(fl,5,1,90,-70); door(fl,5,3,90,-70); door(fl,3,-1,90); door(fl,3,1,90); door(fl,4,-2,0)
# entrance leaves
put('door_leaf_entrance',0-0.48,lvl(0)+0.015,SZ-0.18,0,['front','ext',ftag(0)],door=85)
put('door_leaf_entrance_b',6-0.48,lvl(0)+0.015,SZ-0.18,0,['front','ext',ftag(0)],door=85)
# scale references
put('player_scale_ref',3,0,SZ+1.4); put('player_scale_ref',0,lvl(0),3,0,[ftag(0)]); put('player_scale_ref',-6,lvl(1),3,0,[ftag(1)]); put('player_scale_ref',-6,lvl(3),3,0,[ftag(3)])
# --- Stairs fill the whole core, wall to wall (Bruno, 2026-11-07) ---
_CORE_SAVE=CORE; CORE=4.0
def _wall_face(cx,y,cz,side):
    best=None
    for e in L:
        x,yy,z=e['pos']
        if abs(yy-y)<0.6 and abs(x-(cx+2*side))<0.05 and e['rotY'] in (90,-90,270) and any(k in e['piece'] for k in ('wall','partition')) and abs(z-cz)<=1.05:
            f=CORE/2-0.06-0.02 if 'interior' in e['piece'] else CORE/2-T-0.02   # clear of the skirting
            best=f if best is None else min(best,f)
    return best
_new={}; _holes=[]; pieces_src=dict(pieces)
for e in L:
    if not hasattr(pieces.get(e['piece']),'_uargs'): continue
    cx,y,zf=e['pos']; cz=zf-CORE/2
    fl=_wall_face(cx,y,cz,-1) or CORE/2-T; fr=_wall_face(cx,y,cz,1) or CORE/2-T
    n=f"{e['piece']}_{int(round(fl*100))}_{int(round(fr*100))}"
    if n not in _new: _new[n]=stairs_u(**pieces[e['piece']]._uargs,xl=-fl,xr=fr)
    _holes.append((cx,y,zf,fl,fr,e['piece'])); e['piece']=n
_keep=[]
for e in L:
    pc=pieces.get(e['piece'])
    cx,y,cz=e['pos']
    if hasattr(pc,'_sargs') or e['piece'].startswith('stair_core_rail'):
        dx=0.0 if hasattr(pc,'_sargs') else 1.4
        below=[h for h in _holes if abs(abs(h[0]-cx)-dx)<0.3 and abs(h[2]-CORE/2-cz)<0.3 and h[1]<y-0.5]
        hx=None if not below else max(below,key=lambda h:h[1])
        if hx is None: _keep.append(e); continue
        fl,fr=hx[3],hx[4]
        if hasattr(pc,'_sargs'):
            n=f"{e['piece']}_{int(round(fl*100))}_{int(round(fr*100))}"
            _in=lambda v: v+0.03 if v<CORE/2-0.1 else v+0.02   # slab edge sits at the wall face (tucked 1 cm into exterior walls)
            ua=pieces_src[hx[5]]._uargs; bk=round(min(0.29,CORE-ua['run']-ua['land']),3)   # stops 1 cm inside the 0.3 m back wall
            n=f"{n}_{int(round(bk*100))}"
            if n not in _new: _new[n]=stair_core_slab(*pc._sargs,xl=-_in(fl),xr=_in(fr),back=bk)
            e['piece']=n
        else:
            side=1 if cx>hx[0] else -1
            if _wall_face(hx[0],y,cz,side) is not None: continue   # the wall already closes this side
            if any('hut' in o['piece'] and abs(o['pos'][1]-y)<0.6 and abs(o['pos'][0]-hx[0])<1.0 and abs(o['pos'][2]-cz)<1.0 for o in L): continue   # inside a roof hut
            e['pos'][0]=round(hx[0]+side*((fr if side>0 else fl)+0.05),3)   # on the slab strip, clear of the hole
    _keep.append(e)
L[:]=_keep
_used={e['piece'] for e in L}
for n in [n for n in pieces if (hasattr(pieces[n],'_uargs') or hasattr(pieces[n],'_sargs')) and n not in _used]:
    del pieces[n]
    if __name__=='__main__' and os.path.exists(f'{OUT}/pieces/{n}.glb'): os.remove(f'{OUT}/pieces/{n}.glb')
pieces.update(_new)
if __name__=='__main__':
    for n,p in _new.items(): p.scene(n).export(f'{OUT}/pieces/{n}.glb',include_normals=True)
CORE=_CORE_SAVE

json.dump({'grid':{'module_width':W,'floor_height':H,'ground_floor_height':HG,'ground_floor_raise':RAISE,'wall_thickness':T,'slab':SLAB,'footprint':[2*SX,2*SZ],'mansard_slope':'1 m in 3 m'},'placements':L},open(f'{OUT}/building_layout.json','w'),indent=1)
asm=Piece()
for e in L:
    if e['piece']=='player_scale_ref': continue
    Tm=trimesh.transformations.rotation_matrix(math.radians(e['rotY']),[0,1,0]); Tm[:3,3]=e['pos']
    asm.merge(pieces[e['piece']],Tm)
print('triangulos no montado', retrofit.montar(pieces, L, f'{OUT}/building_assembled.glb')); retrofit.finalizar(f'{OUT}/pieces')
print(len(pieces),'pieces',len(L),'placements',sum(1 for e in L if 'door' in e),'doors')
