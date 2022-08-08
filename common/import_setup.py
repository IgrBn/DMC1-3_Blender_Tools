from random import sample
import sys
import bpy
import os
import imp
import mathutils

# Path hack.
sys.path.insert( 0, os.path.join(os.path.dirname(__file__), '..') )

import common
from common.io import *
imp.reload(common.io)


#=====================================================================

# mat = Matrix([ [.01, 0.0, 0.0, 0.0], 
#                [0.0, 0.0, -.01, 0.], 
#                [0.0, .01, 0.0, 0.0], 
#                [0.0, 0.0, 0.0, 0.0] ])

mat = Matrix([ [1.0, 0.0, 0.0, 0.0], 
               [0.0, 0.0, -1., 0.0], 
               [0.0, 1.0, 0.0, 0.0], 
               [0.0, 0.0, 0.0, 0.0] ])

matId = Matrix([ [1.0, 0.0, 0.0, 0.0], 
               [0.0, 1.0, 0.0, 0.0], 
               [0.0, 0.0, 1.0, 0.0], 
               [0.0, 0.0, 0.0, 0.0] ])


#=====================================================================
#   Setup parsed models
#=====================================================================
def setup_model(context, filepath, Mod):

    # Setup collection
    fileName = os.path.basename(filepath)
    model_collection = bpy.data.collections.new(fileName)
    context.scene.collection.children.link(model_collection)

    # create an empty to parent the model to
    empty = bpy.data.objects.new(fileName, None)

    model_collection.objects.link(empty)

    empty.empty_display_size = 2
    empty.empty_display_type = 'SPHERE' 


    # Setup armature
    armature = bpy.data.armatures.new("Armature")
    armature_object = bpy.data.objects.new("Armature_object", armature)
    armature.show_axes = True
    armature.display_type = 'OCTAHEDRAL'
    # armature.show_names = True

    model_collection.objects.link(armature_object)
    context.view_layer.objects.active = armature_object
    armature_object.parent = empty
    armature_object.select_set(True)

    bpy.ops.object.mode_set(mode='EDIT')


    # Setup bones
    joints = Mod.skeleton.bones

    for joint in joints:
        bone = armature.edit_bones.new(f"bone_{joint.idx}")
        bone.head = joint.transform
        bone.use_relative_parent = True

        if joint.parent != -1:
            bone.parent = armature.edit_bones[joint.parent]
            bone.head += bone.parent.head
    



    # calculate bone tails
    for bone in armature.edit_bones:
        children = bone.children
        
        if children:
            childrenPosAverage = Vector([.0, .0, .0])

            for c in children:
                childrenPosAverage += c.head

            childrenPosAverage /= len(children)

            bone.tail = childrenPosAverage.lerp(bone.head, .5 if len(children) > 1 else 0. )
            
        else:
            bone.tail = bone.head + (bone.head - bone.parent.head) * .5


    # Create view for manual alignment along baseline.
    bpy.ops.transform.create_orientation(name="BASELINE", overwrite=True)
    ### Set baseline
    slot = context.scene.transform_orientation_slots[0]
    # Save current orientation setting
    last_slot = slot.type
    # Set new orientation (custom_orientation isn't available until we set the type to a custom orientation)
    slot.type = 'BASELINE'
    slot.custom_orientation.matrix = mat.to_3x3()
    # Set orientation back to what it was
    # slot.type = last_slot


    # hack to get around blender not allowing 0-length bones
    # for bone in armature_object.pose.bones:
    #     bone.matrix_basis = mat

    for bone in armature.edit_bones:
        # print(f"{bone.name}\n{bone.matrix}\n\n")
        # bone.transform(mat)
        bone.tail = bone.head + Vector([.0, 1.0, .0])

        if bone.length <= 0.00005:
            bone.tail += Vector([.000001, .0, .0])
            # print(f"\n  {bone.name}, {bone.length}")

    # armature.transform(mat)

    #=====================================================================
    # Setup objects 
    #=====================================================================
    for i, obj in enumerate(Mod.objects):

        objName = f"Object_{i}"
        object = bpy.data.objects.new(objName, None)
        model_collection.objects.link(object)
        object.parent = empty


        for j, msh in enumerate(obj.meshes):
            name = f"Object_{i}.Mesh_{j}"

            mesh_data = bpy.data.meshes.new(name)
            mesh_data.from_pydata(msh.positions, [], msh.faces)

            mesh_object = ( bpy.data.objects.new(name, mesh_data) )            

            mesh_object.parent = object
            model_collection.objects.link(mesh_object)

            # Apply normals
            custom_normals = []
            
            for face in mesh_data.polygons:
                
                for vert_index in face.vertices:
                    custom_normals.append(msh.normals[vert_index])

                face.use_smooth = True

            mesh_data.use_auto_smooth = True
            mesh_data.normals_split_custom_set(custom_normals)


            # Apply uvs
            if len(msh.UVs) != 0:
                mesh_data.uv_layers.new(name='UV_0') # 2.8 change
                uv_data = mesh_data.uv_layers[0].data
                
                for u in range( len(uv_data) ):
                    uv_data[u].uv = msh.UVs[mesh_data.loops[u].vertex_index]

                mesh_data.calc_tangents(uvmap = "UV_0")


            # Create vertex groups 
            for b in range(Mod.skeleton.boneCount):
                mesh_object.vertex_groups.new(name = f"bone_{b}")


            # Assign vertices to vertex groups
            for vert in mesh_data.vertices:
                v = vert.index
                bone_indices = msh.boneIndicies[v]
                weights = msh.boneWeights[v]

                for idx, b in enumerate(bone_indices):
                    vgroup = mesh_object.vertex_groups[ b[0] ]
                    vgroup.add([v], weights[idx], "REPLACE")


            # Link the armature to the object
            bpy.ops.object.mode_set(mode='OBJECT')

            # object.parent = armature_object
            modifier = mesh_object.modifiers.new(type='ARMATURE', name="Armature")
            modifier.object = armature_object


    # rotate the model upright
    empty.rotation_euler = mathutils.Matrix.to_euler(mat, 'XYZ')

    # print("\nPOSE MATS:\n")
    # for bone in armature_object.pose.bones:
    #     print(f"{bone.name}\n{bone.matrix}\n\n")
    #     print(f"Basis {bone.name}\n{bone.matrix_basis}\n\n")


