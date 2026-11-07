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
# KIT 14: quartel de bombeiros: 16 x 12 m brick apparatus hall (3 bays, 6 m walls, metal side-gable roof, mezzanine
# dormitory over the back rooms, fire pole), plus an 8 x 10 m white clapboard wing (office, watch room, kitchen)
# =====================================================================================
COL.update({'siding':(236,234,226),'trim':(246,244,238),'frame':(250,250,248),'shutter':(150,40,36),'shutter_dark':(112,28,26),
            'door':(160,36,32),'bay_red':(178,38,32),'bay_panel':(146,28,24),'pole':(214,178,86),'ridge':(70,74,80),
            'iron':(44,44,48),'siren':(196,40,34)})
def metal_roof_texture(px=256,seed=81):
    # tile 1 x 1 m: standing-seam metal, a seam every 0.5 m (lit edge + shadow), faint streaks
    a=np.zeros((px,px,3),np.float32); base=np.array([150,156,162],np.float32); a[:,:,:]=base
    for k in range(2):
        x0=int(k*px/2); a[:,x0:x0+3,:]=base*1.18; a[:,x0+3:x0+7,:]=base*0.72
    n=_noise(px,8,seed)*0.6+_noise(px,48,seed+1)*0.4; a=np.clip(a+n[...,None]*10,0,255).astype(np.uint8)
    return Image.fromarray(a)
from PIL import ImageFont
SIGN_W,SIGN_H=5.6,0.8
def sign_texture13(text='BOMBEIROS  ·  7'):
    w,h=1400,200; im=Image.new('RGB',(w,h),(250,248,240)); d=ImageDraw.Draw(im)
    d.rectangle([8,8,w-9,h-9],outline=(176,38,32),width=10)
    f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',120)
    tw=d.textlength(text,font=f); d.text(((w-tw)/2,28),text,font=f,fill=(176,38,32))
    return im
SIDING_TEX=siding_texture(seed=83); SHINGLE_TEX=shingle_texture(); METAL_TEX=metal_roof_texture(); SIGN_TEX=sign_texture13()
for nm,im in (('siding',SIDING_TEX),('shingle',SHINGLE_TEX),('brick',BRICK_TEX),('metal_roof',METAL_TEX),('sign',SIGN_TEX)): im.save(os.path.join(OUT,nm+'_texture.png'))
TEX={'siding':(SIDING_TEX,1.0,1.0),'shingle':(SHINGLE_TEX,1.0,1.0),'brick':(BRICK_TEX,1.0,1.0),'plaster':(PLASTER_TEX,1.0,1.0),
     'metal_roof':(METAL_TEX,1.0,1.0),'sign':(SIGN_TEX,1.0,1.0)}
SIGN=(-SIGN_W/2,0.0,SIGN_W,SIGN_H)
MATS = {k:PBRMaterial(name=k, baseColorFactor=[c/255 for c in v]+[1.0], metallicFactor=0.0, roughnessFactor=0.9) for k,v in COL.items()}
for k,(im,_,_) in TEX.items(): MATS[k]=PBRMaterial(name=k,baseColorTexture=im,baseColorFactor=[255,255,255,255],metallicFactor=0.0,roughnessFactor=0.9)

HB=6.02            # hall walls: two 3 m levels, 2 cm above the ceiling slab like the upper walls of the houses
HSPH=6.0; KH=0.5   # hall roof: half span 6 m (12 m deep), about 27 deg, ridge along X
HSPW=4.0; KW=0.75  # wing roof: half span 4 m (8 m wide), about 37 deg, ridge along Z
ROOFH=HB-0.02-1.0  # 5.0: hall roof pieces (inner face meets the wall face at y = 6.0)
ROOFW=H2-0.02-1.0  # 2.0: wing roof pieces (inner face meets the wall face at y = 3.0)
def wall_multi(p,mat,ops,h,hw=W/2,inner='plaster',t=T):
    """Wall module with several openings centred on x = 0, stacked: ops = [(width, y0, y1), ...]."""
    xs=sorted(set([-hw,hw]+[s*o[0]/2 for o in ops for s in (-1,1)]))
    ys=sorted(set([0.0,h]+[max(o[1],0.0) for o in ops]+[o[2] for o in ops])); zs=[-t,-t+0.02,0.0]
    def cell(i,j,k):
        xc=(xs[i]+xs[i+1])/2; yc=(ys[j]+ys[j+1])/2
        for ow,a,b in ops:
            if abs(xc)<ow/2 and max(a,0.0)<yc<b: return None
        return inner if k==0 else mat
    for m,mesh in grid_solid(xs,ys,zs,cell).items(): p.add(m,mesh)
