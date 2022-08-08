import sys, os
import imp

from mathutils import *

# Path hack.
sys.path.insert( 0, os.path.join(os.path.dirname(__file__), '..') )

import common
from common.io import *
imp.reload(common.io)

#=====================================================================
#   Generate faces from triangle strips
#=====================================================================
def GetTris(verts, nrmls, triSkip, numVerts):
    tris = []
    p1 = 0
    p2 = 1
    wnd = 1

    for i in range(2, numVerts):
        p3 = i

        if not triSkip[i]:
            # compute the triangle's facing direction
            vert1 = Vector( verts[p1] )
            vert2 = Vector( verts[p2] )
            vert3 = Vector( verts[p3] )

            # get edges for the basis
            faceEdge1 = vert3 - vert1
            faceEdge2 = vert2 - vert1
            faceEdge1.normalize()
            faceEdge2.normalize()

            # calculate the face normal
            z = faceEdge1.cross(faceEdge2)
            z.normalize()
            
            # add imported vertex normals together to get the face normal
            normal1 = Vector( nrmls[p1] )
            normal2 = Vector( nrmls[p2] )
            normal3 = Vector( nrmls[p3] )
            
            normal = Vector( normal1 + normal2 + normal3 )
            normal.normalize()

            # check whether the triangle is facing in the imported normals direction and flip it otherwise
            wnd = 1 if normal.dot(z) > 0.0 else -1

            tris.append( [p1, p3, p2] if wnd == 1 else [p1, p2, p3] )


        p1 = p2
        p2 = p3
    

    return tris


#=====================================================================
#   Vertex desirealization
#=====================================================================
def ParseVerts(self, f, modelHdr):
    #POSITIONS
    f.seek(self.positionsOffs)
    self.positions = [ Vector([ReadFloat(f), ReadFloat(f), ReadFloat(f)]) for i in range(self.numVerts) ]
 
 
    #NORMALS
    f.seek(self.normalsOffs)
    self.normals = [ Vector([ReadFloat(f), ReadFloat(f), ReadFloat(f)]) for i in range(self.numVerts) ]
    

    #TEXTURE COORDINATES
    f.seek(self.UVsOffs)
    self.UVs = [ ([ReadShort(f)/4096., (1. - ReadShort(f)/4096.)]) for i in range(self.numVerts)]


    #BONE INDICES
    if modelHdr.Id != "SCM ":
        f.seek(self.boneIndiciesOffs)

        for i in range(self.numVerts):
            ReadByte(f)
            self.boneIndicies.append( [ [ReadByte(f)//4], [ReadByte(f)//4], [ReadByte(f)//4] ] )


        #BONE WEIGHTS
        f.seek(self.weightsOffs)

        for i in range(self.numVerts):
            w = ReadShort(f)

            w1 = (w & 0x1f) / 31.
            w2 = ( (w >> 5) & 0x1f) / 31.
            w3 = ( (w >> 10) & 0x1f) / 31.

            self.triSkip.append( (w >> 15) & 1 )
            self.boneWeights.append( [w1, w2, w3] )

        # FACES
        self.faces = GetTris(self.positions, self.normals, self.triSkip, self.numVerts)

    else:
        f.seek(self.uknOffs)

        for i in range(self.numVerts):
            f.seek(3, 1)
            self.triSkip.append(ReadByte(f) / 2)

        # FACES
        self.faces = GetTris(self.positions, self.normals, self.triSkip, self.numVerts)