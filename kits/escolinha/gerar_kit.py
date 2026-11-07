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
# =====================================================================================
# KIT 10: casa americana: two-storey front-gable house, full-width porch, exterior brick chimney, side garage
# =====================================================================================
COL.update({'siding':(150,168,186),'trim':(244,244,240),'frame':(250,250,248),'shutter':(52,58,70),'shutter_dark':(38,42,52),
            'shingle':(72,78,88),'ridge':(58,62,70),'door':(126,40,40),'deck':(168,128,92),'concrete':(186,184,178),
            'garage_door':(246,246,242),'garage_panel':(226,226,222),'iron':(40,40,44),'vent':(214,216,212)})
def siding_texture(px=256,seed=61):
    # tile 1 x 1 m: 5 lap boards of 0.2 m, each with a lit top edge and a shadow line under the lap
    rnd=random.Random(seed); base=np.array(COL['siding'],np.float32); a=np.zeros((px,px,3),np.float32); bh=px/5
    for r in range(5):
        y0=int(r*bh); y1=int((r+1)*bh); c=base*(1+rnd.uniform(-0.02,0.02))
        for y in range(y0,y1):
            t=(y-y0)/bh; f=0.86 if t<0.09 else (1.05 if t>0.9 else 1.0-0.05*(1-t))
            a[y,:,:]=c*f
    n=_noise(px,16,seed)*0.5+_noise(px,64,seed+1)*0.6; a=np.clip(a+n[...,None]*8,0,255).astype(np.uint8)
    return Image.fromarray(a).transpose(Image.FLIP_TOP_BOTTOM)
def shingle_texture(px=256,seed=63):
    # tile 1 x 1 m: 5 courses of 0.2 m three-tab shingles (0.33 m tabs), staggered, dark shadow under each course
    rnd=random.Random(seed); im=Image.new('RGB',(px,px),(44,48,56)); d=ImageDraw.Draw(im); rh=px/5; tw=px/3
    base=[(74,80,90),(68,74,84),(80,86,96),(64,70,80)]
    for r in range(5):
        off=(r%3)*tw/3
        for i in range(-1,4):
            c=rnd.choice(base); x0=i*tw+off
            for dx in (-px,0,px):
                d.rectangle([x0+dx+1,r*rh,x0+dx+tw-2,r*rh+rh-3],fill=c)
                d.rectangle([x0+dx+1,r*rh+rh*0.78,x0+dx+tw-2,r*rh+rh-3],fill=tuple(int(v*0.82) for v in c))
    a=np.asarray(im,dtype=np.float32); a=np.clip(a+_noise(px,64,seed)[...,None]*10,0,255).astype(np.uint8)
    return Image.fromarray(a)
def deck_texture(px=256,seed=65):
    # tile 1 x 1 m: 7 boards of ~0.14 m running along u, thin dark gaps
    rnd=random.Random(seed); a=np.zeros((px,px,3),np.float32); bw=px/7; base=np.array(COL['deck'],np.float32)
    for r in range(7):
        c=base*(1+rnd.uniform(-0.05,0.05)); y0=int(r*bw); y1=int((r+1)*bw)
        a[y0:y1,:,:]=c; a[y1-2:y1,:,:]=c*0.55
    a=np.clip(a+_noise(px,24,seed)[...,None]*12,0,255).astype(np.uint8)
    return Image.fromarray(a)
SIDING_TEX=siding_texture(); SHINGLE_TEX=shingle_texture(); DECK_TEX=deck_texture()
for nm,im in (('siding',SIDING_TEX),('shingle',SHINGLE_TEX),('deck',DECK_TEX),('brick',BRICK_TEX)): im.save(os.path.join(OUT,nm+'_texture.png'))
TEX={'siding':(SIDING_TEX,1.0,1.0),'shingle':(SHINGLE_TEX,1.0,1.0),'deck':(DECK_TEX,1.0,1.0),'brick':(BRICK_TEX,1.0,1.0),'plaster':(PLASTER_TEX,1.0,1.0)}
SIGN=(0,0,1,1)
MATS = {k:PBRMaterial(name=k, baseColorFactor=[c/255 for c in v]+[1.0], metallicFactor=0.0, roughnessFactor=0.9) for k,v in COL.items()}
for k,(im,_,_) in TEX.items(): MATS[k]=PBRMaterial(name=k,baseColorTexture=im,baseColorFactor=[255,255,255,255],metallicFactor=0.0,roughnessFactor=0.9)

H2=H+0.02          # upper walls rise 2 cm above the attic floor, so the slab edge never shares a face with them
ROOFB=2*H-1.0      # roof pieces sit here: inner roof face meets the outer wall face at y = 6.0 (no knee wall)
SX,SZ=4.0,6.0      # house 8 x 12 m, front to +Z, ridge along Z
# ---------- walls: blue-grey lap siding, white casings, dark shutters ----------
def casing(p,ow,oy0,oy1):
    x=ow/2; c=0.1
    p.box('trim',-x-c,-x,oy0-0.04,oy1+0.02,0.0,0.025); p.box('trim',x,x+c,oy0-0.04,oy1+0.02,0.0,0.025)
    p.box('trim',-x-c-0.03,x+c+0.03,oy1+0.02,oy1+0.16,0.0,0.035)       # head casing with a small cap