def hall_belt(p,hw=W/2): p.box('trim',-hw,hw,H-0.12+0.015,H+0.015,0.0,0.03)          # covers the mezzanine slab edge
def hall_frieze(p,hw=W/2,h=HB): p.box('trim',-hw,hw,h-0.26+0.015,h+0.015,0.0,0.035)   # top board under the eaves
def door_frame(p,ow,oh,oy0=0.0):
    x=ow/2; p.box('frame',-x,-x+0.07,oy0,oh,-0.22,0.02); p.box('frame',x-0.07,x,oy0,oh,-0.22,0.02); p.box('frame',-x,x,oh-0.07,oh,-0.22,0.02)
LOWW=(0.9,0.85,2.3); UPW=(0.9,3.75,5.2); LOWS=(0.6,1.4,2.2); UPS=(0.6,4.4,5.2); DOOR=(1.0,0.0,2.4)
def wall_hall(kind):
    p=Piece(); ops={'window2':[LOWW,UPW],'door2':[DOOR,UPW],'high':[UPW],'small2':[LOWS,UPS],'plain':[]}[kind]
    wall_multi(p,'brick',ops,HB)
    for ow,a,b in ops:
        if (ow,a,b)==DOOR: door_frame(p,ow,b); p.box('trim',-0.62,0.62,b+0.02,b+0.2,-0.02,0.05)
        else: window(p,ow,a,b,lintel='trim',mull=ow>0.7)
    hall_belt(p); hall_frieze(p); return p
def wall_hall_upper():
    p=Piece(); wall_multi(p,'brick',[],H2); hall_frieze(p,h=H2); return p       # above the wing roof, from y = 3
def wall_hall_party(door,cut=False):
    """Lower 3 m of the hall's left wall where the wing is built against it: plaster both sides. Pivot like an exterior wall."""
    p=Piece(); wall_multi(p,'plaster',[(0.9,0.0,2.1)] if door else [],H,inner='plaster')
    if door:
        for xx in (-0.45,0.45): p.box('frame',xx-0.04,xx+0.04,0,2.14,-T-0.02,0.02)
        p.box('frame',-0.49,0.49,2.08,2.18,-T-0.02,0.02)
    segs=[(-W/2,-0.49),(0.49,W/2)] if door else [(-W/2,W/2)]
    for a,b in segs:
        p.box('trim',a,b,0,0.1,-T-0.015,-T)
        if cut and a<-W/2+0.1: a=-W/2+0.31     # wing-side skirting stops at the wing's back wall
        p.box('trim',a,b,0,0.1,0.0,0.015)
    return p
BAY_W=3.6; BAY_H=4.2
def wall_hall_bay():
    """4 m front wall of one apparatus bay: 3.6 x 4.2 m opening, white jambs and header. Pivot: centre of the 4 m base."""
    p=Piece(); hw=2.0; wall_multi(p,'brick',[(BAY_W,0.0,BAY_H)],HB,hw=hw); x=BAY_W/2
    for s in (-1,1): a,b=sorted((s*(x-0.02),s*(x+0.14))); p.box('trim',a,b,0.0,BAY_H-0.02,-0.305,0.04)
    p.box('trim',-x-0.14,x+0.14,BAY_H-0.02,BAY_H+0.22,-0.305,0.05)
    for s in (-1,1): a,b=sorted((s*(x+0.14),s*hw)); p.box('trim',a,b,H-0.12+0.015,H+0.015,0.0,0.03)   # belt stops at the jambs
    hall_frieze(p,hw=hw); return p
