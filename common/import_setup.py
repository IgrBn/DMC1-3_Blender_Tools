# from gettext import translation
import bpy
import os
import imp
import common
from common.io import *
imp.reload(common.io)


#=====================================================================
#   Setup parsed models
#=====================================================================
def setup_model(context, filepath, Mod):
    mat = Matrix([ [.01, 0.0, 0.0, 0.0], 
                   [0.0, 0.0, -.01, 0.], 
                   [0.0, .01, 0.0, 0.0], 
                   [0.0, 0.0, 0.0, 0.0] ])

    # mat = Matrix([ [1.0, 0.0, 0.0, 0.0], 
    #                [0.0, 0.0, -1., 0.0], 
    #                [0.0, 1.0, 0.0, 0.0], 
    #                [0.0, 0.0, 0.0, 0.0] ])


    # Setup collection
    fileName = os.path.basename(filepath)
    model_collection = bpy.data.collections.new(fileName)
    context.scene.collection.children.link(model_collection)


    # Setup armature
    armature = bpy.data.armatures.new("Armature")
    armature_object = bpy.data.objects.new("Armature_object", armature)
    # armature.show_names = True
    armature.show_axes = True
    armature.display_type = "STICK"

    model_collection.objects.link(armature_object)
    context.view_layer.objects.active = armature_object
    armature_object.select_set(True)

    bpy.ops.object.mode_set(mode='EDIT')

    # Setup bones
    bones = Mod.skeleton.bones

    for bone in bones:
        joint = armature.edit_bones.new(f"bone_{bone.idx}")
        joint.head = bone.transform
        joint.use_relative_parent = True

        if bone.parent != -1:
            joint.parent = armature.edit_bones[bone.parent]
            joint.tail = joint.parent.head
    
        joint.head += joint.tail 


    armature.transform(mat)

    # hack to get around blender not allowing 0-length bones
    for bone in armature.edit_bones:
        if bone.length <= 0.00005:
            bone.head += Vector( [.000001, .000001, .000001] )
            # print(f"\n  {bone.name}, {bone.length}")


    # Setup objects
    for i, obj in enumerate(Mod.objects):

        objName = f"Object_{i}"
        object = bpy.data.objects.new(objName, None)
        model_collection.objects.link(object)


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


            # rotate the object upright
            mesh_object.data.transform(mat)

            # Link the armature to the object
            bpy.ops.object.mode_set(mode='OBJECT')

            # object.parent = armature_object
            modifier = mesh_object.modifiers.new(type='ARMATURE', name="Armature")
            modifier.object = armature_object


#=====================================================================
#   Setup parsed animations
#=====================================================================
def clear_animations():
    for i in range(len(bpy.data.actions)):
        bpy.data.actions[0].user_clear()
        bpy.data.actions.remove(bpy.data.actions[0])


def setup_animation(context, filepath, Mot):
    clear_animations()

    scene = bpy.data.scenes["Scene"]
    scene.render.fps = 60.
    scene.frame_start = Mot.startFrame
    scene.frame_end = Mot.endFrame

    rig = bpy.context.scene.objects["Armature_object"]

    for bone in rig.pose.bones:
        # print(bone.name)
        bone.rotation_mode = "XYZ"


    fileName = os.path.basename(filepath)
    action = bpy.data.actions.new(fileName)

    for trackGroup in Mot.trackGroups:
        print(trackGroup.boneIdx)

        for track in trackGroup.tracks:
            fcurve = action.fcurves.new(data_path = track.transformType, index=track.trackIdx)

            [ fcurve.keyframe_points.insert(key.timeIndex, key.value) for key in track.keys]


    ad = rig.animation_data_create()
    ad.action = action
        
