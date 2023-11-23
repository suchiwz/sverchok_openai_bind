import openai

from .utils_log import *
from .utils_get_addon_name import *
from ..preferences import update_log_info


def openai_function_call(inputs, model, temp, log_path, hist_path):
    """
    Simple text generation method for openai api calling
    Inputs:
    - inputs: A list of string {"role":"", "contents":""} messages
    - model
    - temperature
    - log_path: temp log
    - hist_path: history log
    Outputs:
    - token_used
    - text
    - reason
    """
    message = [json.loads(m) for m in inputs]
    client = openai.OpenAI()
    try:
        # API calling
        response = client.chat.completions.create(
            model=model,
            messages=message,
            temperature=temp,
            response_format={
                "type": "json_object"
            } if json_form else None
        )
        chat = {
            "messages": message,
            "response": response.model_dump()
        }
        # Write the temp log in the file
        with open(log_path, "w") as file:
            file.write(json.dumps(chat))

        tokens_used = response.usage.total_tokens
        text = response.choices[0].message.content
        reason = response.choices[0].finish_reason
        # Write the historical information in the file
        with open(hist_path, "a") as file:
            add = "\n" + "\n".join(inputs) + "\n" + text + "\n"
            file.write(add)
        # Update the usage log
        update_api_log_file(os.environ['OPENAI_LOG_FILE_PATH'],
                            os.environ['OPENAI_CONFIG_FILE_PATH'], tokens_used)
        # Update preferences
        preferences = (
            bpy.context.preferences.addons[get_addon_name()].preferences)
        update_log_info(preferences, bpy.context)

        return tokens_used, text, reason

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return 0, "API call failed", "Fail Call"