def corner_hall():
    p=Piece(); e=0.03; p.box('brick',-T-0.01,e,0,HB-0.01,-T-0.01,e)
    p.box('trim',-T+0.01,e+0.035,HB-0.26+0.015,HB+0.015,-T+0.01,e+0.035); p.box('trim',-T,e+0.03,H-0.12+0.015,H+0.015,-T,e+0.03); return p
def bay_door_leaf(w=1.78,h=4.15):
    """One leaf of a pair of folding apparatus doors: red, white rails, a band of lights. Pivot: hinge, bottom. Closed = along +X."""
    p=Piece(); p.box('bay_red',0,w,0,h,-0.03,0.03)
    for sg in (1,-1):
        za,zb=(0.03,0.045) if sg>0 else (-0.045,-0.03)
        for y0,y1 in ((0.15,1.35),(1.5,2.55),(3.55,4.0)): p.box('bay_panel',0.1,w-0.1,y0,y1,za,zb)
        p.box('trim',0.05,w-0.05,2.62,2.68,za,zb); p.box('trim',0.05,w-0.05,3.42,3.48,za,zb)
    for i in range(3): x0=0.1+i*(w-0.2)/3; p.box('glass',x0+0.04,x0+(w-0.2)/3-0.04,2.72,3.38,-0.035,0.035)
    p.box('metal',w-0.16,w-0.08,1.1,1.3,0.045,0.08); return p
def roof_panel_m(p,x0,x1,hsp,kr,over,mat):
    us=[-over,hsp]; vs=[0.0,0.02,TV]; xs=[x0,x1]
    def cell(i,j,k): return 'plaster' if k==0 else mat
    for m,mesh in grid_solid(xs,us,vs,cell).items():
        v=mesh.vertices.copy(); u=v[:,1].copy(); w=v[:,2].copy()
        v[:,1]=1.0+kr*u+w; v[:,2]=-u; mesh.vertices=v; p.add(m,mesh)
def hall_slope(x0=-W/2,x1=W/2): p=Piece(); roof_panel_m(p,x0,x1,HSPH,KH,0.45,'metal_roof'); return p
def wing_slope(x0=-W/2,x1=W/2,over=0.4): p=Piece(); roof_panel_m(p,x0,x1,HSPW,KW,over,'shingle'); return p
def gable_hall():
    """Brick gable over a 12 m hall side wall: white rake boards, round louvred vent. Pivot: centre of the base, at y = 6.02."""
    p=Piece(); base=ROOFH-HB; top=lambda x:base+roof_in(HSPH-abs(x),KH)+0.15
    outer=Polygon([(-HSPH,0),(HSPH,0),(HSPH,top(HSPH)),(0,top(0)),(-HSPH,top(-HSPH))])
    ext(p,'brick',outer,-T+0.02,0.0); ext(p,'plaster',outer,-T,-T+0.02)
    c=Polygon([(0.55*math.cos(a),1.45+0.55*math.sin(a)) for a in np.linspace(0,2*math.pi,24,endpoint=False)])
    ext(p,'trim',c.difference(c.buffer(-0.08)),0.0,0.04); ext(p,'vent',c.buffer(-0.08),0.0,0.015)
    for i in range(5): y=1.08+i*0.17; p.box('shutter_dark',-0.36,0.36,y,y+0.04,0.015,0.03)
    rk=unary_union([beam((-HSPH,top(-HSPH)-0.12),(0,top(0)-0.12),0.26),beam((HSPH,top(HSPH)-0.12),(0,top(0)-0.12),0.26)]).intersection(outer)
    ext(p,'trim',rk,0.0,0.03); return p
def hall_sign():
    p=Piece(); x=SIGN_W/2; p.box('trim',-x-0.06,x+0.06,-0.06,SIGN_H+0.06,0.0,0.05); p.box('sign',-x,x,0.0,SIGN_H,0.05,0.07); return p
