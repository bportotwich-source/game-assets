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
# KIT 9: shopping gallery (3 floors of shops around a glazed atrium with escalators)
# =====================================================================================
from PIL import ImageFont
COL.update({'render':(236,210,168),'band':(214,186,142),'panel':(196,82,58),'frame2':(70,92,100),'metal':(196,200,204),'steel':(150,156,162),
            'glass':(156,204,214),'roof':(160,156,150),'floor':(226,222,212),'floor_shop':(206,176,136),'tile':(214,226,230),
            'canopy':(140,52,44),'coping':(120,108,96),'canvas':(244,236,220),'sign':(250,246,236),'fascia':(70,92,100),'unit':(204,208,212),'dark':(64,66,70)})
def render_texture(px=256,seed=91):
    n=_noise(px,6,seed)*0.6+_noise(px,32,seed+1)*0.5+_noise(px,128,seed+2)*0.7
    a=np.array(COL['render'],np.float32)[None,None,:]+n[...,None]*14
    im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)); d=ImageDraw.Draw(im)
    d.line([(0,px-1),(px,px-1)],fill=tuple(int(v*0.82) for v in COL['render']),width=2)   # panel joint every metre
    return im
def canvas_texture(px=256):
    im=Image.new('RGB',(px,px),(244,236,220)); d=ImageDraw.Draw(im)
    for i in (0,2): d.rectangle([i*px/4,0,(i+1)*px/4-1,px],fill=(196,58,52))
    return im
def sign_texture(w=1024,h=180,text='GALERIA'):
    im=Image.new('RGB',(w,h),(250,246,236)); d=ImageDraw.Draw(im)
    d.rectangle([8,8,w-9,h-9],outline=(70,92,100),width=8)
    f=ImageFont.load_default(size=120); bb=d.textbbox((0,0),text,font=f)
    d.text(((w-(bb[2]-bb[0]))/2-bb[0],(h-(bb[3]-bb[1]))/2-bb[1]),text,font=f,fill=(70,92,100))
    return im
RENDER_TEX=render_texture(); CANVAS_TEX=canvas_texture(); SIGN_TEX=sign_texture()
for nm,im in (('render',RENDER_TEX),('canvas',CANVAS_TEX),('sign',SIGN_TEX)): im.save(os.path.join(OUT,nm+'_texture.png'))
TEX={'render':(RENDER_TEX,1.0,1.0),'stone':(STONE_TEX,1.0,0.8),'plaster':(PLASTER_TEX,1.0,1.0),'canvas':(CANVAS_TEX,1.0,1.0),'sign':(SIGN_TEX,1.0,1.0)}
SIGN=(-3.0,2.85,6.0,0.9)
MATS = {k:PBRMaterial(name=k, baseColorFactor=[c/255 for c in v]+[1.0], metallicFactor=0.0, roughnessFactor=0.9) for k,v in COL.items()}
for k,(im,_,_) in TEX.items(): MATS[k]=PBRMaterial(name=k,baseColorTexture=im,baseColorFactor=[255,255,255,255],metallicFactor=0.0,roughnessFactor=0.9)

RAISE=0.15; FH=4.0; HI=FH-SLAB; NF=3      # 3 shop floors of 4 m (standard shop height)
def lvl(fl): return RAISE+fl*FH
def rect(x0,y0,x1,y1): return sbox(x0,y0,x1,y1)
def hull(p,mat,pts): p.add(mat,trimesh.convex.convex_hull(np.array(pts,float)))
def ext(p,mat,poly,z0,z1):
    for g in getattr(poly,'geoms',[poly]):
        if g.geom_type!='Polygon' or g.area<1e-6: continue
        m=trimesh.creation.extrude_polygon(g,z1-z0); m.apply_translation([0,0,z0]); p.add(mat,m)
# ---------- exterior walls (one 2 m x 4 m module per floor) ----------
def dress(p,ground,ow=0.0,step=0.0):
    if ground:
        p.box('render',-W/2,W/2,-RAISE,0.0,-T,0.0)
        segs=((-W/2,-ow/2),(ow/2,W/2)) if ow>0 else ((-W/2,W/2),)
        for a,b in segs: p.box('stone',a,b,-RAISE,0.45,0.0,0.04)          # plinth stops at doorways
        if step>0: p.box('stone',-ow/2,ow/2,-RAISE,0.0,0.0,step)
    else:
        p.box('band',-W/2,W/2,-0.25,0.12,0.0,0.05)                          # floor band: hides the slab edge
