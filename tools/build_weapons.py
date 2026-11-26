"""Generate original lightweight 3D weapon viewmodels (CC0 not required: project original).
Requires trimesh + numpy. Dimensions in metres, forward direction -Z.
Visual design is stylized tactical and deliberately NOT a copy of MW3 meshes.

Hybrid authoring (02-01): machined volumes come from the legacy chamfer/ring
primitives, while sculpted surfaces are built by the central parametric library
(tools/asset_pipeline/parametric) and only converted to trimesh for assembly.

Usage:
    python tools/build_weapons.py                  # all eight production weapons
    python tools/build_weapons.py --only pistol    # one weapon into assets/models
    python tools/build_weapons.py --only pistol --out TMPDIR   # reproducible check
"""
import json
from pathlib import Path
import numpy as np
import trimesh
from trimesh.transformations import euler_matrix

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'models'
OUT.mkdir(parents=True, exist_ok=True)
MAT = {
    'black': (38, 43, 46, 255), 'polymer':(54, 61, 61, 255),
    'receiver':(73, 81, 84, 255), 'steel':(103, 111, 112, 255),
    'edge':(118, 126, 127, 255), 'tan':(138, 131, 107, 255),
    'darktan':(82, 77, 63, 255), 'brass':(166, 128, 64, 255),
    'walnut':(126,73,40,255), 'walnut_dark':(86,49,29,255),
    'glass':(48, 93, 92, 255), 'recess':(18, 24, 27, 255),
}

if __package__:
    from .asset_pipeline.parametric.production_surfaces import export_profiled_surface
else:
    from asset_pipeline.parametric.production_surfaces import export_profiled_surface

PROFILES = json.loads((ROOT / "tools/asset_pipeline/parametric/production_surface_profiles.json")
                      .read_text(encoding="utf-8"))["profiles"]


def export_surface(meshes):
    return export_profiled_surface(
        ((mesh.metadata["surface_profile"], mesh) for mesh in meshes), PROFILES)