def siren_mast():
    p=Piece(); p.cyl('iron',0.06,0,2.8,sec=10); p.box('iron',-0.2,0.2,0,0.05,-0.2,0.2)
    p.cyl('siren',0.22,2.8,3.2,sec=16); p.cone('siren',0.24,3.2,3.4,sec=16)
    return p
# ---------- mezzanine: gallery over the apparatus floor, fire pole ----------
def gallery_rail(x0=-W/2): p=Piece(); _rail(p,x0,W/2,0.0,y0=0.0); return p
def gallery_beam(x0=-W/2): p=Piece(); p.box('iron',x0,W/2,-0.25,0.0,-0.075,0.075); return p
def gallery_post(): p=Piece(); p.box('iron',-0.08,0.08,0.0,H-SLAB-0.25,-0.08,0.08); return p
PH=0.5
def floor_tile_pole():
    """Gallery floor module with a 1 x 1 m hole for the fire pole. Pivot: centre."""
    p=Piece(); h=W/2
    for (a,b,c,d) in ((-h,-PH,-h,h),(PH,h,-h,h),(-PH,PH,-h,-PH),(-PH,PH,PH,h)):
        p.box('floor',a,b,-0.03,0,c,d)
    e=0.02
    for (a,b,c,d) in ((-h+e,-PH-e,-h+e,h-e),(PH+e,h-e,-h+e,h-e),(-PH-e,PH+e,-h+e,-PH-e),(-PH-e,PH+e,PH+e,h-e)):
        p.box('plaster',a,b,-SLAB,-0.03,c,d)
    return p
def pole_guard():
    p=Piece(); _rail(p,-PH,PH,-PH-0.06,y0=0.0)                         # behind the hole
    q=Piece(); _rail(q,-PH-0.06,W/2-0.08,0.0,y0=0.0)
    p.merge(q,trimesh.transformations.translation_matrix([PH+0.06,0,0])@trimesh.transformations.rotation_matrix(-math.pi/2,[0,1,0]))
    return p
def fire_pole():
    p=Piece(); p.cyl('pole',0.05,0.0,5.95,sec=14); p.cyl('dark',0.55,0.0,0.04,sec=20)
    p.seg('iron',(0,5.9,0),(0,5.9,-1.06),0.06); return p
def attic_wall(x0=-W/2):
    p=Piece(); p.box('plaster',x0,W/2,0.0,2.1,-0.06,0.06); return p
def interior_wall_wide13(h=H-SLAB,ow=1.6):
    p=Piece(); t=0.12; wall_with_opening(p,'plaster',ow,0,2.2,h,inner='plaster',t=t,centered=True)
    for xx in (-ow/2,ow/2): p.box('frame',xx-0.04,xx+0.04,0,2.24,-t/2-0.02,t/2+0.02)
    p.box('frame',-ow/2-0.04,ow/2+0.04,2.18,2.28,-t/2-0.02,t/2+0.02)
    for a,b in ((-W/2,-ow/2-0.04),(ow/2+0.04,W/2)): p.box('trim',a,b,0,0.1,t/2,t/2+0.015); p.box('trim',a,b,0,0.1,-t/2-0.015,-t/2)
    return p
def _rail(p,x0,x1,z,y0=0.0,h=0.9):
    p.box('trim',x0,x1,y0+h-0.06,y0+h,z-0.05,z+0.05); p.box('trim',x0,x1,y0+0.08,y0+0.14,z-0.03,z+0.03)
    L=x1-x0; k=max(2,int(L/0.13))
    for i in range(1,k): xx=x0+i*L/k; p.box('trim',xx-0.018,xx+0.018,y0+0.14,y0+h-0.06,z-0.018,z+0.018)
def stair_guard(x0,x1):
    p=Piece(); _rail(p,x0,x1,0.0); return p
def wing_wall(kind):
    if kind=='door_hood':
        p=_wsd('door',True); p.merge(door_hood()); p.box('concrete',-0.8,0.8,0,0.15,0.0,0.6); return p
    return _wsd(kind,True)

