from ctypes import *

#region Structs
class _SM64Surface(Structure):
		_fields_ = (
		    ('type', c_int16),
	   		('force', c_int16),
		    ('terrain', c_uint16),
		    ('vertices', c_int16*3*3)
		)
class _SM64MarioInputs(Structure):
	_fields_ = (
	    ('camLookX',c_float),('camLookZ',c_float),
		('stickX',c_float),('stickY',c_float),
	    ('buttonA',c_uint8),('buttonB',c_uint8),('buttonZ',c_uint8)
	)
class _SM64ObjectTransform(Structure):
	_fields_ = (
		('position',c_float*3),
		('eulerRotation',c_float*3)
	)
class _SM64SurfaceObject(Structure):
		_fields_ = (
		    ('transform',_SM64ObjectTransform),
	    	('surfaceCount',c_uint32),
	    	('surfaces',POINTER(_SM64Surface))
		)
class _SM64MarioState(Structure):
	_fields_ = (
	    ('position',c_float*3),
		('velocity',c_float*3),
		('faceAngle',c_float),
		('health',c_int16),
	)
class _SM64MarioGeometryBuffers(Structure):
	_fields_ = (
    	('position',POINTER(c_float)),
    	('normal',POINTER(c_float)),
    	('color',POINTER(c_float)),
    	('uv',POINTER(c_float)),
    	('numTrianglesUsed',c_uint16)
	)
#endregion
#region typedefs pointer
_SM64DebugPrintFunctionPtr = CFUNCTYPE(None,c_char_p)
_SM64DebugPrintFunctionPtr.old_param = _SM64DebugPrintFunctionPtr.from_param
def from_param(cls, obj):
    if obj is None:
        return None
    return cls.old_param(obj)
_SM64DebugPrintFunctionPtr.from_param = classmethod(from_param)
#endregion
#region enum
_SM64_TEXTURE_WIDTH = 704
_SM64_TEXTURE_HEIGHT = 64
_SM64_GEO_MAX_TRIANGLES = 1024
#endregion
#region library/python classes

class sm64_surface:
	def __init__( self, type=0,force=0,terrain=0,vertices=[[10,0,0],[10,0,0],[0,0,10]]):
		self.type = type
		self.force = force
		self.terrain = terrain
		self.vertices = vertices
	def __getattr__(self,name:str):
		if name == '_as_parameter_':
			param = _SM64Surface()
			param.type = self.type
			param.force = self.force
			param.terrain = self.terrain
			param.vertices = (c_int16*3*3)()
			sv = self.vertices
			for i in range(3):
				param.vertices[i][:] =sv[i]
			del sv
			return param
		else: return self.__dict__[name]

class sm64_mario_inputs():
	def __init__( self,axisX:float=0,axisY:float=0,camX:float=0,camY:float=0,A:bool=False,B:bool=True,Z:bool=True):
		self.axisX=axisX
		self.axisY=axisY
		self.camX=camX
		self.camY=camY
		self.A=A
		self.B=B
		self.Z=Z
	def __getattr__(self,name:str):
		if name == '_as_parameter_':
			param = _SM64MarioInputs()
			param.camLookX=self.camX
			param.camLookZ=self.camY
			param.stickX=self.axisX
			param.stickY=self.axisY
			param.buttonA=c_uint8(self.A)
			param.buttonB=c_uint8(self.B)
			param.buttonZ=c_uint8(self.Z)
			return param
		else: return self.__dict__[name]

