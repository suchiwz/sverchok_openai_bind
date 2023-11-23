import bpy
import sys
from bpy.app.handlers import persistent

from sverchok.ui.nodeview_space_menu import add_node_menu
from .preferences import OpenAIAddonPreferences, update_api_info, \
    update_log_info
from .nodes.node_openai_text_generation import SvOpenAITextGenerationNode
from .operators.ot_openai_set_all_call import OT_OpenAISetAllCall
from .nodes.node_openai_message import SvOpenAIMessageNode
from .panels.pt_openai_node_manager import PT_OpenAINodeManager
from .nodes.node_iter_openai_text_generation import SvIterOpenAITextGenerationNode, BoolPropertyGroup

bl_info = {
    "name": "sverchok_openai_bind",
    "description": "Description.",
    "author": "wwz",
    "category": "Object",
    "version": (0, 1),
    "blender": (2, 80, 0),
}

node_categories = [
    {
        "OpenAI": [
            'SvOpenAITextGenerationNode',
            'SvIterOpenAITextGenerationNode',
            'SvOpenAIMessageNode'
        ]
    }
]


@persistent
def reset_api_called(scene):
    for ng in bpy.data.node_groups:
        if ng.bl_idname == 'SverchCustomTreeType':
            process_nodes(ng.nodes)


def process_nodes(nodes):
    for node in nodes:
        if node.bl_idname == 'SvOpenAITextGenerationNode':
            node.flag_call_api = False
            print(f"Reset {node.name} api_called prop")
        elif node.bl_idname == 'SvIterOpenAITextGenerationNode':
            for idd, item in enumerate(node.flag_call_api):
                item.value = False
            print(f"Reset {node.name} api_called prop")
        elif node.bl_idname == 'SvGroupTreeNode':
            internal_nodes = node.node_tree.nodes
            process_nodes(internal_nodes)


def my_register():
    bpy.utils.register_class(OpenAIAddonPreferences)
    bpy.utils.register_class(BoolPropertyGroup)
    bpy.utils.register_class(SvOpenAITextGenerationNode)
    bpy.utils.register_class(SvIterOpenAITextGenerationNode)
    bpy.utils.register_class(SvOpenAIMessageNode)
    bpy.utils.register_class(OT_OpenAISetAllCall)
    bpy.utils.register_class(PT_OpenAINodeManager)
    add_node_menu.append_from_config(node_categories)
    add_node_menu.register()

    p = bpy.context.preferences.addons[__name__].preferences
    update_api_info(p, bpy.context)
    update_log_info(p, bpy.context)


def check_sverchok_loaded_and_register(count):
    if "sverchok" in sys.modules:
        my_register()
    else:
        print(f"Sverchok unload, wait for it. Try = {count}")
        if count > 5:
            print("Failed to load openai bind")
        else:
            bpy.app.timers.register(
                lambda: check_sverchok_loaded_and_register(count + 1),
                first_interval=1.0)


def register():
    check_sverchok_loaded_and_register(0)
    bpy.app.handlers.load_post.append(reset_api_called)


def unregister():
    bpy.utils.unregister_class(OpenAIAddonPreferences)
    bpy.utils.unregister_class(BoolPropertyGroup)
    bpy.utils.unregister_class(SvOpenAITextGenerationNode)
    bpy.utils.unregister_class(SvIterOpenAITextGenerationNode)
    bpy.utils.unregister_class(SvOpenAIMessageNode)
    bpy.utils.unregister_class(OT_OpenAISetAllCall)
    bpy.utils.unregister_class(PT_OpenAINodeManager)
    bpy.app.handlers.load_post.remove(reset_api_called)
