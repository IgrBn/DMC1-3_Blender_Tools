from __future__ import annotations
import sys, os
from math import degrees
import string
from io import BufferedReader
from enum import Enum
import imp

# import bpy
import bl_math

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

# Track type flags
TRANSLATION_X = (1 << 8)
TRANSLATION_Y = (1 << 7)
TRANSLATION_Z = (1 << 6)
ROTATION_X = (1 << 5)
ROTATION_Y = (1 << 4)
ROTATION_Z = (1 << 3)
SCALE_X = (1 << 2)
SCALE_Y = (1 << 1)
SCALE_Z = (1 << 0)

class Compression(Enum):
    LINEAR_FLOAT32 = 0
    HERMITE_FLOAT32 = 1
    LINEAR_INT16 = 2
    HERMITE_INT16  = 3


EPSILON_16 = (0.000015259022) # 1./65535.


#=====================================================================
#   Hermite spline interpolation
#=====================================================================
def Hermite(currentFrameTime, valueMin, timeMin, tangent0, valueMax, timeMax, tangent1):
    t = currentFrameTime - timeMin
    timeStep = 1.0 / (timeMax - timeMin)
    time1a = t * t * timeStep
    time0a = t * t * (timeStep * timeStep)
    v9 = time0a * t
    timea = v9

    return (t + timea - time1a - time1a) * tangent0 \
         + (timeStep * v9 + timeStep * v9 - time0a * 3.0 + 1.0) * valueMin \
         + (time0a * 3.0 - (timeStep * v9 + timeStep * v9)) * valueMax \
         + (timea - time1a) * tangent1


#=====================================================================
#   Keyframe
#=====================================================================
class Keyframe:
    def __init__(self, track: Track, f: BufferedReader):
        tmp = ReadUShort(f)
        self.timeIndex = tmp & 0x7fff
        self.uknFlag = tmp >> 15
        self.value = ReadUShort(f) * track.range * EPSILON_16 + track.min

        # if 'rotation_euler' in track.transformType:
        #     self.value = 180. - self.value
        #     self.value = degrees(self.value)

        if track.comprsnType == Compression.HERMITE_INT16:
            self.inTangent = ReadUShort(f) * track.inRange * EPSILON_16 + track.inTMin
            self.outTanget = ReadUShort(f) * track.outRange * EPSILON_16 + track.outTMin


#=====================================================================
#   Track
#=====================================================================
class Track:
    def __init__(self, type: string, trackIdx, f: BufferedReader):
        # print( f"   Reading track at {hex( f.tell() )}" )
        self.size = ReadUShort(f)
        self.keyCount = ReadUShort(f)
        self.comprsnType = Compression( ReadUShort(f) )
        self.startTime = ReadUShort(f)
        self.min = ReadFloat(f)
        self.range = ReadFloat(f)
        self.keys: Keyframe = []
        self.transformType = type
        self.trackIdx = trackIdx

        if self.comprsnType == Compression.HERMITE_INT16:
            self.inTMin = ReadFloat(f)
            self.inRange = ReadFloat(f)
            self.outTMin = ReadFloat(f)
            self.outRange = ReadFloat(f)
    
            self.keys = [ Keyframe(self, f) for i in range(self.keyCount) ]

        elif self.comprsnType != Compression.LINEAR_INT16:
            print( f" Unknown compression type at {hex( f.tell() )}" )
            return

    
    def SampleKeyframe(self, frame_time, p0, p1, t):
        if self.comprsnType == Compression.HERMITE_INT16:
            return Hermite(float(frame_time), p0.value, p0.timeIndex, p0.outTanget, p1.value, p1.timeIndex, p1.inTangent)

        else:
            return bl_math.lerp(p0.value, p1.value, t)


#=====================================================================
#   Track groups per bone
#=====================================================================
class BoneTrackGroup:
    def __init__(self, Mot: Motion, trackTypes, boneIdx, f: BufferedReader):
        self.boneIdx = boneIdx
        self.tracks: Track = []

        data_path_pos = 'pose.bones["bone_%d"].location'
        data_path_rot = 'pose.bones["bone_%d"].rotation_euler'
        data_path_scl = 'pose.bones["bone_%d"].scale'
        
        if trackTypes & TRANSLATION_X:
            self.tracks.append( Track(data_path_pos % boneIdx, trackIdx=0, f=f) )

        if trackTypes & TRANSLATION_Y:
            self.tracks.append( Track(data_path_pos % boneIdx, trackIdx=1, f=f) )
        
        if trackTypes & TRANSLATION_Z:
            self.tracks.append( Track(data_path_pos % boneIdx, trackIdx=2, f=f) )

        if trackTypes & ROTATION_X:
            self.tracks.append( Track(data_path_rot % boneIdx, trackIdx=0, f=f) )

        if trackTypes & ROTATION_Y:
            self.tracks.append( Track(data_path_rot % boneIdx, trackIdx=1, f=f) )

        if trackTypes & ROTATION_Z:
            self.tracks.append( Track(data_path_rot % boneIdx, trackIdx=2, f=f) )

        if trackTypes & SCALE_X:
            self.tracks.append( Track(data_path_scl % boneIdx, trackIdx=0, f=f) )

        if trackTypes & SCALE_Y:
            self.tracks.append( Track(data_path_scl % boneIdx, trackIdx=1, f=f) )

        if trackTypes & SCALE_Z:
            self.tracks.append( Track(data_path_scl % boneIdx, trackIdx=2, f=f) )            


#=====================================================================
#   Motion
#=====================================================================
class Motion:
    def __init__(self, f: BufferedReader):
        self.f = f
        self.size = ReadUInt(f)
        self.Id = ReadInt(f)
        self.startFrame = ReadFloat(f)
        self.endFrame = ReadFloat(f)
        self.startFrame2 = ReadFloat(f)
        self.endFrame2 = ReadFloat(f)
        self.ukn = ReadUShort(f)
        self.ukn1 = ReadUShort(f)
        self.boneCount = ReadUShort(f)
        self.ukn2 = []
        self.trackGroups: BoneTrackGroup = []

        self.trackTypes = [ ReadUShort(f) for i in range(self.boneCount) ]

        while f.tell() < self.size:
            self.ukn2.append( ReadUShort(f) )


    def ParseTracks(self):
        for boneIdx, trackFlags in enumerate(self.trackTypes):
            
            if trackFlags:
                # print(boneIdx)
                self.trackGroups.append( BoneTrackGroup(self, trackFlags, boneIdx, self.f) )


#=====================================================================
#   Import
#=====================================================================
def Import(context, filepath):
    with open(filepath, 'rb') as f:

        print("\nImporting animation...")
        
        Mot = Motion(f)
        f.seek(Mot.size, os.SEEK_SET)
        trackCount = ReadUInt(f)
        Mot.ParseTracks()

        import_setup.setup_animation(context, filepath, Mot)
        
        print("\nDone!\n")


    return {'FINISHED'}
