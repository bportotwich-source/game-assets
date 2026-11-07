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
# KIT 15: posto de gasolina: 14 x 8 m convenience store (painted block, glass storefront, blue parapet band),
# 18 x 10 m flat canopy on 4 columns over 2 pump islands, price pylon, dumpster enclosure
# =====================================================================================
from PIL import ImageFont
COL.update({'block':(234,226,208),'band':(34,72,140),'trim':(246,246,242),'alu':(196,200,204),'glass':(150,190,210),
            'door':(34,72,140),'tile':(224,226,222),'store_floor':(208,204,196),'concrete':(186,184,178),'light':(255,244,214),
            'bollard':(236,196,40),'screen':(36,42,52),'dark':(62,64,70),'hose':(30,30,32),'pump':(244,244,240),'red':(196,44,38)})
def block_texture(px=256,seed=91):
    # tile 1.0 x 0.4 m: two courses of 0.2 m painted blocks, 0.5 m long, running bond, soft shading
    rnd=random.Random(seed); h=int(px*0.4); im=Image.new('RGB',(px,h),(206,198,182)); d=ImageDraw.Draw(im); m=max(2,int(px*0.008))
    base=[(234,226,208),(230,222,204),(236,229,212)]
    for r in range(2):
        off=px/4 if r%2 else 0; y0=r*h/2
        for i in range(-1,3):
            c=rnd.choice(base); x0=i*px/2+off
            for dx in (-px,0,px): d.rectangle([x0+dx+m/2,y0+m/2,x0+dx+px/2-m/2,y0+h/2-m/2],fill=c)
    a=np.asarray(im,dtype=np.float32); n=_noise(px,16,seed)[:h,:]*0.6+_noise(px,64,seed+1)[:h,:]*0.5
    a=np.clip(a+n[...,None]*8,0,255).astype(np.uint8)
    return Image.fromarray(a).transpose(Image.FLIP_TOP_BOTTOM)
PY_W,PY_H=2.4,1.6
def pylon_texture(top='POSTO',sub='24 HORAS'):
    w,h=600,400; im=Image.new('RGB',(w,h),(34,72,140)); d=ImageDraw.Draw(im)
    d.rectangle([14,14,w-15,h-15],outline=(246,246,242),width=10)
    f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',130); g=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',64)
    tw=d.textlength(top,font=f); d.text(((w-tw)/2,60),top,font=f,fill=(246,246,242))
    d.rectangle([60,236,w-60,246],fill=(236,196,40))
    tw=d.textlength(sub,font=g); d.text(((w-tw)/2,270),sub,font=g,fill=(236,196,40))
    return im
BLOCK_TEX=block_texture(); SIGN_TEX=pylon_texture()
for nm,im in (('block',BLOCK_TEX),('sign',SIGN_TEX)): im.save(os.path.join(OUT,nm+'_texture.png'))
TEX={'block':(BLOCK_TEX,1.0,0.4),'plaster':(PLASTER_TEX,1.0,1.0),'sign':(SIGN_TEX,1.0,1.0)}
SIGN=(-PY_W/2,4.3,PY_W,PY_H)
MATS = {k:PBRMaterial(name=k, baseColorFactor=[c/255 for c in v]+[1.0], metallicFactor=0.0, roughnessFactor=0.9) for k,v in COL.items()}
for k,(im,_,_) in TEX.items(): MATS[k]=PBRMaterial(name=k,baseColorTexture=im,baseColorFactor=[255,255,255,255],metallicFactor=0.0,roughnessFactor=0.9)

HS=4.0; HI=HS-SLAB      # store walls, interior partitions up to the ceiling
def store_band(p): p.box('band',-W/2,W/2,HS-0.45+0.015,HS+0.015,0.0,0.03)     # blue band at the wall top: hides the roof edge
def store_plinth(p,segs=((-W/2,W/2),)):
    for a,b in segs: p.box('dark',a,b,0,0.3,0.0,0.02)
def alu_frame(p,ow,oy0,oy1,bars=(),mull=()):
    x=ow/2; f=0.06
    p.box('alu',-x,-x+f,oy0,oy1,-0.2,-0.08); p.box('alu',x-f,x,oy0,oy1,-0.2,-0.08)
    p.box('alu',-x,x,oy1-f,oy1,-0.2,-0.08)
    if oy0>0.01: p.box('alu',-x,x,oy0,oy0+f,-0.2,-0.08)
    for y in bars: p.box('alu',-x+f,x-f,y-0.03,y+0.03,-0.19,-0.09)
    for xx in mull: p.box('alu',xx-0.03,xx+0.03,oy0,oy1,-0.19,-0.09)
