import bpy


class OT_OpenAISetAllCall(bpy.types.Operator):
    bl_idname = "sverchok.set_openai_set_all_call"
    bl_label = "Set All API Call"

    state: bpy.props.BoolProperty()

    def execute(self, context):
        for ng in bpy.data.node_groups:
            if ng.bl_idname == 'SverchCustomTreeType':
                self.process_nodes(ng.nodes)
        return {'FINISHED'}

    def process_nodes(self, nodes):
        for node in nodes:
            if node.bl_idname == 'SvOpenAITextGenerationNode':
                node.flag_call_api = self.state
                print(f"Reset {node.name} flag_call_api to {self.state}")
            elif node.bl_idname == 'SvIterOpenAITextGenerationNode':
                for idd, item in enumerate(node.flag_call_api):
                    item.value = self.state
                print(f"Reset {node.name} api_called prop to {self.state}")
            elif node.bl_idname == 'SvGroupTreeNode':
                internal_nodes = node.node_tree.nodes
                self.process_nodes(internal_nodes)