def wall_render(ground=False,kind='plain'):
    p=Piece()
    if kind=='window':
        wall_with_opening(p,'render',1.2,1.2,2.6,FH); window(p,1.2,1.2,2.6,lintel=None)
    elif kind=='small':
        wall_with_opening(p,'render',0.6,1.9,2.6,FH); window(p,0.6,1.9,2.6,mull=False,lintel=None)
    else:
        wall_with_opening(p,'render',0,0,0,FH)
    if kind=='panel':                                                      # red cladding panel
        p.box('panel',-0.85,0.85,0.5,3.5,0.0,0.05); p.box('frame2',-0.85,0.85,1.6,1.66,0.05,0.07)
    dress(p,ground); return p
def wall_shop_ext(door=False):
    """Ground floor shop window (1.8 x 2.6) or shop door (1.0 x 2.4 + side light). Pivot: bottom-centre of the outer face."""
    p=Piece()
    if door:
        ow=1.0; x=ow/2; wall_with_opening(p,'render',ow,0.015,2.4,FH)
        for (a,b) in ((-x,-x+0.07),(x-0.07,x)): p.box('frame2',a,b,0.015,2.4,-0.24,0.0)
        p.box('frame2',-x,x,2.33,2.4,-0.24,0.0); p.box('metal',-x+0.07,x-0.07,0.0,0.02,-0.24,0.01)
        p.box('frame2',-x-0.05,x+0.05,2.4,2.46,0.0,0.03)
        dress(p,True,ow,0.4)
    else:
        ow=1.8; wall_with_opening(p,'render',ow,0.45,3.05,FH); window(p,ow,0.45,3.05,mull=False,lintel=None)
        p.box('frame2',-0.03,0.03,0.45,3.05,-0.17,-0.1)
        dress(p,True)
    p.box('fascia',-W/2,W/2,3.15,3.6,0.0,0.07); return p
def awning_striped():
    """Red and white canvas awning for one ground floor shop bay. Pivot: bottom-centre of the facade."""
    p=Piece(); d=1.2; y0,y1=3.1,2.55
    hull(p,'canvas',[(x,y,z) for x in (-W/2,W/2) for (y,z) in ((y0,0.065),(y0+0.05,0.065),(y1,d),(y1+0.05,d))])
    p.box('canvas',-W/2,W/2,y1-0.25,y1+0.03,d-0.02,d+0.02); return p
def corner_render(ground=False):
    p=Piece(); a=-T-0.02; y0=-RAISE if ground else -0.25
    p.box('render',a,0.06,y0,FH,a,0.06)
    if ground: p.box('stone',a+0.01,0.1,-RAISE,0.45,a+0.01,0.1)
    else: p.box('band',a+0.01,0.09,-0.25,0.12,a+0.01,0.09)
    return p
# ---------- glass curtain wall over the entrance ----------
def curtain(h=FH,door=False,top=False):
    """2 m curtain wall bay: mullions at the bay edges, spandrel at the slab, glass. Pivot: bottom-centre of the outer face.
    door=True leaves a 1.8 x 2.4 m opening for a pair of glass doors."""
    p=Piece(); sp=0.5
    for (a,b) in ((-W/2,-W/2+0.05),(W/2-0.05,W/2)): p.box('frame2',a,b,-0.25,h-0.25,-0.15,0.03)
    if door:
        for (a,b) in ((-W/2+0.05,-0.9),(0.9,W/2-0.05)): p.box('frame2',a,b,-0.25,0.015,-0.15,0.02)
        for (a,b) in ((-0.95,-0.9),(0.9,0.95)): p.box('frame2',a,b,0.015,2.4,-0.15,0.02)
        p.box('frame2',-0.95,0.95,2.4,2.48,-0.15,0.02)
        for (a,b) in ((-W/2+0.05,-0.95),(0.95,W/2-0.05)): p.box('glass',a,b,0.015,2.4,-0.11,-0.09)
        p.box('glass',-0.95,0.95,2.48,h-0.25,-0.11,-0.09)
        p.box('stone',-0.9,0.9,-RAISE,0.0,0.0,0.5)                        # entrance step flush with the floor
    else:
        p.box('frame2',-W/2+0.05,W/2-0.05,-0.25,sp,-0.15,0.02)                 # spandrel: hides the slab edge
        p.box('glass',-W/2+0.05,W/2-0.05,sp,h-0.25,-0.11,-0.09)
        p.box('frame2',-W/2+0.05,W/2-0.05,2.6,2.65,-0.13,0.0)
    if top: p.box('frame2',-W/2,W/2,h-0.25,h,-0.15,0.03)
    return p
