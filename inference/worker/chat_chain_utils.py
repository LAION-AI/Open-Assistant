import json
import re
import threading

import requests
import transformers
from chat_chain_prompts import INSTRUCTIONS, OBSERVATION_SEQ, TOOLS_PREFIX, V2_ASST_PREFIX, V2_PROMPTER_PREFIX
from hf_langchain_inference import HFInference
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from loguru import logger
from oasst_shared.schemas import inference
from opeanapi_parser import prepare_plugin_for_llm
from settings import settings

tokenizer_lock = threading.Lock()

RESPONSE_MAX_LENGTH = 2048

llm_parser = HFInference(
    inference_server_url=settings.inference_server_url,
    max_new_tokens=512,
    stop_sequences=["</s>"],
    top_k=5,
    temperature=0.20,
    repetition_penalty=(1 / 0.83),
)


# NOTE: https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance
# We are using plugin API-s endpoint/paths as tool names,
# e.g.: /get_weather, /get_news etc... so this algo should be fine
# possible improvement: try levenshtein or vector distances
# but best way is to just use better models.
def similarity(ts1: str, ts2: str) -> float:
    if ts1 == ts2:
        return 1

    match = 0
    len1, len2 = len(ts1), len(ts2)
    max_dist = (max(len1, len2) // 2) - 1

    hash_ts1 = [0] * len1
    hash_ts2 = [0] * len2

    for i in range(len1):
        for j in range(max(0, i - max_dist), min(len2, i + max_dist + 1)):
            if ts1[i] == ts2[j] and hash_ts2[j] == 0:
                hash_ts1[i] = 1
                hash_ts2[j] = 1
                match += 1
                break

    if match == 0:
        return 0

    t = 0
    point = 0

    for i in range(len1):
        if hash_ts1[i] == 1:
            while hash_ts2[point] == 0:
                point += 1
            if ts1[i] != ts2[point]:
                t += 1
            point += 1

    t /= 2
    return (match / len1 + match / len2 + (match - t) / match) / 3.0


# TODO: Can be improved, like... try to use another pass trough LLM
# with custom tuned prompt for fixing the formatting.
# e.g. "This is malformed text, please fix it: {malformed text} -> FIX magic :)"
def extract_tool_and_input(llm_output: str, ai_prefix: str) -> tuple[str, str]:
    llm_output = llm_output.strip().replace("```", "")
    if f"{ai_prefix}:" in llm_output:
        return ai_prefix, llm_output.split(f"{ai_prefix}:")[-1].strip()
    regex = r"Action: (.*?)[\n]*Action Input:\n?(.*)"
    # match = re.search(regex, llm_output) # this is for 65B llama :(
    match = re.search(regex, llm_output, re.MULTILINE | re.DOTALL)
    if not match:
        if OBSERVATION_SEQ in llm_output:
            return ai_prefix, llm_output.split(OBSERVATION_SEQ)[-1].strip()
        return ai_prefix, llm_output
    action = match.group(1)
    action_input = match.group(2)
    return action.strip().replace("'", ""), action_input.strip().strip(" ")


# Truncate string, but append matching bracket if string starts with [ or { or (
# it helps in a way, that LLM will not try to just continue generating output
# continuation
def truncate_str(output: str, max_length: int = 1024) -> str:
    if len(output) > max_length:
        if output[0] == "(":
            return output[:max_length] + "...)"
        elif output[0] == "[":
            return output[:max_length] + "...]"
        elif output[0] == "{":
            return output[:max_length] + "...}"
        else:
            return output[:max_length] + "..."
    return output


# Parse JSON and try to fix it if it's not valid
def prepare_json(json_str: str) -> str:
    json_str = json_str.strip()
    fixed_json = json_str
    try:
        json.loads(json_str)
    except json.decoder.JSONDecodeError:
        # Fix missing quotes around keys and replace Python's True, False, and None
        fixed_json = re.sub(r"(?<=\{|\,)(\s*)(\w+)(\s*):", r'\1"\2"\3:', json_str)
        fixed_json = fixed_json.replace("True", "true").replace("False", "false").replace("None", "null")

        # Remove excessive closing braces/brackets
        brace_count = bracket_count = 0
        result = []
        for c in fixed_json:
            if c == "{":
                brace_count += 1
            elif c == "}":
                brace_count -= 1
            elif c == "[":
                bracket_count += 1
            elif c == "]":
                bracket_count -= 1

            if brace_count >= 0 and bracket_count >= 0:
                result.append(c)
        # Add missing closing braces/brackets
        result.extend(["}"] * brace_count)
        result.extend(["]"] * bracket_count)
        fixed_json = "".join(result)

        try:
            json.loads(fixed_json)
        except json.decoder.JSONDecodeError as e:
            logger.warning(f"JSON is still not valid, trying to fix it with LLM {fixed_json}")
            # if it's still not valid, try with LLM fixer
            prompt = f"""{V2_PROMPTER_PREFIX}Below is malformed JSON object string:
--------------
{json_str}
--------------
Parsing error:
--------------
{e}

RULES:
1. If malformed JSON object string contains multiple objects, you merge them into one.
2. You will never made up or add any new data, you will only fix the malformed JSON object string.

Here is the fixed JSON object string:</s>{V2_ASST_PREFIX}"""
            logger.warning(f"JSON Fix Prompt: {prompt}")
            out = llm_parser.generate(prompts=[prompt]).generations[0][0].text
            out = out[: out.find("}") + 1]
            logger.warning(f"JSON Fix Output: {out}")
            return out

    return fixed_json


def use_tool(tool_name: str, tool_input: str, tools: list) -> str:
    for tool in tools:
        # This should become stricter and stricter as we get better models
        if similarity(tool.name, tool_name) > 0.75 or tool.name in tool_name:
            # check if tool_input is valid json, and if not, try to fix it
            tool_input = prepare_json(tool_input)
            return tool.func(tool_input)
    return f"ERROR! {tool_name} is not a valid tool. Try again with different tool!"


# Needs more work for errors, error-prompt tweaks are currently based on
# `OpenAssistant/oasst-sft-6-llama-30b-epoch-1 model`
# TODO: Add other missing methods and Content-Types etc...
class RequestsForLLM:
    def run(self, params: str, url: str, param_location: str, type: str, payload: str | None = None) -> str:
        return self.run_request(params, url, param_location, type, payload)

    def run_request(self, params: str, url: str, param_location: str, type: str, payload: str = None) -> str:
        try:
            query_params = params
            if param_location == "path":
                for key, value in query_params.items():
                    url = url.replace(f"{{{key}}}", value)
                query_params = {}

            headers = {"Content-Type": "application/json"} if payload else None

            if type.lower() == "get":
                logger.info(
                    f"Running {type.upper()} request on {url} with\nparams: {params}\nparam_location: {param_location}\npayload: {payload}"
                )
                res = requests.get(url, params=query_params, headers=headers)
            elif type.lower() == "post":
                # model didn't generated separate payload object, so we just put params as payload and hope for the best...
                data = json.dumps(payload) if payload else json.dumps(params)
                logger.info(
                    f"Running {type.upper()} request on {url} with\nparams: {params}\nparam_location: {param_location}\npayload: {data}"
                )
                res = requests.post(url, params=query_params, data=data, headers=headers)
            else:
                return f"ERROR! Unsupported request type: {type}. Only GET and POST are supported. Try again!"

            return self.process_response(res)

        except Exception as e:
            return f"ERROR! That didn't work, try modifying Action Input.\n{e}. Try again!"

    def process_response(self, res):
        logger.info(f"Request response: {res.text}")
        if res.status_code != 200:
            return f"ERROR! That didn't work, try modifying Action Input.\n{res.text}. Try again!"

        if res.text is None or len(res.text) == 0:
            return "ERROR! That didn't work, try modifying Action Input.\nEmpty response. Try again!"

        if "null" in res.text.lower() and len(res.text) < 10:
            return "ERROR! That didn't work, try modifying Action Input.\nEmpty response. Try again!"

        return truncate_str(res.text, RESPONSE_MAX_LENGTH)


def compose_tools_from_plugin(plugin: inference.PluginEntry | None) -> tuple[str, list[Tool]]:
    if not plugin:
        return "", []

    llm_plugin = prepare_plugin_for_llm(plugin.url)
    if not llm_plugin:
        return "", []

    tools = []
    request_tool = RequestsForLLM()

    def create_tool_func(endpoint, param_location):
        def func(req):
            try:
                json_obj = json.loads(req)
                request = json_obj.get("request", {})
                params = request.get("params", {})
                payload = request.get("payload", None)
            except json.JSONDecodeError:
                print("Error: Invalid JSON input")
                request, params, payload = {}, {}, None
            except Exception as e:
                print(f"Error: {e}")
                request, params, payload = {}, {}, None

            return request_tool.run(
                url=endpoint.url, params=params, param_location=param_location, type=endpoint.type, payload=payload
            )

        return func

    # Generate tool for each endpoint of the plugin
    # NOTE: This approach is a bit weird, but it is a good way to help LLM
    # to use tools, so LLM does not need to choose api server url
    # and paramter locations: query, path, body, etc. on its own.
    # LLM will only, choose what endpoint, what parameters and what values
    # to use. Modifying this part of the prompt, we can degrade or improve
    # performance of tool usage.
    for endpoint in llm_plugin["endpoints"]:
        params = "\n\n".join(
            [
                f""" name: "{param.name}",\n in: "{param.in_}",\n description: "{truncate_str(param.description, 128)}",\n schema: {param.schema_},\n required: {param.required}"""
                for param in endpoint.params
            ]
        )

        # NOTE: LangChain is using internaly {input_name} for templating
        # and some OA/ChatGPT plugins of course, can have {some_word} in theirs
        # descriptions
        params = params.replace("{", "{{").replace("}", "}}")
        payload_description = ""
        if endpoint.payload:
            try:
                payload_description = "payload: " + truncate_str(json.dumps(endpoint.payload, indent=4), 256)
                payload_description = payload_description.replace("{", "{{").replace("}", "}}")
            except Exception as e:
                logger.warning(f"Failed to convert payload to json string: {e}")

        payload_description += "" if not payload_description or payload_description.endswith("\n") else "\n"
        if len(payload_description) > 0:
            payload_description = "\n" + payload_description + "\n"

        parameters_description = f"params:\n{params}\n" if params else "\n"

        openapi_specification_title = (
            "\nOpenAPI specification\n" if len(payload_description) > 0 or len(params) > 0 else ""
        )

        param_location = endpoint.params[0].in_ if len(endpoint.params) > 0 else "query"
        tool = Tool(
            name=endpoint.operation_id,  # Could be path, e.g /api/v1/endpoint
            # but it can lead LLM to makeup some URLs
            # and problem with EP description is that
            # it can be too long for some plugins
            func=create_tool_func(endpoint, param_location),
            description=f"{openapi_specification_title}{parameters_description}{payload_description}tool description: {endpoint.summary}\n",
        )
        tools.append(tool)

    tools_string = "\n".join([f"> {tool.name}{tool.description}" for tool in tools])
    # NOTE: This can be super long for some plugins, that I tested so far.
    # and because we don't have 32k CTX size, we need to truncate it.
    plugin_description_for_model = truncate_str(llm_plugin["description_for_model"], 512)
    return (
        f"{TOOLS_PREFIX}{tools_string}\n\n{llm_plugin['name_for_model']} plugin description:\n{plugin_description_for_model}\n\n{INSTRUCTIONS}",
        tools,
    )


# TODO:
# here we will not be not truncating per token, but will be deleting messages
# from the history, and we will leave hard truncation to work.py which if
# occurs it will degrade quality of the output.
def prepare_prompt(
    input_prompt: str,
    prompt_template: PromptTemplate,
    memory: ConversationBufferMemory,
    tools_names: list[str] | None,
    current_time: str,
    language: str,
    tokenizer: transformers.PreTrainedTokenizer,
    worker_config: inference.WorkerConfig,
    action_input_format: str,
) -> tuple[ConversationBufferMemory, str]:
    max_input_length = worker_config.model_config.max_input_length

    args = {
        "input": input_prompt,
        "language": language,
        "current_time": current_time,
        "chat_history": memory.buffer,
    }

    if tools_names:
        args["tools_names"] = tools_names
        args["action_input_format"] = action_input_format

    out_prompt = prompt_template.format(**args)

    with tokenizer_lock:
        ids = tokenizer.encode(out_prompt)

    # soft truncation
    while len(ids) > max_input_length and len(memory.chat_memory.messages) > 0:
        memory.chat_memory.messages.pop(0)
        args = {
            "input": input_prompt,
            "language": language,
            "current_time": current_time,
            "chat_history": memory.buffer,
        }

        if tools_names:
            args["tools_names"] = tools_names
            args["action_input_format"] = action_input_format

        out_prompt = prompt_template.format(**args)

        with tokenizer_lock:
            ids = tokenizer.encode(out_prompt)
        logger.warning(f"Prompt too long, deleting chat history. New length: {len(ids)}")

    return memory, out_prompt