def belt(p):  ledge(p,H,mat='trim',th=0.14,d=0.03)      # floor-line band: covers the slab edge
def frieze(p): ledge(p,H2,mat='trim',th=0.26,d=0.035)   # top board under the eaves
def wall_siding(kind,upper=False):
    p=Piece(); h=H2 if upper else H
    if kind=='window':
        ow,oy0,oy1=0.9,0.85,2.3
        wall_with_opening(p,'siding',ow,oy0,oy1,h); window(p,ow,oy0,oy1,lintel=None); casing(p,ow,oy0,oy1); shutters(p,ow,oy0,oy1,z0=0.03)
        # shutters stop clear of the casing: shift them by trimming? casing is 0.1 wide, shutters start at ow/2+0.03 -> move out
    elif kind=='small':
        ow,oy0,oy1=0.6,1.4,2.2
        wall_with_opening(p,'siding',ow,oy0,oy1,h); window(p,ow,oy0,oy1,lintel=None,mull=False); casing(p,ow,oy0,oy1)
    elif kind=='plain':
        wall_with_opening(p,'siding',0,0,0,h)
    elif kind in ('door','door_back'):
        ow=1.1; x=ow/2; oy0=0.015; wall_with_opening(p,'siding',ow,oy0,2.4,h)
        p.box('frame',-x,-x+0.07,oy0,2.4,-0.22,0.02); p.box('frame',x-0.07,x,oy0,2.4,-0.22,0.02); p.box('frame',-x,x,2.33,2.4,-0.22,0.02)
        casing(p,ow+0.0,oy0+0.04,2.4)
        if kind=='door_back': p.box('concrete',-0.8,0.8,0,0.15,0.0,0.6)                  # stoop
    elif kind=='door_inner':
        ow=0.9; x=ow/2; oy0=0.015; wall_with_opening(p,'siding',ow,oy0,2.1,h)
        p.box('frame',-x,-x+0.07,oy0,2.1,-0.24,0.02); p.box('frame',x-0.07,x,oy0,2.1,-0.24,0.02); p.box('frame',-x,x,2.03,2.1,-0.24,0.02)
    if upper: frieze(p)
    else: belt(p)
    return p
def shutters(p,ow,oy0,oy1,z0=0.03):
    """Pair of panelled shutters flat against the siding, outside the 0.1 m casing."""
    w=ow/2
    for s in (-1,1):
        a,b=sorted((s*(ow/2+0.12),s*(ow/2+0.12+w)))
        p.box('shutter',a,b,oy0,oy1,z0,z0+0.03)
        n=int((oy1-oy0)/0.12)
        for i in range(1,n): y=oy0+i*(oy1-oy0)/n; p.box('shutter_dark',a+0.05,b-0.05,y-0.015,y+0.01,z0+0.03,z0+0.042)
def corner_board(upper=False):
    p=Piece(); e=0.04; h=H2 if upper else H
    p.box('trim',-T-0.01,e,0,h-0.01 if upper else h,-T-0.01,e)
    if upper: p.box('trim',-T+0.01,e+0.035,h-0.26+0.015,h+0.015,-T+0.01,e+0.035)
    else: p.box('trim',-T,e+0.03,H-0.14+0.015,H+0.015,-T,e+0.03)
    return p
# ---------- roof: dark shingles, 45 deg, ridge along Z, rakes on the front and back gables ----------
def gable_siding(hsp=HSP,kr=KR,base=ROOFB-2*H-0.02,vent=True,win=None):
    """Gable end over the 8 m front or back wall: siding, white rake boards, louvred vent. Pivot: centre of the base at the facade,
    placed on top of the upper walls (y = 6.02)."""
    p=Piece(); top=lambda x:base+roof_in(hsp-abs(x),kr)+0.15
    outer=Polygon([(-hsp,0),(hsp,0),(hsp,top(hsp)),(0,top(0)),(-hsp,top(-hsp))])
    holes=[]
    if win: ow,oy0,oy1=win; holes.append(rect(-ow/2,oy0,ow/2,oy1))
    body=outer
    for h_ in holes: body=body.difference(h_)
    ext(p,'siding',body,-T+0.02,0.0); ext(p,'plaster',body,-T,-T+0.02)
    if win:
        ow,oy0,oy1=win; window(p,ow,oy0,oy1,lintel=None,mull=False); casing(p,ow,oy0,oy1)
    if vent:   # gable vent: white frame, grey louvres, pointed head following the roof
        vy=(win[2]+0.45) if win else 1.3; vw=0.8; vh=0.9
        pts=[(-vw/2,vy),(vw/2,vy),(vw/2,vy+vh),(0,vy+vh+vw/2),(-vw/2,vy+vh)]
        fr=Polygon(pts); ext(p,'trim',fr.difference(fr.buffer(-0.07)),0.0,0.04); ext(p,'vent',fr.buffer(-0.07),0.0,0.015)
        n=7
        for i in range(n): y=vy+0.12+i*(vh-0.1)/n; p.box('shutter_dark',-vw/2+0.08,vw/2-0.08,y,y+0.03,0.015,0.03)
    rk=unary_union([beam((-hsp,top(-hsp)-0.12),(0,top(0)-0.12),0.26),beam((hsp,top(hsp)-0.12),(0,top(0)-0.12),0.26)]).intersection(outer)
    ext(p,'trim',rk,0.0,0.03)
    return p
def chimney_exterior():
    """Exterior brick chimney against a side wall: 1.6 m breast up to 4.4 m, sloped shoulders, 0.9 m stack above the ridge.
    Pivot: centre of the wall face at ground level, chimney toward +Z (out of the wall)."""
    p=Piece(); d=0.75; top=CHIM_TOP
    p.box('brick',-0.8,0.8,0,4.2,-0.01,d)
    hull(p,'brick',[(x,y,z) for z in (-0.01,d) for (x,y) in ((-0.8,4.2),(0.8,4.2),(-0.45,4.9),(0.45,4.9))])
    p.box('brick',-0.45,0.45,4.9,top,-0.01,d)
    p.box('concrete',-0.55,0.55,top,top+0.1,-0.1,d+0.1); p.box('brick',-0.25,0.25,top+0.1,top+0.35,0.15,d-0.2)
    p.box('dark',-0.18,0.18,top+0.35,top+0.37,0.22,d-0.27)
    p.box('concrete',-0.82,0.82,4.2,4.26,0.0,0.02)   # never level: thin flashing ledge stays inside the brick face
    return p
# ---------- front porch: 2.4 m deep, deck 18 cm above the ground, white posts and rails, shingled shed roof ----------
PD=0.18; PDEP=2.4; PB0,PB1=2.55,2.95; PR0,PR1=3.55,2.95   # deck top, depth, header beam, roof top at the wall and at the front edge
def porch_deck(ext_l=0.0,ext_r=0.0):
    p=Piece(); x0,x1=-W/2-ext_l,W/2+ext_r
    p.box('deck',x0,x1,-0.12,PD,0.0,PDEP-0.03)
    p.box('trim',x0,x1,-0.12,PD-0.01,PDEP-0.03,PDEP)
    if ext_l: p.box('trim',x0-0.03,x0,-0.12,PD-0.01,0.0,PDEP)
    if ext_r: p.box('trim',x1,x1+0.03,-0.12,PD-0.01,0.0,PDEP)
    return p
