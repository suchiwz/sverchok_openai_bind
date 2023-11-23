import bpy
import os
import json


def read_log_file(log_file_path):
    """
    Read the log file to get stored API call data.
    """
    if os.path.isfile(log_file_path):
        with open(log_file_path, 'r') as log_file:
            return json.load(log_file)
    else:
        return {}


def write_log_file(log_file_path, log_data):
    """
    Write the API call data to the log file.
    """
    with open(log_file_path, 'w') as log_file:
        json.dump(log_data, log_file)


def update_api_log_file(log_file_path, label, tokens_used):
    """
    Update attributes in the log file
    """
    log_file = read_log_file(log_file_path)
    log_file[label]["api_call_count"] += 1
    log_file[label]["api_tokens_count"] += tokens_used
    write_log_file(log_file_path, log_file)
