import bpy, glob, os, re, json, mathutils, sys, math
root=os.environ['ROOT']; outd=os.environ['OUTD']; K=float(os.environ.get('K','0.19'))
rot=json.loads(os.environ.get('ROT','{}'))      # name -> extra rotation deg around up
mount=json.loads(os.environ.get('MOUNT','{}'))  # name -> 'wall'|'ceiling'
CAT={'Bathroom':'banheiro','Beds':'camas','Carpets':'tapetes','Chairs':'cadeiras','Doors':'portas','Drawers':'comodas','Electronics':'eletronicos','Kitchen':'cozinha','Lights':'luzes','Miscellaneous':'diversos','Shelves':'estantes','Sofas':'sofas','Tables':'mesas','Windows':'janelas'}
cat=[]
for f in sorted(glob.glob(root+'/**/*.fbx',recursive=True)):
    rel=os.path.relpath(f,root); c=CAT[rel.split('/')[0]]
    name=re.sub(r'[^a-z0-9]+','_',os.path.basename(f)[:-4].lower()).strip('_')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=f)
    ms=[o for o in bpy.context.scene.objects if o.type=='MESH']
    for o in list(bpy.context.scene.objects):
        if o.type!='MESH': bpy.data.objects.remove(o)
    # bake world transform into mesh
    W={o.name:o.matrix_world.copy() for o in ms}
    for o in ms: o.animation_data_clear()
    for o in ms:
        if o.data.users>1: o.data=o.data.copy()
    for o in ms:
        o.parent=None
    bpy.context.view_layer.update()
    for o in ms:
        o.data.transform(W[o.name]); o.matrix_basis=mathutils.Matrix()
        if W[o.name].determinant()<0: o.data.flip_normals()
    R=mathutils.Matrix.Rotation(math.radians(rot.get(name,0)),4,'Z') if rot.get(name) else None
    bpy.context.view_layer.update()
    S=mathutils.Matrix.Scale(K,4)
    for o in ms:
        o.data.transform(S)
        if R: o.data.transform(R)
    mn=mathutils.Vector((1e9,)*3); mx=-mn
    for o in ms:
        for v in o.data.vertices: mn=mathutils.Vector(map(min,mn,v.co)); mx=mathutils.Vector(map(max,mx,v.co))
    m=mount.get(name,'floor')
    if m=='floor': off=mathutils.Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z))
    elif m=='ceiling': off=mathutils.Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mx.z))
    else: off=mathutils.Vector(((mn.x+mx.x)/2,mx.y,mn.z))  # wall: back face (+Y blender = -Z glTF), bottom
    for o in ms: o.data.transform(mathutils.Matrix.Translation(-off))
    for mat in bpy.data.materials:
        if mat.node_tree:
            for n in list(mat.node_tree.nodes):
                if n.type=='NORMAL_MAP': mat.node_tree.nodes.remove(n)
            p=mat.node_tree.nodes.get('Principled BSDF')
            if p: p.inputs['Roughness'].default_value=0.8; p.inputs['Metallic'].default_value=0.0
    for i,o in enumerate(ms): o.name=name if len(ms)==1 else f"{name}_{i}"
    os.makedirs(f"{outd}/{c}",exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=f"{outd}/{c}/{name}.glb",export_format='GLB',export_apply=True,export_yup=True,export_materials='EXPORT',export_animations=False)
    d=mx-mn
    cat.append(dict(id=name,categoria=c,arquivo=f"{c}/{name}.glb",origem=rel,montagem=m,tamanho_m=[round(d.x,2),round(d.z,2),round(d.y,2)],tris=sum(len(p.vertices)-2 for o in ms for p in o.data.polygons),partes=len(ms)))
json.dump(cat,open(outd+'/catalogo.json','w'),indent=1,ensure_ascii=False)