def entry_canopy():
    """Steel canopy over one 2 m entrance bay. Pivot: bottom-centre of the facade."""
    p=Piece(); p.box('canopy',-W/2,W/2,3.0,3.2,0.03,2.0); p.box('trim',-W/2,W/2,2.98,3.0,0.03,2.0)
    p.seg('steel',(0,3.18,1.9),(0,4.2,0.04),0.05); return p
def crown_roof():
    """Roof of the glass lantern over the entrance (8 x 4 m) with the GALERIA sign. Pivot: front edge centre, at the lantern top."""
    p=Piece(); p.box('coping',-4.08,4.08,0.0,0.3,-4.08,0.08)
    x0,y0,w,h=SIGN; y0=y0-2.5
    p.box('sign',x0,x0+w,0.45,0.45+h,0.06,0.12)
    for (a,b,c,d) in ((x0-0.1,x0+w+0.1,0.35,0.45),(x0-0.1,x0+w+0.1,0.45+h,0.55+h),(x0-0.1,x0,0.45,0.45+h),(x0+w,x0+w+0.1,0.45,0.45+h)):
        p.box('frame2',a,b,c,d,0.04,0.14)
    p.box('frame2',x0+0.2,x0+0.3,0.3,0.35,0.04,0.14); p.box('frame2',x0+w-0.3,x0+w-0.2,0.3,0.35,0.04,0.14)
    return p
SIGN=(-3.0,0.45,6.0,0.9)
# ---------- roof ----------
def parapet():
    p=Piece(); p.box('render',-W/2,W/2,-0.15,1.0,-T,0.02); p.box('coping',-W/2,W/2,1.0,1.08,-T-0.04,0.08); return p
def corner_parapet():
    p=Piece(); a=-T-0.02; p.box('render',a+0.01,0.07,-0.15,1.0,a+0.01,0.07); p.box('coping',a-0.04,0.1,1.0,1.08,a-0.04,0.1); return p
def roof_tile_flat():
    p=Piece(); p.box('roof',-W/2,W/2,-0.04,0,-W/2,W/2); p.box('plaster',-W/2+0.02,W/2-0.02,-SLAB,-0.04,-W/2+0.02,W/2-0.02); return p
def skylight_curb(y0=-0.25):
    """Curb around the atrium opening on the roof. Pivot: opening edge, roof level; the opening is toward +Z."""
    p=Piece(); p.box('render',-W/2,W/2,y0,0.4,-0.3,0.03); p.box('coping',-W/2,W/2,0.4,0.45,-0.34,0.07); return p
VR=4.6; VY=0.46-math.sqrt(VR**2-4.07**2)     # vault radius and centre height (springs from the curb top at x = +-4.07)
def vault_arc(r0,r1):
    """Ring sector between radii r0 < r1, springing at x = +-4.07 on the curb top."""
    a0=math.asin(4.07/VR); n=24
    ang=[-a0+2*a0*i/n for i in range(n+1)]
    out=[(r1*math.sin(a),VY+r1*math.cos(a)) for a in ang]; inn=[(r0*math.sin(a),VY+r0*math.cos(a)) for a in ang]
    return Polygon(out+inn[::-1]),[(VR*math.sin(a),VY+VR*math.cos(a)) for a in ang]
def skylight_vault():
    """2 m long bay of the glazed barrel vault over the atrium (span 8 m). Pivot: atrium centre line, roof level; runs along Z."""
    p=Piece(); poly,out=vault_arc(VR-0.03,VR)
    ext(p,'glass',poly,-W/2,W/2)
    rib,_=vault_arc(VR-0.12,VR+0.05); ext(p,'frame2',rib,-0.05,0.05)
    for i in range(4,24,4):
        x,y=out[i]; c=trimesh.creation.cylinder(radius=0.04,height=W-0.02,sections=8); c.apply_translation([x*(VR+0.05)/VR,VY+(y-VY)*(VR+0.05)/VR,0]); p.add('frame2',c)
    return p