pieces={'floor_tile':floor_tile(),'floor_tile_bath':floor_tile_bath(),'apparatus_floor':garage_floor(),'floor_tile_pole':floor_tile_pole(),
 'stair_core_slab':stair_core_slab(),'stairs_u_3m':stairs_u(H),'stair_guard':stair_guard(-0.9,0.9),
 'gallery_rail':gallery_rail(),'gallery_beam':gallery_beam(),'gallery_rail_end':gallery_rail(-W/2+0.25),'gallery_beam_end':gallery_beam(-W/2+0.25),'attic_wall_end':attic_wall(-W/2+0.25),'gallery_post':gallery_post(),'pole_guard':pole_guard(),'fire_pole':fire_pole(),'attic_wall':attic_wall(),
 'door_leaf_front':door_leaf(0.94,2.36,True,'door'),'door_leaf_back':door_leaf(0.96,2.3,True,'frame'),'door_leaf_hall':door_leaf(0.86,2.3,True,'door'),
 'door_leaf_interior':door_leaf(0.86,2.08,False,'frame'),'bay_door_leaf':bay_door_leaf(),
 'interior_wall_plain':interior_wall(False),'interior_wall_doorway':interior_wall(True),'interior_wall_wide':interior_wall_wide13(),
 'interior_wall_end':interior_wall_end(),'interior_wall_end_doorway':interior_wall_end_doorway(),
 'wall_hall_window':wall_hall('window2'),'wall_hall_door':wall_hall('door2'),'wall_hall_high_window':wall_hall('high'),
 'wall_hall_small_window':wall_hall('small2'),'wall_hall_plain':wall_hall('plain'),'wall_hall_upper':wall_hall_upper(),
 'wall_hall_party':wall_hall_party(False),'wall_hall_party_end':wall_hall_party(False,True),'wall_hall_party_door':wall_hall_party(True),'wall_hall_bay':wall_hall_bay(),'corner_hall':corner_hall(),
 'gable_hall':gable_hall(),'hall_slope':hall_slope(),'hall_slope_end':hall_slope(x1=W/2+0.3),'hall_slope_end_l':hall_slope(x0=-W/2-0.3),
 'hall_ridge_cap':ridge_cap(hsp=HSPH,kr=KH),'hall_ridge_cap_end':ridge_cap(-0.17,0.17,hsp=HSPH,kr=KH),'hall_sign':hall_sign(),'siren_mast':siren_mast(),
 'wing_wall_window':wing_wall('window'),'wing_wall_small_window':wing_wall('small'),'wing_wall_plain':wing_wall('plain'),
 'wing_wall_door_hood':wing_wall('door_hood'),'wing_wall_door_back':wing_wall('door_back'),'wing_corner_board':corner_board(True),
 'wing_gable':gable_siding(hsp=HSPW,kr=KW,vent=True),
 'wing_slope':wing_slope(),'wing_slope_end':wing_slope(x1=W/2+0.3),'wing_slope_end_l':wing_slope(x0=-W/2-0.3),
 'wing_slope_wall':wing_slope(over=0.02),'wing_slope_wall_end':wing_slope(x1=W/2+0.3,over=0.02),'wing_slope_wall_end_l':wing_slope(x0=-W/2-0.3,over=0.02),
 'wing_ridge_cap':ridge_cap(hsp=HSPW,kr=KW),'wing_ridge_cap_end':ridge_cap(-0.17,0.17,hsp=HSPW,kr=KW),
 'player_scale_ref':player_ref(),
}
import shutil; shutil.rmtree(f'{OUT}/pieces',ignore_errors=True); os.makedirs(f'{OUT}/pieces')
for n,p in pieces.items(): p.scene(n).export(f'{OUT}/pieces/{n}.glb',include_normals=True)

# ================= assembly: hall x -2..14, z -7..5 (front +Z); wing x -10..-2, z -3..7 =================
HX0,HX1,HZ0,HZ1=-2,14,-7,5; WX0,WX1,WZ0,WZ1=-10,-2,-3,7; RZ=-1   # hall ridge at z = -1, wing ridge at x = -6
SX,SZ=14.0,7.0
L=[]
def put(n,x,y,z,ry=0,tags=(),door=None):
    e={'piece':n,'pos':[round(x,3),round(y,3),round(z,3)],'rotY':ry,'tags':list(tags)}
    if door is not None: e['door']={'closed':ry,'open':ry+door}; e['tags'].append('door')
    L.append(e)
