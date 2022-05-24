import __init__ as libsm64
from ursina import *
l = libsm64.library()

def createSurface(points:list[list[int]],color=color.red) -> tuple[Entity,libsm64.sm64_surface]:
	return Entity(model=Mesh([Vec3(*points[0]),Vec3(*points[1]),Vec3(*points[2])],colors=[color]*3,mode='tristrip'),double_sided=True),libsm64.sm64_surface(vertices=points)

app = Ursina()
_cam = EditorCamera()

def debug_print(string):
	print(string)
dp = libsm64._SM64DebugPrintFunctionPtr(debug_print)

with open('baserom.us.z64','rb') as rom:
	texture_bytes = b'\00' * (4 * l.SM64_TEXTURE_WIDTH * l.SM64_TEXTURE_HEIGHT)
	rom_data = rom.read()
	l.sm64_global_init(rom_data,texture_bytes,dp)
	del rom_data

tile,tile_sm64  = createSurface([
		[10,0,10],
		[0,0,10],
		[0,0,0]
	],color=color.pink)
tile2,tile2_sm64 = createSurface([
		[10,0,10],
		[10,0,0],
		[0,0,0]
	],color=color.blue)
mario_cube = Entity(model='cube',color=color.red)
print('loading surfaces')
l.sm64_static_surfaces_load([tile_sm64,tile2_sm64])
print('spawning mario')
mario = l.sm64_mario_create(0,10,0)
print('mario id:',mario)
print('preparing classes')
mario_geobuf = l.util.generateBlankMarioGeoBuffers()
mario_state = l.SM64MarioState()
mario_input = libsm64.sm64_mario_inputs()



def update():
	l.sm64_mario_tick(mario,mario_input,mario_state,mario_geobuf)
	mario_cube.x = mario_state.position[0]
	mario_cube.y = mario_state.position[1]
	mario_cube.z = mario_state.position[2]
app.run()