class Gun:
    def __init__(self):
        self.scene = trimesh.Scene()
        self.count = 0
        self.groups = {'body': [], 'mag': [], 'action': []}

    def _group_for(self, name):
        # Split mechanically moving parts into their own draw meshes.
        # The original whole-weapon GLB remains available for NPCs and pickups.
        if name != 'magazine_tube' and name.startswith(('magazine', 'stick_magazine', 'drum', 'pistol_magazine')):
            return 'mag'
        if name.startswith(('slide', 'ejection', 'front_sight', 'rear_sight',
                            'pump_action', 'pump_rib', 'charging_handle')):
            return 'action'
        return 'body'
    def add(self, mesh, color, name='part', profile='painted_metal'):
        mesh.metadata["surface_profile"] = profile
        mesh.visual.face_colors = np.array(MAT.get(color, color), dtype=np.uint8)
        self.count += 1
        self.scene.add_geometry(mesh, geom_name=f'{name}_{self.count:03d}', node_name=f'{name}_{self.count:03d}')
        self.groups[self._group_for(name)].append(mesh)
    def add_parametric(self, spec, color, name='part', matrix=None, offset=None, profile='painted_metal'):
        """Add a mesh produced by the central parametric library.

        The IR mesh owns the surface definition; conversion here preserves every
        vertex and triangle index exactly, so the source of the geometry remains
        the library recipe instead of a second, preview-only model.
        """
        mesh = trimesh.Trimesh(vertices=np.array(spec.vertices, dtype=float),
                               faces=np.array(spec.triangles, dtype=np.int64),
                               process=False)
        if not mesh.is_watertight or mesh.volume <= 0:
            raise ValueError(f'{name}: parametric mesh is not a closed outward solid')
        if matrix is not None:
            mesh.apply_transform(matrix)
        if offset is not None:
            mesh.apply_translation(offset)
        self.add(mesh, color, name, profile)
        return mesh

    def chamfer(self, pos, dims, color, bevel=0.012, angles=(0,0,0), name='shell', profile='painted_metal'):
        # Octagonal XZ outline with slightly inset top/bottom rings, so edges catch light.
        w,h,d = dims; b = min(bevel,w*.20,h*.22,d*.20)
        x,z = w/2,d/2
        points=[(-x+b,-z), (x-b,-z), (x,-z+b), (x,z-b), (x-b,z), (-x+b,z), (-x,z-b),(-x,-z+b)]
        rings=[]
        for y, inset in [(-h/2,b*.75),(-h/2+b,0),(h/2-b,0),(h/2,b*.75)]:
            rings += [(px-np.sign(px)*inset, y, pz-np.sign(pz)*inset) for px,pz in points]
        vs=np.asarray(rings,dtype=float)
        # Shape the furniture in profile while keeping the attachment interfaces fixed.
        fore = (.5 - vs[:,2] / d)
        if name in ('wood_stock', 'solid_stock', 'heavy_stock'):
            vs[:,0] *= 1.0 - .34 * fore
            vs[:,1] *= 1.0 - .48 * fore
            vs[:,1] += h * (.17 * fore - .18 * (1.0 - fore)**2)
        elif name in ('slide', 'slide_top', 'dust_cover'):
            vs[:,0] *= 1.0 - .16 * fore**3
            vs[:,1] -= h * .09 * fore**3
        elif name in ('front_handguard', 'pump_action', 'cooling_shroud', 'lower_handguard'):
            vs[:,0] *= .84 + .16 * (1.0 - abs(vs[:,1]) / (h / 2))
            vs[:,1] += .08 * h * fore
        elif name in ('grip', 'pistol_grip', 'foregrip'):
            vs[:,0] *= .88 + .14 * (.5 - vs[:,1] / h)
            vs[:,2] += .12 * d * (.5 - vs[:,1] / h)**2
        fs=[]
        for j in range(3):
            for i in range(8):
                a=j*8+i; b2=j*8+(i+1)%8; c=(j+1)*8+(i+1)%8; d2=(j+1)*8+i
                fs.extend([(a,b2,c),(a,c,d2)])
        for i in range(1,7):
            fs.append((0,i+1,i)); fs.append((24,24+i,24+i+1))
        mesh=trimesh.Trimesh(vertices=vs,faces=np.array(fs),process=False)
        # The procedural chamfer previously had *all* triangles wound inward.
        # Godot back-face culling then hid the visible exterior of the gun,
        # making receivers/stocks look hollow or transparent. Flip every face.
        mesh.invert()
        if mesh.volume <= 0:
            raise ValueError('Invalid chamfer orientation (expected outward normals)')
        if angles!=(0,0,0): mesh.apply_transform(euler_matrix(*angles))
        mesh.apply_translation(pos)
        self.add(mesh,color,name,profile)
    def cylinder(self, pos, radius, length, color, sections=12, angles=(0,0,0), name='cylinder', profile='painted_metal'):
        m=trimesh.creation.cylinder(radius=radius,height=length,sections=sections)
        if angles!=(0,0,0):m.apply_transform(euler_matrix(*angles))
        m.apply_translation(pos);self.add(m,color,name,profile)
    def rod(self, a,b,radius,color,sections=9,name='rod', profile='painted_metal'):
        a=np.array(a,dtype=float);b=np.array(b,dtype=float); vec=b-a
        mesh=trimesh.creation.cylinder(radius=radius,height=float(np.linalg.norm(vec)),sections=sections)
        mesh.apply_transform(trimesh.geometry.align_vectors([0,0,1],vec/np.linalg.norm(vec)))
        mesh.apply_translation((a+b)/2)
        self.add(mesh,color,name,profile)
    def ring(self, pos, outer, inner, length, color, name='muzzle', profile='painted_metal'):
        rings=[]; faces=[]; num=20
        for r,z in [(outer,-length/2),(outer,length/2),(inner,-length/2),(inner,length/2)]:
            rings.extend([(np.cos(i*2*np.pi/num)*r,np.sin(i*2*np.pi/num)*r,z) for i in range(num)])
        # Outside wall and front lip are counter-clockwise; inside wall
        # and rear lip need the opposite winding (the bore must remain open).
        for first,last,reverse in [(0,1,False),(2,3,True),(0,2,True),(1,3,False)]:
            for i in range(num):
                j=(i+1)%num; a=first*num+i;b=first*num+j;c=last*num+j;d=last*num+i
                if reverse:
                    faces.extend([(a,c,b),(a,d,c)])
                else:
                    faces.extend([(a,b,c),(a,c,d)])
        m=trimesh.Trimesh(vertices=np.array(rings)+np.array(pos),faces=np.array(faces),process=False)
        if m.volume <= 0:
            raise ValueError('Invalid muzzle ring orientation')
        self.add(m,color,name,profile)
    def curved_magazine(self):
        outline = [(-.038,-.063),(-.027,-.074),(.027,-.074),(.038,-.063),
                   (.038,.063),(.027,.074),(-.027,.074),(-.038,.063)]
        vertices = []
        for t in np.linspace(0,1,9):
            a = .52 * t
            center_y = -.056 - .36 * t
            center_z = -.162 - .136 * t * t
            vertices.extend((x, center_y + z*np.sin(a), center_z + z*np.cos(a))
                            for x,z in outline)
        faces = []
        for ring in range(8):
            for i in range(8):
                a = ring*8+i
                b = ring*8+(i+1)%8
                faces.extend(((a,b,b+8),(a,b+8,a+8)))
        for i in range(1,7):
            faces.extend(((0,i+1,i),(64,64+i,64+i+1)))
        mesh = trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
        if mesh.volume < 0:
            mesh.invert()
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
            raise ValueError('Invalid curved magazine')
        self.add(mesh,'black','magazine')
        for x in (-.038,.038):
            for z in (-.040,.0,.040):
                for t in np.linspace(.14,.82,5):
                    self.chamfer((x,-.056-.36*t,-.162-.136*t*t+z),
                                 (.007,.056,.010),'receiver',.003,
                                 angles=(-.61*t,0,0),name='magazine_rib')
        self.chamfer((0,-.417,-.298),(.083,.026,.155),'steel',.007,
                     angles=(-.52,0,0),name='magazine_heel')

    def fixed_sight_bridge(self, parent_name, child_names, name):
        """Connect decorative sight meshes to the fixed visual body.
        Coordinates and extents come from the actual game meshes, not a
        separate manually maintained set of attachment offsets.
        """
        def parts(label):
            matches = [mesh for key, mesh in self.scene.geometry.items()
                       if key.rsplit('_', 1)[0] == label]
            if not matches:
                raise ValueError(f'Missing sight geometry: {label}')
            if any(not any(mesh is body for body in self.groups['body']) for mesh in matches):
                raise ValueError(f'Sight geometry must remain in the fixed body: {label}')
            return matches

        parents = parts(parent_name)
        if len(parents) != 1:
            raise ValueError(f'Ambiguous visual attachment: {parent_name}')
        parent = parents[0]
        children = [mesh for label in child_names for mesh in parts(label)]
        bounds = np.array([mesh.bounds for mesh in children])
        lo = bounds[:, 0, :].min(axis=0)
        hi = bounds[:, 1, :].max(axis=0)
        # A small positive overlap avoids light leaking between meshes.
        top = bounds[:, 0, 1].max() + .006
        bottom = min(parent.bounds[1, 1] - .012, top - .020)
        if bottom <= parent.bounds[0, 1] or top >= bounds[:, 1, 1].min():
            raise ValueError(f'Invalid decorative sight support: {name}')
        center = ((lo[0] + hi[0]) / 2, (bottom + top) / 2, (lo[2] + hi[2]) / 2)
        self.chamfer(center, (hi[0] - lo[0] + .012, top - bottom,
                              hi[2] - lo[2] + .012), 'black', .003, name=name)

    def validate_geometry(self):
        """Reject invalid solid parts before exporting any grouped GLB."""
        seen = set()
        for name, mesh in self.scene.geometry.items():
            if not np.isfinite(mesh.vertices).all():
                raise ValueError(f'{name}: nonfinite vertex')
            if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
                raise ValueError(f'{name}: invalid solid geometry')
            if np.any(mesh.area_faces <= 1e-12):
                raise ValueError(f'{name}: degenerate face')
            if np.any(mesh.visual.face_colors[:, 3] != 255):
                raise ValueError(f'{name}: unexpected alpha in solid geometry')
            # Detect accidental duplicate solid parts independently of vertex order.
            vertices = tuple(sorted(map(tuple, np.round(mesh.vertices, 7))))
            signature = (len(mesh.faces), vertices)
            if signature in seen:
                raise ValueError(f'{name}: duplicate solid geometry')
            seen.add(signature)

    def save(self,name):
        self.validate_geometry()
        merged = self.scene.geometry.values()
        (OUT/f'{name}.glb').write_bytes(export_surface(merged))
        for key, meshes in self.groups.items():
            target = OUT / f'{name}_{key}.glb'
            if meshes:
                target.write_bytes(export_surface(meshes))
            elif target.exists():
                target.unlink()
        print(name, self.count, len((OUT/f'{name}.glb').read_bytes()),
              {group: len(parts) for group, parts in self.groups.items()})

