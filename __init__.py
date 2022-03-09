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
import bpy
from bpy.types import Operator, Panel

from bpy.props import (
    # BoolProperty,
    # CollectionProperty,
    # StringProperty,
    EnumProperty
)

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy.types import Operator

sys.path.insert( 0, os.path.abspath( os.path.dirname(__file__) ) )

# My imports
import imp
import DMC3.operators
imp.reload(DMC3.operators)
import DMC3.model
imp.reload(DMC3.model)
import DMC3.motion
imp.reload(DMC3.motion)


#=====================================================================
#   SIDE PANEL UI
#=====================================================================
class DMC_PT_panel(Panel):
    bl_idname = 'DMC_PT_panel'
    bl_label = 'DMC 1-3 tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
 
    # Draw the ui buttons and shit
    def draw(self, context):
        layout = self.layout
        layout.operator(DMC_OT_panel_OP.bl_idname, text='Clear scene').action = 'CLEAR'
        layout.operator(DMC3.operators.DMC3_OT_importer.bl_idname, text='Import DMC3 model')
        # op = layout.operator(DMC3.operators.DMC3_OT_importer.bl_idname, text='Import DMC3 motion')
        # layout.operator(DMC_OT_panel_OP.bl_idname, text='Import a set model for testing').action = 'TEST'
        # layout.operator(DMC_OT_panel_OP.bl_idname, text='Import a set anim for testing').action = 'TEST_ANIM'

        # op.filter_glob = "*.mot"
        # op.type = 'MOTION'
        # op.func(DMC3.motion.Import)


# panel operator
class DMC_OT_panel_OP(Operator):
    bl_idname = 'dmc.panel_op'
    bl_label = 'DMC 1-3 asset tools'
    bl_description = 'Test'
    bl_options = {'REGISTER', 'UNDO'}

    action: EnumProperty(
        items=(
            ('CLEAR', 'clear scene', 'clear scene'),
            ('TEST', 'test import', 'test import'),
            ('TEST_ANIM', 'test anim import', 'test anim import'),
        )
    )

    @staticmethod
    def clear_scene(context):
        for collection in bpy.data.collections:

            if collection.name != "Collection":

                for obj in bpy.data.objects:
                    bpy.data.objects.remove(obj, do_unlink=True)

                for mesh in bpy.data.meshes:
                    bpy.data.meshes.remove(mesh)
                
                for armtr in bpy.data.armatures:
                    bpy.data.armatures.remove(armtr)

                bpy.data.collections.remove(collection)
 

    def execute(self, context):
        if self.action == 'CLEAR':
            self.clear_scene(context=context)
            
        elif self.action == 'TEST':
            DMC3.model.Import(context, "D:\\Games\\Devil May Cry HD\\data\\dmc3\\All pacs unpacked\\pl023\\pl023_001.mod")
            
        elif self.action == 'TEST_ANIM':
            DMC3.motion.Import(context, "D:\\games\\Devil May Cry HD\\data\\dmc3\\All pacs unpacked\\pl021\\pl021_002\\pl021_002_002.mot")


        return {'FINISHED'}
 

#=====================================================================
#   REGISTRATION
#=====================================================================
classes = (
    DMC3.operators.DMC3_OT_importer,
    DMC_OT_panel_OP,
    DMC_PT_panel
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
