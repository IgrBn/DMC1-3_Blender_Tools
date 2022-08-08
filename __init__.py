bl_info = {
	"name": "DMC 1-3 tools",
	"author": "",
	"blender": (3, 0, 0),
	"location": "File > Import-Export",
	"description": "Import DMC 1, 2, 3 models and animations.",
	"warning": "",
	"category": "Import-Export",
}

import os
from os import remove
import sys
import imp
import typing
import bpy
# ImportHelper is a helper class, defines filename and invoke() function which calls the file selector.
from bpy.types import Operator, Panel

from bpy.props import (
    # BoolProperty,
    # CollectionProperty,
    # StringProperty,
    EnumProperty
)

sys.path.insert( 0, os.path.abspath( os.path.dirname(__file__) ) )

# My imports
import DMC3.operators
import DMC3.model
import DMC3.motion
imp.reload(DMC3.operators)
imp.reload(DMC3.model)
imp.reload(DMC3.motion)


#=====================================================================
#   SIDE PANEL UI
#=====================================================================
class DMC_panel_base():
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'UI'
    bl_category: str = 'Item'


# Main panel
class DMC_PT_panel_main(Panel, DMC_panel_base):
    bl_idname: str = 'DMC_PT_panel_main'
    bl_label: str = 'DMC 1-3 tools'
 
    def draw(self, context):
        layout = self.layout
        layout.operator(DMC_OT_panel_OP.bl_idname, text='Clear scene').action = 'CLEAR'
        layout.operator(DMC_OT_panel_OP.bl_idname, text='Clear animations').action = 'CLEAR_ANIMS'
        # layout.operator(DMC_OT_panel_OP.bl_idname, text='Test model').action = 'TEST'
        # layout.operator(DMC_OT_panel_OP.bl_idname, text='Test anim').action = 'TEST_ANIM'


# Subpanel for DMC3 stuff
class DMC3_PT_panel_import(Panel, DMC_panel_base):
    bl_idname: str = 'DMC3_PT_panel_import'
    bl_label: str = 'DMC 3'
    bl_parent_id: str ='DMC_PT_panel_main'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Import")

        # layout.prop(context.scene, 'my_unfiltered_filepath')
        # layout.prop(context.scene, 'FileType')
        layout.operator(DMC3.operators.DMC3_OT_importer.bl_idname, text='Import DMC3 model').type = 'MODEL'
        # DMC3.operators.DMC3_OT_importer_filter.add(layout, context.scene, 'my_filtered_filepath', 'mod', 'scm')

        layout.operator(DMC3.operators.DMC3_OT_importer.bl_idname, text='Import DMC3 motion').type = 'MOTION'
        # DMC3_OP_imp.filter_glob = "*.mot"
        # DMC3_OP_imp.type = 'MOTION'
        # DMC3_OP_imp.func(DMC3.motion.Import)
        

# Panel operator
class DMC_OT_panel_OP(Operator):
    bl_idname: str = 'dmc.panel_op'
    bl_label: str = 'DMC 1-3 asset tools'
    bl_description: str = 'Test'
    bl_options = {'REGISTER', 'UNDO'}

    action: EnumProperty(
        items=(
            ('CLEAR', 'clear scene', 'clear scene'),
            ('CLEAR_ANIMS', 'clear anims', 'clear anims'),
            ('TEST', 'test import', 'test import'),
            ('TEST_ANIM', 'test anim import', 'test anim import'),
        )
    )

    @staticmethod
    def clear_anims():
        for action in bpy.data.actions:
            action.user_clear()
            bpy.data.actions.remove(action)


    @staticmethod
    def clear_scene():
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

        for mesh in bpy.data.meshes:
            bpy.data.meshes.remove(mesh)
        
        for armtr in bpy.data.armatures:
            bpy.data.armatures.remove(armtr)

        for action in bpy.data.actions:
            action.user_clear()
            bpy.data.actions.remove(action)
        
        for collection in bpy.data.collections:
            if collection.name != "Collection":
                bpy.data.collections.remove(collection)
 

    def execute(self, context):
        if self.action == 'CLEAR':
            self.clear_scene()

        elif self.action == 'CLEAR_ANIMS':
            self.clear_anims()
            
        elif self.action == 'TEST':
            DMC3.model.Import(context, "D:/Games/Devil May Cry HD/data/dmc3/All pacs unpacked/pl023/pl023_001.mod")
            
        elif self.action == 'TEST_ANIM':
            DMC3.motion.Import(context, "D:/Devil May Cry 3/New folder/0 GData/pl000_00_0/pl000_00_0_001.mot")


        return {'FINISHED'}
 

#=====================================================================
#   REGISTRATION
#=====================================================================
classes = (
    DMC3.operators.DMC3_OT_importer,
    DMC_OT_panel_OP,
    DMC_PT_panel_main,
    DMC3_PT_panel_import
)

def menu_func_import(self, context):
    self.layout.operator(DMC3.operators.DMC3_OT_importer.bl_idname, text="DMC3 HD model")

# search for your plugin modules in blender python sys.modules and remove them
def cleanse_modules():
    for module_name in sorted(sys.modules.keys()):
        if module_name.startswith(__name__):
            del sys.modules[module_name]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    cleanse_modules()


# ------------------------------------------------------

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_scene.dmc3('INVOKE_DEFAULT')
