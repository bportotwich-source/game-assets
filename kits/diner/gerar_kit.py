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
    p=Piece(); n=math.ceil(rise/0.18-1e-9); n+=n%2; k=n//2; st=rise/n; tr=run/k
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
from shapely.ops import unary_union
KNEE=1.3
def lvl(fl): return fl*H
def ext(p,mat,poly,z0,z1):
    for g in getattr(poly,'geoms',[poly]):
        if g.geom_type!='Polygon' or g.area<1e-6: continue
        m=trimesh.creation.extrude_polygon(g,z1-z0); m.apply_translation([0,0,z0]); p.add(mat,m)
def hull(p,mat,pts): p.add(mat,trimesh.convex.convex_hull(np.array(pts,float)))
def beam(a,b,w=0.12):
    a,b=np.array(a,float),np.array(b,float); d=b-a; n=np.array([-d[1],d[0]])/np.linalg.norm(d)*w/2
    return Polygon([a+n,b+n,b-n,a-n])
def rect(x0,y0,x1,y1): return sbox(x0,y0,x1,y1)
def timber(p,polys,clip,cut=None,z0=0.0,z1=0.03):
    """Half-timber boards: union of beams, clipped to the wall outline, window holes cut out, 3 cm proud of the render."""
    U=unary_union(polys).intersection(clip)
    if cut is not None: U=U.difference(cut)
    ext(p,'timber',U,z0,z1)
def shutters(p,ow,oy0,oy1,z0=0.035):
    """A pair of open louvred shutters flat against the wall beside an opening."""
    w=ow/2
    for s in (-1,1):
        a,b=sorted((s*(ow/2+0.03),s*(ow/2+0.03+w)))
        p.box('shutter',a,b,oy0,oy1,z0,z0+0.035)
        n=int((oy1-oy0)/0.16)
        for i in range(1,n): y=oy0+i*(oy1-oy0)/n; p.box('shutter_dark',a+0.04,b-0.04,y-0.02,y+0.01,z0+0.035,z0+0.05)

HSP=4.0     # half span of the house roof (depth 8 m)
KR=1.0      # 45 degree pitch
TV=0.3
def roof_in(u,kr=KR): return 1.0+kr*u
def roof_out(u,kr=KR): return 1.0+TV+kr*u
def roof_panel(p,x0,x1,hole=None,hsp=HSP,kr=KR,over=0.4):
    """Roof slope for one module, eave overhang `over` to the ridge `hsp` m in. Grid (x,u,v): u in from the facade, v layer."""
    us=[-over,hsp]; vs=[0.0,0.02,TV]
    if hole:
        hx,u1=hole; xs=[x0,-hx,hx,x1]; us=[-over,u1,hsp]
        def cell(i,j,k): return None if (i==1 and j==0) else ('plaster' if k==0 else 'shingle')
    else:
        xs=[x0,x1]
        def cell(i,j,k): return 'plaster' if k==0 else 'shingle'
    for m,mesh in grid_solid(xs,us,vs,cell).items():
        v=mesh.vertices.copy(); u=v[:,1].copy(); w=v[:,2].copy()
        v[:,1]=1.0+kr*u+w; v[:,2]=-u; mesh.vertices=v
        p.add(m,mesh)
def roof_slope(**k): p=Piece(); roof_panel(p,-W/2,W/2,**k); return p
def roof_slope_end(**k): p=Piece(); roof_panel(p,-W/2,W/2+0.3,**k); return p
def roof_slope_end_l(**k): p=Piece(); roof_panel(p,-W/2-0.3,W/2,**k); return p
def roof_slope_dormer(): p=Piece(); roof_panel(p,-W/2,W/2,hole=(0.6,DORMER_U1)); return p
def ridge_cap(x0=-W/2,x1=W/2,hsp=HSP,kr=KR):
    p=Piece(); y=roof_out(hsp,kr); d=0.22
    hull(p,'ridge',[(x,yy,z) for x in (x0,x1) for (yy,z) in ((y-d*kr-0.04,d),(y-d*kr-0.04,-d),(y+0.08,0.0),(y-d*kr+0.06,d),(y-d*kr+0.06,-d))]); return p