def skylight_end():
    """Glazed end wall of the vault (half disc). Pivot: atrium centre line, roof level, at the end of the opening; faces +Z."""
    p=Piece(); _,out=vault_arc(VR-0.03,VR); poly=Polygon(out[::-1]+[]).buffer(0)
    ext(p,'glass',poly,-0.02,0.0)
    for x in (-2.0,0.0,2.0):
        q=poly.buffer(0.04).intersection(rect(x-0.05,0.41,x+0.05,10)); ext(p,'frame2',q,-0.04,0.02)
    return p
# ---------- inside ----------
def floor_tile_mall():
    p=Piece(); p.box('floor',-W/2,W/2,-0.03,0,-W/2,W/2); p.box('plaster',-W/2+0.02,W/2-0.02,-SLAB,-0.03,-W/2+0.02,W/2-0.02); return p
def floor_tile_shop():
    p=Piece(); p.box('floor_shop',-W/2,W/2,-0.03,0,-W/2,W/2); p.box('plaster',-W/2+0.02,W/2-0.02,-SLAB,-0.03,-W/2+0.02,W/2-0.02); return p
def atrium_rail():
    """Edge of a gallery slab over the atrium: fascia on the slab edge + glass balustrade 1.1 m. Pivot: slab edge, floor level; void toward +Z."""
    p=Piece(); p.box('fascia',-W/2,W/2,-0.3,0.02,0.0,0.04)
    p.box('glass',-W/2+0.03,W/2-0.03,0.08,1.02,-0.1,-0.08)
    p.box('steel',-W/2+0.01,W/2-0.01,1.02,1.08,-0.13,-0.05)
    for x in (-0.7,0.7): p.box('steel',x-0.03,x+0.03,0.0,1.02,-0.12,-0.06)
    return p
def shopfront(door=False,h=HI):
    """Glass shop front on the gallery (centred, 0.12 m), with a fascia band for the shop sign. Pivot: centre line, floor level."""
    p=Piece(); t=0.12; top=3.0
    p.box('fascia',-W/2,W/2,top,h-0.005,-t/2,t/2)
    for (a,b) in ((-W/2,-W/2+0.07),(W/2-0.07,W/2)): p.box('frame2',a,b,0.0,top,-t/2,t/2)
    if door:
        for (a,b) in ((-W/2+0.07,-0.96),(0.96,W/2-0.07)): p.box('glass',a,b,0.12,top,-0.01,0.01); p.box('frame2',a,b,0.0,0.12,-0.04,0.04)
        for s in (-1,1): a,b=sorted((s*0.9,s*0.96)); p.box('frame2',a,b,0.0,top,-t/2,t/2)
        p.box('frame2',-0.9,0.9,2.6,top,-0.04,0.04)
    else:
        p.box('glass',-W/2+0.07,W/2-0.07,0.12,top,-0.01,0.01); p.box('frame2',-W/2+0.07,W/2-0.07,0.0,0.12,-0.04,0.04)
    return p