def wall_store(kind):
    p=Piece()
    if kind=='storefront':
        ow,oy0,oy1=1.8,0.6,3.2; wall_with_opening(p,'block',ow,oy0,oy1,HS)
        p.box('glass',-ow/2,ow/2,oy0,oy1,-0.15,-0.13); alu_frame(p,ow,oy0,oy1,bars=(2.5,))
        p.box('alu',-ow/2-0.04,ow/2+0.04,oy0-0.06,oy0+0.005,-0.06,0.05); store_plinth(p)
    elif kind=='entry':
        ow,oy1=1.8,3.2; wall_with_opening(p,'block',ow,0.0,oy1,HS)
        p.box('glass',-ow/2+0.06,ow/2-0.06,2.56,oy1-0.06,-0.15,-0.13); alu_frame(p,ow,0.0,oy1,bars=(2.53,))
        store_plinth(p,((-W/2,-ow/2),(ow/2,W/2)))
    elif kind=='small':
        ow,oy0,oy1=0.6,1.6,2.4; wall_with_opening(p,'block',ow,oy0,oy1,HS); window(p,ow,oy0,oy1,lintel=None,mull=False); store_plinth(p)
    elif kind=='service':
        ow=1.0; wall_with_opening(p,'block',ow,0.0,2.3,HS); x=ow/2
        p.box('frame',-x,-x+0.07,0,2.3,-0.22,0.02); p.box('frame',x-0.07,x,0,2.3,-0.22,0.02); p.box('frame',-x,x,2.23,2.3,-0.22,0.02)
        p.box('alu',-0.7,0.7,2.4,2.46,0.0,0.5)    # small steel canopy over the door
        store_plinth(p,((-W/2,-x),(x,W/2)))
    else:
        wall_with_opening(p,'block',0,0,0,HS); store_plinth(p)
    store_band(p); return p
def corner_store():
    p=Piece(); e=0.03; p.box('block',-T-0.01,e,0,HS-0.01,-T-0.01,e)
    p.box('band',-T+0.01,e+0.03,HS-0.45+0.015,HS+0.015,-T+0.01,e+0.03); p.box('dark',-T+0.01,e+0.02,0,0.3,-T+0.01,e+0.02); return p
def parapet(corner_=False):
    """Blue parapet with a white stripe and cap on the store roof edge. Pivot like the walls, at the roof level."""
    p=Piece()
    def bx(mat,y0,y1,d,back=-T):
        if corner_: p.box(mat,back,0.03+d,y0,y1,back,0.03+d)
        elif mat=='trim': p.box(mat,-W/2-0.002,W/2+0.002,y0,y1,back,0.03+d)   # stripe runs 2 mm into the next module: its end never shares the band's end face
        else: p.box(mat,-W/2,W/2,y0,y1,back,0.03+d)
    bx('band',0.0,0.7,0.0); bx('trim',0.24,0.36,0.02,back=-0.01); bx('trim',0.7,0.8,0.04,back=-T-0.04)
    return p
def store_floor(mat='store_floor'):
    p=Piece(); p.box(mat,-W/2,W/2,-0.03,0,-W/2,W/2); p.box('plaster',-W/2+0.02,W/2-0.02,-SLAB,-0.03,-W/2+0.02,W/2-0.02); return p
def door_leaf_glass(w=0.83,h=2.47):
    """Aluminium and glass shop door leaf. Pivot: hinge, bottom. Closed = along +X."""
    p=Piece(); f=0.07
    p.box('alu',0,f,0,h,-0.025,0.025); p.box('alu',w-f,w,0,h,-0.025,0.025); p.box('alu',f,w-f,0,0.2,-0.025,0.025); p.box('alu',f,w-f,h-f,h,-0.025,0.025)
    p.box('glass',f,w-f,0.2,h-f,-0.008,0.008); p.box('dark',w-0.16,w-0.12,0.8,1.5,0.025,0.06); p.box('dark',w-0.16,w-0.12,0.8,1.5,-0.06,-0.025); return p