def interior_wall_end_doorway(h=H-SLAB):
    p=Piece(); t=0.12; e=W/2-T
    xs=[-W/2,-0.45,0.45,e]; ys=[0.0,2.1,h]; zs=[-t/2,t/2]
    def cell(i,j,k): return None if (i==1 and j==0) else 'plaster'
    for m,mesh in grid_solid(xs,ys,zs,cell).items(): p.add(m,mesh)
    for xx in (-0.45,0.45): p.box('frame',xx-0.04,xx+0.04,0,2.14,-t/2-0.02,t/2+0.02)
    p.box('frame',-0.49,0.49,2.08,2.18,-t/2-0.02,t/2+0.02)
    for (a,b) in ((-W/2,-0.49),(0.49,e)): p.box('trim',a,b,0,0.1,t/2,t/2+0.015); p.box('trim',a,b,0,0.1,-t/2-0.015,-t/2)
    return p
def stair_core_rail():
    p=Piece(); railing(p,-0.02,0.02,-1.98,1.98,0,sides=(False,True,False),n=24); return p
def interior_wall_wide(h=H-SLAB,ow=1.6):
    """Wide cased opening (no door), e.g. living room to dining."""
    p=Piece(); t=0.12; wall_with_opening(p,'plaster',ow,0,2.2,h,inner='plaster',t=t,centered=True)
    for xx in (-ow/2,ow/2): p.box('frame',xx-0.04,xx+0.04,0,2.24,-t/2-0.02,t/2+0.02)
    p.box('frame',-ow/2-0.04,ow/2+0.04,2.18,2.28,-t/2-0.02,t/2+0.02)
    for a,b in ((-W/2,-ow/2-0.04),(ow/2+0.04,W/2)): p.box('trim',a,b,0,0.1,t/2,t/2+0.015); p.box('trim',a,b,0,0.1,-t/2-0.015,-t/2)
    return p
# =====================================================================================
# KIT 12: diner: streamlined stainless-steel diner, rounded ends, ribbon windows, entrance vestibule, roof sign
# =====================================================================================
COL.update({'steel':(206,212,218),'steel_dark':(150,158,166),'enamel':(52,96,160),'enamel_red':(176,48,46),'glass':(150,200,222),
            'frame':(226,230,234),'trim':(236,236,232),'roof_flat':(132,134,136),'floor_red':(184,62,56),'tile':(222,230,232),
            'door':(196,204,212),'door_service':(120,128,136),'concrete':(176,174,168),'sign_frame':(40,46,70)})
def checker_texture(px=256):
    # tile 1 x 1 m: black and white 0.25 m checkerboard, soft grout
    a=np.zeros((px,px,3),np.uint8); q=px//4
    for i in range(4):
        for j in range(4): a[i*q:(i+1)*q,j*q:(j+1)*q]=(238,236,230) if (i+j)%2==0 else (40,40,44)
    a[::q,:]=(150,150,150); a[:,::q]=(150,150,150)
    return Image.fromarray(a)
from PIL import ImageFont
SIGN_W,SIGN_H=4.0,1.1
def sign_texture(px=1024):
    h=int(px*SIGN_H/SIGN_W); im=Image.new('RGB',(px,h),(30,36,64)); d=ImageDraw.Draw(im)
    d.rectangle([12,12,px-13,h-13],outline=(236,220,180),width=10)
    f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',int(h*0.62))
    t='DINER'; bb=d.textbbox((0,0),t,font=f); tw,th=bb[2]-bb[0],bb[3]-bb[1]
    x0=(px-tw)//2-bb[0]; y0=(h-th)//2-bb[1]
    d.text((x0+8,y0+8),t,font=f,fill=(10,12,24)); d.text((x0,y0),t,font=f,fill=(214,60,56))
    return im   # sign UVs run bottom-up already, so no flip
CHECK_TEX=checker_texture(); SIGN_TEX=sign_texture()
for nm,im in (('checker',CHECK_TEX),('sign',SIGN_TEX)): im.save(os.path.join(OUT,nm+'_texture.png'))
TEX={'checker':(CHECK_TEX,1.0,1.0),'sign':(SIGN_TEX,1.0,1.0),'plaster':(PLASTER_TEX,1.0,1.0)}
MATS = {k:PBRMaterial(name=k, baseColorFactor=[c/255 for c in v]+[1.0], metallicFactor=0.0, roughnessFactor=0.9) for k,v in COL.items()}
for k,(im,_,_) in TEX.items(): MATS[k]=PBRMaterial(name=k,baseColorTexture=im,baseColorFactor=[255,255,255,255],metallicFactor=0.0,roughnessFactor=0.9)