def porch_post():
    p=Piece(); s=0.09; z=PDEP-0.25
    p.box('trim',-s-0.03,s+0.03,PD,PD+0.25,z-s-0.03,z+s+0.03); p.box('trim',-s,s,PD+0.25,PB0,z-s,z+s)
    p.box('trim',-s-0.04,s+0.04,PB0-0.14,PB0,z-s-0.04,z+s+0.04); return p
def porch_beam(x0=-W/2,x1=W/2):
    p=Piece(); z=PDEP-0.25; p.box('trim',x0,x1,PB0,PB1,z-0.1,z+0.1); return p
def _ry(z): return PR0+(PR1-PR0)*(z+0.05)/(PDEP+0.3)
def porch_roof(x0=-W/2,x1=W/2,fascia=0):
    p=Piece(); z0,z1=-0.05,PDEP+0.25
    hull(p,'shingle',[(x,y,z) for x in (x0,x1) for z in (z0,z1) for y in (_ry(z),_ry(z)-0.03)])
    hull(p,'trim',[(x,y,z) for x in (x0+0.01,x1-0.01) for z in (z0,z1-0.01) for y in (_ry(z)-0.035,_ry(z)-0.17)])
    return p
def _rail(p,x0,x1,z,y0=PD,h=0.9):
    p.box('trim',x0,x1,y0+h-0.06,y0+h,z-0.05,z+0.05); p.box('trim',x0,x1,y0+0.08,y0+0.14,z-0.03,z+0.03)
    L=x1-x0; k=max(2,int(L/0.13))
    for i in range(1,k): xx=x0+i*L/k; p.box('trim',xx-0.018,xx+0.018,y0+0.14,y0+h-0.06,z-0.018,z+0.018)
def porch_rail(x0=-W/2+0.12,x1=W/2-0.12):
    p=Piece(); _rail(p,x0,x1,PDEP-0.25); return p
def porch_rail_side():
    """Rail on the open end of the porch, from the house wall to the corner post. Pivot like the deck, rail along Z at x=0."""
    p=Piece(); q=Piece(); _rail(q,0.05,PDEP-0.37,0.0)
    Tm=trimesh.transformations.rotation_matrix(-math.pi/2,[0,1,0]); p.merge(q,Tm); return p
def porch_steps():
    p=Piece(); p.box('deck',-0.75,0.75,-0.12,PD/2,PDEP,PDEP+0.35); p.box('trim',-0.75,0.75,-0.12,PD/2-0.01,PDEP+0.35,PDEP+0.38); return p
# ---------- stair guard over the down flight, upstairs ----------
def stair_guard(x0,x1):
    p=Piece(); _rail(p,x0,x1,0.0,y0=0.0); return p
# ---------- garage: 4 x 6 m on the right, own front gable, white carriage doors ----------
GH=3.5; GHSP=2.0; GY=2.2
def wall_garage(win=False):
    p=Piece()
    if win: wall_with_opening(p,'siding',0.9,1.3,2.2,GH); window(p,0.9,1.3,2.2,lintel=None); casing(p,0.9,1.3,2.2)
    else: wall_with_opening(p,'siding',0,0,0,GH)
    p.box('concrete',-W/2,W/2,0,0.3,0.0,0.03); return p
def corner_garage():
    p=Piece(); e=0.04; p.box('trim',-T-0.01,e,0,GY+1.15,-T-0.01,e); p.box('concrete',-T-0.02,e+0.03,0,0.3,-T-0.02,e+0.03); return p
def garage_gable(front=True,inset=(T,T)):
    p=Piece(); top=lambda x:GY+roof_in(GHSP-abs(x))+0.15
    xl,xr=-GHSP+inset[0],GHSP-inset[1]
    outer=Polygon([(xl,0),(xr,0),(xr,top(xr)),(0,top(0)),(xl,top(xl))])
    hole=rect(-1.3,0.015,1.3,2.3) if front else rect(-0.3,3.0,0.3,3.6)
    body=outer.difference(hole); ext(p,'siding',body,-T+0.02,0.0); ext(p,'plaster',body,-T,-T+0.02)
    plinth=rect(xl,0,xr,0.3).difference(hole.union(rect(-1.42,0,1.42,2.46)) if front else hole); ext(p,'concrete',plinth,0.0,0.03)
    if front:
        for s in (-1,1): a_,b_=sorted((s*1.28,s*1.42)); p.box('trim',a_,b_,0.0,2.28,-0.31,0.035)
        p.box('trim',-1.42,1.42,2.28,2.46,-0.31,0.035)
    else: window(p,0.6,3.0,3.6,mull=False,lintel=None); casing(p,0.6,3.0,3.6)
    rk=unary_union([beam((-GHSP,top(-GHSP)-0.12),(0,top(0)-0.12),0.26),beam((GHSP,top(GHSP)-0.12),(0,top(0)-0.12),0.26)]).intersection(outer)
    ext(p,'trim',rk.difference(rect(-1.42,0,1.42,2.46)),0.0,0.03)
    return p
def garage_door_leaf(w=1.28,h=2.25):
    """One leaf of the white carriage-style garage door: 4 raised panels, top row of small lights. Pivot: hinge, bottom. Closed = along +X."""
    p=Piece(); p.box('garage_door',0,w,0,h,-0.025,0.025)
    for sg in (1,-1):
        za,zb=(0.025,0.04) if sg>0 else (-0.04,-0.025)
        for r in range(3):
            y0=0.12+r*0.56; p.box('garage_panel',0.08,w-0.08,y0,y0+0.44,za,zb)
    for i in range(3): x0=0.08+i*(w-0.16)/3; p.box('glass',x0+0.03,x0+(w-0.16)/3-0.03,1.86,2.14,-0.03,0.03)
    p.box('iron',w-0.12,w-0.07,1.0,1.2,0.04,0.07); return p
