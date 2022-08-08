from io import BufferedReader
from mathutils import *
from struct import *

#=====================================================================
#   Write
#=====================================================================
def WriteString(f, s):
    f.write(bytes (s, 'UTF-8') )

# byte
def WriteUByte(f, v):      
    f.write( pack('<B', int(v) ) )

def WriteByte(f, v):  #signed    
    f.write(pack ('<b', int(v) ) )

# short
def WriteUShort(f, v):      
    f.write(pack( '<H', int(v) ) )

def WriteShort(f, v):  #signed
    f.write(pack( '<h', int(v) ) )

# int
def WriteUInt(f, v):      
    f.write(pack( '<L', v) )

def WriteInt(f, v):  #signed    
    f.write(pack( '<l', v) )

# int64
def WriteUInt64(f, v):      
    f.write(pack( '<Q', v) )

def WriteInt64(f, v):  #signed
    f.write(pack( '<q', v) )

# float
def WriteFloat(f, v):
    f.write(pack( '<f', v) )
    

#=====================================================================
#   Read
#=====================================================================
# byte
def ReadUByte(f):   
    return unpack('<B', f.read(1) )[0]

def ReadByte(f):  #signed
    return unpack( '<b', f.read(1) )[0]

# short
def ReadUShort(f): 
	return unpack( '<H', f.read(2) )[0]

def ReadShort(f): #signed
	return unpack( '<h', f.read(2) )[0]

# int
def ReadUInt(f):  
	return unpack( '<L', f.read(4) )[0]
    
def ReadInt(f):  #signed
	return unpack( '<l', f.read(4) )[0]

# int64
def ReadUInt64(f):  
	return unpack( '<Q', f.read(8) )[0]

def ReadInt64(f):  #signed
	return unpack( '<q', f.read(8) )[0]
	    
# float
def ReadFloat(f): 
	return unpack( '<f', f.read(4) )[0]

def ReadMatrix(f: BufferedReader):
    Mat = mathutils.Matrix()
    Mat[0] = ( ReadFloat(f), ReadFloat(f), ReadFloat(f), ReadFloat(f) )
    Mat[1] = ( ReadFloat(f), ReadFloat(f), ReadFloat(f), ReadFloat(f) )
    Mat[2] = ( ReadFloat(f), ReadFloat(f), ReadFloat(f), ReadFloat(f) )
    tYZ = [-ReadFloat(f), -ReadFloat(f), ReadFloat(f)]
    Mat[3] = ( tYZ[0], tYZ[1], tYZ[2], ReadFloat (f) )

    return Mat