HD=3.5             # wall height = roof top; the steel cornice rises above it as a low parapet
RF0,RF1=3.3,3.5    # roof slab underside and top
SX,SZ=6.0,4.0      # straight body x -6..6, z -4..4; rounded ends of radius 4 centred at x = +-6
RC=4.0
ARC=RC*math.pi/6   # 30 deg arc at the outer face
def diner_wall(p,x0,x1,kind='window'):
    """Diner wall between x0 and x1 (outer face z=0, inner -T): enamel skirt, fluted steel, ribbon window, blue band,
    rounded steel cornice. kind: window | small | plain | door | service."""
    c=(x0+x1)/2; zs=[-T,-T+0.02,0.0]
    if kind=='window': ow,oy0,oy1=(x1-x0)-0.2,0.9,2.3
    elif kind=='small': ow,oy0,oy1=0.8,1.4,2.2
    elif kind=='door': ow,oy0,oy1=1.1,0.015,2.4
    elif kind=='service': ow,oy0,oy1=1.0,0.015,2.2
    else: ow=0
    if ow:
        xs=[x0,c-ow/2,c+ow/2,x1]; ys=sorted(set([0.0,oy0,oy1,HD]))
        def cell(i,j,k):
            if i==1 and ys[j]>=oy0-1e-9 and ys[j+1]<=oy1+1e-9: return None
            return 'plaster' if k==0 else 'steel'
    else:
        xs=[x0,x1]; ys=[0.0,HD]
        def cell(i,j,k): return 'plaster' if k==0 else 'steel'
    for m,mesh in grid_solid(xs,ys,zs,cell).items(): p.add(m,mesh)
    door=kind in ('door','service')
    segs=[(x0,c-ow/2-0.06),(c+ow/2+0.06,x1)] if door else [(x0,x1)]      # skirt and flutes stop at a door
    for a,b in segs:
        p.box('enamel_red',a,b,0.0,0.5,0.0,0.025)
        for y in (0.6,0.7,0.8): p.box('steel_dark',a,b,y,y+0.03,0.0,0.012)
    if ow and not door:
        x=ow/2
        p.box('glass',c-x+0.03,c+x-0.03,oy0+0.03,oy1-0.03,-0.16,-0.14)   # edges hidden inside the frame
        p.box('frame',c-x,c+x,oy0,oy0+0.06,-0.18,-0.06); p.box('frame',c-x,c+x,oy1-0.06,oy1,-0.18,-0.06)
        for xx in ((c-x,c-x+0.06),(c+x-0.06,c+x)): p.box('frame',xx[0],xx[1],oy0,oy1,-0.18,-0.06)
        if kind=='window': p.box('frame',c-0.025,c+0.025,oy0,oy1,-0.17,-0.1)
        p.box('steel',c-x-0.04,c+x+0.04,oy0-0.05,oy0+0.015,-0.04,0.06)    # sill, 1.5 cm above the opening floor
    if door:
        x=ow/2
        p.box('frame',c-x,c-x+0.07,oy0,oy1,-0.24,0.03); p.box('frame',c+x-0.07,c+x,oy0,oy1,-0.24,0.03); p.box('frame',c-x,c+x,oy1-0.07,oy1,-0.24,0.03)
    p.box('enamel',x0,x1,2.45,2.95,0.0,0.025)
    for y in (2.55,2.7,2.85): p.box('steel',x0,x1,y,y+0.025,0.025,0.035)
    prof=[(0.0,2.95),(0.0,3.66),(0.02,3.66),(0.14,3.6),(0.21,3.45),(0.22,3.2),(0.17,3.02),(0.06,2.95)]   # rounded nose, outside the wall
    hull(p,'steel',[(xx,y,z) for xx in (x0,x1) for (z,y) in prof])
    hull(p,'steel',[(xx,y,z) for xx in (x0,x1) for (z,y) in ((-T-0.02,HD),(-T-0.02,3.66),(0.02,3.66),(0.02,HD))])   # cap over the wall top
    return p
def bend(p,R=RC):
    """Wrap a straight wall built over x in [0, ARC] (outer face z=0) around a circle: theta = x/R, radius R+z.
    Pivot: circle centre; the arc runs from +Z (theta 0) toward +X."""
    q=Piece()
    for mat,ms in p.parts.items():
        for m in ms:
            v,f=trimesh.remesh.subdivide_to_size(m.vertices,m.faces,max_edge=0.18)
            th=v[:,0]/R; r=R+v[:,2]
            nv=np.stack([r*np.sin(th),v[:,1],r*np.cos(th)],1)
            q.add(mat,trimesh.Trimesh(vertices=nv,faces=f,process=False))
    return q