def hinge(x,z,ry,lx,lz):
    r=math.radians(ry); return x+lx*math.cos(r)+lz*math.sin(r), z-lx*math.sin(r)+lz*math.cos(r)
def ftag(fl): return f'floor{fl}'
E0=['ext',ftag(0)]
# hall: front (3 bays + 2 piers), back, sides
for bc in (0,6,12):
    put('wall_hall_bay',bc,0,HZ1,0,['front','hall']+E0)
    put('bay_door_leaf',bc-1.78,0.015,HZ1-0.1,0,['front','hall']+E0,door=-85); put('bay_door_leaf',bc+1.78,0.015,HZ1-0.1,180,['front','hall']+E0,door=85)
put('wall_hall_door',3,0,HZ1,0,['front','hall']+E0); put('wall_hall_window',9,0,HZ1,0,['front','hall']+E0)
put('door_leaf_hall',3-0.43,0.015,HZ1-0.18,0,['front','hall']+E0,door=85)
put('hall_sign',6,4.62,HZ1,0,['front','hall']+E0)
BK={-1:'wall_hall_window',1:'wall_hall_window',3:'wall_hall_window',5:'wall_hall_high_window',7:'wall_hall_high_window',9:'wall_hall_door',11:'wall_hall_window',13:'wall_hall_small_window'}
for x,n in BK.items(): put(n,x,0,HZ0,180,['back','hall']+E0)
hx,hz=hinge(9,HZ0,180,-0.43,-0.18); put('door_leaf_back',hx,0.015,hz,180,['back','hall']+E0,door=85)
for z in (-6,-4,-2,0,2,4):
    put('wall_hall_small_window' if z<-3 else 'wall_hall_window',HX1,0,z,90,['right','hall']+E0)
    if z<WZ0: put('wall_hall_window',HX0,0,z,-90,['left','hall']+E0)
    else:
        put('wall_hall_party_door' if z==0 else 'wall_hall_party_end' if z==WZ0+1 else 'wall_hall_party',HX0,0,z,-90,['left','hall',ftag(0)])
        put('wall_hall_upper',HX0,H,z,-90,['left','hall','ext',ftag(1)])
hx,hz=hinge(HX0,0,-90,-0.43,-0.15); put('door_leaf_interior',hx,0,hz,-90,['hall',ftag(0)],door=85)
for ry,x,z,tg in [(0,HX1,HZ1,('front','right')),(90,HX1,HZ0,('right','back')),(180,HX0,HZ0,('back','left')),(-90,HX0,HZ1,('left','front'))]:
    put('corner_hall',x,0,z,ry,tg+('hall','ext',ftag(0)))
# hall roof: metal side gable, ridge along X at z = -1
for x in range(HX0+1,HX1,2):
    put('hall_slope_end_l' if x==HX0+1 else 'hall_slope_end' if x==HX1-1 else 'hall_slope',x,ROOFH,HZ1,0,['front','roof','hall'])
    put('hall_slope_end' if x==HX0+1 else 'hall_slope_end_l' if x==HX1-1 else 'hall_slope',x,ROOFH,HZ0,180,['back','roof','hall'])
    put('hall_ridge_cap',x,ROOFH,RZ,0,['roof','hall'])
