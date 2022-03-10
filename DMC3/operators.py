import bpy
import os
from enum import Enum

from bpy_extras.io_utils import (ImportHelper, path_reference_mode, ExportHelper)
from bpy.types import Operator
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    StringProperty,
    EnumProperty,
    IntProperty
)

import imp

class type(Enum):
    MODEL = 0
    MOTION = 1

#=====================================================================
#   DMC3 model
#=====================================================================
import DMC3.model
imp.reload(DMC3.model)
import DMC3.motion
imp.reload(DMC3.motion)


# import
class DMC3_OT_importer(Operator, ImportHelper):
    """Import models and animations from the first 3 DMC games of any version"""
    bl_idname = "import_scene.dmc3"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "DMC3 HD models (.mod, .scm)"

    # ImportHelper mixin class uses this
    filename_ext = ".mod, .scm"

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    filter_glob: StringProperty(
        default="*.mod;*.scm",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
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
        files = self.files
        import_dir = os.path.dirname(self.filepath)
        # print(f"\n    {type(files)}\n    {files}\n")
        
        for file in files:
            filepath = (os.path.join(import_dir, file.name))
            print(f"\n{file.name}")

            if self.type == 'MODEL':
                DMC3.model.Import(context, filepath)

            elif self.type == 'MOTION':
                DMC3.motion.Import(context, filepath)

        return {'FINISHED'}


#=====================================================================
#   REGISTRATION
#=====================================================================
classes = (
    DMC3_OT_importer
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

