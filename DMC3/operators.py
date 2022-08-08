import time
import bpy
import os
from enum import Enum

from bpy_extras.io_utils import (
    ImportHelper, 
    path_reference_mode, 
    ExportHelper
)

from bpy.types import (
    Operator,
    Scene
)

from bpy.props import (
    BoolProperty,
    CollectionProperty,
    StringProperty,
    EnumProperty,
    IntProperty
)

import imp


#=====================================================================
#   DMC3 model
#=====================================================================
import DMC3.model
import DMC3.motion
imp.reload(DMC3.model)
imp.reload(DMC3.motion)


def update_fliter(self, context):
    print(bpy.ops.IMPORT_SCENE_OT_dmc3.type)

    # try:
    if bpy.ops.IMPORT_SCENE_OT_dmc3.type == 'MODEL':
        bpy.ops.IMPORT_SCENE_OT_dmc3.filter_glob = "*.mod;*.scm"
        bpy.ops.IMPORT_SCENE_OT_dmc3.filename_ext = ".mod, .scm"
        print("Mod")

    elif bpy.ops.IMPORT_SCENE_OT_dmc3.type == 'MOTION':
        bpy.ops.IMPORT_SCENE_OT_dmc3.filter_glob = "*.mot"
        bpy.ops.IMPORT_SCENE_OT_dmc3.filename_ext = ".mot"
        print("Mot")

    # print(bpy.ops.IMPORT_SCENE_OT_dmc3.filter_glob)
    # except:
    #     print("Get fucked")


Scene.FileType = EnumProperty(
    items = (
        ('MODEL', 'Model', 'model'),
        ('MOTION', 'Motion', 'motion')
    ),
    name = "File type",
    default = 'MODEL',
    update = update_fliter
)


# import
class DMC3_OT_importer(Operator, ImportHelper):
    """Import models and animations from DMC3 of any version"""
    bl_idname: str = "import_scene.dmc3"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label: str = "DMC3 HDC models (.mod, .scm)"

    # ImportHelper mixin class uses this
    filename_ext: str = ".mod, .scm"

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    filter_glob: StringProperty(
        default = "*.mod;*.scm",
        options = {'HIDDEN'},
        maxlen = 255,  # Max internal buffer length, longer would be clamped.
    )

    type: EnumProperty(
        items = (
            ('MODEL', 'Model', 'model'),
            ('MOTION', 'Motion', 'motion')
        ),
        name = "Asset type",
        default = 'MODEL',
        # update = update_fliter
    )
        
    files: CollectionProperty(
        type = bpy.types.OperatorFileListElement,
        options = {'HIDDEN', 'SKIP_SAVE'},
    )


    # def draw(self, context):
    #     self.layout.prop(self, 'type')

    #     if self.type == 'MODEL':
    #         self.filter_glob = "*.mod;*.scm"
    #         self.filename_ext = ".mod, .scm"

    #     elif self.type == 'MOTION':
    #         self.filter_glob = "*.mot"
    #         self.filename_ext = ".mot"

    #     print(self.type)
    #     print(self.filter_glob)


    # def invoke(self, context, event):
    #     if self.type == 'MODEL':
    #         self.filter_glob = "*.mod;*.scm"
    #         self.filename_ext = ".mod, .scm"

    #     elif self.type == 'MOTION':
    #         self.filter_glob = "*.mot"
    #         self.filename_ext = ".mot"

    #     return super().invoke(context, event)


    def execute(self, context):
        startTime = time.perf_counter()
        files = self.files
        import_dir = os.path.dirname(self.filepath)
        print(self.type)
        # print(f"\n    {type(files)}\n    {files}\n")
        
        for file in files:
            filepath = (os.path.join(import_dir, file.name))
            # print(f"\n{file.name}")

            if self.type == 'MODEL':
                DMC3.model.Import(context, filepath)

            elif self.type == 'MOTION':
                DMC3.motion.Import(context, filepath)
                

        print(f"Import took {time.perf_counter() - startTime}")

        return {'FINISHED'}


Scene.my_filtered_filepath = StringProperty(name = 'Filtered',
                                            description="Import a model or animation",
                                            default="",
                                            subtype='NONE') # important


class DMC3_OT_importer_filter(Operator, ImportHelper):
    """Import models and animations from DMC3 of any version"""
    bl_idname: str = "import_scene.dmc3_filter"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label: str = "DMC3 HDC models (.mod, .scm)"
    
    # ImportHelper mixin class uses this
    filename_ext: str = ".mod, .scm"

    filter_glob: StringProperty(
        default="",
        options={'HIDDEN'},
        maxlen=255  # Max internal buffer length, longer would be clamped.
    )

    type: EnumProperty(
        items=(
            ('MODEL', 'Model', 'model'),
            ('MOTION', 'Motion', 'motion')
        )
    )
    
    files: CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )


    def execute(self, context):
        setattr(self.scene, self.string_prop_name, bpy.path.relpath(self.filepath))

        return {'FINISHED'}


    def invoke(self, context, event):
        self.filter_glob = "*" + ";*".join(self.ext)

        return super().invoke(context, event)


    @classmethod
    def add(cls, layout, scene, string_prop_name, *ext):
        cls.ext = ext
        cls.scene = scene
        cls.string_prop_name = string_prop_name

        col = layout.split(factor=.33)
        col.label(text=scene.bl_rna.properties[string_prop_name].name)

        row = col.row(align=True)

        if scene.bl_rna.properties[string_prop_name].subtype != 'NONE':
            row.label("ERROR: Change subtype of {} property to 'NONE'".format(string_prop_name), icon='ERROR')
        else:
            row.prop(scene, string_prop_name, icon_only=True)
            row.operator(cls.bl_idname, icon='FILEBROWSER')


#=====================================================================
#   REGISTRATION
#=====================================================================
classes = (
    DMC3_OT_importer,
    DMC3_OT_importer_filter
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

