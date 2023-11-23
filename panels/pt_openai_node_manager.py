import bpy
import bpy_types


class PT_OpenAINodeManager(bpy.types.Panel):
    bl_label = "OpenAI Node Manager"
    bl_idname = "PT_OpenAINodeManager"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Sverchok'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator(
            "sverchok.set_openai_set_all_call",
            text="Select All"
        ).state = True
        row.operator(
            "sverchok.set_openai_set_all_call",
            text="Unselect All"
        ).state = False

        for ng in bpy.data.node_groups:
            if ng.bl_idname == 'SverchCustomTreeType':
                self.draw_nodes(ng.nodes, layout)

    def draw_nodes(self, nodes, layout):
        for node in nodes:
            if node.bl_idname == 'SvOpenAITextGenerationNode':
                row = layout.row()
                row.prop(node, "flag_call_api", text=node.name)
            elif node.bl_idname == 'SvIterOpenAITextGenerationNode':
                for idd, item in enumerate(node.flag_call_api):
                    row = layout.row()
                    row.prop(item, "value", text=node.name + str(idd))
            elif node.bl_idname == 'SvGroupTreeNode':
                self.draw_nodes(node.node_tree.nodes, layout)

