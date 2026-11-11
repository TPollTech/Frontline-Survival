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
    g.chamfer((0,.055,-.12),(.16,.105,.34),'receiver',.018,name='slide')
    g.chamfer((0,.035,-.13),(.145,.050,.32),'black',.007,name='frame')
    g.chamfer((0,-.12,.015),(.107,.26,.13),'polymer',.025,angles=(-.19,0,0),name='grip')
    g.chamfer((0,-.20,.035),(.11,.018,.13),'black',.006,name='grip_base')
    g.chamfer((0,-.205,.024),(.079,.18,.091),'black',.005,name='pistol_magazine')
    g.chamfer((0,-.315,.024),(.098,.017,.11),'steel',.005,name='magazine_heel')
    g.chamfer((0,.115,-.28),(.042,.035,.040),'recess',.006,name='front_sight')
    g.chamfer((0,.115,.02),(.10,.035,.034),'recess',.006,name='rear_sight')
    g.chamfer((.083,.080,-.105),(.006,.031,.09),'recess',.002,name='ejection')
    for j in range(5): g.chamfer((.082,.064,.005-j*.017),(.007,.052,.008),'black',.002,name='slide_groove')
    g.rod((-.065,-.06,-.08),(-.065,-.145,-.08),.009,'steel',name='trigger_guard')
    g.rod((-.065,-.145,-.08),(.065,-.145,-.08),.009,'steel',name='trigger_guard')
    g.rod((.015,-.07,-.10),(.025,-.115,-.08),.008,'steel',name='trigger')
    hardware(g,-.308); g.save('pistol')

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
    g.chamfer((0,.210,z-.048),(.008,.034,.010),'brass',.003,name='aiming_post')
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
    optic(g,-.07); hardware(g,-.69); g.save('smg')

def rifle():
    g=Gun()
    common_receiver(g,.26,-.25,'receiver',(.205,.17))
    g.chamfer((0,0,-.45),(.215,.155,.49),'tan',.032,name='m_lok_handguard')
    for x in [-.109,.109]:
        for z in [-.32,-.39,-.46,-.53,-.60]:
            g.chamfer((x,.025,z),(.009,.032,.043),'recess',.004,name='handguard_slot')
    g.chamfer((0,-.19,.00),(.10,.32,.11),'polymer',.02,angles=(-.15,0,0),name='magazine')
    g.chamfer((0,-.34,-.015),(.115,.055,.115),'recess',.012,name='magazine_heel')
    g.chamfer((0,.013,.41),(.105,.10,.31),'black',.015,name='buffer_tube')
    g.chamfer((0,-.015,.62),(.20,.22,.31),'polymer',.032,name='adjustable_stock')
    g.chamfer((0,-.015,.79),(.21,.24,.06),'recess',.02,name='rubber_pad')
    for x in [-.073,.073]:
        g.rod((x,.08,.48),(x,-.08,.72),.011,'steel',name='stock_brace')
    g.cylinder((0,.018,-.79),.027,.29,'steel',name='barrel')
    g.chamfer((.115,.045,.10),(.028,.031,.067),'steel',.005,name='charging_handle')
    optic(g,.08); hardware(g,-.95); g.save('rifle')

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
    g.rod((-.11,.16,-.13),(-.10,.31,.07),.014,'steel',name='carry_handle')
    g.rod((-.10,.31,.07),(.10,.31,.07),.014,'steel',name='carry_handle')
    g.rod((.10,.31,.07),(.11,.16,-.13),.014,'steel',name='carry_handle')
    g.rod((-.08,-.07,-.78),(-.20,-.43,-.83),.016,'black',name='bipod')
    g.rod((.08,-.07,-.78),(.20,-.43,-.83),.016,'black',name='bipod')
    g.chamfer((.146,.035,.18),(.038,.035,.10),'steel',.006,name='charging_handle')
    optic(g,.12); g.save('lmg')

if __name__=='__main__':
    pistol();smg();rifle();shotgun();lmg()
