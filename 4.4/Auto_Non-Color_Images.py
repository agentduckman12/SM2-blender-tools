bl_info = {
    "name": "Auto Non-Color Images (Always On)",
    "author": "violet :3",
    "version": (1, 2),
    "blender": (4, 4, 0),
    "location": "Image Editor > Sidebar > SM2 Tools",
    "description": "Automatically sets color space to Non-Color for _spec, _cc, _nm images (always enabled)",
    "category": "SM2 Tools",
}

import bpy
import re

# Check if image name matches the pattern
def should_be_non_color(image_name):
    return re.search(r'(_spec|_cc|_nm)(\.[a-zA-Z0-9]+)?$', image_name, re.IGNORECASE)

# Handler to set color space when images are added
def image_load_handler(dummy):
    for img in bpy.data.images:
        if not img.has_data or not img.filepath:
            continue

        if img.get("auto_noncolor_checked"):
            continue

        if should_be_non_color(img.name):
            img.colorspace_settings.name = 'Non-Color'
        img["auto_noncolor_checked"] = True

# Panel UI in Image Editor > Sidebar > SM2 Tools
class IMAGE_PT_auto_noncolor(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "SM2 Tools"
    bl_label = "Auto Non-Color (Always On)"

    def draw(self, context):
        layout = self.layout
        layout.label(text="This feature is always active.")
        layout.label(text="Sets Non-Color for:")
        layout.label(text="• _spec   • _cc   • _nm")

# Registration
classes = (IMAGE_PT_auto_noncolor,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.load_post.append(image_load_handler)
    bpy.app.handlers.depsgraph_update_post.append(image_load_handler)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.load_post.remove(image_load_handler)
    bpy.app.handlers.depsgraph_update_post.remove(image_load_handler)

if __name__ == "__main__":
    register()