def garage_floor():
    p=Piece(); p.box('concrete',-W/2,W/2,-0.03,0,-W/2,W/2); p.box('plaster',-W/2+0.02,W/2-0.02,-SLAB,-0.03,-W/2+0.02,W/2-0.02); return p
def interior_wall_wide(h=H-SLAB,ow=1.6):
    """Wide cased opening (no door), e.g. living room to dining."""
    p=Piece(); t=0.12; wall_with_opening(p,'plaster',ow,0,2.2,h,inner='plaster',t=t,centered=True)
    for xx in (-ow/2,ow/2): p.box('frame',xx-0.04,xx+0.04,0,2.24,-t/2-0.02,t/2+0.02)
    p.box('frame',-ow/2-0.04,ow/2+0.04,2.18,2.28,-t/2-0.02,t/2+0.02)
    for a,b in ((-W/2,-ow/2-0.04),(ow/2+0.04,W/2)): p.box('trim',a,b,0,0.1,t/2,t/2+0.015); p.box('trim',a,b,0,0.1,-t/2-0.015,-t/2)
    return p
# =====================================================================================
# KIT 11: duplex: two mirrored two-storey homes under one side-gable roof, central front cross gable over two garages
# =====================================================================================
COL.update({'siding':(226,204,140),'shutter':(42,54,90),'shutter_dark':(30,38,66),'shingle':(70,98,80),'ridge':(52,76,60),
            'door':(150,40,36),'door_b':(40,70,110)})
def shingle_texture_green(px=256,seed=71):
    rnd=random.Random(seed); im=Image.new('RGB',(px,px),(40,58,46)); d=ImageDraw.Draw(im); rh=px/5; tw=px/3
    base=[(72,100,82),(66,94,76),(78,106,88),(62,88,72)]
    for r in range(5):
        off=(r%3)*tw/3
        for i in range(-1,4):
            c=rnd.choice(base); x0=i*tw+off
            for dx in (-px,0,px):
                d.rectangle([x0+dx+1,r*rh,x0+dx+tw-2,r*rh+rh-3],fill=c)
                d.rectangle([x0+dx+1,r*rh+rh*0.78,x0+dx+tw-2,r*rh+rh-3],fill=tuple(int(v*0.82) for v in c))
    a=np.asarray(im,dtype=np.float32); a=np.clip(a+_noise(px,64,seed)[...,None]*10,0,255).astype(np.uint8)
    return Image.fromarray(a)
SIDING_TEX=siding_texture(seed=73); SHINGLE_TEX=shingle_texture_green()
for nm,im in (('siding',SIDING_TEX),('shingle',SHINGLE_TEX)): im.save(os.path.join(OUT,nm+'_texture.png'))
for nm in ('deck','brick'):
    if os.path.exists(os.path.join(OUT,nm+'_texture.png')): os.remove(os.path.join(OUT,nm+'_texture.png'))
TEX={'siding':(SIDING_TEX,1.0,1.0),'shingle':(SHINGLE_TEX,1.0,1.0),'plaster':(PLASTER_TEX,1.0,1.0)}
MATS = {k:PBRMaterial(name=k, baseColorFactor=[c/255 for c in v]+[1.0], metallicFactor=0.0, roughnessFactor=0.9) for k,v in COL.items()}
for k,(im,_,_) in TEX.items(): MATS[k]=PBRMaterial(name=k,baseColorTexture=im,baseColorFactor=[255,255,255,255],metallicFactor=0.0,roughnessFactor=0.9)

SX,SZ=8.0,6.0      # 16 x 12 m, front to +Z, main ridge along X at z=0
KM=0.75            # main and cross roof pitch (about 37 deg)
HM=6.0             # main roof half span (12 m deep)
HC=4.0             # cross gable half span (8 m wide, x -4..4)
def door_hood():
    """Small gabled hood over a front door, on two brackets. Pivot: centre of the wall face at ground level."""
    p=Piece(); x=0.8; d=0.9; ye=2.62; yr=3.0-0.06; t=0.03
    for s in (-1,1):
        hull(p,'shingle',[(xx,y,z) for (xx,y) in ((0,yr),(s*(x+0.08),ye-0.06)) for z in (0.0,d) for y in (y,y-t)])
        hull(p,'trim',[(xx,y,z) for (xx,y) in ((0,yr-t-0.005),(s*(x+0.04),ye-0.06-t-0.005)) for z in (0.0,d-0.01) for y in (y,y-0.1)])
    for s in (-1,1): p.seg('trim',(s*(x-0.08),1.95,0.04),(s*(x-0.08),ye-0.2,d-0.12),0.07)
    return p
def wall_garage_front():
    """4 m front wall of one garage bay: 2.6 x 2.3 m opening, white jambs and header, floor-line band. Pivot: centre of the 4 m base."""
    p=Piece(); hw=2.0; ow=2.6; x=ow/2; oy1=2.3; zs=[-T,-T+0.02,0.0]
    xs=[-hw,-x,x,hw]; ys=[0.0,oy1,H]
    def cell(i,j,k):
        if i==1 and j==0: return None
        return 'plaster' if k==0 else 'siding'
    for m,mesh in grid_solid(xs,ys,zs,cell).items(): p.add(m,mesh)
    for s in (-1,1): a_,b_=sorted((s*(x-0.02),s*(x+0.12))); p.box('trim',a_,b_,0.0,oy1-0.02,-0.31,0.035)
    p.box('trim',-x-0.12,x+0.12,oy1-0.02,oy1+0.16,-0.31,0.035)
    p.box('trim',-hw,hw,H-0.14+0.015,H+0.015,0.0,0.03)          # floor-line band
    return p
_wsd=wall_siding
def wall_siding(kind,upper=False):
    if kind=='door_hood':
        p=_wsd('door'); p.merge(door_hood()); p.box('concrete',-0.8,0.8,0,0.15,0.0,0.6); return p
    return _wsd(kind,upper)