def escalator(rise=FH,run=6.0,w=1.2):
    """Escalator flight (modelled as a walkable stair, 24 steps of 16.7 x 25 cm). Pivot: bottom end, centre, lower floor; rises toward -Z. Balustrades stop at the void edges so nothing stands in the galleries; only flush 0.6 m comb plates reach the floors."""
    p=Piece(); n=24; r=rise/n; t=run/n; x=w/2
    for i in range(n):
        top=(i+1)*r; p.box('steel',-x,x,max(0.0,top-0.4),top,-(i+1)*t,-i*t); p.box('dark',-x,x,top-0.012,top+0.002,-(i+1)*t+0.005,-(i+1)*t+0.03)
    p.box('steel',-x,x,0.0,0.002,0.0,0.6); p.box('steel',-x,x,rise,rise+0.002,-run-0.6,-run)
    hull(p,'steel',[(xx,y,z) for xx in (-x,x) for (z,y) in ((-0.4,0.0),(-0.4,0.02),(-run,rise-0.6),(-run,rise-0.4))])
    for s in (-1,1):
        a,b=sorted((s*x,s*(x+0.1)))
        hull(p,'metal',[(xx,y,z) for xx in (a,b) for (z,y) in ((0.0,0.0),(0.0,0.25),(-run,rise),(-run,rise+0.25))])
        a,b=sorted((s*(x+0.03),s*(x+0.05)))
        hull(p,'glass',[(xx,y,z) for xx in (a,b) for (z,y) in ((-0.05,0.25),(-0.05,0.95),(-run+0.05,rise+0.25),(-run+0.05,rise+0.95))])
        a,b=sorted((s*(x+0.0),s*(x+0.1)))
        hull(p,'dark',[(xx,y,z) for xx in (a,b) for (z,y) in ((0.0,0.95),(0.0,1.02),(-run,rise+0.95),(-run,rise+1.02))])
    return p
def interior_wall_end_doorway(h=HI):
    p=Piece(); t=0.12; e=W/2-T
    xs=[-W/2,-0.45,0.45,e]; ys=[0.0,2.1,h]; zs=[-t/2,t/2]
    def cell(i,j,k): return None if (i==1 and j==0) else 'plaster'
    for m,mesh in grid_solid(xs,ys,zs,cell).items(): p.add(m,mesh)
    for xx in (-0.45,0.45): p.box('frame',xx-0.04,xx+0.04,0,2.14,-t/2-0.02,t/2+0.02)
    p.box('frame',-0.49,0.49,2.08,2.18,-t/2-0.02,t/2+0.02)
    for (a,b) in ((-W/2,-0.49),(0.49,e)): p.box('trim',a,b,0,0.1,t/2,t/2+0.015); p.box('trim',a,b,0,0.1,-t/2-0.015,-t/2)
    return p
def door_leaf_glass(w=0.88,h=2.38):
    p=Piece(); f=0.07
    p.box('frame2',0,f,0,h,-0.025,0.025); p.box('frame2',w-f,w,0,h,-0.025,0.025)
    p.box('frame2',f,w-f,0,0.18,-0.025,0.025); p.box('frame2',f,w-f,h-f,h,-0.025,0.025)
    p.box('glass',f,w-f,0.18,h-f,-0.008,0.008); p.box('metal',w-0.2,w-0.16,0.8,1.5,0.025,0.06); return p
def roof_hvac():
    p=Piece(); p.box('steel',-0.9,0.9,0.0,0.15,-0.6,0.6); p.box('unit',-0.85,0.85,0.15,1.15,-0.55,0.55)
    for x in (-0.4,0.4): p.cyl('dark',0.3,1.15,1.18,x,0.0,20); p.cyl('steel',0.06,1.18,1.2,x,0.0,8)
    return p
CROWN_H=2.4
pieces={'floor_tile_mall':floor_tile_mall(),'floor_tile_shop':floor_tile_shop(),'floor_tile_bath':floor_tile_bath(),'roof_tile_flat':roof_tile_flat(),
 'wall_render_plain_ground':wall_render(True),'wall_render_window_ground':wall_render(True,'window'),'wall_render_small_window_ground':wall_render(True,'small'),
 'wall_render_plain':wall_render(),'wall_render_window':wall_render(False,'window'),'wall_render_small_window':wall_render(False,'small'),'wall_render_panel':wall_render(False,'panel'),
 'wall_shop_window':wall_shop_ext(False),'wall_shop_door':wall_shop_ext(True),'awning_striped':awning_striped(),
 'corner_render_ground':corner_render(True),'corner_render':corner_render(),
 'curtain_wall':curtain(),'curtain_wall_entry':curtain(door=True),'curtain_wall_crown':curtain(CROWN_H,top=True),'entry_canopy':entry_canopy(),'crown_roof':crown_roof(),
 'parapet':parapet(),'corner_parapet':corner_parapet(),'skylight_curb':skylight_curb(),'skylight_curb_end':skylight_curb(-0.27),'skylight_vault':skylight_vault(),'skylight_end':skylight_end(),
 'atrium_rail':atrium_rail(),'shopfront_glass':shopfront(False),'shopfront_door':shopfront(True),'escalator':escalator(),
 'interior_wall_plain':interior_wall(False,HI),'interior_wall_doorway':interior_wall(True,HI),'interior_wall_end':interior_wall_end(HI),'interior_wall_end_doorway':interior_wall_end_doorway(),
 'door_leaf_glass':door_leaf_glass(),'door_leaf_shop':door_leaf_glass(0.94,2.37),'door_leaf_interior':door_leaf(0.86,2.08,False,'frame'),
 'roof_hvac':roof_hvac(),'ac_unit':ac_unit(),'player_scale_ref':player_ref(),
}
import shutil; shutil.rmtree(f'{OUT}/pieces',ignore_errors=True); os.makedirs(f'{OUT}/pieces')
for n,p in pieces.items(): p.scene(n).export(f'{OUT}/pieces/{n}.glb',include_normals=True)

