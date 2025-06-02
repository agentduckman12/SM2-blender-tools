bl_info = {
    "name": "Bake Shader Toggle",
    "blender": (4, 4, 0),
    "category": "SM2 Tools",
    "version": (1, 3),
    "author": "violet :3",
    "description": "Toggles baking setup by changing shader output to use SM2 group bake outputs and sets bake settings. Connects _a/Base Color bake or _spec bake for baking."
}

import bpy

class BAKE_OT_prepare(bpy.types.Operator):
    bl_idname = "bake.prepare_shader"
    bl_label = "Prepare SM2 Shader for Bake"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        group_name_prefix = "SM2 Universal Shader"
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue

            tree = mat.node_tree
            nodes = tree.nodes
            links = tree.links

            output_node = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeOutputMaterial)), None)
            group_node = next((n for n in nodes if n.type == 'GROUP' and n.node_tree and n.node_tree.name.startswith(group_name_prefix)), None)

            if output_node and group_node:
                # Remove Surface links to output
                for link in list(links):
                    if link.to_node == output_node and link.to_socket.name == 'Surface':
                        links.remove(link)
                if '_a/Base Color bake' in group_node.outputs:
                    links.new(group_node.outputs['_a/Base Color bake'], output_node.inputs['Surface'])

        scene = context.scene
        scene.render.engine = 'CYCLES'
        scene.cycles.bake_type = 'EMIT'
        scene.render.bake.use_clear = False

        for mat in bpy.data.materials:
            if mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.label.lower() in ['base color', 'basecolor']:
                        node.select = True
                        mat.node_tree.nodes.active = node

        return {'FINISHED'}


class BAKE_OT_restore(bpy.types.Operator):
    bl_idname = "bake.restore_shader"
    bl_label = "Restore SM2 Shader Output"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        group_name_prefix = "SM2 Universal Shader"
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue

            tree = mat.node_tree
            nodes = tree.nodes
            links = tree.links

            output_node = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeOutputMaterial)), None)
            group_node = next((n for n in nodes if n.type == 'GROUP' and n.node_tree and n.node_tree.name.startswith(group_name_prefix)), None)

            if output_node and group_node:
                for link in list(links):
                    if link.to_node == output_node and link.to_socket.name == 'Surface':
                        links.remove(link)
                if 'BSDF' in group_node.outputs:
                    links.new(group_node.outputs['BSDF'], output_node.inputs['Surface'])

        return {'FINISHED'}


class BAKE_OT_connect_spec(bpy.types.Operator):
    bl_idname = "bake.connect_spec_output"
    bl_label = "Connect _spec Bake to Surface"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        group_name_prefix = "SM2 Universal Shader"
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue

            tree = mat.node_tree
            nodes = tree.nodes
            links = tree.links

            output_node = next((n for n in nodes if isinstance(n, bpy.types.ShaderNodeOutputMaterial)), None)
            group_node = next((n for n in nodes if n.type == 'GROUP' and n.node_tree and n.node_tree.name.startswith(group_name_prefix)), None)

            if output_node and group_node:
                for link in list(links):
                    if link.to_node == output_node and link.to_socket.name == 'Surface':
                        links.remove(link)
                if '_spec bake' in group_node.outputs:
                    links.new(group_node.outputs['_spec bake'], output_node.inputs['Surface'])

            # Select the _spec texture node if found
            for node in nodes:
                if node.type == 'TEX_IMAGE' and '_spec' in node.name.lower():
                    node.select = True
                    nodes.active = node

        return {'FINISHED'}


class BAKE_PT_shader_bake_tools(bpy.types.Panel):
    bl_label = "SM2 Bake Tools"
    bl_idname = "BAKE_PT_shader_bake_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SM2 Tools'

    def draw(self, context):
        layout = self.layout
        layout.operator("bake.prepare_shader", text="Prepare for Bake")
        layout.operator("bake.restore_shader", text="Restore Shader")
        layout.operator("bake.connect_spec_output", text="Connect _spec Bake Output")


classes = [
    BAKE_OT_prepare,
    BAKE_OT_restore,
    BAKE_OT_connect_spec,
    BAKE_PT_shader_bake_tools,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
