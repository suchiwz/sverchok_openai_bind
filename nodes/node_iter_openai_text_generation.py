import bpy
import os
import json
from sverchok.node_tree import SverchCustomTreeNode
from bpy.props import StringProperty, FloatProperty, BoolProperty, IntProperty, CollectionProperty
from bpy_types import PropertyGroup
from ..utils.utils_log import *
from ..utils.utils_openai_text_generation import openai_text_generation

import openai


class BoolPropertyGroup(PropertyGroup):
    value: BoolProperty(name="Value", default=False)


class SvIterOpenAITextGenerationNode(bpy.types.Node, SverchCustomTreeNode):
    """
    A custom node that interacts with OpenAI's API
    call the openai chat completion method for text generation

    Inputs:
    - messages: A list in the form [{"role":"", "content":""}, ...]
    - model_name
    - temperature
    - json_form: Force the output to JSON
    - id_iter: iter index
    - num_iter: num of iters

    Outputs:
    - response: A string of the response, failed when "API Call Failed"
    - contents: The same as messages
    """

    bl_idname = 'SvIterOpenAITextGenerationNode'
    bl_label = 'OpenAI Iter Text Generation Node'
    bl_icon = 'OUTLINER_OB_EMPTY'

    messages: StringProperty(
        name='Messages',
        description='A list in the form [{"role":"", "content":""}, ...]',
        default=''
    )
    model_name: StringProperty(
        name='Model',
        default='gpt-4-1106-preview'
    )
    temperature: FloatProperty(
        name='Temperature',
        default=0.8
    )
    json_form: BoolProperty(
        name='JSON',
        default=False
    )
    id_iter: IntProperty(
        name='ID iter',
        default=0
    )
    num_iter: IntProperty(
        name='Num Iter',
        default=1
    )

    # Flag to control the call of api
    flag_call_api: CollectionProperty(
        name='Call API',
        type=BoolPropertyGroup
    )

    def sv_init(self, context):
        self.inputs.new(
            'SvStringsSocket',
            'Messages'
        ).prop_name = 'messages'
        self.inputs.new(
            'SvStringsSocket',
            'Model'
        ).prop_name = 'model_name'
        self.inputs.new(
            'SvStringsSocket',
            'Temperature'
        ).prop_name = 'temperature'
        self.inputs.new(
            'SvStringsSocket',
            'Num Iter'
        ).prop_name = 'num_iter'
        self.inputs.new(
            'SvStringsSocket',
            'ID Iter'
        ).prop_name = 'id_iter'

        self.outputs.new(
            'SvStringsSocket',
            'Response')
        self.outputs.new(
            'SvStringsSocket',
            'Contents')

    def sv_draw_buttons(self, context, layout):
        layout.prop(self, "json_form", text="JSON")

    def process(self):
        messages = self.inputs['Messages'].sv_get()
        model_name = self.inputs['Model'].sv_get()[0][0]
        temperature = self.inputs['Temperature'].sv_get()[0][0]
        id_iter = self.inputs['ID Iter'].sv_get()[0][0]
        num_iter = self.inputs['Num Iter'].sv_get()[0][0]
        node_label = self.name + f"_{id_iter}_{num_iter}"
        if num_iter != len(self.flag_call_api):
            self.flag_call_api.clear()
            for i in range(num_iter):
                item = self.flag_call_api.add()
                item.value = False

        flag_call_api = self.flag_call_api[id_iter].value

        temp_file_name = f"temp_{node_label}.log"
        hist_file_name = f"history_{node_label}.log"
        temp_path = os.environ['OPENAI_BIND_LOG_DIR'] + temp_file_name
        hist_path = os.environ['OPENAI_BIND_LOG_DIR'] + hist_file_name

        # Only call the API when the call api flag is True
        if flag_call_api:
            print(f"Start calling the openai api at {node_label}")
            token_used, response, reason = openai_text_generation(
                messages,
                model_name,
                temperature,
                self.json_form,
                temp_path,
                hist_path
            )
            print(f"Call finished at {node_label}: "
                  f"token:{token_used}, reason:{reason}")
            self.outputs['Response'].sv_set([response])
            self.outputs['Contents'].sv_set(messages)
        else:
            with open(temp_path, "r") as file:
                response = json.load(file)["response"]["choices"][0]["message"]["content"]
            self.outputs['Response'].sv_set([response])
            self.outputs['Contents'].sv_set(messages)


