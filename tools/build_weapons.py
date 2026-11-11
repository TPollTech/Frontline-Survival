"""Generate original lightweight 3D weapon viewmodels (CC0 not required: project original).
Requires trimesh + numpy. Dimensions in metres, forward direction -Z.
Visual design is stylized tactical and deliberately NOT a copy of MW3 meshes.
"""
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
    def add(self, mesh, color, name='part'):
        mesh.visual.face_colors = np.array(MAT.get(color, color), dtype=np.uint8)
        self.count += 1
        self.scene.add_geometry(mesh, geom_name=f'{name}_{self.count:03d}', node_name=f'{name}_{self.count:03d}')
        self.groups[self._group_for(name)].append(mesh)
    def chamfer(self, pos, dims, color, bevel=0.012, angles=(0,0,0), name='shell'):
        # Octagonal XZ outline with slightly inset top/bottom rings, so edges catch light.
        w,h,d = dims; b = min(bevel,w*.20,h*.22,d*.20)
        x,z = w/2,d/2
        points=[(-x+b,-z), (x-b,-z), (x,-z+b), (x,z-b), (x-b,z), (-x+b,z), (-x,z-b),(-x,-z+b)]
        rings=[]
        for y, inset in [(-h/2,b*.75),(-h/2+b,0),(h/2-b,0),(h/2,b*.75)]:
            rings += [(px-np.sign(px)*inset, y, pz-np.sign(pz)*inset) for px,pz in points]
        vs=np.asarray(rings,dtype=float)
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
        self.add(mesh,color,name)
    def cylinder(self, pos, radius, length, color, sections=12, angles=(0,0,0), name='cylinder'):
        m=trimesh.creation.cylinder(radius=radius,height=length,sections=sections)
        if angles!=(0,0,0):m.apply_transform(euler_matrix(*angles))
        m.apply_translation(pos);self.add(m,color,name)
    def rod(self, a,b,radius,color,sections=9,name='rod'):
        a=np.array(a,dtype=float);b=np.array(b,dtype=float); vec=b-a
        mesh=trimesh.creation.cylinder(radius=radius,height=float(np.linalg.norm(vec)),sections=sections)
        mesh.apply_transform(trimesh.geometry.align_vectors([0,0,1],vec/np.linalg.norm(vec)))
        mesh.apply_translation((a+b)/2)
        self.add(mesh,color,name)
    def ring(self, pos, outer, inner, length, color, name='muzzle'):
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
        self.add(m,color,name)
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
            faces.extend(((0,i,i+1),(64,64+i+1,64+i)))
        mesh = trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
        trimesh.repair.fix_normals(mesh)
        if not mesh.is_watertight or mesh.volume <= 0:
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

    def save(self,name):
        # Concatena geometrias em 1 mesh colorida: 1 draw call aproximada por arma.
        merged = trimesh.util.concatenate(list(self.scene.geometry.values()))
        scene = trimesh.Scene(merged)
        (OUT/f'{name}.glb').write_bytes(scene.export(file_type='glb'))
        for key, meshes in self.groups.items():
            target = OUT / f'{name}_{key}.glb'
            if meshes:
                group_scene = trimesh.Scene(trimesh.util.concatenate(meshes))
                target.write_bytes(group_scene.export(file_type='glb'))
            elif target.exists():
                target.unlink()
        print(name, self.count, len((OUT/f'{name}.glb').read_bytes()),
              {group: len(parts) for group, parts in self.groups.items()})

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
    g.chamfer((0,-.123,.012),(.087,.245,.112),'polymer',.019,angles=(-.28,0,0),name='grip')
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
    g.chamfer((0,.115,(front+back)*.5),(.10,.028,length*.88),'recess',.005,name='top_rail')
    for i in range(9):
        z=back-.065-i*(length-.13)/8
        g.chamfer((0,.133,z),(.105,.013,.014),'edge',.003,name='rail_tooth')
    # Trigger and guard, folding stock, receiver fasteners.
    g.chamfer((0,-.18,back-.085),(.095,.25,.13),'polymer',.014,angles=(-.23,0,0),name='pistol_grip')
    g.rod((-.075,-.07,back-.18),(-.075,-.22,back-.18),.008,'black',name='guard')
    g.rod((-.075,-.22,back-.18),(.075,-.22,back-.18),.008,'black',name='guard')
    for i in [-1,1]:
        g.cylinder((i*(body[0]/2+.003),.025,back-.08),.014,.011,'black',angles=(0,np.pi/2,0),name='receiver_pin')

