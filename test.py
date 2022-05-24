import __init__ as libsm64
import ctypes as c
l = libsm64.library()

def debug_print(string):
	print(string)
dp = libsm64._SM64DebugPrintFunctionPtr(debug_print)

with open('baserom.us.z64','rb') as rom:
	texture_bytes = b'\00' * (4 * l.SM64_TEXTURE_WIDTH * l.SM64_TEXTURE_HEIGHT)
	rom_data = rom.read()
	l.sm64_global_init(rom_data,texture_bytes,dp)
	del rom_data
	surface = libsm64.sm64_surface()
	surface.vertices[0][1] = 12
	print(surface._as_parameter_)