class library:
	def __init__(self,libsm64_path:str = './libsm64.so'):
		sharedLibrary = CDLL(libsm64_path)
		#region cdll io setup
		
		#lifecycle
		sharedLibrary.sm64_global_init.argtypes = [ c_char_p, c_char_p, _SM64DebugPrintFunctionPtr ]
		sharedLibrary.sm64_global_init.restype = ( None )
		sharedLibrary.sm64_global_terminate.argtypes = ( None )
		sharedLibrary.sm64_global_terminate.restype = ( None )

		#objects
		sharedLibrary.sm64_static_surfaces_load.argtypes = [ POINTER(_SM64Surface),c_uint32 ]
		sharedLibrary.sm64_static_surfaces_load.restype = ( None )

		#mario
		sharedLibrary.sm64_mario_create.argtypes = [ c_int16, c_int16, c_int16 ]
		sharedLibrary.sm64_mario_create.restype = ( c_int32 )
		sharedLibrary.sm64_mario_tick.argtypes = [ c_int32, POINTER(_SM64MarioInputs), POINTER(_SM64MarioState), POINTER(_SM64MarioGeometryBuffers) ]
		sharedLibrary.sm64_mario_tick.restype = ( None )
		sharedLibrary.sm64_mario_delete.argtypes = [ c_int32 ]
		sharedLibrary.sm64_mario_delete.restype = ( None )

		#surfaces
		sharedLibrary.sm64_surface_object_create.argtypes = [ POINTER(_SM64SurfaceObject) ]
		sharedLibrary.sm64_surface_object_create.restype = ( c_uint32 )
		sharedLibrary.sm64_surface_object_move.argtypes = [ c_uint32, POINTER(_SM64ObjectTransform) ]
		sharedLibrary.sm64_surface_object_move.restype = ( None )
		sharedLibrary.sm64_surface_object_delete.argtypes = [ c_uint32 ]
		sharedLibrary.sm64_surface_object_delete.restype = ( None )

		#endregion
		self.CDLL = sharedLibrary
	#region classes
	class SM64Surface(_SM64Surface): pass
	class SM64MarioInputs(_SM64MarioInputs): pass
	class SM64ObjectTransform(_SM64ObjectTransform): pass
	class SM64SurfaceObject(_SM64SurfaceObject): pass
	class SM64MarioState(_SM64MarioState): pass
	class SM64MarioGeometryBuffers(_SM64MarioGeometryBuffers):pass
	#endregion
	#region enums
	SM64DebugPrintFunctionPtr=_SM64DebugPrintFunctionPtr
	SM64_TEXTURE_WIDTH = _SM64_TEXTURE_WIDTH
	SM64_TEXTURE_HEIGHT = _SM64_TEXTURE_HEIGHT
	SM64_GEO_MAX_TRIANGLES = _SM64_GEO_MAX_TRIANGLES
	#endregion
	#region python definitions
	def sm64_global_init( self, rom:bytes, texture_bytes:bytes, debugPrintFunction: _SM64DebugPrintFunctionPtr|None = None ):
		tbc = c_char_p(texture_bytes)
		self.CDLL.sm64_global_init(c_char_p(rom),texture_bytes,debugPrintFunction)
		texture_bytes = tbc.value
	def sm64_global_terminate( self ):
		self.CDLL.sm64_global_terminate()
	def sm64_static_surfaces_load( self, surfaceArray:list[sm64_surface] ):
		surfaceArrayTMP = (_SM64Surface * len(surfaceArray))()
		cout = 0
		for surface in surfaceArray:
			surfaceArrayTMP[cout] = surface._as_parameter_
			cout += 1
		surfaceArrayPointer = surfaceArrayTMP
		self.CDLL.sm64_static_surfaces_load(surfaceArrayPointer,c_uint32(len(surfaceArray)))
	def sm64_mario_create( self, x:int, y:int, z:int)->int:
		return self.CDLL.sm64_mario_create(x,y,z)
	def sm64_mario_tick(self,mario_id:int,inputs:sm64_mario_inputs,state:_SM64MarioState,geobuf:_SM64MarioGeometryBuffers):
		self.CDLL.sm64_mario_tick(mario_id,byref(inputs._as_parameter_),byref(state),byref(geobuf))


	#endregion
	class util:
		def generateBlankMarioGeoBuffers()->_SM64MarioGeometryBuffers:
			geobuf = _SM64MarioGeometryBuffers()
			geobuf.position = (c_float*(9*_SM64_GEO_MAX_TRIANGLES))()
			geobuf.color = (c_float * (9 * _SM64_GEO_MAX_TRIANGLES))()
			geobuf.normal = (c_float * (9 * _SM64_GEO_MAX_TRIANGLES))()
			geobuf.uv = (c_float * (6 * _SM64_GEO_MAX_TRIANGLES))()
			return geobuf


#endregion