def optic(g,z):
    g.chamfer((0,.168,z),(.09,.055,.10),'black',.012,name='optic_mount')
    g.ring((0,.232,z),.073,.045,.07,'black',name='holo_sight')
    # The previous fully opaque glass disk hid the aiming point. Use an
    # open aperture and a narrow real 3D post instead of a 2D crosshair.
    g.chamfer((0,.2095,z-.048),(.008,.045,.010),'brass',.003,name='aiming_post')
    g.chamfer((0,.27,z),(.026,.024,.06),'edge',.004,name='adjust_knob')

def smg():
    g=Gun()
    common_receiver(g,.25,-.34,'black',(.19,.18))
    g.chamfer((0,-.16,-.13),(.09,.32,.085),'receiver',.012,angles=(-.10,0,0),name='stick_magazine')
    g.chamfer((0,-.23,-.16),(.10,.035,.09),'steel',.008,name='magazine_heel')
    g.chamfer((0,0,-.39),(.21,.15,.32),'polymer',.024,name='front_handguard')
    for x in [-.112,.112]:
        for j in range(4):
            g.chamfer((x,.035,-.305-j*.06),(.012,.021,.028),'recess',.006,name='vent')
    g.rod((-.095,.015,.25),(-.125,.0,.52),.015,'steel',name='folding_stock')
    g.rod((.095,.015,.25),(.125,.0,.52),.015,'steel',name='folding_stock')
    g.chamfer((0,-.025,.53),(.28,.18,.038),'polymer',.015,name='stock_pad')
    g.cylinder((0,.018,-.59),.023,.20,'steel',name='barrel')
    g.chamfer((.102,.062,.07),(.022,.025,.078),'steel',.005,name='charging_handle')
    g.chamfer((0,-.01,-.43),(.08,.16,.09),'polymer',.018,name='foregrip')
    g.chamfer((0,.10,-.53),(.13,.024,.14),'steel',.006,name='sight_bridge')
    optic(g,-.07); hardware(g,-.69); g.save('smg')

def rifle():
    g=Gun()
    # Stamped receiver, wooden furniture and continuous curved magazine.
    g.chamfer((0,.009,.016),(.150,.147,.522),'receiver',.010,name='receiver')
    g.chamfer((0,.096,.014),(.139,.089,.466),'black',.023,name='top_cover')
    g.chamfer((0,.019,.399),(.105,.096,.299),'walnut_dark',.013,name='stock_wrist')
    g.chamfer((0,-.004,.589),(.136,.175,.353),'walnut',.024,angles=(.13,0,0),name='wood_stock')
    g.chamfer((0,-.035,.769),(.139,.174,.031),'steel',.006,name='butt_plate')
    g.chamfer((0,-.188,.184),(.092,.216,.111),'walnut_dark',.013,angles=(-.26,0,0),name='grip')
    for x in (-.078,.078):
        for z in (-.169,.144,.213):
            g.cylinder((x,.011,z),.010,.009,'steel',angles=(0,np.pi/2,0),name='receiver_rivet')
    g.chamfer((.077,.056,-.067),(.009,.034,.234),'recess',.003,name='bolt_track')
    g.chamfer((.091,.058,.004),(.026,.023,.069),'steel',.005,name='charging_handle')
    g.chamfer((.081,.008,.058),(.009,.026,.215),'black',.005,angles=(-.19,0,0),name='selector')
    g.rod((0,-.063,.099),(0,-.164,.069),.009,'steel',name='guard')
    g.rod((0,-.164,.069),(0,-.164,-.078),.009,'steel',name='guard')
    g.rod((0,-.164,-.078),(0,-.074,-.10),.009,'steel',name='guard')
    g.rod((0,-.072,.016),(0,-.132,.029),.008,'black',name='trigger')
    # Sweep the full magazine cross-section along an arc, avoiding stacked-box seams.
    g.curved_magazine()
    g.chamfer((0,.005,-.419),(.148,.121,.334),'walnut',.022,name='lower_handguard')
    g.chamfer((0,.104,-.438),(.108,.071,.272),'walnut_dark',.014,name='upper_handguard')
    for x in (-.073,.073):
        for z in (-.35,-.41,-.47,-.53):
            g.chamfer((x,.021,z),(.009,.021,.041),'walnut_dark',.004,name='wood_relief')
    g.cylinder((0,.039,-.690),.023,.454,'steel',name='barrel')
    g.cylinder((0,.105,-.552),.025,.234,'black',name='gas_tube')
    g.chamfer((0,.075,-.663),(.076,.118,.064),'steel',.009,name='gas_block')
    g.chamfer((0,.093,-.797),(.059,.109,.066),'black',.008,name='front_block')
    for x in (-.025,.025):
        g.chamfer((x,.150,-.803),(.009,.051,.037),'steel',.003,name='iron_sight_wing')
        g.chamfer((x,.163,-.218),(.012,.024,.035),'steel',.003,name='iron_sight_notch')
    g.chamfer((0,.163,-.803),(.009,.028,.016),'steel',.003,name='iron_sight_post')
    g.ring((0,.039,-.914),.032,.016,.070,'steel','muzzle_brake')
    g.save('rifle')