# ================= assembly: 24 x 26 m gallery, 3 floors, front on +Z =================
SX,SZ=12.0,13.0
L=[]
def put(n,x,y,z,ry=0,tags=(),door=None):
    e={'piece':n,'pos':[round(x,3),round(y,3),round(z,3)],'rotY':ry,'tags':list(tags)}
    if door is not None: e['door']={'closed':ry,'open':ry+door}; e['tags'].append('door')
    L.append(e)
def hinge(x,z,ry,lx,lz):
    r=math.radians(ry); return x+lx*math.cos(r)+lz*math.sin(r), z-lx*math.sin(r)+lz*math.cos(r)
FB=list(range(-11,12,2)); SB=list(range(-12,13,2))
faces=[(0,FB,lambda u:(u,SZ),'front'),(90,SB,lambda u:(SX,-u),'right'),(180,FB,lambda u:(-u,-SZ),'back'),(-90,SB,lambda u:(-SX,u),'left')]
def ft(fl): return f'floor{fl}'
P,WN,SM,RP,SH,SD,CW,CE='plain','window','small_window','panel','wall_shop_window','wall_shop_door','curtain_wall','curtain_wall_entry'
G0={'front':{-11:SH,-9:SD,-7:SH,-5:SH,-3:CW,-1:CE,1:CE,3:CW,5:SH,7:SH,9:SD,11:SH},
    'back':{-11:P,-9:WN,-7:P,-5:WN,-3:SM,-1:SM,1:SD,3:WN,5:WN,7:P,9:WN,11:P},
    'left':{12:SH,10:SH,8:P,6:SH,4:P,2:P,0:SH,-2:P,-4:P,-6:SH,-8:P,-10:WN,-12:P},
    'right':{12:SH,10:SH,8:P,6:SH,4:P,2:P,0:SH,-2:P,-4:P,-6:SH,-8:P,-10:WN,-12:P}}
GU={'front':{-11:WN,-9:RP,-7:RP,-5:WN,-3:CW,-1:CW,1:CW,3:CW,5:WN,7:RP,9:RP,11:WN},
    'back':{-11:P,-9:WN,-7:P,-5:WN,-3:SM,-1:SM,1:P,3:WN,5:WN,7:P,9:WN,11:P},
    'left':{12:WN,10:RP,8:P,6:WN,4:RP,2:P,0:WN,-2:RP,-4:P,-6:WN,-8:RP,-10:WN,-12:P},
    'right':{12:WN,10:RP,8:P,6:WN,4:RP,2:P,0:WN,-2:RP,-4:P,-6:WN,-8:RP,-10:WN,-12:P}}
