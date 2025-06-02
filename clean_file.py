bl_info = {
    "name": "SM2: Clean Armatures, Sync Data, and Clean Materials",
    "author": "violet :3",
    "version": (1, 2),
    "blender": (4, 4, 0),
    "location": "View3D > Sidebar > SM2 Tools",
    "description": "One-button cleanup: Removes empty armature modifiers, syncs data/UVs, renames and cleans materials",
    "category": "SM2 Tools",
}

import bpy
import re

# ------------------ Armature Cleanup ------------------

def remove_empty_armature_modifiers():
    removed = 0
    for obj in bpy.data.objects:
        for mod in obj.modifiers:
            if mod.type == 'ARMATURE' and mod.object is None:
                obj.modifiers.remove(mod)
                removed += 1
    return removed

# ------------------ Data/UV Sync ------------------

def sync_data_names_and_uvs():
    renamed_data = 0
    renamed_uvs = 0
    for obj in bpy.data.objects:
        if obj.data:
            if obj.data.name != obj.name:
                obj.data.name = obj.name
                renamed_data += 1
            if obj.type == 'MESH':
                for uv in obj.data.uv_layers:
                    if uv.name != "UVMap":
                        uv.name = "UVMap"
                        renamed_uvs += 1
    return renamed_data, renamed_uvs

# ------------------ Material Cleanup ------------------

def rename_materials():
    for mat in bpy.data.materials:
        match = re.search(r"(ch_|vhl_|wpn_).*", mat.name)
        if match:
            new_name = match.group(0)
            if mat.name != new_name:
                mat.name = new_name

def get_base_material_name(name):
    return re.sub(r"\.\d{3}$", "", name)

def clean_and_merge_materials():
    for mat in bpy.data.materials:
        base_name = get_base_material_name(mat.name)
        if mat.name != base_name and base_name in bpy.data.materials:
            original_mat = bpy.data.materials[base_name]
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    for slot in obj.material_slots:
                        if slot.material == mat:
                            slot.material = original_mat

    for obj in bpy.data.objects:
        if obj.type != 'MESH' or not obj.data.materials:
            continue

        mesh = obj.data
        old_mats = list(mesh.materials)
        mat_to_index = {}
        new_materials = []
        index_remap = {}

        for i, mat in enumerate(old_mats):
            if mat not in mat_to_index:
                new_index = len(new_materials)
                mat_to_index[mat] = new_index
                new_materials.append(mat)
            index_remap[i] = mat_to_index[mat]

        new_poly_indices = [index_remap.get(poly.material_index, poly.material_index) for poly in mesh.polygons]

        mesh.materials.clear()
        for mat in new_materials:
            mesh.materials.append(mat)

        for poly, new_index in zip(mesh.polygons, new_poly_indices):
            poly.material_index = new_index

    unused = [mat for mat in bpy.data.materials if mat.users == 0]
    for mat in unused:
        bpy.data.materials.remove(mat)

# ------------------ Combined Operator ------------------

class SM2_OT_CleanEverything(bpy.types.Operator):
    """Cleans armatures, syncs data/UVs, and cleans materials"""
    bl_idname = "sm2_tools.clean_everything"
    bl_label = "SM2 Full Clean"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armatures_removed = remove_empty_armature_modifiers()
        renamed_data, renamed_uvs = sync_data_names_and_uvs()
        rename_materials()
        clean_and_merge_materials()
        self.report({'INFO'}, (
            f"Removed {armatures_removed} empty armature(s), "
            f"Renamed {renamed_data} data block(s), "
            f"Renamed {renamed_uvs} UV map(s) to 'UVMap', "
            f"Materials cleaned."
        ))
        return {'FINISHED'}

# ------------------ Panel ------------------

class SM2_PT_ToolsPanel(bpy.types.Panel):
    bl_label = "SM2 Tools"
    bl_idname = "SM2_PT_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SM2 Tools'

    def draw(self, context):
        layout = self.layout
        layout.operator("sm2_tools.clean_everything", icon="BRUSH_DATA")

# ------------------ Register ------------------

classes = (
    SM2_OT_CleanEverything,
    SM2_PT_ToolsPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
