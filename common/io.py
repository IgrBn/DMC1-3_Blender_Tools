from mathutils import *
from struct import *

""" ----Write---- """
def WriteString(f, s):
    f.write(bytes(s, 'UTF-8'))

# byte
def WriteUByte(f, v):  #unsigned    
    f.write(pack('<B',int(v)))

def WriteByte(f, v):  #signed    
    f.write(pack('<b',int(v)))

# short
def WriteUShort(f, v):  #unsigned    
    f.write(pack('<H', int(v)))

def WriteShort(f, v):  #signed
    f.write(pack('<h', int(v)))

# int
def WriteUInt(f,v):  #unsigned    
    f.write(pack('<L', v))

def WriteInt(f,v):  #signed    
    f.write(pack('<l', v))

# int64
def WriteUInt64(f, v):  #unsigned    
    f.write(pack('<Q', v))

def WriteInt64(f, v):  #signed
    f.write(pack('<q', v))

# float
def WriteFloat(f, v):
    f.write(pack('<f', v))
    

""" ----Read---- """
# byte
def ReadUByte(f):  #unsigned    
    return unpack('<B', f.read(1))[0]

def ReadByte(f):  #signed
    return unpack('<b', f.read(1))[0]

# short
def ReadUShort(bstream): #unsigned    
	return unpack('<H', bstream.read(2))[0]

def ReadShort(bstream): #signed
	return unpack( '<h', bstream.read(2) )[0]

# int
def ReadUInt(bstream):  #unsigned
	return unpack('<L', bstream.read(4))[0]
    
def ReadInt(bstream):  #signed
	return unpack('<l', bstream.read(4))[0]

# int64
def ReadUInt64(bstream):  #unsigned
	return unpack('<Q', bstream.read(8))[0]

def ReadInt64(bstream):  #signed
	return unpack('<q', bstream.read(8))[0]
	    
# float
def ReadFloat(bstream): 
	return unpack('<f', bstream.read(4))[0]

def ReadMatrix(bstream):
    Mat = mathutils.Matrix()
    Mat[0] = ( (ReadFloat(bstream)), (ReadFloat(bstream)), (ReadFloat(bstream)), (ReadFloat(bstream)) )
    Mat[1] = ( (ReadFloat(bstream)), (ReadFloat(bstream)), (ReadFloat(bstream)), (ReadFloat(bstream)) )
    Mat[2] = ( (ReadFloat(bstream)), (ReadFloat(bstream)), (ReadFloat(bstream)), (ReadFloat(bstream)) )
    #print (Mat[0],Mat[1],Mat[2])
    tYZ = [-ReadFloat (bstream), -ReadFloat (bstream), ReadFloat (bstream)]	 
    Mat[3] = ( tYZ[0],tYZ[1],tYZ[2], (ReadFloat (bstream)) )
    return Mat
    
def ReadMatrixB(bstream):
    Mat = mathutils.Matrix()
    Mat[0] = ((ReadFloat (bstream)),(ReadFloat (bstream)),(ReadFloat (bstream)),(ReadFloat (bstream)))
    Mat[1] = ((ReadFloat (bstream)),(ReadFloat (bstream)),(ReadFloat (bstream)),(ReadFloat (bstream)))
    Mat[2] = ((ReadFloat (bstream)),(ReadFloat (bstream)),(ReadFloat (bstream)),(ReadFloat (bstream)))
    #print (Mat[0],Mat[1],Mat[2])
    #tYZ = [-ReadFloat (bstream),-ReadFloat (bstream),ReadFloat (bstream)]	 
    #Mat[3] = (tYZ[0],tYZ[1],tYZ[2], (ReadFloat (bstream)))
    return Mat