AWN={('front',-11),('front',-9),('front',-7),('front',-5)}
for fl in range(NF):
    y=lvl(fl); Gm=G0 if fl==0 else GU
    for ry,bays,f,tag in faces:
        for u in bays:
            x,z=f(u); wk=x if tag in ('front','back') else z; k=Gm[tag][wk]
            n=k if k.startswith(('wall_','curtain')) else f'wall_render_{k}'+('_ground' if fl==0 else '')
            if n=='wall_render_panel_ground': n='wall_render_plain_ground'
            put(n,x,y,z,ry,[tag,'ext',ft(fl)])
            if fl==0 and (tag,wk) in AWN: put('awning_striped',x,y,z,ry,[tag,'ext'])
            if n==SD:
                hx,hz=hinge(x,z,ry,-0.47,-0.18)
                put('door_leaf_shop',hx,y+0.015,hz,ry,[tag,'ext',ft(fl)],door=85)
            if n==CE:
                hx,hz=hinge(x,z,ry,-0.9,-0.12); put('door_leaf_glass',hx,y+0.015,hz,ry,[tag,'ext',ft(fl)],door=-85)
                hx,hz=hinge(x,z,ry,0.9,-0.12); put('door_leaf_glass',hx,y+0.015,hz,ry+180,[tag,'ext',ft(fl)],door=85)
    for ry,x,z,tg in [(0,SX,SZ,('front','right')),(90,SX,-SZ,('right','back')),(180,-SX,-SZ,('back','left')),(-90,-SX,SZ,('left','front'))]:
        put('corner_render_ground' if fl==0 else 'corner_render',x,y,z,ry,tg+('ext',ft(fl)))
for x in (-3,-1,1,3): put('entry_canopy',x,lvl(0),SZ,0,['front','ext'])
# roof: parapet, lantern over the entrance, skylight over the atrium, plant
YR=lvl(NF)
for ry,bays,f,tag in faces:
    for u in bays:
        x,z=f(u)
        if tag=='front' and abs(x)<4: put('curtain_wall_crown',x,YR,z,ry,['front','roof']); continue
        put('parapet',x,YR,z,ry,[tag,'roof'])
for ry,x,z,tg in [(0,SX,SZ,('front','right')),(90,SX,-SZ,('right','back')),(180,-SX,-SZ,('back','left')),(-90,-SX,SZ,('left','front'))]:
    put('corner_parapet',x,YR,z,ry,tg+('roof',))
for z in (10,12): put('curtain_wall_crown',-4,YR,z,-90,['left','roof']); put('curtain_wall_crown',4,YR,z,90,['right','roof'])
for x in (-3,-1,1,3): put('curtain_wall_crown',x,YR,9,180,['roof'])
put('crown_roof',0,YR+CROWN_H,SZ,0,['front','roof'])
for z in range(-6,7,2): put('skylight_curb',-4,YR,z,90,['roof']); put('skylight_curb',4,YR,z,-90,['roof']); put('skylight_vault',0,YR,z,0,['roof','skylight'])
for x in (-3,-1,1,3): put('skylight_curb_end',x,YR,7,180,['roof']); put('skylight_curb_end',x,YR,-7,0,['roof'])
put('skylight_end',0,YR,7,0,['roof']); put('skylight_end',0,YR,-7,180,['roof'])
for n,x,z,ry in (('roof_hvac',-8,-6,0),('roof_hvac',8,2,90),('roof_hvac',-8,4,90),('ac_unit',8,-10,0),('ac_unit',-9,-11,0),('ac_unit',9,8,0)):
    put(n,x,YR,z,ry,['roof'])
# slabs: atrium void x in [-4,4], z in [-7,7] on the upper floors, bridge at z in [-1,1]; lantern void over the entrance hall at roof level
def atrium(a,b): return abs(a)<4 and abs(b)<7
for fl in range(NF+1):
    y=lvl(fl)
    for a in FB:
        for b in SB:
            if fl>0 and atrium(a,b) and b!=0: continue
            if fl==NF and atrium(a,b): continue
            if fl==NF and abs(a)<4 and b>9: continue
            if fl==NF: put('roof_tile_flat',a,y,b,0,['roof']); continue
            mall=(abs(a)<6 and -9<b<9) or (abs(a)<4 and b>9)
            bath=(-4<a<0 and b<-9)
            put('floor_tile_bath' if bath else ('floor_tile_mall' if mall else 'floor_tile_shop'),a,y,b,0,[ft(fl)])
# atrium balustrades (gaps where the escalators arrive)
ESC_A=(-3,lvl(0),7); ESC_B=(3,lvl(1),-1)
put('escalator',*ESC_A,0,[ft(0)]); put('escalator',*ESC_B,0,[ft(1)])
for fl in (1,2):
    y=lvl(fl)
    for z in (-6,-4,-2,2,4,6): put('atrium_rail',-4,y,z,90,[ft(fl)]); put('atrium_rail',4,y,z,-90,[ft(fl)])
    for x in (-3,-1,1,3):
        if not (fl==2 and x==3): put('atrium_rail',x,y,-7,0,[ft(fl)])
        put('atrium_rail',x,y,7,180,[ft(fl)])
        if not (fl==1 and x==-3): put('atrium_rail',x,y,1,0,[ft(fl)])
        if not (fl==1 and x==3): put('atrium_rail',x,y,-1,180,[ft(fl)])