def shotgun():
    g=Gun()
    common_receiver(g,.26,-.24,'receiver',(.205,.20))
    g.chamfer((0,.00,-.42),(.22,.165,.42),'darktan',.032,name='pump_action')
    for z in np.linspace(-.62,-.22,9):
        g.chamfer((0,-.086,z),(.185,.013,.018),'tan',.003,name='pump_rib')
    g.cylinder((0,.065,-.62),.036,.82,'steel',name='upper_barrel')
    g.cylinder((0,-.045,-.58),.029,.68,'black',name='magazine_tube')
    g.chamfer((0,-.04,.55),(.15,.20,.65),'tan',.03,name='solid_stock')
    g.chamfer((0,-.055,.88),(.19,.24,.05),'black',.022,name='rubber_butt')
    g.chamfer((0,.14,-1.01),(.033,.033,.020),'brass',.004,name='bead_sight')
    g.chamfer((0,.015,-.44),(.07,.14,.10),'tan',.016,name='vertical_grip')
    g.chamfer((.114,.01,.04),(.018,.042,.12),'recess',.004,name='shell_gate')
    g.ring((0,.065,-1.04),.041,.026,.065,'steel');g.save('shotgun')

def lmg():
    g=Gun()
    common_receiver(g,.32,-.31,'black',(.265,.23))
    g.chamfer((0,-.03,-.54),(.29,.20,.45),'receiver',.03,name='cooling_shroud')
    for x in [-.153,.153]:
        for z in np.linspace(-.36,-.72,6):
            g.chamfer((x,-.015,z),(.015,.075,.035),'recess',.006,name='heat_port')
    g.cylinder((0,.017,-.89),.042,.48,'steel',name='heavy_barrel')
    hardware(g,-1.13)
    g.cylinder((0,-.27,-.035),.205,.21,'darktan',sections=24,angles=(0,np.pi/2,0),name='drum')
    g.cylinder((.11,-.27,-.035),.12,.009,'black',sections=16,angles=(0,np.pi/2,0),name='drum_hub')
    g.chamfer((0,.00,.52),(.24,.21,.48),'polymer',.035,name='heavy_stock')
    g.chamfer((0,-.015,.79),(.265,.245,.052),'recess',.018,name='butt_pad')
    # Offset the carry handle so it never crosses the optic's viewing axis.
    g.rod((-.128,.14,-.17),(-.174,.275,-.12),.013,'steel',name='carry_handle')
    g.rod((-.174,.275,-.12),(-.174,.275,.12),.013,'steel',name='carry_handle')
    g.rod((-.174,.275,.12),(-.127,.14,.16),.013,'steel',name='carry_handle')
    g.rod((-.08,-.07,-.78),(-.20,-.43,-.83),.016,'black',name='bipod')
    g.rod((.08,-.07,-.78),(.20,-.43,-.83),.016,'black',name='bipod')
    g.chamfer((.146,.035,.18),(.038,.035,.10),'steel',.006,name='charging_handle')
    g.chamfer((0,-.18,-.11),(.28,.18,.18),'darktan',.022,name='ammo_box')
    g.chamfer((0,.09,-.16),(.16,.05,.14),'steel',.008,name='feed_cover')
    optic(g,.12); g.save('lmg')

if __name__=='__main__':
    pistol();smg();rifle();shotgun();lmg()