for x in (HX0-0.15,HX1+0.15): put('hall_ridge_cap_end',x,ROOFH,RZ,0,['roof','hall'])
put('gable_hall',HX1,HB,RZ,90,['right','hall','ext',ftag(2)]); put('gable_hall',HX0,HB,RZ,-90,['left','hall','ext',ftag(2)])
put('siren_mast',12,ROOFH+roof_out(HSPH,KH)-0.12,RZ,0,['roof','hall'])
# hall floors: apparatus floor + back rooms (ground), mezzanine rooms + gallery (y = 3), ceiling over the rooms (y = 6)
CORE={(5,-6),(7,-6),(5,-4),(7,-4)}
for x in range(HX0+1,HX1,2):
    for z in (-6,-4,-2,0,2,4):
        if z<-3: n='floor_tile_bath' if x==13 else 'apparatus_floor' if x in (9,11) else 'floor_tile'
        else: n='apparatus_floor'
        put(n,x,0,z,0,['hall',ftag(0)])
    for z in (-6,-4):
        if (x,z) not in CORE: put('floor_tile_bath' if x==13 else 'floor_tile',x,H,z,0,['hall',ftag(1)])
        put('floor_tile',x,2*H,z,0,['hall','roof',ftag(2)])   # ceiling over the mezzanine rooms
    put('floor_tile_pole' if x==11 else 'floor_tile',x,H,-2,0,['hall',ftag(1)])
    sfx,ry=('_end',0) if x==HX0+1 else ('_end',180) if x==HX1-1 else ('',0)
    put('gallery_rail'+sfx,x,H,-1.08,ry,['hall',ftag(1)]); put('gallery_beam'+sfx,x,H-SLAB,-1.08,ry,['hall',ftag(1)])
    put('attic_wall'+sfx,x,2*H,-3,ry,['hall',ftag(2)])
for x in (2,10): put('gallery_post',x,0,-1.12,0,['hall',ftag(0)])
put('pole_guard',11,H,-2,0,['hall',ftag(1)]); put('fire_pole',11,0,-2,0,['hall',ftag(0)])
put('stair_core_slab',6,H,-5,0,['hall',ftag(1)]); put('stairs_u_3m',6,0,-3,0,['hall',ftag(0)]); put('stair_guard',5,H,-2.95,0,['hall',ftag(1)])
def wl_x(fl,z,x0,x1,doors=(),wide=(),end_lo=False,end_hi=False,y=None):
    y=lvl(fl) if y is None else y
    for c in range(x0+1,x1,2):
        d=c in doors
        if c==x1-1 and end_hi: put('interior_wall_end_doorway' if d else 'interior_wall_end',c,y,z,0,[ftag(fl)])
        elif c==x0+1 and end_lo: put('interior_wall_end_doorway' if d else 'interior_wall_end',c,y,z,180,[ftag(fl)])
        else: put('interior_wall_wide' if c in wide else 'interior_wall_doorway' if d else 'interior_wall_plain',c,y,z,0,[ftag(fl)])
def wl_z(fl,x,z0,z1,doors=(),end_lo=False,end_hi=False):
    y=lvl(fl)
    for c in range(z0+1,z1,2):
        d=c in doors
        if c==z1-1 and end_hi: put('interior_wall_end_doorway' if d else 'interior_wall_end',x,y,c,-90,[ftag(fl)])
        elif c==z0+1 and end_lo: put('interior_wall_end_doorway' if d else 'interior_wall_end',x,y,c,90,[ftag(fl)])
        else: put('interior_wall_doorway' if d else 'interior_wall_plain',x,y,c,90,[ftag(fl)])
def door(fl,x,z,ry,ang=85):
    hx,hz=hinge(x,z,ry,-0.43,0); put('door_leaf_interior',hx,lvl(fl),hz,ry,[ftag(fl)],door=ang)
# ground: workshop | stair | gear room (wide openings) | WC;  mezzanine: dormitory 1 | stair top | dormitory 2 | bathroom
wl_x(0,-3,-2,4,doors=(1,),end_lo=True); wl_x(0,-3,8,14,doors=(13,),wide=(9,11),end_hi=True)
wl_x(1,-3,-2,4,doors=(1,),end_lo=True); wl_x(1,-3,8,14,doors=(11,13),end_hi=True)
for fl in (0,1):
    for xw in (4,8,12): wl_z(fl,xw,-7,-3,end_lo=True)