def wall_curve():
    p=Piece(); diner_wall(p,0.0,ARC,'window'); return bend(p)
def wall_straight(kind):
    p=Piece(); diner_wall(p,-W/2,W/2,kind); return p
def sector(mat,r,y0,y1,a0=0.0,a1=math.pi/6,n=6):
    pts=[(0,0)]+[(r*math.sin(a0+(a1-a0)*i/n),r*math.cos(a0+(a1-a0)*i/n)) for i in range(n+1)]
    m=trimesh.creation.extrude_polygon(Polygon([(x,-z) for x,z in pts]),y1-y0)   # polygon in (x,-z), extruded along +Z
    m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0])); m.apply_translation([0,y0,0]); return m
def floor_curve():
    p=Piece(); p.add('floor_red',sector('floor_red',RC,-0.03,0.0)); p.add('plaster',sector('plaster',RC-0.02,-SLAB,-0.03)); return p
def roof_curve():
    p=Piece(); p.add('roof_flat',sector('roof_flat',RC,RF1-0.04,RF1)); p.add('plaster',sector('plaster',RC-0.02,RF0,RF1-0.04)); return p
def floor_checker():
    p=Piece(); p.box('checker',-W/2,W/2,-0.03,0,-W/2,W/2); p.box('plaster',-W/2+0.02,W/2-0.02,-SLAB,-0.03,-W/2+0.02,W/2-0.02); return p
def roof_flat():
    p=Piece(); p.box('roof_flat',-W/2,W/2,RF1-0.04,RF1,-W/2,W/2); p.box('plaster',-W/2+0.02,W/2-0.02,RF0,RF1-0.04,-W/2+0.02,W/2-0.02); return p
VD,VW,VH=1.8,1.2,3.0   # vestibule depth, half width, height
def vestibule():
    """Entrance vestibule in front of the door module: steel and glass box, flat roof with a blue fascia, glass front door
    opening 1.1 x 2.3 m. Pivot: centre of the door module at the facade, ground level; box toward +Z."""
    p=Piece(); t=0.1; z0=-0.02
    p.box('steel_dark',-VW+0.01,VW-0.01,-0.05,0.012,0.0,VD-0.01)                                   # floor
    for s in (-1,1):   # side walls: steel base, glass, steel top
        a,b=sorted((s*VW,s*(VW-t)))
        p.box('steel',a,b,0,0.9,z0,VD); p.box('steel',a,b,2.3,VH,z0,VD)
        p.box('glass',a+0.04,b-0.04,0.9,2.3,z0,VD-t)
        p.box('frame',a,b,0.9,2.3,VD-t-0.06,VD-t)
    xs=[-VW,-0.55,0.55,VW]; ys=[0.0,2.3,VH]; zs=[VD-t,VD]
    def cell(i,j,k): return None if (i==1 and j==0) else 'steel'
    for m,mesh in grid_solid(xs,ys,zs,cell).items(): p.add(m,mesh)
    p.box('frame',-0.55,-0.48,0.012,2.3,VD-t-0.02,VD+0.02); p.box('frame',0.48,0.55,0.012,2.3,VD-t-0.02,VD+0.02); p.box('frame',-0.55,0.55,2.23,2.3,VD-t-0.02,VD+0.02)
    p.box('enamel_red',-VW,-0.62,0.0,0.5,VD,VD+0.02); p.box('enamel_red',0.62,VW,0.0,0.5,VD,VD+0.02)
    p.box('steel',-VW-0.06,VW+0.06,VH,VH+0.18,z0,VD+0.06); p.box('enamel',-VW-0.08,VW+0.08,VH-0.3,VH+0.12,VD+0.06,VD+0.09)
    p.box('plaster',-VW+t,VW-t,VH-0.02,VH,z0,VD-t)                                  # ceiling
    return p