# ---------- canopy: 18 x 10 m deck at 5.0 m on 4 clad columns, 1.1 m blue fascia with a white stripe ----------
CY=5.0; CT=5.6
def canopy_panel():
    p=Piece(); p.box('trim',-W/2,W/2,CY,CT,-W/2,W/2); p.box('light',-0.35,0.35,CY-0.02,CY,-0.35,0.35); return p
def canopy_fascia(corner_=False):
    """Edge of the canopy. Pivot: on the deck edge line at ground level, outside to +Z."""
    p=Piece(); d=0.15
    if corner_:
        p.box('band',0,d,CY-0.1,CT+0.4,0,d)
        p.box('trim',0,d+0.02,5.3,5.5,d,d+0.02); p.box('trim',d,d+0.02,5.3,5.5,0,d)
        p.box('trim',0,d+0.03,CT+0.4,CT+0.46,0,d+0.03)
    else:
        p.box('band',-W/2,W/2,CY-0.1,CT+0.4,0.0,d); p.box('trim',-W/2,W/2,5.3,5.5,d,d+0.02); p.box('trim',-W/2,W/2,CT+0.4,CT+0.46,-0.05,d+0.03)
    return p
def canopy_column():
    p=Piece(); s=0.25; p.box('trim',-s,s,0.0,CY,-s,s); p.box('band',-s-0.02,s+0.02,0.0,1.1,-s-0.02,s+0.02); p.box('trim',-s-0.04,s+0.04,1.1,1.16,-s-0.04,s+0.04); return p
IL=3.6
def pump_island():
    p=Piece(); p.box('concrete',-IL,IL,0,0.15,-0.6,0.6); p.box('bollard',-IL-0.01,IL+0.01,0.0,0.1,-0.61,-0.59)
    p.box('bollard',-IL-0.01,IL+0.01,0.0,0.1,0.59,0.61)
    for x in (-IL+0.3,IL-0.3): p.cyl('bollard',0.1,0.15,1.1,x,0,10)
    return p
def fuel_pump():
    p=Piece(); p.box('pump',-0.45,0.45,0,1.75,-0.25,0.25); p.box('band',-0.47,0.47,1.75,1.95,-0.27,0.27)
    for s in (-1,1):
        z0,z1=sorted((s*0.25,s*0.27)); p.box('screen',-0.25,0.25,1.15,1.5,z0,z1); p.box('dark',-0.35,-0.15,0.6,0.95,z0,z1)
        z0,z1=sorted((s*0.25,s*0.33)); p.box('hose',0.2,0.32,0.7,1.0,z0,z1)
    return p
def price_pylon():
    """Tall brand sign on two legs. Pivot: centre at ground level, sign face to +Z."""
    p=Piece(); x=PY_W/2
    for s in (-1,1): p.box('alu',s*(x-0.05)-0.1,s*(x-0.05)+0.1,0,4.2,-0.1,0.1)
    p.box('band',-x-0.1,x+0.1,4.2,4.2+PY_H+0.2,-0.2,0.2); p.box('sign',-x,x,4.3,4.3+PY_H,0.2,0.22)
    p.box('trim',-x-0.14,x+0.14,4.2+PY_H+0.2,4.2+PY_H+0.28,-0.24,0.24); p.box('concrete',-x-0.3,x+0.3,0,0.3,-0.4,0.4); return p
def dumpster_enclosure():
    """Block screen walls (1.8 m) on three sides of a 3 x 2.4 m pad, open to +Z. Pivot: centre of the pad."""
    p=Piece(); t=0.2; h=1.8
    p.box('concrete',-1.5,1.5,0,0.08,-1.2,1.2)
    p.box('block',-1.5-t,1.5+t,0,h,-1.2-t,-1.2); p.box('block',-1.5-t,-1.5,0,h,-1.2,1.2); p.box('block',1.5,1.5+t,0,h,-1.2,1.2)
    p.box('trim',-1.5-t-0.03,1.5+t+0.03,h,h+0.06,-1.2-t-0.03,-1.2+0.03); p.box('trim',-1.5-t-0.03,-1.5+0.03,h,h+0.06,-1.2,1.2+0.03)
    p.box('trim',1.5-0.03,1.5+t+0.03,h,h+0.06,-1.2,1.2+0.03); return p