def _loft_library():
    try:
        from asset_pipeline.parametric.organic import (OrganicLoft, LoftSection,
                                                      build_organic)
    except ModuleNotFoundError:  # imported as tools.build_weapons
        from tools.asset_pipeline.parametric.organic import (OrganicLoft, LoftSection,
                                                             build_organic)
    return OrganicLoft, LoftSection, build_organic


def hybrid_loft(g, name, color, length, sections, axis='y', angles=(0, 0, 0),
                pos=(0, 0, 0), radial=24, steps=4, power=2.0, profile='painted_metal'):
    """Closed sculpted surface from the central library.

    ``sections`` are (t, rx, rz, cx, cz) with t in [0, 1]; radii and centres are
    metres in the part's local frame. ``axis='z'`` rotates the loft so its length
    runs from the receiver towards +Z (stocks, pump, handguards) while the part
    keeps the same origin and attachment planes as the replaced chamfer.
    """
    OrganicLoft, LoftSection, build_organic = _loft_library()
    loft = tuple(LoftSection((t - 0.5) * length, (cx, cz), (rx, rz))
                 for t, rx, rz, cx, cz in sections)
    transform = euler_matrix(*angles)
    if axis == 'z':
        transform = transform @ euler_matrix(np.pi / 2.0, 0, 0)
    g.add_parametric(build_organic(OrganicLoft(name, loft, radial_segments=radial,
                                              steps_per_interval=steps,
                                              section_power=power)),
                     color, name, matrix=transform, offset=pos, profile=profile)


def hybrid_grip(g, name, color, dims, angles=(0, 0, 0), pos=(0, 0, 0), power=3.2, profile='painted_metal'):
    """Sculpted pistol/vertical grip inside the replaced chamfer envelope."""
    w, h, d = dims
    hybrid_loft(g, name, color, h, (
        (0.00, w * .330, d * .330, 0.0, d * .050),
        (0.12, w * .450, d * .440, 0.0, d * .020),
        (0.30, w * .500, d * .490, 0.0, 0.0),
        (0.50, w * .500, d * .480, 0.0, -d * .020),
        (0.70, w * .500, d * .470, 0.0, -d * .035),
        (0.88, w * .500, d * .480, 0.0, -d * .010),
        (1.00, w * .500, d * .500, 0.0, d * .020),
    ), angles=angles, pos=pos, profile=profile)


