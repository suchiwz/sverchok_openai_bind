import bpy
import json
from sverchok.node_tree import SverchCustomTreeNode
from bpy.props import StringProperty


class SvOpenAIMessageNode(bpy.types.Node, SverchCustomTreeNode):
    """
    A custom node that manage messages
    """

    bl_idname = 'SvOpenAIMessageNode'
    bl_label = 'OpenAI Message Node'
    bl_icon = 'OUTLINER_OB_EMPTY'

    role: StringProperty(
        name='Role',
        default='user'
    )
    content: StringProperty(
        name='Content',
        default=''
    )

    def sv_init(self, context):
        self.inputs.new(
            'SvStringsSocket',
            'Role'
        ).prop_name = 'role'
        self.inputs.new(
            'SvStringsSocket',
            'Content'
        ).prop_name = 'content'

        self.outputs.new(
            'SvStringsSocket',
            'Message'
        )

    def sv_update(self):
        self.process()

    def process(self):
        role = self.inputs['Role'].sv_get()[0][0]
        content = self.inputs['Content'].sv_get()[0][0]
        message = {"role": role, "content": content}
        message_json = json.dumps(message)
        self.outputs["Message"].sv_set([message_json])
