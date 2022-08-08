import sys, os
import imp
# import bpy

# Path hack.
sys.path.insert( 0, os.path.join(os.path.dirname(__file__), '..') )

import common
from common.io import *
import common.MeshUtils as MeshUtils
import common.import_setup as import_setup
imp.reload(common.io)
imp.reload(MeshUtils)
imp.reload(import_setup)

      
#=====================================================================
#   Mesh
#=====================================================================
class Mesh:
    def __init__(self, f, meshIdx):
        self.meshIdx = meshIdx
        self.f = f
        self.numVerts = ReadShort(f)
        self.texInd = ReadShort(f)
        f.seek(12 ,1)
        self.positionsOffs = ReadInt64(f)
        self.normalsOffs = ReadInt64(f)
        self.UVsOffs = ReadInt64(f)
        
        if Mod.Id != "SCM ":
            self.boneIndiciesOffs = ReadInt64(f)
            self.weightsOffs = ReadInt64(f)
            f.seek(8, 1)
        else:
            f.seek(16, 1)
            self.uknOffs = ReadInt64(f)
        
        self.ukn = ReadInt64(f)
        f.seek(8, 1)
       
        self.positions = []
        self.normals = []
        self.UVs = []
        self.boneIndicies = []
        self.boneWeights = []
        self.triSkip = []
        self.faces = []
        self.vertGrp = [None]*Mod.boneCount

        
    def ParseVerts(self):
        MeshUtils.ParseVerts(self, self.f, Mod)
        
    
#=====================================================================
#   Object
#=====================================================================
class Object:
    def __init__(self, f, objectIdx):
        self.f = f
        self.objectIdx = objectIdx
        self.meshCount = ReadByte(f)
        self.ukn = ReadByte(f)
        self.numVerts = ReadShort(f)
        ReadInt(f)
        self.mshOffs = ReadInt64(f)
        self.flags = ReadInt(f)
        f.seek(28, 1)
        self.X = ReadFloat(f)
        self.Y = ReadFloat(f)
        self.Z = ReadFloat(f)
        self.radius = ReadFloat(f)
        self.meshes = []


    def ParseMeshes(self):
        f = self.f
        f.seek(self.mshOffs)

        for i in range(self.meshCount):
            self.meshes.append( Mesh(f, i) )


    def ParseVerts(self):
        for mesh in self.meshes:
            mesh.ParseVerts()


#=====================================================================
#   Bones
#=====================================================================
class Bone:
    def __init__(self, vec, idx):
        self.transform = vec
        self.idx = idx
        self.parent = None


class Skeleton:
    def __init__(self, f, boneCount):
        base_offset = f.tell()
        self.f = f
        self.boneCount = boneCount
        self.hierarchyOffs = ReadInt(f)
        self.hierarchyOrderOffs = ReadInt(f)
        self.uknOffs = ReadInt(f)
        self.transformsOffs = ReadInt(f)
        self.bones = []

        # Collect bone hierarchy parents
        f.seek(base_offset + self.hierarchyOffs)
        self.hierarchy = []

        for i in range(boneCount):
            self.hierarchy.append( ReadByte(f) )

        # Collect hierarchy indicies
        f.seek(base_offset + self.hierarchyOrderOffs)
        self.hierarchyOrder = []

        for i in range(boneCount):
            self.hierarchyOrder.append( ReadByte(f) )

        # Collect unknown bytes
        f.seek(base_offset + self.uknOffs)
        self.unknown = []

        for i in range(boneCount):
            self.unknown.append( ReadByte(f) )

        # Collect bone transforms
        f.seek(base_offset + self.transformsOffs)

        for i in range(boneCount):
            self.bones.append( Bone( Vector( [ReadFloat(f), ReadFloat(f), ReadFloat(f)] ), i) )
            f.seek(0x14, os.SEEK_CUR)

        # remap the ownership
        self.parents = []

        for i in range(boneCount):
            self.parents.append(-1)

        for i in range(boneCount):
            self.bones[self.hierarchyOrder[i]].parent = self.hierarchy[i]


#=====================================================================
#   Model file
#=====================================================================
class Model:
    def __init__(self, f):
        self.f = f
        self.Id = ReadInt(f)
        self.version = ReadFloat(f)
        self.padding = ReadInt64(f)
        self.objectCount = ReadByte(f)
        self.boneCount = ReadByte(f)
        self.numTex = ReadByte(f)
        self.uknByte = ReadByte(f)
        self.ukn = ReadInt(f)
        self.ukn2 = ReadInt64(f)
        self.skeletonOffs = ReadInt64(f)
        self.objects = []
        self.skeleton = None


    def ParseObjects(self):
        f = self.f
        f.seek(0x40)

        for i in range(self.objectCount):
            self.objects.append( Object(f, i) )


    def ParseMeshes(self):
        for obj in self.objects:
            obj.ParseMeshes()
        

    def ParseVerts(self):
        for obj in self.objects:
            obj.ParseVerts()


    def ParseSkeleton(self):
        self.f.seek(self.skeletonOffs)
        self.skeleton = Skeleton(self.f, self.boneCount)


#=====================================================================
#   Import
#=====================================================================
def Import(context, filepath):
    with open(filepath, 'rb') as f:

        # print("\nImporting model...")
        
        global Mod
        Mod = Model(f)
        Mod.ParseObjects()
        Mod.ParseMeshes()
        Mod.ParseVerts()
        Mod.ParseSkeleton()

        import_setup.setup_model(context, filepath, Mod)
        
        # print("\nDone!\n")


    return {'FINISHED'}

