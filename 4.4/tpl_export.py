bl_info = {
    "name": "Auto Export to USF and TPL",
    "author": "violet :3",
    "version": (1, 1),
    "blender": (4, 4, 0),
    "location": "File > Export > glTF 2.0 > Sidebar Panel",
    "description": "Adds a button to glTF export panel to export and auto run ModelConverter.exe and convert_tpl.py",
    "category": "SM2 Tools",
}

import bpy
import os
import subprocess
from bpy.props import StringProperty
from bpy.types import AddonPreferences, Operator, OperatorFileBrowser

# Preferences

class GLTFExportAutoConvertPreferences(AddonPreferences):
    bl_idname = __name__

    model_converter_path: StringProperty(
        name="ModelConverter.exe Path",
        subtype='FILE_PATH',
        description="Path to ModelConverter.exe (choose .exe file)"
    )

    convert_tpl_script: StringProperty(
        name="convert_tpl.py Path",
        subtype='FILE_PATH',
        description="Path to convert_tpl.py (choose .py file)"
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "model_converter_path")
        row.operator("gltf_autoconvert.pick_modelconverter", text="Browse .exe")
        row = layout.row(align=True)
        row.prop(self, "convert_tpl_script")
        row.operator("gltf_autoconvert.pick_convertpy", text="Browse .py")


# File picker operators

class GLTF_OT_pick_modelconverter(Operator, OperatorFileBrowser):
    bl_idname = "gltf_autoconvert.pick_modelconverter"
    bl_label = "Select ModelConverter.exe"
    bl_description = "Pick the ModelConverter.exe file"
    filename_ext = ".exe"
    filter_glob: StringProperty(default="*.exe", options={'HIDDEN'})

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        prefs.model_converter_path = self.filepath
        self.report({'INFO'}, f"Selected ModelConverter.exe: {self.filepath}")
        return {'FINISHED'}


class GLTF_OT_pick_convertpy(Operator, OperatorFileBrowser):
    bl_idname = "gltf_autoconvert.pick_convertpy"
    bl_label = "Select convert_tpl.py"
    bl_description = "Pick the convert_tpl.py file"
    filename_ext = ".py"
    filter_glob: StringProperty(default="*.py", options={'HIDDEN'})

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        prefs.convert_tpl_script = self.filepath
        self.report({'INFO'}, f"Selected convert_tpl.py: {self.filepath}")
        return {'FINISHED'}


# Main export operator button added to glTF export UI

class EXPORT_OT_gltf_auto_convert_button(bpy.types.Operator):
    """Export using current GLTF settings and then auto run ModelConverter and convert_tpl.py"""
    bl_idname = "export_scene.gltf_auto_convert_button"
    bl_label = "Export and Auto Convert to USF/TPL"
    bl_options = {'REGISTER'}

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        model_converter = bpy.path.abspath(prefs.model_converter_path)
        convert_tpl = bpy.path.abspath(prefs.convert_tpl_script)

        export_op = context.space_data.active_operator
        if export_op is None or export_op.bl_idname != "EXPORT_SCENE_OT_gltf":
            self.report({'ERROR'}, "GLTF export operator not found.")
            return {'CANCELLED'}

        export_path = export_op.filepath
        if not export_path:
            self.report({'ERROR'}, "No export filepath specified.")
            return {'CANCELLED'}

        # Copy all export operator properties except internal ones
        args = {}
        exclude_props = {'bl_idname', 'bl_label', 'bl_options', 'bl_rna', 'rna_type', 'filepath'}
        for prop_name in export_op.properties.bl_rna.properties.keys():
            if prop_name not in exclude_props:
                args[prop_name] = getattr(export_op, prop_name)

        args['filepath'] = export_path

        # Export GLTF with current settings
        bpy.ops.export_scene.gltf(**args)

        folder = os.path.dirname(export_path)
        basename = os.path.splitext(os.path.basename(export_path))[0]
        usf_path = os.path.join(folder, basename + ".usf")

        working_dir = os.path.dirname(model_converter)

        def quote_path(path):
            if ' ' in path or '(' in path or ')' in path:
                return f'"{path}"'
            else:
                return path

        if os.name == 'nt':
            cmd = (
                f'{quote_path(model_converter)} {quote_path(export_path)} && '
                f'python {quote_path(convert_tpl)} {quote_path(usf_path)} && exit'
            )
            subprocess.Popen(
                ['cmd.exe', '/c', 'start', '', 'cmd.exe', '/k', cmd],
                cwd=working_dir,
            )
        else:
            cmd = (
                f'{quote_path(model_converter)} {quote_path(export_path)} && '
                f'python3 {quote_path(convert_tpl)} {quote_path(usf_path)} && exit'
            )
            subprocess.Popen(cmd, shell=True, cwd=working_dir)

        self.report({'INFO'}, "Exported GLTF and launched auto convert processes.")
        return {'FINISHED'}


# Add button to glTF export UI Panel in the Sidebar

def draw_auto_convert_button(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(EXPORT_OT_gltf_auto_convert_button.bl_idname, icon='EXPORT')


classes = (
    GLTFExportAutoConvertPreferences,
    GLTF_OT_pick_modelconverter,
    GLTF_OT_pick_convertpy,
    EXPORT_OT_gltf_auto_convert_button,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.EXPORT_SCENE_OT_gltf.append(draw_auto_convert_button)


def unregister():
    bpy.types.EXPORT_SCENE_OT_gltf.remove(draw_auto_convert_button)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