def roof_sign():
    """Roof sign: DINER panel in a dark frame on four steel legs. Pivot: centre on the roof surface."""
    p=Piece(); x=SIGN_W/2; y0=0.6; d=0.25
    p.box('sign',-x,x,y0,y0+SIGN_H,d-0.02,d)
    p.box('sign_frame',-x-0.08,x+0.08,y0-0.08,y0+SIGN_H+0.08,-d,d-0.02)
    p.box('sign_frame',-x-0.08,x+0.08,y0-0.08,y0,d-0.02,d+0.04); p.box('sign_frame',-x-0.08,x+0.08,y0+SIGN_H,y0+SIGN_H+0.08,d-0.02,d+0.04)
    for xx in (-x-0.08,x): p.box('sign_frame',xx,xx+0.08,y0,y0+SIGN_H,d-0.02,d+0.04)
    for xx in (-x+0.3,x-0.3):
        for zz in (-0.12,0.12): p.box('steel_dark',xx-0.05,xx+0.05,0.0,y0-0.08,zz-0.05,zz+0.05)
    return p
SIGN=(-SIGN_W/2,0.6,SIGN_W,SIGN_H)
def vent_stack():
    p=Piece(); p.cyl('steel',0.25,0,1.4,sec=16); p.cone('steel',0.4,1.4,1.7,sec=16); p.box('steel_dark',-0.5,0.5,0,0.08,-0.5,0.5); return p
def roof_hatch():
    p=Piece(); p.box('steel_dark',-0.5,0.5,0,0.35,-0.5,0.5); p.box('steel',-0.55,0.55,0.35,0.42,-0.55,0.55); return p
IH=RF0
pieces={'floor_checker':floor_checker(),'floor_tile_bath':floor_tile_bath(),'floor_curve':floor_curve(),'roof_flat':roof_flat(),'roof_curve':roof_curve(),
 'wall_diner_window':wall_straight('window'),'wall_diner_small_window':wall_straight('small'),'wall_diner_plain':wall_straight('plain'),
 'wall_diner_door':wall_straight('door'),'wall_diner_service_door':wall_straight('service'),'wall_diner_curve':wall_curve(),
 'vestibule':vestibule(),'roof_sign':roof_sign(),'vent_stack':vent_stack(),'roof_hatch':roof_hatch(),
 'door_leaf_front':door_leaf(0.96,2.36,True,'door'),'door_leaf_vestibule':door_leaf(0.96,2.26,True,'door'),'door_leaf_service':door_leaf(0.9,2.16,False,'door_service'),
 'door_leaf_interior':door_leaf(0.86,2.08,False,'frame'),
 'interior_wall_plain':interior_wall(False,h=IH),'interior_wall_doorway':interior_wall(True,h=IH),'interior_wall_wide':interior_wall_wide(h=IH),
 'interior_wall_end':interior_wall_end(h=IH),'interior_wall_end_doorway':interior_wall_end_doorway(h=IH),
 'player_scale_ref':player_ref(),
}
import shutil; shutil.rmtree(f'{OUT}/pieces',ignore_errors=True); os.makedirs(f'{OUT}/pieces')
for n,p in pieces.items(): p.scene(n).export(f'{OUT}/pieces/{n}.glb',include_normals=True)

# ================= assembly: 12 x 8 m straight body + two rounded ends (radius 4), front to +Z =================
L=[]
def put(n,x,y,z,ry=0,tags=(),door=None):
    e={'piece':n,'pos':[round(x,3),round(y,3),round(z,3)],'rotY':ry,'tags':list(tags)}
    if door is not None: e['door']={'closed':ry,'open':ry+door}; e['tags'].append('door')
    L.append(e)
def hinge(x,z,ry,lx,lz):
    r=math.radians(ry); return x+lx*math.cos(r)+lz*math.sin(r), z-lx*math.sin(r)+lz*math.cos(r)
FB=[-5,-3,-1,1,3,5]; SB=[-3,-1,1,3]
FRONT={-5:'wall_diner_window',-3:'wall_diner_window',-1:'wall_diner_window',1:'wall_diner_door',3:'wall_diner_window',5:'wall_diner_window'}
BACK={-5:'wall_diner_small_window',-3:'wall_diner_small_window',-1:'wall_diner_plain',1:'wall_diner_plain',3:'wall_diner_service_door',5:'wall_diner_small_window'}
for x in FB:
    put(FRONT[x],x,0,SZ,0,['front','ext']); put(BACK[x],x,0,-SZ,180,['back','ext'])
for k in range(12):
    cx=SX if k<6 else -SX
    put('wall_diner_curve',cx,0,0,30*k,['right' if k<6 else 'left','ext']+(['front'] if k in (0,1,10,11) else []))
    put('floor_curve',cx,0,0,30*k,['floor0']); put('roof_curve',cx,0,0,30*k,['roof'])
