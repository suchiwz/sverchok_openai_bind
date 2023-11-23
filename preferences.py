import bpy
import os
import json

from .utils.utils_log import *
from .utils.utils_get_addon_name import *


def load_key(file_path):
    """
    Load api key from config file.
    The config file is a json file in the form:
    {
        "OPENAI_API_KEY": "Your openai api key beginning with sk-",
        "OPENAI_API_BASE": "API base",
        ...(more in the future)
    }
    """
    if os.path.isfile(file_path):
        with open(file_path, 'r') as config_file:
            file_data = json.load(config_file)
            if "OPENAI_API_KEY" in file_data.keys():
                os.environ['OPENAI_API_KEY'] = file_data['OPENAI_API_KEY']
                print(f"Set openai api key at {file_path}")
            else:
                print(f"Failed to find key 'OPENAI_API_KEY' in {file_path}")
            if "OPENAI_API_BASE" in file_data.keys():
                os.environ['OPENAI_API_BASE'] = file_data['OPENAI_API_BASE']
                print(f"Set openai api base at {file_path}")
            else:
                os.environ['OPENAI_API_BASE'] = "https://api.openai.com/v1"
                print(f"Failed to find 'OPENAI_API_BASE' in {file_path}. We "
                      f"set it to default {os.environ['OPENAI_API_BASE']}")


def update_api_info(self, context):
    """
    Drawback function called when config file path is changed
    """
    # Load new api config in the file
    os.environ['OPENAI_CONFIG_FILE_PATH'] = self.config_file_path
    load_key(self.config_file_path)


def update_log_info(self, context):
    """
    Drawback function called when log file direction is changed
    """
    path = self.log_file_dir
    if os.path.exists(path):
        os.environ['OPENAI_BIND_LOG_DIR'] = self.log_file_dir
        os.environ['OPENAI_LOG_FILE_PATH'] = os.path.join(self.log_file_dir, "openai_log.json")
        print(f"Set log direction at {os.environ['OPENAI_BIND_LOG_DIR']}")
        # Load existing log data
        log_file_path = os.environ['OPENAI_LOG_FILE_PATH']
        log_data = read_log_file(log_file_path)
        # Check if the label(path) is in the log file
        if self.config_file_path in log_data.keys():
            # Exist: Collect the data in the file
            this_path_log_data = log_data[self.config_file_path]
            self.api_call_count = this_path_log_data.get("api_call_count", 0)
            self.api_tokens_count = this_path_log_data.get("api_tokens_count", 0)
            print(f"Loaded log data: {this_path_log_data}")
        else:
            # Not exist(file or item): Create a new item in the (new) file
            self.api_call_count = 0
            self.api_tokens_count = 0
            log_data[self.config_file_path] = {
                "api_call_count": self.api_call_count,
                "api_tokens_count": self.api_tokens_count
            }
            write_log_file(log_file_path, log_data)
            print(f"The log of current api {self.config_file_path} does not "
                  f"exist. We create one.")
    else:
        print(f"File direction not exist {os.environ['OPENAI_BIND_LOG_DIR']}")


class OpenAIAddonPreferences(bpy.types.AddonPreferences):
    """
    Addon Preference Panel
    """
    bl_idname = get_addon_name()

    config_file_path: bpy.props.StringProperty(
        name="Config File Path",
        description="Path to the openai api config file",
        default="Your/path/to/config.json",
        subtype='FILE_PATH',
        update=update_api_info
    )

    log_file_dir: bpy.props.StringProperty(
        name="Log File Direction",
        description="File direction to save the openai outputs",
        default="Your/path/",
        subtype='FILE_PATH',
        update=update_log_info
    )

    api_call_count: bpy.props.IntProperty(
        name="API Call Count",
        description="Number of OpenAI calls made (Successful calls)",
        default=0
    )

    api_tokens_count: bpy.props.IntProperty(
        name="API Tokens Count",
        description="Number of OpenAI token usage",
        default=0
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"API Call Count:{self.api_call_count}")
        layout.label(text=f"API Tokens Count:{self.api_tokens_count}")
        layout.prop(self, "config_file_path")
        layout.prop(self, "log_file_dir")