def main_slope(x0=-W/2,x1=W/2,over=0.4): p=Piece(); roof_panel(p,x0,x1,hsp=HM,kr=KM,over=over); return p
def cross_slope(x0=-W/2,x1=W/2): p=Piece(); roof_panel(p,x0,x1,hsp=HC,kr=KM,over=0.4); return p
# =====================================================================================
# KIT 20: escolinha: one-room schoolhouse, 8 x 12 m red clapboard block on a brick foundation, steep front-gable roof,
# gabled entry vestibule with a cloakroom, bell cupola on the ridge, brick chimney, teacher's platform, back door, woodshed
# =====================================================================================
from shapely.geometry import Point
from shapely.ops import unary_union
COL.update({'siding':(168,50,42),'trim':(250,248,242),'frame':(250,250,248),'door':(52,70,58),'brick':(150,72,56),
            'shingle':(78,80,88),'ridge':(60,62,70),'dark':(46,46,50),'brass':(206,164,74),'louvre':(236,234,228),
            'wood':(170,124,82),'floor':(176,132,90),'board':(132,96,66),'pole':(46,46,50)})
SIDING_TEX=siding_texture(seed=131); SHINGLE_TEX=shingle_texture(seed=133); BRICK_TEX=brick_texture(seed=135)
for nm in os.listdir(OUT):
    if nm.endswith('_texture.png'): os.remove(os.path.join(OUT,nm))
for nm,im in (('siding',SIDING_TEX),('shingle',SHINGLE_TEX),('brick',BRICK_TEX),('plaster',PLASTER_TEX)): im.save(os.path.join(OUT,nm+'_texture.png'))
TEX={'siding':(SIDING_TEX,1.0,1.0),'shingle':(SHINGLE_TEX,1.0,1.0),'brick':(BRICK_TEX,1.0,1.0),'plaster':(PLASTER_TEX,1.0,1.0)}
MATS = {k:PBRMaterial(name=k, baseColorFactor=[c/255 for c in v]+[1.0], metallicFactor=0.0, roughnessFactor=0.9) for k,v in COL.items()}
for k,(im,_,_) in TEX.items(): MATS[k]=PBRMaterial(name=k,baseColorTexture=im,baseColorFactor=[255,255,255,255],metallicFactor=0.0,roughnessFactor=0.9)

FY=0.6              # floor on a brick foundation: 4 steps of 15 cm
HN=3.6              # classroom walls above the floor
HW=FY+HN+0.02       # 4.22
ROOF=FY+HN-1.0      # 3.2: roof pieces (inner face meets the wall face at y = 4.2)
HSP=4.0; KS=1.0     # 8 m wide, 45 deg
VW=FY+2.6           # vestibule walls (inner roof face meets them at 3.2)
VHW=VW+0.02
VROOF=VW-1.0
VHSP=1.5            # vestibule: 3 m wide
VX=1.5; VZ0,VZ1=6.0,8.4
def wall_poly(p,poly,hole=None,x0=-W/2,x1=W/2,top=HW,frieze=True,skip=None):
    """Clapboard wall: brick foundation below the floor (4 cm proud, cap 3 cm over the floor), siding above, plaster inside."""
    body=poly if hole is None else poly.difference(hole)
    up=body.intersection(sbox(x0,FY,x1,top+1)); lo=body.intersection(sbox(x0,-1,x1,FY))
    ext(p,'siding',up,-T+0.02,0.0); ext(p,'plaster',up,-T,-T+0.02); ext(p,'brick',lo,-T,0.0)
    pr=lo if skip is None else lo.difference(skip); ext(p,'brick',pr,0.0,0.04)
    cap=sbox(x0,FY-0.06,x1,FY+0.03); cap=cap if hole is None else cap.difference(hole); cap=cap if skip is None else cap.difference(skip); ext(p,'trim',cap,0.04,0.07)
    if frieze: p.box('trim',x0,x1,top-0.28+0.015,top+0.015,0.0,0.04)
WIN=(1.0,FY+0.85,FY+3.0)
def sash(p,w,y0,y1):
    window(p,w,y0,y1,lintel=None); casing(p,w,y0,y1)
    if 'retrofit' in globals(): return   # a janela detalhada ja tem travessa e baguetes
    x=w/2; p.box('frame',-x,x,(y0+y1)/2-0.03,(y0+y1)/2+0.03,-0.17,-0.1)
    for f in (1/3,2/3):
        for yy0,yy1 in ((y0,(y0+y1)/2),((y0+y1)/2,y1)): xx=-x+f*w; p.box('frame',xx-0.015,xx+0.015,yy0,yy1,-0.165,-0.11)
def school_wall(kind,w=W):
    p=Piece(); x=w/2; outline=sbox(-x,0,x,HW)
    if kind=='window':
        ww,y0,y1=WIN; wall_poly(p,outline,sbox(-ww/2,y0,ww/2,y1),-x,x); sash(p,ww,y0,y1)
    elif kind in ('door','backdoor'):
        ow=1.0; oh=FY+2.3; wall_poly(p,outline,sbox(-ow/2,FY-0.03,ow/2,oh),-x,x,skip=sbox(-VX-0.05,-1,VX+0.05,FY+1) if kind=='door' else None); d=ow/2
        p.box('frame',-d,-d+0.07,FY,oh,-0.22,0.02); p.box('frame',d-0.07,d,FY,oh,-0.22,0.02); p.box('frame',-d,d,oh-0.07,oh,-0.22,0.02)
        casing(p,ow,FY+0.04,oh)
        if kind=='backdoor': p.box('trim',-0.75,0.75,oh+0.3,oh+0.36,0.0,0.6); p.box('trim',-0.75,0.75,oh+0.22,oh+0.3,0.54,0.6)   # small hood
    else: wall_poly(p,outline,None,-x,x)
    return p
def school_corner(top=HW):
    p=Piece(); e=0.05; p.box('trim',-T-0.01,e,FY+0.03,top-0.01,-T-0.01,e); p.box('brick',-T-0.01,e+0.02,0,FY-0.06,-T-0.01,e+0.02)
    p.box('trim',-T,e+0.05,FY-0.06,FY+0.03,-T,e+0.05)
    p.box('trim',-T+0.01,e+0.04,top-0.28+0.015,top+0.015,-T+0.01,e+0.04); return p