#=====================================================================
#   Setup parsed animations
#=====================================================================
def clear_animations():
    for action in bpy.data.actions:
        action.user_clear()
        bpy.data.actions.remove(action)


def setup_animation(context, filepath, Mot):
    clear_animations()

    scene = bpy.data.scenes["Scene"]
    scene.render.fps = 60

    if len(bpy.data.actions) > 0:
        if scene.frame_start > Mot.startFrame:
            scene.frame_start = int(Mot.startFrame)
        
        if scene.frame_end < Mot.endFrame:
            scene.frame_end = int(Mot.endFrame)

    else:
        scene.frame_start = int(Mot.startFrame)
        scene.frame_end = int(Mot.endFrame)

    if context.object.type == 'scene.objects.active':
        rig = context.object
    else:
        rig = context.scene.objects["Armature_object"]

    for bone in rig.pose.bones:
        # print(bone.name)
        bone.rotation_mode = "XYZ"


    fileName = os.path.basename(filepath)
    action = bpy.data.actions.new(fileName)

    for trackGroup in Mot.trackGroups:
        # print(trackGroup.boneIdx)

        for track in trackGroup.tracks:
            fcurve = action.fcurves.new(data_path=track.transformType, index=track.trackIdx)
            keys = track.keys
            
            for i in range(1, len(keys)):
                frame_time_range = (keys[i].timeIndex - keys[i-1].timeIndex)

                for frame_time in range(keys[i-1].timeIndex, keys[i].timeIndex):
                    t = (float(frame_time) - keys[i-1].timeIndex) / frame_time_range
                    
                    sample_value = track.SampleKeyframe(frame_time, keys[i-1], keys[i], t)
                    
                    fcurve.keyframe_points.insert(frame_time, sample_value)


    ad = rig.animation_data_create()
    ad.action = action
    
    
    for window in context.window_manager.windows:
        screen = window.screen

        for area in screen.areas:
            if area.type == 'DOPESHEET_EDITOR':

                for region in area.regions:
                    if region.type == 'WINDOW':
                        with context.temp_override(window=window, area=area, region=region):
                            bpy.ops.action.view_all()
                        
                        return
        