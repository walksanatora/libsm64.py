import __init__ as libsm64
import ctypes as c
l = libsm64.library()

def debug_print(string):
	print(string)
dp = libsm64._SM64DebugPrintFunctionPtr(debug_print)

with open('baserom.us.z64','rb') as rom:
	string_buf_size = 4 * l.SM64_TEXTURE_WIDTH * l.SM64_TEXTURE_HEIGHT
	tex = c.create_string_buffer(string_buf_size)
	rom_data = c.c_char_p(rom.read())
	l.sm64_global_init(rom_data,tex,dp)
	del rom_data,string_buf_size