def gable(hsp,kr,roof,hw,vent='louvre',vy=None):
    """Gable triangle above the wall top, siding, raking trim, a vent. Pivot: centre of the wall face at the wall top."""
    p=Piece(); base=roof-hw; top=lambda x:base+roof_in(hsp-abs(x),kr)+0.15
    outer=Polygon([(-hsp,0),(hsp,0),(hsp,top(hsp)),(0,top(0)),(-hsp,top(-hsp))]); body=outer
    if vent=='louvre':
        vy=vy or top(0)*0.45; h=sbox(-0.35,vy-0.4,0.35,vy+0.4).union(Point(0,vy+0.4).buffer(0.35,resolution=10)); body=body.difference(h)
        ext(p,'dark',h,-0.2,-0.18)
        for i in range(6): y=vy-0.34+i*0.15; p.box('louvre',-0.33,0.33,y,y+0.05,-0.16,-0.08)
        ext(p,'trim',h.buffer(0.09,resolution=10).difference(h),0.0,0.03)
    ext(p,'siding',body,-T+0.02,0.0); ext(p,'plaster',body,-T,-T+0.02)
    rk=unary_union([beam((-hsp,top(-hsp)-0.13),(0,top(0)-0.13),0.28),beam((hsp,top(hsp)-0.13),(0,top(0)-0.13),0.28)]).intersection(outer)
    ext(p,'trim',rk,0.0,0.03)
    p.box('trim',-hsp,hsp,-0.015,0.14,0.0,0.05)
    return p
def slope(x0=-W/2,x1=W/2,hsp=HSP,kr=KS,over=0.4):
    p=Piece(); us=[-over,hsp]; vs=[0.0,0.02,TV]; xs=[x0,x1]
    def cell(i,j,k): return 'plaster' if k==0 else 'shingle'
    for m,mesh in grid_solid(xs,us,vs,cell).items():
        v=mesh.vertices.copy(); u=v[:,1].copy(); w=v[:,2].copy()
        v[:,1]=1.0+kr*u+w; v[:,2]=-u; mesh.vertices=v; p.add(m,mesh)
    return p
# ---------- vestibule (entry with cloakroom), pivot: centre of its front face at ground, x -1.5..1.5, z 6..8.4 ----------
def vest_front():
    p=Piece(); outline=sbox(-VX,0,VX,VHW); ow=1.0; oh=FY+2.15
    wall_poly(p,outline,sbox(-ow/2,FY-0.03,ow/2,oh),-VX,VX,top=VHW); d=ow/2
    p.box('frame',-d,-d+0.07,FY,oh,-0.22,0.02); p.box('frame',d-0.07,d,FY,oh,-0.22,0.02); p.box('frame',-d,d,oh-0.07,oh,-0.22,0.02)
    casing(p,ow,FY+0.04,oh); p.box('trim',-0.25,0.25,oh+0.2,oh+0.42,0.0,0.02); p.box('brass',-0.06,0.06,oh+0.27,oh+0.35,0.02,0.035)
    return p
def vest_side():
    """Side wall of the vestibule, 2.1 m (from the classroom wall to the vestibule front wall's inner face), small window.
    Pivot: front end of the wall's outer face at ground (the wall runs along -X local)."""
    p=Piece(); L=VZ1-VZ0-T; outline=sbox(-L,0,0,VHW); w=0.6; y0,y1=FY+1.2,FY+2.1; c=-L/2
    hole=sbox(c-w/2,y0,c+w/2,y1); wall_poly(p,outline,hole,-L,0,top=VHW)
    q=Piece(); window(q,w,y0,y1,lintel=None,mull=False); casing(q,w,y0,y1); Tm=np.eye(4); Tm[0,3]=c; p.merge(q,Tm)
    return p
def vest_floor():
    p=Piece(); x=VX-T; p.box('floor',-x,x,-0.03,0,VZ0-VZ1,0.0); p.box('brick',-x,x,-FY,-0.03,VZ0-VZ1,-T); return p
def vest_ceiling():
    p=Piece(); x=VX-T; p.box('plaster',-x,x,-0.02,0,VZ0-VZ1,-T); return p
def entry_steps():
    """Four 15 cm steps up to the vestibule door. Pivot: centre of the front wall line at ground."""
    p=Piece(); r=FY/4; x=0.85
    for k in range(1,4): p.box('wood',-x,x,0,k*r,0.0,(4-k)*0.3)
    p.box('wood',-x,x,0,FY-0.05,0.0,0.02)
    for s in (-1,1): p.box('trim',s*x-0.03,s*x+0.03,0,FY+0.9,0.85,0.91); p.seg('trim',(s*x,FY+0.85,0.0),(s*x,r+0.85,0.88),0.05)
    return p
def back_steps():
    p=Piece(); r=FY/4; x=0.7
    p.box('wood',-x,x,0,FY-0.05,0.0,1.0)
    for k in range(1,4): p.box('wood',-x,x,0,k*r,1.0,1.0+(4-k)*0.3)
    return p