pieces={'store_floor':store_floor(),'floor_tile':floor_tile(),'floor_tile_bath':floor_tile_bath(),'storage_floor':store_floor('concrete'),'roof_tile':roof_tile(),
 'door_leaf_glass':door_leaf_glass(),'door_leaf_service':door_leaf(0.86,2.22,False,'door'),'door_leaf_interior':door_leaf(0.86,2.08,False,'frame'),
 'interior_wall_plain':interior_wall(False,h=HI),'interior_wall_doorway':interior_wall(True,h=HI),
 'interior_wall_end':interior_wall_end(h=HI),'interior_wall_end_doorway':interior_wall_end_doorway(h=HI),
 'wall_store_storefront':wall_store('storefront'),'wall_store_entry':wall_store('entry'),'wall_store_small_window':wall_store('small'),
 'wall_store_service_door':wall_store('service'),'wall_store_plain':wall_store('plain'),'corner_store':corner_store(),
 'parapet':parapet(),'parapet_corner':parapet(True),'ac_unit':ac_unit(),
 'canopy_panel':canopy_panel(),'canopy_fascia':canopy_fascia(),'canopy_fascia_corner':canopy_fascia(True),'canopy_column':canopy_column(),
 'pump_island':pump_island(),'fuel_pump':fuel_pump(),'price_pylon':price_pylon(),'dumpster_enclosure':dumpster_enclosure(),
 'player_scale_ref':player_ref(),
}
import shutil; shutil.rmtree(f'{OUT}/pieces',ignore_errors=True); os.makedirs(f'{OUT}/pieces')
for n,p in pieces.items(): p.scene(n).export(f'{OUT}/pieces/{n}.glb',include_normals=True)

# ================= assembly: store x -7..7, z -10..-2 (front +Z); canopy x -9..9, z 2..12 =================
SX0,SX1,SZ0,SZ1=-7,7,-10,-2; CX0,CX1,CZ0,CZ1=-9,9,2,12
SX,SZ=9.0,12.0
L=[]
def put(n,x,y,z,ry=0,tags=(),door=None):
    e={'piece':n,'pos':[round(x,3),round(y,3),round(z,3)],'rotY':ry,'tags':list(tags)}
    if door is not None: e['door']={'closed':ry,'open':ry+door}; e['tags'].append('door')
    L.append(e)
def hinge(x,z,ry,lx,lz):
    r=math.radians(ry); return x+lx*math.cos(r)+lz*math.sin(r), z-lx*math.sin(r)+lz*math.cos(r)
def ftag(fl): return f'floor{fl}'
E0=['ext',ftag(0)]; XS=range(SX0+1,SX1,2); ZS=range(SZ0+1,SZ1,2)
FR={-6:'wall_store_plain',0:'wall_store_entry',6:'wall_store_plain'}
BK={-4:'wall_store_service_door',0:'wall_store_small_window',4:'wall_store_small_window',6:'wall_store_small_window'}
for x in XS:
    put(FR.get(x,'wall_store_storefront'),x,0,SZ1,0,['front','store']+E0); put(BK.get(x,'wall_store_plain'),x,0,SZ0,180,['back','store']+E0)
    put('parapet',x,HS,SZ1,0,['front','roof']); put('parapet',x,HS,SZ0,180,['back','roof'])
for z in ZS:
    put('wall_store_storefront' if z==-3 else 'wall_store_plain',SX1,0,z,90,['right','store']+E0)
    put('wall_store_storefront' if z==-3 else 'wall_store_plain',SX0,0,z,-90,['left','store']+E0)
    put('parapet',SX1,HS,z,90,['right','roof']); put('parapet',SX0,HS,z,-90,['left','roof'])
for ry,x,z,tg in [(0,SX1,SZ1,('front','right')),(90,SX1,SZ0,('right','back')),(180,SX0,SZ0,('back','left')),(-90,SX0,SZ1,('left','front'))]:
    put('corner_store',x,0,z,ry,tg+('store','ext',ftag(0))); put('parapet_corner',x,HS,z,ry,tg+('roof',))