def hybrid_stock(g, name, color, dims, pos, angles=(0, 0, 0), waist=0.86, shoulder=0.99, power=3.6, profile='painted_metal'):
    """Rounded stock surface inscribed in the replaced chamfer envelope.

    The section radii stay at or below half the original width/height, so the
    butt pad, recoil plate and receiver interfaces keep meeting the surface
    they were modelled against: the loft round the corners instead of
    shrinking the part into a cone. ``waist`` is the width factor at the wrist
    and at the butt (0.80 has been enough for every production stock); the
    centre offset drops the comb towards the butt as the chamfer did.
    """
    w, h, d = dims
    # Centre offsets reproduce the comb drop of the replaced profile (+X local
    # becomes -Y after the axis rotation): high at the wrist, low at the butt.
    hybrid_loft(g, name, color, d, (
        (0.00, w * .50 * waist, h * .50 * (waist - .02), 0.0, -h * .120),
        (0.10, w * .50 * .94, h * .50 * .92, 0.0, -h * .090),
        (0.30, w * .50 * shoulder, h * .50 * .97, 0.0, -h * .020),
        (0.60, w * .50, h * .50 * .99, 0.0, h * .070),
        (0.85, w * .50, h * .50 * .98, 0.0, h * .130),
        (0.96, w * .50 * .97, h * .50 * .94, 0.0, h * .150),
        (1.00, w * .50 * .93, h * .50 * .88, 0.0, h * .160),
    ), axis='z', angles=angles, pos=pos, power=power, profile=profile)



def hybrid_pistol_grip(g):
    """Sculpt ergonomic pistol grip with the central parametric library.

    Reference for the section language: published compact 9 mm pistol data
    (185 mm overall, 128 mm height with magazine, 34 mm frame width, 70 mm
    trigger distance) in docs/PADRAO_ARTISTICO_3D.md. The absolute envelope is
    inherited from the production part, not rescaled here, so frame, heel and
    viewmodel contracts stay fixed; the reference guides the palm swell,
    backstrap rake and section count. Proportion targets belong to 02-03. The
    loft replaces the former octagonal chamfer box while the machined slide,
    frame and furniture keep their original recipes: that split is the hybrid
    rule of the standard.
    """
    try:
        from asset_pipeline.parametric.organic import (OrganicLoft, LoftSection,
                                                      build_organic)
    except ModuleNotFoundError:  # imported as tools.build_weapons
        from tools.asset_pipeline.parametric.organic import (OrganicLoft, LoftSection,
                                                             build_organic)
    # Local +Y runs from the magazine heel to the beavertail. Sections bulge at
    # the palm swell and taper at the butt; the centre offset adds the rake
    # that a moulded polymer grip carries into the frame.
    sections = (
        LoftSection(-0.1225, (0.0, 0.0060), (0.0300, 0.0380)),
        LoftSection(-0.0950, (0.0, 0.0030), (0.0400, 0.0490)),
        LoftSection(-0.0550, (0.0, 0.0000), (0.0435, 0.0550)),
        LoftSection(-0.0150, (0.0, -0.0020), (0.0435, 0.0540)),
        LoftSection(0.0300, (0.0, -0.0040), (0.0435, 0.0520)),
        LoftSection(0.0800, (0.0, -0.0010), (0.0435, 0.0540)),
        LoftSection(0.1225, (0.0, 0.0020), (0.0437, 0.0560)),
    )
    loft = OrganicLoft('weapon_pistol_grip', sections, radial_segments=24,
                       steps_per_interval=4, section_power=3.0)
    g.add_parametric(build_organic(loft), 'polymer', 'grip',
                     matrix=euler_matrix(-.28, 0, 0), offset=(0, -.123, .012), profile="polymer")


def hardware(g,zfront):
    # Open bore and minimal flash hider at forward end.
    g.ring((0,.018,zfront), .034,.019,.065,'steel','front_muzzle')
    g.cylinder((0,.018,zfront-.037),.016,.005,'recess',name='bore')

def pistol():
    g=Gun()
    # Compact striker-fired silhouette: a slim slide over a sculpted frame.
    g.chamfer((0,.062,-.113),(.105,.074,.343),'receiver',.012,name='slide')
    g.chamfer((0,.096,-.105),(.082,.022,.315),'steel',.009,name='slide_top')
    g.chamfer((0,.008,-.095),(.105,.050,.30),'black',.009,name='frame')
    g.chamfer((0,-.012,-.207),(.092,.045,.122),'polymer',.010,name='dust_cover')
    hybrid_pistol_grip(g)
    g.chamfer((0,-.227,.047),(.087,.037,.111),'black',.009,name='grip_heel')
    g.chamfer((0,-.154,.040),(.066,.179,.076),'black',.006,angles=(-.28,0,0),name='pistol_magazine')
    g.chamfer((0,-.257,.049),(.088,.018,.104),'polymer',.005,name='magazine_heel')
    g.chamfer((0,.112,-.257),(.019,.018,.026),'black',.003,name='front_sight')
    for x in (-.032,.032):
        g.chamfer((x,.112,.031),(.019,.019,.025),'black',.003,name='rear_sight')
        for j in range(7):
            g.chamfer((x*1.65,.060,.038-j*.013),(.004,.045,.005),'recess',.002,angles=(.24,0,0),name='slide_groove')
        for j in range(7):
            g.chamfer((x*1.32,-.089-j*.019,.010+j*.006),(.005,.008,.065),'recess',.002,name='grip_texture')
    g.chamfer((.044,.099,-.103),(.040,.014,.066),'recess',.004,name='ejection')
    g.chamfer((.044,.106,-.123),(.030,.009,.022),'steel',.003,name='ejection_barrel_hood')
    guard=[(0,-.014,-.169),(0,-.078,-.147),(0,-.094,-.098),(0,-.068,-.048)]
    for start,end in zip(guard,guard[1:]):
        g.rod(start,end,.010,'polymer',name='trigger_guard')
    g.rod((0,-.023,-.082),(0,-.065,-.086),.006,'steel',name='trigger')
    g.ring((0,.061,-.277),.029,.014,.027,'steel','slide_muzzle')
    g.cylinder((0,.061,-.278),.013,.004,'recess',name='bore')
    g.save('pistol')

