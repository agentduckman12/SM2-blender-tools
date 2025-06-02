bl_info = {
    "name": "SM2 LOD Duplicator",
    "author": "violet :3",
    "version": (1, 3),
    "blender": (4, 1, 0),
    "location": "View3D > Sidebar > SM2 Tools",
    "description": "Create LODs by duplicating objects and applying decimate modifiers",
    "category": "SM2 Tools",
}

import bpy
import re

def clean_base_name(name):
    return re.sub(r'(\.\d+|_\d+)$', '', name)

class SM2_OT_DuplicateLODs(bpy.types.Operator):
    bl_idname = "object.sm2_duplicate_lods"
    bl_label = "Make LODs"
    bl_description = "Duplicate selected Meshes/Empties 5 times, parent them, and add decimates for LODs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type in {'MESH', 'EMPTY'}]

        if not selected_objects:
            self.report({'WARNING'}, "No mesh or empty objects selected.")
            return {'CANCELLED'}

        for obj in selected_objects:
            base_name = clean_base_name(obj.name)

            for i in range(1, 6):
                lod_name = f"{base_name}_lod{i}"
                dup = obj.copy()
                if obj.type == 'MESH':
                    dup.data = obj.data.copy()
                context.collection.objects.link(dup)
                dup.parent = obj
                dup.name = lod_name

                if dup.type == 'MESH':
                    for j in range(i):
                        mod = dup.modifiers.new(name=f"Decimate_{j+1}", type='DECIMATE')
                        mod.ratio = 0.5

                    bpy.context.view_layer.objects.active = dup
                    dup.select_set(True)
                    for mod in list(dup.modifiers):
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    dup.select_set(False)

        return {'FINISHED'}

class SM2_PT_LODPanel(bpy.types.Panel):
    bl_label = "SM2 Tools"
    bl_idname = "SM2_PT_lod_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SM2 Tools'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.sm2_duplicate_lods", text="Make LODs", icon='MOD_DECIM')

classes = (
    SM2_OT_DuplicateLODs,
    SM2_PT_LODPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