# ---------- bell cupola and chimney ----------
RIDGE=ROOF+1.0+KS*HSP+TV       # 8.5 outer ridge
def cupola():
    """Square bell cupola on the ridge: shingled base, open belfry with a bell, rails, pyramid roof, ball and weathervane.
    Pivot: on the ridge line, at ground level (all heights absolute)."""
    p=Piece(); b=0.7; y0=RIDGE+0.45
    p.box('siding',-b,b,RIDGE-1.2,y0,-b,b); p.box('trim',-b-0.04,b+0.04,y0-0.2,y0,-b-0.04,b+0.04)
    for sx in (-1,1):
        for sz in (-1,1): p.box('trim',sx*b-0.06,sx*b+0.06,RIDGE-0.6,y0-0.2,sz*b-0.06,sz*b+0.06)
    d=b+0.12; p.box('trim',-d,d,y0,y0+0.1,-d,d)
    for sx in (-1,1):
        for sz in (-1,1): p.box('trim',sx*(b-0.02)-0.07,sx*(b-0.02)+0.07,y0+0.1,y0+1.2,sz*(b-0.02)-0.07,sz*(b-0.02)+0.07)
    for ry in (0,90,180,270):
        q=Piece(); q.box('trim',-b+0.05,b-0.05,y0+0.4,y0+0.46,b-0.04,b);
        for i in range(6): xx=-b+0.15+i*(2*b-0.3)/5; q.box('trim',xx-0.02,xx+0.02,y0+0.1,y0+0.4,b-0.03,b-0.01)
        p.merge(q,trimesh.transformations.rotation_matrix(math.radians(ry),[0,1,0]))
    prof=[(0.0,y0+0.45),(0.12,y0+0.45),(0.33,y0+0.5),(0.3,y0+0.62),(0.22,y0+0.9),(0.0,y0+0.98)]
    pr=prof+[prof[0]]; m=trimesh.creation.revolve(np.array([(r,y) for r,y in pr],float),sections=16)
    m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0])); p.add('brass',m)
    p.cyl('dark',0.03,y0+0.98,y0+1.2)
    e=b+0.2; p.box('trim',-e,e,y0+1.2,y0+1.38,-e,e)
    hull(p,'shingle',[(sx*(e+0.05),y0+1.38,sz*(e+0.05)) for sx in (-1,1) for sz in (-1,1)]+[(0,y0+2.3,0)])
    p.sphere('brass',0.09,0,y0+2.36,0); p.cyl('pole',0.02,y0+2.4,y0+3.1)
    p.seg('pole',(-0.32,y0+2.85,0),(0.32,y0+2.85,0),0.025); hull(p,'pole',[(0.32,y0+2.78,0),(0.32,y0+2.92,0),(0.48,y0+2.85,0),(0.32,y0+2.85,0.015),(0.32,y0+2.85,-0.015)])
    for a in (0,90):
        q=Piece(); q.box('pole',-0.2,0.2,y0+2.6,y0+2.62,-0.01,0.01); p.merge(q,trimesh.transformations.rotation_matrix(math.radians(a),[0,1,0]))
    return p
def chimney():
    """Brick chimney from the ceiling up through the roof, corbelled cap. Pivot: its centre at ground level."""
    p=Piece(); c=0.32; y0=FY+HN; y1=RIDGE-0.4
    p.box('brick',-c,c,y0,y1,-c,c); p.box('brick',-c-0.06,c+0.06,y1,y1+0.14,-c-0.06,c+0.06); p.box('dark',-c+0.08,c-0.08,y1+0.14,y1+0.15,-c+0.08,c-0.08)
    return p
def teacher_platform():
    """Raised platform for the teacher's desk across the back of the classroom, 20 cm, 1.6 m deep. Pivot: centre of its front edge on the floor."""
    p=Piece(); x=HSP-T; p.box('wood',-x,x,0,0.2,-1.6,0.0); p.box('trim',-x,x,0.17,0.2,0.0,0.03); return p
def woodshed():
    """Small open-front woodshed, 2.4 x 1.8 m, shed roof. Pivot: centre at ground, open side to +Z."""
    p=Piece(); x=1.2; z=0.9; hf,hb=2.3,1.9
    for sx in (-1,1):
        for sz,hh in ((1,hf),(-1,hb)): p.box('board',sx*(x-0.06)-0.05,sx*(x-0.06)+0.05,0,hh,sz*(z-0.06)-0.05,sz*(z-0.06)+0.05)
    p.box('board',-x+0.01,x-0.01,0.0,hb-0.05,-z+0.01,-z+0.04)
    for sx in (-1,1):
        a,b=sorted((sx*(x-0.01),sx*(x-0.04))); hull(p,'board',[(xx,0.0,zz) for xx in (a,b) for zz in (-z+0.01,z-0.01)]+[(xx,hb-0.05,-z+0.01) for xx in (a,b)]+[(xx,hf-0.05,z-0.01) for xx in (a,b)])
    p.box('wood',-x,x,0.15,0.2,-z+0.05,z-0.05)
    hull(p,'shingle',[(xx,hh,zz) for xx in (-x-0.15,x+0.15) for zz,hh in ((-z-0.2,hb-0.06),(z+0.25,hf+0.02))]+[(xx,hh+0.08,zz) for xx in (-x-0.15,x+0.15) for zz,hh in ((-z-0.2,hb-0.06),(z+0.25,hf+0.02))])
    return p

import sys as _s; _s.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts', 'detalhe'))
import retrofit
retrofit.aplicar(globals(), {'siding': 'siding', 'shingle': 'shingles', 'brick': 'brick', 'plaster': 'plaster'}, tabuas=0.14)
pieces={'floor_tile':floor_tile(),'roof_tile':roof_tile(),
 'school_wall_window':school_wall('window'),'school_wall_plain':school_wall('plain'),'school_wall_door':school_wall('door',w=4.0),'school_wall_backdoor':school_wall('backdoor'),
 'school_corner':school_corner(),'vest_corner':school_corner(VHW),
 'gable_front':gable(HSP,KS,ROOF,HW),'gable_back':gable(HSP,KS,ROOF,HW),'vest_gable':gable(VHSP,KS,VROOF,VHW,vent=None),
 'roof_slope':slope(),'roof_slope_end':slope(-W/2,W/2+0.3),'roof_slope_end_l':slope(-W/2-0.3,W/2),
 'ridge_cap':ridge_cap(hsp=HSP,kr=KS),'ridge_cap_end':ridge_cap(-0.16,0.16,hsp=HSP,kr=KS),
 'vest_slope':slope(VZ0-VZ1-0.3,0.0,VHSP,KS),'vest_ridge':ridge_cap(VZ0-VZ1-0.31,0.0,hsp=VHSP,kr=KS),
 'vest_front':vest_front(),'vest_side':vest_side(),'vest_floor':vest_floor(),'vest_ceiling':vest_ceiling(),'entry_steps':entry_steps(),'back_steps':back_steps(),
 'cupola':cupola(),'chimney':chimney(),'teacher_platform':teacher_platform(),'woodshed':woodshed(),
 'door_leaf_front':door_leaf(0.84,2.13,True,'door'),'door_leaf_class':door_leaf(0.84,2.28,True,'door'),'door_leaf_back':door_leaf(0.84,2.28,False,'door'),
 'player_scale_ref':player_ref(),
}
import shutil; shutil.rmtree(f'{OUT}/pieces',ignore_errors=True); os.makedirs(f'{OUT}/pieces')
for n,p in pieces.items(): p.scene(n).export(f'{OUT}/pieces/{n}.glb',include_normals=True)