def common_receiver(g,back,front,main_color='receiver',body=(.20,.16)):
    length=back-front
    g.chamfer((0,0,(front+back)*.5),(body[0],body[1],length),main_color,.026,name='receiver')
    g.chamfer((0,body[1]*.5+.009,(front+back)*.5),(.10,.028,length*.88),'recess',.005,name='top_rail')
    for i in range(9):
        z=back-.065-i*(length-.13)/8
        g.chamfer((0,body[1]*.5+.027,z),(.105,.013,.014),'edge',.003,name='rail_tooth')
    # Trigger and guard, folding stock, receiver fasteners.
    hybrid_grip(g,'pistol_grip','polymer',(.095,.25,.13),angles=(-.23,0,0),pos=(0,-.18,back-.085), profile='polymer')
    g.rod((-.075,-.07,back-.18),(-.075,-.22,back-.18),.008,'black',name='guard')
    g.rod((-.075,-.22,back-.18),(.075,-.22,back-.18),.008,'black',name='guard')
    for i in [-1,1]:
        g.cylinder((i*(body[0]/2+.003),.025,back-.08),.014,.011,'black',angles=(0,np.pi/2,0),name='receiver_pin')

def optic(g,z):
    g.chamfer((0,.168,z),(.09,.055,.10),'black',.012,name='optic_mount')
    g.ring((0,.232,z),.073,.045,.07,'black',name='holo_sight')
    # The previous fully opaque glass disk hid the aiming point. Use an
    # open aperture and a narrow real 3D post instead of a 2D crosshair.
    g.chamfer((0,.2035,z-.028),(.008,.057,.018),'brass',.003,name='aiming_post', profile='brass')
    g.fixed_sight_bridge('top_rail', ('optic_mount',), 'fixed_optic_bridge')
    g.chamfer((0,.27,z),(.026,.024,.06),'edge',.004,name='adjust_knob')

def smg():
    g=Gun()
    common_receiver(g,.25,-.34,'black',(.19,.18))
    g.chamfer((0,-.16,-.13),(.09,.32,.085),'receiver',.012,angles=(-.10,0,0),name='stick_magazine')
    g.chamfer((0,-.319,-.147),(.10,.035,.09),'steel',.008,name='magazine_heel')
    g.chamfer((0,0,-.39),(.21,.15,.32),'polymer',.024,name='front_handguard')
    for x in [-.094,.094]:
        for j in range(4):
            g.chamfer((x,.035,-.305-j*.06),(.012,.021,.028),'recess',.006,name='vent')
    g.rod((-.095,.015,.25),(-.125,.0,.52),.015,'steel',name='folding_stock', profile='exposed_metal')
    g.rod((.095,.015,.25),(.125,.0,.52),.015,'steel',name='folding_stock', profile='exposed_metal')
    g.chamfer((0,-.025,.53),(.28,.18,.038),'polymer',.015,name='stock_pad', profile='rubber')
    g.cylinder((0,.018,-.59),.023,.20,'steel',name='barrel', profile='exposed_metal')
    g.chamfer((.102,.062,.07),(.022,.025,.078),'steel',.005,name='charging_handle', profile='exposed_metal')
    hybrid_grip(g,'foregrip','polymer',(.08,.16,.09),pos=(0,-.01,-.43),power=4.0, profile='polymer')
    g.chamfer((0,.081,-.53),(.13,.034,.14),'steel',.006,name='sight_bridge')
    optic(g,-.07); hardware(g,-.69); g.save('smg')