door(0,1,-3,0); door(0,13,-3,0); door(1,1,-3,0); door(1,11,-3,0); door(1,13,-3,0)
# wing: walls, roof, floors, rooms (office and watch room at the front, kitchen at the back)
WF={-9:'wing_wall_window',-7:'wing_wall_window',-5:'wing_wall_door_hood',-3:'wing_wall_window'}
WB={-9:'wing_wall_window',-7:'wing_wall_door_back',-5:'wing_wall_window',-3:'wing_wall_small_window'}
for x in (-9,-7,-5,-3):
    put(WF[x],x,0,WZ1,0,['front','wing']+E0); put(WB[x],x,0,WZ0,180,['back','wing']+E0)
for z,n in ((-2,'wing_wall_window'),(0,'wing_wall_small_window'),(2,'wing_wall_window'),(4,'wing_wall_window'),(6,'wing_wall_window')):
    put(n,WX0,0,z,-90,['left','wing']+E0)
put('wing_wall_small_window',WX1,0,6,90,['right','wing']+E0)
put('door_leaf_front',-5-0.47,0.015,WZ1-0.18,0,['front','wing']+E0,door=85)
hx,hz=hinge(-7,WZ0,180,-0.48,-0.18); put('door_leaf_back',hx,0.015,hz,180,['back','wing']+E0,door=85)
for ry,x,z,tg in [(0,WX1,WZ1,('front','right')),(180,WX0,WZ0,('back','left')),(-90,WX0,WZ1,('left','front'))]:
    put('wing_corner_board',x,0,z,ry,tg+('wing','ext',ftag(0)))
for z in range(WZ0+1,WZ1,2):
    put('wing_slope_end' if z==WZ1-1 else 'wing_slope_end_l' if z==WZ0+1 else 'wing_slope',WX0,ROOFW,z,-90,['left','roof','wing'])
    put('wing_slope_wall_end_l' if z==WZ1-1 else 'wing_slope_wall_end' if z==WZ0+1 else 'wing_slope_wall',WX1,ROOFW,z,90,['right','roof','wing'])
    put('wing_ridge_cap',-6,ROOFW,z,90,['roof','wing'])
for z in (WZ1+0.15,WZ0-0.15): put('wing_ridge_cap_end',-6,ROOFW,z,90,['roof','wing'])
put('wing_gable',-6,H2,WZ1,0,['front','wing','ext',ftag(1)]); put('wing_gable',-6,H2,WZ0,180,['back','wing','ext',ftag(1)])
for x in (-9,-7,-5,-3):
    for z in range(WZ0+1,WZ1,2):
        put('floor_tile',x,0,z,0,['wing',ftag(0)]); put('floor_tile',x,H,z,0,['wing','roof',ftag(1)])
wl_x(0,3,-10,-2,doors=(-5,),end_lo=True); wl_z(0,-6,3,7,doors=(4,),end_hi=True)
door(0,-5,3,0); door(0,-6,4,90)
put('player_scale_ref',3,0,HZ1+1.4); put('player_scale_ref',8,0,1,0,['hall',ftag(0)]); put('player_scale_ref',0,H,-2,0,['hall',ftag(1)])
put('player_scale_ref',-7,0,0,0,['wing',ftag(0)])
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

json.dump({'grid':{'module_width':W,'floor_height':H,'wall_thickness':T,'slab':SLAB,'footprint':[24,14],
  'hall':{'x':[HX0,HX1],'z':[HZ0,HZ1],'wall_height':HB,'roof':'metal side gable ~27 deg, ridge along X at z=-1'},
  'wing':{'x':[WX0,WX1],'z':[WZ0,WZ1],'wall_height':H2,'roof':'shingle front gable ~37 deg, ridge along Z at x=-6'}},'placements':L},open(f'{OUT}/building_layout.json','w'),indent=1)
asm=Piece()
for e in L:
    if e['piece']=='player_scale_ref': continue
    Tm=trimesh.transformations.rotation_matrix(math.radians(e['rotY']),[0,1,0]); Tm[:3,3]=e['pos']
    asm.merge(pieces[e['piece']],Tm)
asm.scene('building').export(f'{OUT}/building_assembled.glb',include_normals=True)
print(len(pieces),'pieces',len(L),'placements',sum(1 for e in L if 'door' in e),'doors')