# interior walls: shops on the sides (6 x 6), corner shops front and back (8 x 4), WCs + office at the back
def wl(fl,x0,z0,x1,z1,doors=(),fronts=None):
    y=lvl(fl)
    if z0==z1:
        for c in range(int(min(x0,x1))+1,int(max(x0,x1)),2):
            if fronts is not None and c in fronts: put('shopfront_door' if c in doors else 'shopfront_glass',c,y,z0,0,[ft(fl)]); continue
            end=abs(c)+1>=SX; d=c in doors
            put(('interior_wall_end' if end else 'interior_wall_'+('doorway' if d else 'plain'))+('_doorway' if end and d else ''),c,y,z0,(0 if c>0 else 180) if end else 0,[ft(fl)])
            if d: hx,hz=hinge(c,z0,0,-0.43,0); put('door_leaf_interior',hx,y,hz,0,[ft(fl)],door=70)
    else:
        for c in range(int(min(z0,z1))+1,int(max(z0,z1)),2):
            if fronts is not None and c in fronts: put('shopfront_door' if c in doors else 'shopfront_glass',x0,y,c,90,[ft(fl)]); continue
            end=abs(c)+1>=SZ; d=c in doors
            put(('interior_wall_end' if end else 'interior_wall_'+('doorway' if d else 'plain'))+('_doorway' if end and d else ''),x0,y,c,(-90 if c>0 else 90) if end else 90,[ft(fl)])
            if d: hx,hz=hinge(x0,c,90,-0.43,0); put('door_leaf_interior',hx,y,hz,90,[ft(fl)],door=70)
ALLZ=set(range(-8,9,2))
for fl in range(NF):
    for x in (-6,6): wl(fl,x,-9,x,9,doors=(-6,0,6),fronts=ALLZ)           # side shop fronts on the galleries
    for x in (-12,6):
        for z in (-3,3): wl(fl,x,z,x+6,z)                                   # dividers between side shops
    for z in (9,-9):
        wl(fl,-12,z,-6,z); wl(fl,6,z,12,z)                                  # side shop | corner shop
        wl(fl,-6,z,-4,z,doors=(-5,),fronts={-5}); wl(fl,4,z,6,z,doors=(5,),fronts={5})
    for x in (-4,4): wl(fl,x,9,x,13)                                        # corner shops | entrance hall / lounge
    wl(fl,-4,-13,-4,-9); wl(fl,-2,-13,-2,-9); wl(fl,0,-13,0,-9); wl(fl,4,-13,4,-9)
    wl(fl,-4,-9,4,-9,doors=(-3,-1,1))             # WCs, office (ground) / storage
put('player_scale_ref',-6,0,SZ+3); put('player_scale_ref',0,lvl(0),4,0,[ft(0)]); put('player_scale_ref',-5,lvl(1),0,0,[ft(1)]); put('player_scale_ref',5,lvl(2),-4,0,[ft(2)])
json.dump({'grid':{'module_width':W,'floor_height':FH,'floors':NF,'wall_thickness':T,'slab':SLAB,'floor_raise':RAISE,'footprint':[2*SX,2*SZ],
  'atrium':{'x':[-4,4],'z':[-7,7],'bridge_z':[-1,1]},'roof':'flat with parapet, glazed barrel vault over the atrium, glass lantern over the entrance'},'placements':L},open(f'{OUT}/building_layout.json','w'),indent=1)
asm=Piece()
for e in L:
    if e['piece']=='player_scale_ref': continue
    Tm=trimesh.transformations.rotation_matrix(math.radians(e['rotY']),[0,1,0]); Tm[:3,3]=e['pos']
    asm.merge(pieces[e['piece']],Tm)
asm.scene('building').export(f'{OUT}/building_assembled.glb',include_normals=True)
print(len(pieces),'pieces',len(L),'placements',sum(1 for e in L if 'door' in e),'doors')