def rifle():
    g=Gun()
    # Stamped receiver, wooden furniture and continuous curved magazine.
    g.chamfer((0,.009,.016),(.150,.147,.522),'receiver',.010,name='receiver')
    # Rounded stamped cover with shallow transverse ribs and tapered ends.
    sections = [(-.233,.83),(-.222,.96),(-.18,1.0),(-.17,1.045),(-.16,1.0),
                (-.025,1.0),(-.015,1.045),(-.005,1.0),(.135,1.0),(.145,1.045),
                (.155,1.0),(.218,.96),(.233,.83)]
    outline = [(np.cos(a)*.068, .070 + np.sin(a)*.065) for a in np.linspace(0,np.pi,13)]
    outline.extend([(-.066,.056),(.066,.056)])
    vertices = [(x*scale, .070+(y-.070)*scale, z+.014)
                for z,scale in sections for x,y in outline]
    count = len(outline)
    faces = []
    for row in range(len(sections)-1):
        for side in range(count):
            a = row*count + side
            b = row*count + (side+1)%count
            faces.extend([(a,b,b+count),(a,b+count,a+count)])
    end = (len(sections)-1)*count
    for side in range(1,count-1):
        faces.extend([(0,side+1,side),(end,end+side,end+side+1)])
    cover = trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
    if cover.volume < 0:
        cover.invert()
    g.add(cover,'receiver','top_cover')
    g.chamfer((0,.019,.399),(.105,.096,.299),'walnut_dark',.013,name='stock_wrist', profile='wood')
    hybrid_stock(g,'wood_stock','walnut',(.136,.175,.353),pos=(0,-.004,.589),angles=(.13,0,0),shoulder=.83,power=4.0, profile='wood')
    g.chamfer((0,-.035,.769),(.139,.174,.031),'steel',.006,name='butt_plate')
    hybrid_grip(g,'grip','walnut_dark',(.092,.216,.111),angles=(-.26,0,0),pos=(0,-.188,.184), profile='wood')
    for x in (-.078,.078):
        for z in (-.169,.144,.213):
            g.cylinder((x,.011,z),.010,.009,'steel',angles=(0,np.pi/2,0),name='receiver_rivet')
    g.chamfer((.077,.056,-.067),(.009,.034,.234),'recess',.003,name='bolt_track')
    g.chamfer((.091,.058,.004),(.026,.023,.069),'steel',.005,name='charging_handle', profile='exposed_metal')
    g.chamfer((.081,.008,.058),(.009,.026,.215),'black',.005,angles=(-.19,0,0),name='selector')
    g.rod((0,-.063,.099),(0,-.164,.069),.009,'steel',name='guard')
    g.rod((0,-.164,.069),(0,-.164,-.078),.009,'steel',name='guard')
    g.rod((0,-.164,-.078),(0,-.074,-.10),.009,'steel',name='guard')
    g.rod((0,-.072,.016),(0,-.132,.029),.008,'black',name='trigger')
    # Sweep the full magazine cross-section along an arc, avoiding stacked-box seams.
    g.curved_magazine()
    g.chamfer((0,.005,-.419),(.148,.121,.334),'walnut',.022,name='lower_handguard', profile='wood')
    g.chamfer((0,.104,-.438),(.108,.071,.272),'walnut_dark',.014,name='upper_handguard', profile='wood')
    for x in (-.073,.073):
        for z in (-.35,-.41,-.47,-.53):
            g.chamfer((x,.021,z),(.009,.021,.041),'walnut_dark',.004,name='wood_relief', profile='wood')
    g.cylinder((0,.039,-.690),.023,.454,'steel',name='barrel', profile='exposed_metal')
    g.cylinder((0,.105,-.552),.025,.234,'black',name='gas_tube')
    g.chamfer((0,.075,-.663),(.076,.118,.064),'steel',.009,name='gas_block')
    g.chamfer((0,.093,-.797),(.059,.109,.066),'black',.008,name='front_block')
    for x in (-.025,.025):
        g.chamfer((x,.150,-.803),(.009,.051,.037),'steel',.003,name='iron_sight_wing')
        g.chamfer((x,.164,-.218),(.012,.026,.035),'steel',.003,name='iron_sight_notch')
    g.chamfer((0,.158,-.803),(.009,.038,.016),'steel',.003,name='iron_sight_post')
    g.chamfer((0,.133,-.218),(.084,.044,.062),'black',.006,name='fixed_rifle_rear_base')
    g.ring((0,.039,-.914),.032,.016,.070,'steel','muzzle_brake')
    g.save('rifle')

def shotgun():
    g=Gun()
    common_receiver(g,.26,-.24,'receiver',(.205,.20))
    hybrid_loft(g,'pump_action','darktan',.42,(
        (0.00, .22*.50*.80, .165*.50*.78, 0.0, 0.0),
        (0.08, .22*.50*.93, .165*.50*.92, 0.0, 0.0),
        (0.35, .22*.50, .165*.50, 0.0, 0.0),
        (0.65, .22*.50, .165*.50, 0.0, 0.0),
        (0.92, .22*.50*.93, .165*.50*.92, 0.0, 0.0),
        (1.00, .22*.50*.80, .165*.50*.78, 0.0, 0.0),
    ), axis='z', pos=(0,0,-.42), power=3.2)
    for z in np.linspace(-.62,-.22,9):
        g.chamfer((0,-.086,z),(.185,.013,.018),'tan',.003,name='pump_rib')
    g.cylinder((0,.065,-.62),.036,.82,'steel',name='upper_barrel')
    g.cylinder((0,-.045,-.58),.029,.68,'black',name='magazine_tube')
    hybrid_stock(g,'solid_stock','tan',(.15,.20,.65),pos=(0,-.04,.55),shoulder=.79,power=3.2)
    g.chamfer((0,-.055,.88),(.19,.24,.05),'black',.022,name='rubber_butt', profile='rubber')
    g.chamfer((0,.14,-1.01),(.033,.033,.020),'brass',.004,name='bead_sight', profile='brass')
    g.fixed_sight_bridge('upper_barrel', ('bead_sight',), 'fixed_bead_base')
    hybrid_grip(g,'vertical_grip','tan',(.07,.14,.10),pos=(0,.015,-.44))
    g.chamfer((.114,.01,.04),(.018,.042,.12),'recess',.004,name='shell_gate')
    g.ring((0,.065,-1.04),.041,.026,.065,'steel');g.save('shotgun')