# ================= assembly: classroom x -4..4, z -6..6 (front +Z, ridge along Z at x = 0); vestibule x -1.5..1.5, z 6..8.4 =================
X0,X1,Z0,Z1=-4,4,-6,6
L=[]
def put(n,x,y,z,ry=0,tags=(),door=None):
    e={'piece':n,'pos':[round(x,3),round(y,3),round(z,3)],'rotY':ry,'tags':list(tags)}
    if door is not None: e['door']={'closed':ry,'open':ry+door}; e['tags'].append('door')
    L.append(e)
def hinge(x,z,ry,lx,lz):
    r=math.radians(ry); return x+lx*math.cos(r)+lz*math.sin(r), z-lx*math.sin(r)+lz*math.cos(r)
def ftag(fl): return f'floor{fl}'
G=['ext',ftag(0)]
XS=range(X0+1,X1,2); ZS=range(Z0+1,Z1,2)
put('school_wall_window',-3,0,Z1,0,['front']+G); put('school_wall_door',0,0,Z1,0,['front']+G); put('school_wall_window',3,0,Z1,0,['front']+G)
for x in XS: put('school_wall_backdoor' if x==3 else 'school_wall_window' if x==-3 else 'school_wall_plain',x,0,Z0,180,['back']+G)
for z in ZS:
    k='school_wall_plain' if abs(z)==5 else 'school_wall_window'
    put(k,X1,0,z,90,['right']+G); put(k,X0,0,z,-90,['left']+G)
for ry,x,z,tg in [(0,X1,Z1,('front','right')),(90,X1,Z0,('right','back')),(180,X0,Z0,('back','left')),(-90,X0,Z1,('left','front'))]:
    put('school_corner',x,0,z,ry,list(tg)+['ext'])
put('gable_front',0,HW,Z1,0,['front','roof']); put('gable_back',0,HW,Z0,180,['back','roof'])
for z in ZS:
    n,nl=('roof_slope_end_l','roof_slope_end') if z==Z1-1 else ('roof_slope_end','roof_slope_end_l') if z==Z0+1 else ('roof_slope','roof_slope')
    put(n,X1,ROOF,z,90,['roof']); put(nl,X0,ROOF,z,-90,['roof'])
    put('ridge_cap',0,ROOF,z,90,['roof'])
for zc in (Z1+0.15,Z0-0.15): put('ridge_cap_end',0,ROOF,zc,90,['roof'])
# vestibule
put('vest_front',0,0,VZ1,0,['front','vest']+G)
put('vest_side',VX,0,VZ0,90,['front','vest']+G); put('vest_side',-VX,0,VZ1-T,-90,['front','vest']+G)
for ry,x in ((0,VX),(-90,-VX)): put('vest_corner',x,0,VZ1,ry,['front','vest','ext'])
put('vest_gable',0,VHW,VZ1,0,['front','vest','roof'])
put('vest_slope',VX,VROOF,VZ0,90,['vest','roof']); put('vest_slope',-VX,VROOF,VZ1+0.3,-90,['vest','roof'])
put('vest_ridge',0,VROOF,VZ0,90,['vest','roof'])
put('vest_floor',0,FY,VZ1,0,['vest',ftag(0)]); put('vest_ceiling',0,VW,VZ1,0,['vest','roof'])
put('entry_steps',0,0,VZ1,0,['front','site']); put('back_steps',3,0,Z0,180,['back','site'])
# doors: vestibule (opens in), classroom (opens in), back (opens in)
hx,hz=hinge(0,VZ1,0,-0.42,-0.15); put('door_leaf_front',hx,FY,hz,0,['front','vest']+G,door=85)
hx,hz=hinge(0,Z1,0,-0.42,-0.15); put('door_leaf_class',hx,FY,hz,0,['front']+G,door=85)
hx,hz=hinge(3,Z0,180,-0.42,-0.15); put('door_leaf_back',hx,FY,hz,180,['back']+G,door=85)
# floor, ceiling, platform, cupola, chimney, woodshed
for x in XS:
    for z in ZS: put('floor_tile',x,FY,z,0,[ftag(0)]); put('floor_tile',x,FY+HN,z,0,['roof'])
put('teacher_platform',0,FY,-4.1,0,[ftag(0)])
put('cupola',0,0,3.6,0,['roof']); put('chimney',1.8,0,-4.4,0,['roof'])
put('woodshed',-7.5,0,-4,90,['site'])
put('player_scale_ref',2.5,0,10.5); put('player_scale_ref',-2,FY,1,0,[ftag(0)])

json.dump({'grid':{'module_width':W,'wall_height':HN,'floor_level':FY,'wall_thickness':T,'slab':SLAB,'footprint':[X1-X0,Z1-Z0],
  'classroom':{'x':[X0,X1],'z':[Z0,Z1],'roof':'gable 45 deg, ridge along Z at x=0','ridge':RIDGE},'vestibule':{'x':[-VX,VX],'z':[VZ0,VZ1]}},'placements':L},open(f'{OUT}/building_layout.json','w'),indent=1)
asm=Piece()
for e in L:
    if e['piece']=='player_scale_ref': continue
    Tm=trimesh.transformations.rotation_matrix(math.radians(e['rotY']),[0,1,0]); Tm[:3,3]=e['pos']
    asm.merge(pieces[e['piece']],Tm)
print('triangulos no montado', retrofit.montar(pieces, L, f'{OUT}/building_assembled.glb')); retrofit.finalizar(f'{OUT}/pieces')
print(len(pieces),'pieces',len(L),'placements',sum(1 for e in L if 'door' in e),'doors')