WC={(-5,-3),(-5,-1),(-3,-3),(-3,-1)}
for a in FB:
    for b in SB:
        put('floor_tile_bath' if (a,b) in WC else 'floor_checker',a,0,b,0,['floor0']); put('roof_flat',a,0,b,0,['roof'])
put('vestibule',1,0,SZ,0,['front','ext'])
put('roof_sign',-1.5,RF1,1.2,0,['roof']); put('vent_stack',4,RF1,-2.2,0,['roof']); put('roof_hatch',-1,RF1,-2,0,['roof'])
def wl(x0,z0,x1,z1,doors=(),wide=(),ends=()):
    if z0==z1:
        for c in range(int(min(x0,x1))+1,int(max(x0,x1)),2):
            put('interior_wall_wide' if c in wide else 'interior_wall_doorway' if c in doors else 'interior_wall_plain',c,0,z0,0,['floor0'])
    else:
        for c in range(int(min(z0,z1))+1,int(max(z0,z1)),2):
            if abs(c)+1>=SZ: put('interior_wall_end_doorway' if c in doors else 'interior_wall_end',x0,0,c,-90 if c>0 else 90,['floor0']); continue
            put('interior_wall_wide' if c in wide else 'interior_wall_doorway' if c in doors else 'interior_wall_plain',x0,0,c,90,['floor0'])
def door(x,z,ry,ang=70):
    hx,hz=hinge(x,z,ry,-0.43,0); put('door_leaf_interior',hx,0,hz,ry,['floor0'],door=ang)
# back of house: 2 restrooms, storage, kitchen (pass-through to the dining room, service door at the back)
wl(-6,0,6,0,doors=(-5,-3,1),wide=(3,)); wl(-6,-4,-6,0); wl(6,-4,6,0); wl(-4,-4,-4,0); wl(-2,-4,-2,0); wl(0,-4,0,0,doors=(-3,))
door(-5,0,0,70); door(-3,0,0,70); door(1,0,0,70); door(0,-3,90,-70)   # storage door swings into the kitchen
put('door_leaf_front',1-0.48,0.015,SZ-0.18,0,['front','ext'],door=85)
put('door_leaf_vestibule',1-0.48,0.015,SZ+VD-0.05,0,['front','ext'],door=-85)
hx,hz=hinge(3,-SZ,180,-0.45,-0.18); put('door_leaf_service',hx,0.015,hz,180,['back','ext'],door=85)
put('player_scale_ref',3.2,0,SZ+2.6); put('player_scale_ref',-6.5,0,1,0,['floor0']); put('player_scale_ref',3,0,-2,0,['floor0'])

json.dump({'grid':{'module_width':W,'wall_height':HD,'wall_thickness':T,'slab':SLAB,'footprint':[2*SX+2*RC,2*SZ],'end_radius':RC,
  'roof':'flat, top at 3.5 m, steel cornice parapet; rounded ends built from 30 deg sectors centred at x = +-6'},'placements':L},open(f'{OUT}/building_layout.json','w'),indent=1)
asm=Piece()
for e in L:
    if e['piece']=='player_scale_ref': continue
    Tm=trimesh.transformations.rotation_matrix(math.radians(e['rotY']),[0,1,0]); Tm[:3,3]=e['pos']
    asm.merge(pieces[e['piece']],Tm)
asm.scene('building').export(f'{OUT}/building_assembled.glb',include_normals=True)
print(len(pieces),'pieces',len(L),'placements',sum(1 for e in L if 'door' in e),'doors')
# vidros transparentes iguais aos dos outros kits (scripts/detalhe/vidro.py)
import sys, glob as _g; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts', 'detalhe')); from vidro import vidro_glb
for _f in _g.glob(f'{OUT}/**/*.glb', recursive=True): vidro_glb(_f)
# folha da janela em no proprio, para o jogo abrir (scripts/detalhe/folhas.py, grava janelas.json)
import sys as _s, os as _o; _s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), '..', '..', 'scripts', 'detalhe')); import folhas as _folhas
_folhas.kit(OUT)
# vao da janela rebocado por dentro (scripts/detalhe/vao.py)
import vao as _vao, glob as _gl
for _f in _gl.glob(_o.path.join(OUT, 'pieces', '*win*.glb')): _vao.rebocar(_f)