def lmg():
    g=Gun()
    common_receiver(g,.32,-.31,'black',(.265,.23))
    g.chamfer((0,-.012,-.54),(.29,.20,.45),'receiver',.03,name='cooling_shroud')
    for x in [-.130,.130]:
        for z in np.linspace(-.36,-.72,6):
            g.chamfer((x,-.015,z),(.015,.075,.035),'recess',.006,name='heat_port')
    g.cylinder((0,.017,-.89),.042,.48,'steel',name='heavy_barrel')
    hardware(g,-1.13)
    g.cylinder((0,-.27,-.035),.205,.21,'darktan',sections=24,angles=(0,np.pi/2,0),name='drum')
    g.cylinder((.11,-.27,-.035),.12,.009,'black',sections=16,angles=(0,np.pi/2,0),name='drum_hub')
    hybrid_stock(g,'heavy_stock','polymer',(.24,.21,.48),pos=(0,.00,.52),shoulder=.91,power=5.0)
    g.chamfer((0,-.015,.79),(.265,.245,.052),'recess',.018,name='butt_pad')
    # Offset the carry handle so it never crosses the optic's viewing axis.
    g.rod((-.128,.14,-.17),(-.174,.275,-.12),.013,'steel',name='carry_handle')
    g.rod((-.174,.275,-.12),(-.174,.275,.12),.013,'steel',name='carry_handle')
    g.rod((-.174,.275,.12),(-.127,.14,.16),.013,'steel',name='carry_handle')
    g.rod((-.08,-.07,-.735),(-.20,-.43,-.83),.016,'black',name='bipod')
    g.rod((.08,-.07,-.735),(.20,-.43,-.83),.016,'black',name='bipod')
    g.chamfer((.146,.035,.18),(.038,.035,.10),'steel',.006,name='charging_handle', profile='exposed_metal')
    g.chamfer((0,-.18,-.11),(.28,.18,.18),'darktan',.022,name='ammo_box')
    g.chamfer((0,.09,-.16),(.16,.05,.14),'steel',.008,name='feed_cover')
    optic(g,.12); g.save('lmg')

def sniper():
    g=Gun()
    # MRS-7: original lightweight bolt-action precision rifle; forward is -Z.
    g.chamfer((0.0, 0.0, -0.095), (.188, .172, .57), 'receiver', .020, name='receiver')
    g.chamfer((0.0, .094, -.12), (.145, .045, .51), 'black', .012, name='receiver_rail')
    g.chamfer((0.0, -.040, .35), (.108, .135, .54), 'polymer', .023, name='stock_wrist', profile='wood')
    hybrid_stock(g,'precision_stock','black',(.17,.22,.29),pos=(0.0,-.055,.66),shoulder=.81,power=4.5)
    g.chamfer((0.0, -.058, .815), (.19, .235, .055), 'polymer', .015, name='butt_pad')
    hybrid_grip(g,'pistol_grip','polymer',(.100,.23,.13),angles=(-.22,0,0),pos=(0.0,-.174,.135), profile='polymer')
    g.chamfer((0.0, -.22, -.165), (.108, .20, .136), 'black', .015, name='magazine_box')
    g.chamfer((0.0, -.326, -.16), (.111, .027, .144), 'steel', .007, name='magazine_heel')
    g.chamfer((0.0, -.01, -.47), (.245, .17, .50), 'polymer', .026, name='freefloat_handguard')
    for x in (-.126,.126):
        for z in np.linspace(-.35,-.66,6):
            g.chamfer((x, .015, z), (.013, .026, .057), 'recess', .004, name='vent_slot')
    g.cylinder((0.0, .037, -.91), .025, 1.12, 'steel', sections=16, name='precision_barrel')
    g.cylinder((0.0, .037, -1.35), .042, .14, 'black', sections=16, name='barrel_brake')
    g.ring((0.0, .037, -1.425), .040, .020, .06, 'steel', name='muzzle_ring')
    g.chamfer((.112, .053, -.018), (.030, .023, .10), 'steel', .006, name='charging_handle', profile='exposed_metal')
    g.chamfer((.078, .063, -.10), (.014, .027, .19), 'recess', .004, name='bolt_slot')
    g.chamfer((0.0, .15, -.20), (.095, .024, .08), 'black', .008, name='iron_rear_base')
    for side in (-.037, .037):
        g.chamfer((side, .17825, -.22), (.012, .0305, .033), 'steel', .004, name='iron_rear_sight')
        g.chamfer((side, .183, -1.17), (.010, .051, .038), 'steel', .003, name='iron_front_guard')
    g.chamfer((0.0, .178, -1.17), (.010, .031, .018), 'steel', .003, name='iron_front_post')
    g.fixed_sight_bridge('receiver_rail', ('iron_rear_sight',), 'fixed_rear_bridge')
    g.fixed_sight_bridge('precision_barrel', ('iron_front_guard', 'iron_front_post'), 'fixed_front_bridge')
    for x in (-.11, .11):
        g.rod((x,-.10,-.71),(x*1.5,-.41,-.80),.012,'black',name='folding_bipod')
    g.save('sniper')