# front double door (opens out), service door at the back (storage)
put('door_leaf_glass',-0.9+0.06,0.015,SZ1-0.14,0,['front','store']+E0,door=-85); put('door_leaf_glass',0.9-0.06,0.015,SZ1-0.14,180,['front','store']+E0,door=85)
hx,hz=hinge(-4,SZ0,180,-0.43,-0.18); put('door_leaf_service',hx,0.015,hz,180,['back','store']+E0,door=85)
# floors and roof
for x in XS:
    for z in ZS:
        back=z<-6
        n='storage_floor' if (back and x<-1) else 'floor_tile' if (back and x in (0,2)) else 'floor_tile_bath' if back else 'store_floor'
        put(n,x,0,z,0,['store',ftag(0)]); put('roof_tile',x,HS,z,0,['roof'])
put('ac_unit',-3,HS,-7,0,['roof']); put('ac_unit',3,HS,-8,0,['roof'])
# rooms: sales floor at the front; storage, office and 2 WCs along the back
def wl_x(z,x0,x1,doors=(),end_lo=False,end_hi=False):
    for c in range(x0+1,x1,2):
        d=c in doors
        if c==x1-1 and end_hi: put('interior_wall_end_doorway' if d else 'interior_wall_end',c,0,z,0,[ftag(0)])
        elif c==x0+1 and end_lo: put('interior_wall_end_doorway' if d else 'interior_wall_end',c,0,z,180,[ftag(0)])
        else: put('interior_wall_doorway' if d else 'interior_wall_plain',c,0,z,0,[ftag(0)])
def wl_z(x,z0,z1,end_lo=False):
    for c in range(z0+1,z1,2):
        put('interior_wall_end' if (c==z0+1 and end_lo) else 'interior_wall_plain',x,0,c,90,[ftag(0)])
def door(x,z,ry,ang=85):
    hx,hz=hinge(x,z,ry,-0.43,0); put('door_leaf_interior',hx,0,hz,ry,[ftag(0)],door=ang)
wl_x(-6,SX0,SX1,doors=(-4,0,4,6),end_lo=True,end_hi=True)
for xw in (-1,3,5): wl_z(xw,SZ0,-6,end_lo=True)
for x in (-4,0,4,6): door(x,-6,0)
# canopy
for x in range(CX0+1,CX1,2):
    for z in range(CZ0+1,CZ1,2): put('canopy_panel',x,0,z,0,['canopy','roof'])
    put('canopy_fascia',x,0,CZ1,0,['canopy','front']); put('canopy_fascia',x,0,CZ0,180,['canopy'])
for z in range(CZ0+1,CZ1,2): put('canopy_fascia',CX1,0,z,90,['canopy','right']); put('canopy_fascia',CX0,0,z,-90,['canopy','left'])
for ry,x,z in [(0,CX1,CZ1),(90,CX1,CZ0),(180,CX0,CZ0),(-90,CX0,CZ1)]: put('canopy_fascia_corner',x,0,z,ry,['canopy'])
for zi in (4.5,9.5):
    put('pump_island',0,0,zi,0,['canopy']);
    for xc in (-2.7,2.7): put('canopy_column',xc,0.15,zi,0,['canopy'])
    for xp in (-1.0,1.0): put('fuel_pump',xp,0.15,zi,0,['canopy'])
put('price_pylon',11,0,13,-30,['site']); put('dumpster_enclosure',9.5,0,-8,0,['site'])
put('player_scale_ref',-3,0,0.5); put('player_scale_ref',2,0,4.5+1.5,0,['canopy']); put('player_scale_ref',3,0,-4,0,['store',ftag(0)])

json.dump({'grid':{'module_width':W,'wall_height':HS,'wall_thickness':T,'slab':SLAB,'footprint':[18,22],
  'store':{'x':[SX0,SX1],'z':[SZ0,SZ1],'roof':'flat, blue parapet'},'canopy':{'x':[CX0,CX1],'z':[CZ0,CZ1],'clear_height':CY}},'placements':L},open(f'{OUT}/building_layout.json','w'),indent=1)
asm=Piece()
for e in L:
    if e['piece']=='player_scale_ref': continue
    Tm=trimesh.transformations.rotation_matrix(math.radians(e['rotY']),[0,1,0]); Tm[:3,3]=e['pos']
    asm.merge(pieces[e['piece']],Tm)
asm.scene('building').export(f'{OUT}/building_assembled.glb',include_normals=True)
print(len(pieces),'pieces',len(L),'placements',sum(1 for e in L if 'door' in e),'doors')