def bolt_sniper():
    g=Gun()
    # VLR-8: traditional walnut-stock rifle, open bolt/ejection assembly.
    # Distinct silhouette from the MRS-7's modern freefloat polymer chassis.
    hybrid_stock(g,'stock_body','walnut',(.158,.165,1.16),pos=(0.0,-.044,.23),waist=.88,shoulder=.92,power=3.0, profile='wood')
    hybrid_stock(g,'cheek_rest','walnut_dark',(.155,.20,.20),pos=(0.0,-.050,.73),waist=.92, profile='wood')
    g.chamfer((0.0, -.048, .86), (.18, .20, .047), 'black', .012, name='stock_pad', profile='rubber')
    g.chamfer((0.0, -.03, -.185), (.177, .155, .50), 'walnut_dark', .018, name='forearm_wood', profile='wood')
    for side in (-.076,.076):
        for z in (-.22,-.32,-.43):
            g.chamfer((side,-.075,z),(.007,.017,.07),'walnut',.003,name='wood_grip_rib', profile='wood')
    g.chamfer((0.0, .043, -.04), (.145, .145, .37), 'steel', .018, name='steel_receiver')
    g.chamfer((0.0, .122, -.04), (.102, .022, .34), 'recess', .006, name='receiver_sight_rail')
    hybrid_grip(g,'grip_stock','walnut',(.084,.25,.106),angles=(-.29,0,0),pos=(0.0,-.17,.03), profile='wood')
    g.chamfer((0.0, -.225, -.06), (.101, .177, .142), 'black', .012, name='magazine_box')
    g.chamfer((0.0, -.31, -.065), (.11, .025, .15), 'steel', .006, name='magazine_heel')
    g.cylinder((0.0, .050, -.85), .023, 1.20, 'steel', sections=16, name='long_barrel')
    g.chamfer((0.0, .053, -1.42), (.052, .069, .086), 'black', .010, name='fixed_front_sight_base')
    g.ring((0.0, .051, -1.47), .032, .017, .065, 'steel', name='open_muzzle')
    # Rear notch and forward blade allow proper scoped and unscoped tests.
    for side in (-.032,.032):
        g.chamfer((side,.17875,-.13),(.011,.0345,.035),'black',.003,name='iron_rear_notch')
        g.chamfer((side,.17,-1.42),(.010,.046,.029),'black',.003,name='iron_front_wing')
    g.chamfer((0.0,.183,-1.42),(.009,.026,.015),'steel',.003,name='iron_front_blade')
    g.fixed_sight_bridge('receiver_sight_rail', ('iron_rear_notch',), 'fixed_rear_bridge')
    g.fixed_sight_bridge('fixed_front_sight_base', ('iron_front_wing', 'iron_front_blade'), 'fixed_front_bridge')
    # All moving bolt parts belong to the action GLB for real animation.
    g.chamfer((.048,.090,.03),(.043,.043,.26),'steel',.008,name='charging_handle_bolt_body')
    g.rod((.094,.092,.08),(.178,.10,.07),.012,'steel',name='charging_handle_stem')
    g.cylinder((.182,.102,.07),.020,.037,'black',angles=(0,np.pi/2,0),name='charging_handle_knob')
    g.chamfer((.073,.102,-.04),(.012,.035,.17),'recess',.004,name='fixed_ejection_port')
    g.save('bolt_sniper')


def sentinela():
    g = Gun()
    hybrid_stock(g,'heavy_stock','darktan',(.14,.16,.62),pos=(0,-.045,.32))
    hybrid_stock(g,'lower_handguard','darktan',(.13,.12,.56),pos=(0,-.02,-.30),shoulder=.90,power=5.0)
    hybrid_grip(g,'grip','polymer',(.084,.17,.10),angles=(-.25,0,0),pos=(0,-.12,.14))
    g.cylinder((0,.055,-.02),.054,.47,'receiver',sections=20,name='receiver')
    g.cylinder((0,.055,-.68),.025,.88,'steel',sections=20,name='barrel', profile='exposed_metal')
    g.ring((0,.055,-1.12),.032,.015,.075,'black')
    g.chamfer((0,-.13,-.12),(.08,.16,.12),'black',.01,name='magazine')
    g.rod((.035,.065,.12),(.09,.015,.15),.012,'steel',name='charging_handle', profile='exposed_metal')
    g.chamfer((0,.13,-.99),(.01,.08,.014),'black',.002,name='sight_post')
    for x in (-.024,.024):
        g.chamfer((x,.133,.12),(.014,.074,.025),'black',.003,name='sight_notch')
    g.fixed_sight_bridge('receiver', ('sight_notch',), 'fixed_rear_bridge')
    g.fixed_sight_bridge('barrel', ('sight_post',), 'fixed_front_bridge')
    g.save('sentinela')

RECIPES = {'pistol': pistol, 'smg': smg, 'rifle': rifle, 'shotgun': shotgun,
           'lmg': lmg, 'sniper': sniper, 'bolt_sniper': bolt_sniper,
           'sentinela': sentinela}

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', choices=sorted(RECIPES),
                        help='rebuild a single weapon instead of the whole arsenal')
    parser.add_argument('--out', help='write GLBs to this directory instead of assets/models')
    args = parser.parse_args()
    if args.out:
        OUT = Path(args.out).resolve()
        OUT.mkdir(parents=True, exist_ok=True)
    for key in ([args.only] if args.only else RECIPES):
        RECIPES[key]()
