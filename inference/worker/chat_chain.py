import datetime

import interface
import transformers
import utils
import websocket
from chat_chain_prompts import (
    ASSISTANT_PREFIX,
    CUSTOM_INSTRUCTIONS_PREFIX,
    HUMAN_PREFIX,
    JSON_FORMAT_NO_PAYLOAD,
    JSON_FORMAT_PAYLOAD,
    OBSERVATION_SEQ,
    PREFIX,
    SUFFIX,
    THOUGHT_SEQ,
)
from chat_chain_utils import compose_tools_from_plugin, extract_tool_and_input, prepare_prompt, use_tool
from hf_langchain_inference import HFInference
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from loguru import logger
from oasst_shared.model_configs import ModelConfig
from oasst_shared.schemas import inference
from settings import settings
from utils import special_tokens

# Exclude tools description from final prompt. Saves ctx space but can hurt output
# quality especially if truncation kicks in. Dependent on model used
REMOVE_TOOLS_FROM_FINAL_PROMPT = False

llm = HFInference(
    inference_server_url=settings.inference_server_url,
    max_new_tokens=512,
    stop_sequences=[],
    top_k=50,
    temperature=0.20,
    seed=43,
    repetition_penalty=(1 / 0.92),  # Best with > 0.88
)


class PromptedLLM:
    """
    Handles calls to an LLM via LangChain with a prompt template and memory.
    """

    def __init__(
        self,
        tokenizer: transformers.PreTrainedTokenizer,
        worker_config: inference.WorkerConfig,
        parameters: interface.GenerateStreamParameters,
        prompt_template: PromptTemplate,
        memory: ConversationBufferMemory,
        tool_names: list[str],
        language: str,
        action_input_format: str,
        custom_instructions: str = "",
    ):
        self.tokenizer = tokenizer
        self.worker_config = worker_config
        self.parameters = parameters
        self.prompt_template = prompt_template
        self.memory = memory
        self.tool_names = tool_names
        self.language = language
        self.action_input_format = action_input_format
        self.current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.custom_instructions = custom_instructions

    def call(self, prompt: str) -> tuple[str, str]:
        """Prepares and truncates prompt, calls LLM, returns used prompt and response."""
        prompt = prepare_prompt(
            prompt,
            self.prompt_template,
            self.memory,
            self.tool_names,
            self.current_time,
            self.language,
            self.tokenizer,
            self.worker_config,
            self.action_input_format,
            self.custom_instructions,
        )

        # We do not strip() outputs as it seems to degrade instruction-following abilities of the model
        prompt = utils.truncate_prompt(self.tokenizer, self.worker_config, self.parameters, prompt, True)

        response = (
            llm.generate(prompts=[prompt], stop=[ASSISTANT_PREFIX, OBSERVATION_SEQ, f"\n{OBSERVATION_SEQ}"])
            .generations[0][0]
            .text
        )

        if response:
            response = response.replace("\n\n", "\n")
            if response[0] != "\n":
                response = f"\n{response}"

        return prompt, response


def handle_plugin_usage(
    input_prompt: str,
    prompt_template: PromptTemplate,
    language: str,
    memory: ConversationBufferMemory,
    worker_config: inference.WorkerConfig,
    tokenizer: transformers.PreTrainedTokenizer,
    parameters: interface.GenerateStreamParameters,
    tools: list[Tool],
    plugin: inference.PluginEntry | None,
    plugin_max_depth: int,
    ws: websocket.WebSocket,
    work_request_id: str,
    custom_instructions: str = "",
) -> tuple[str, inference.PluginUsed]:
    execution_details = inference.PluginExecutionDetails(
        inner_monologue=[],
        final_tool_output="",
        final_prompt="",
        final_generation_assisted=False,
        error_message="",
        status="failure",
    )
    plugin_used = inference.PluginUsed(
        name=None,
        url=None,
        execution_details=execution_details,
    )

    if plugin is None:
        return input_prompt, plugin_used

    chain_finished = False
    achieved_depth = 0
    assisted = False
    inner_prompt = ""
    inner_monologue = []

    action_input_format = (
        JSON_FORMAT_PAYLOAD if prompt_template.template.find("payload") != -1 else JSON_FORMAT_NO_PAYLOAD
    )
    eos_token = ""
    if special_tokens["end"]:
        eos_token = special_tokens["end"]
    elif hasattr(tokenizer, "eos_token"):
        eos_token = tokenizer.eos_token
    tool_names = [tool.name for tool in tools]

    chain = PromptedLLM(
        tokenizer,
        worker_config,
        parameters,
        prompt_template,
        memory,
        tool_names,
        language,
        action_input_format,
        custom_instructions,
    )

    # send "thinking..." intermediate step to UI (This will discard queue position 0) immediately
    utils.send_response(
        ws,
        inference.PluginIntermediateResponse(
            request_id=work_request_id,
            current_plugin_thought="thinking...",
            current_plugin_action_taken="",
            current_plugin_action_input="",
            current_plugin_action_response="",
        ),
    )

    init_prompt = f"{input_prompt}{eos_token}{special_tokens['assistant']}"
    init_prompt, chain_response = chain.call(init_prompt)

    inner_monologue.append("In: " + str(init_prompt))
    inner_monologue.append("Out: " + str(chain_response))

    current_action_thought = ""
    if THOUGHT_SEQ in chain_response:
        current_action_thought = chain_response.split(THOUGHT_SEQ)[1].split("\n")[0]

    # Tool name/assistant prefix, Tool input/assistant response
    prefix, response = extract_tool_and_input(llm_output=chain_response, ai_prefix=ASSISTANT_PREFIX)
    assisted = False if ASSISTANT_PREFIX in prefix else True
    chain_finished = not assisted

    if assisted:
        # model decided to use a tool, so send that thought to the client
        utils.send_response(
            ws,
            inference.PluginIntermediateResponse(
                request_id=work_request_id,
                current_plugin_thought=current_action_thought,
                current_plugin_action_taken=prefix,
                current_plugin_action_input=chain_response,
                current_plugin_action_response=response,
            ),
        )

    while not chain_finished and assisted and achieved_depth < plugin_max_depth:
        tool_response = use_tool(prefix, response, tools)

        # Save previous chain response for use in final prompt
        prev_chain_response = chain_response
        new_prompt = (
            f"{input_prompt}{eos_token}{special_tokens['assistant']}{chain_response}{OBSERVATION_SEQ} {tool_response}"
        )

        new_prompt, chain_response = chain.call(new_prompt)

        inner_monologue.append("In: " + str(new_prompt))
        inner_monologue.append("Out: " + str(chain_response))

        current_action_thought = ""
        if THOUGHT_SEQ in chain_response:
            current_action_thought = chain_response.split(THOUGHT_SEQ)[1].split("\n")[0]

        # Send deep plugin intermediate steps to UI
        utils.send_response(
            ws,
            inference.PluginIntermediateResponse(
                request_id=work_request_id,
                current_plugin_thought=current_action_thought,
                current_plugin_action_taken=prefix,
                current_plugin_action_input=chain_response,
                current_plugin_action_response=response,
            ),
        )

        prefix, response = extract_tool_and_input(llm_output=chain_response, ai_prefix=ASSISTANT_PREFIX)
        assisted = False if ASSISTANT_PREFIX in prefix else True

        # Check if tool response contains ERROR string and force retry
        # Current models sometimes decide to retry on error but sometimes just ignore
        if tool_response.find("ERROR") != -1 and assisted is False:
            chain_response = prev_chain_response
            assisted = True

        if not assisted:
            chain_finished = True

            if REMOVE_TOOLS_FROM_FINAL_PROMPT:
                TEMPLATE = f"""{special_tokens['prompter']}{PREFIX}{SUFFIX}"""
                input_variables = ["input", "chat_history", "language", "current_time"]

                prompt_template = PromptTemplate(input_variables=input_variables, template=TEMPLATE)
                tool_names = None

            final_input = f"{input_prompt}{eos_token}{special_tokens['assistant']}\n{prev_chain_response}{OBSERVATION_SEQ} {tool_response}"
            inner_prompt = prepare_prompt(
                final_input,
                prompt_template,
                memory,
                tool_names,
                chain.current_time,
                language,
                tokenizer,
                worker_config,
                action_input_format,
                custom_instructions,
            )

            inner_prompt = f"{inner_prompt}\n{THOUGHT_SEQ} I now know the final answer\n{ASSISTANT_PREFIX}:  "

            plugin_used.execution_details.inner_monologue = inner_monologue
            plugin_used.execution_details.final_tool_output = tool_response
            plugin_used.execution_details.final_prompt = inner_prompt
            plugin_used.execution_details.final_generation_assisted = True
            plugin_used.execution_details.achieved_depth = achieved_depth + 1
            plugin_used.execution_details.status = "success"
            plugin_used.name = plugin.plugin_config.name_for_human
            plugin_used.trusted = plugin.trusted
            plugin_used.url = plugin.url

            return inner_prompt, plugin_used
        achieved_depth += 1

    plugin_used.name = plugin.plugin_config.name_for_human
    plugin_used.trusted = plugin.trusted
    plugin_used.url = plugin.url
    plugin_used.execution_details.inner_monologue = inner_monologue

    # Re-add ASSISTANT_PREFIX to chain_response, omitted with stop=[ASSISTANT_PREFIX]
    chain_response = f"{chain_response}{ASSISTANT_PREFIX}:  "

    if chain_finished:
        if not response:
            # Malformed non-assisted LLM output
            plugin_used.execution_details.status = "failure"
            plugin_used.execution_details.error_message = "Malformed LLM output"
            return init_prompt, plugin_used

        plugin_used.execution_details.status = "success"
        return f"{init_prompt}{THOUGHT_SEQ} I now know the final answer\n{ASSISTANT_PREFIX}:  ", plugin_used
    else:
        # Max depth reached, answer without tool
        plugin_used.execution_details.final_prompt = init_prompt
        plugin_used.execution_details.achieved_depth = achieved_depth
        plugin_used.execution_details.status = "failure"
        plugin_used.execution_details.error_message = f"Max depth reached: {plugin_max_depth}"
        init_prompt = f"{init_prompt}{THOUGHT_SEQ} I now know the final answer\n{ASSISTANT_PREFIX}:  "
        return init_prompt, plugin_used


def handle_standard_usage(
    original_prompt: str,
    prompt_template: PromptTemplate,
    language: str,
    memory: ConversationBufferMemory,
    worker_config: inference.WorkerConfig,
    tokenizer: transformers.PreTrainedTokenizer,
    custom_instructions: str = "",
):
    eos_token = ""
    if special_tokens["end"]:
        eos_token = special_tokens["end"]
    elif hasattr(tokenizer, "eos_token"):
        eos_token = tokenizer.eos_token
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Non-plugin prompt template can include some external data e.g. datetime, language
    action_input_format = (
        JSON_FORMAT_PAYLOAD if prompt_template.template.find("payload") != -1 else JSON_FORMAT_NO_PAYLOAD
    )
    input = f"{original_prompt}{eos_token}{special_tokens['assistant']}"
    init_prompt = prepare_prompt(
        input,
        prompt_template,
        memory,
        None,
        current_time,
        language,
        tokenizer,
        worker_config,
        action_input_format,
        custom_instructions,
    )
    return init_prompt, None


def build_memory(work_request: inference.WorkRequest) -> ConversationBufferMemory:
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="input",
        output_key="output",
        ai_prefix=ASSISTANT_PREFIX,
        human_prefix=HUMAN_PREFIX,
    )

    for message in work_request.thread.messages[:-1]:
        if message.role == "prompter" and message.state == inference.MessageState.manual and message.content:
            memory.chat_memory.add_user_message(message.content)
        elif message.role == "assistant" and message.state == inference.MessageState.complete and message.content:
            memory.chat_memory.add_ai_message(message.content)

    return memory


def handle_conversation(
    work_request: inference.WorkRequest,
    worker_config: inference.WorkerConfig,
    parameters: interface.GenerateStreamParameters,
    tokenizer: transformers.PreTrainedTokenizer,
    ws: websocket.WebSocket,
) -> tuple[str, inference.PluginUsed | None]:
    try:
        original_prompt = work_request.thread.messages[-1].content
        if not original_prompt:
            raise ValueError("Prompt is empty")

        language = "English"
        plugin = next((p for p in parameters.plugins if p.enabled), None)

        tools_instructions_template, tools = compose_tools_from_plugin(plugin)
        plugin_enabled = len(tools) > 0
        memory: ConversationBufferMemory = build_memory(work_request)

        TEMPLATE = f"""{special_tokens['prompter']}{PREFIX}{tools_instructions_template}{SUFFIX}"""
        input_variables = [
            "input",
            "chat_history",
            "language",
            "current_time",
            "action_input_format",
            "custom_instructions",
        ] + (["tools_names"] if plugin_enabled else [])

        # TODO: Consider passing language from the UI here
        prompt_template = PromptTemplate(input_variables=input_variables, template=TEMPLATE)

        custom_instructions = (
            f"""\n{CUSTOM_INSTRUCTIONS_PREFIX.format(
            user_profile=work_request.parameters.user_profile,
            user_response_instructions=work_request.parameters.user_response_instructions,
        )}"""
            if work_request.parameters.user_response_instructions or work_request.parameters.user_profile
            else ""
        )

        if plugin_enabled:
            return handle_plugin_usage(
                original_prompt,
                prompt_template,
                language,
                memory,
                worker_config,
                tokenizer,
                parameters,
                tools,
                plugin,
                work_request.parameters.plugin_max_depth,
                ws,
                work_request.id,
                custom_instructions,
            )

        return handle_standard_usage(
            original_prompt, prompt_template, language, memory, worker_config, tokenizer, custom_instructions
        )
    except Exception as e:
        logger.error(f"Error while handling conversation: {e}")
        return "", None


if __name__ == "__main__":
    plugin = inference.PluginEntry(
        enabled=True,
        url="http://localhost:8082/ai-plugin.json",
        plugin_config=inference.PluginConfig(
            name_for_human="Local dev plugin",
            name_for_model="Local dev plugin",
            description_for_model="Local dev plugin",
            description_for_human="Local dev plugin",
            schema_version="0.0.1",
            api={"type": "openapi", "url": "http://localhost:8082/openapi.json", "has_user_authentication": False},
            auth={"type": "none"},
        ),
    )

    model_config = ModelConfig(
        model_id="decapoda-research/llama-30b-hf",
        max_input_length=1024,
        max_total_length=2048,
    )

    work_parameters = inference.WorkParameters(model_config=model_config, do_sample=True, seed=42, plugins=[plugin])
    parameters = interface.GenerateStreamParameters.from_work_parameters(work_parameters)

    worker_config = inference.WorkerConfig(
        model_config=model_config,
        model_id=model_config.model_id,
        max_input_length=model_config.max_input_length,
        max_total_length=model_config.max_total_length,
        do_sample=True,
        seed=42,
    )

    while True:
        input_ = input("Enter your input: ")
        if input == "exit":
            break
        work_request = inference.WorkRequest(
            request_type="work",
            parameters=work_parameters,
            thread=inference.Thread(
                messages=[
                    inference.MessageRead(
                        id="1",
                        chat_id="1",
                        parent_id=None,
                        content="Hi, what is your name?",
                        created_at=datetime.datetime.now(),
                        role="prompter",
                        state=inference.MessageState.complete,
                        score=0,
                        work_parameters=work_parameters,
                        reports=[],
                    ),
                    inference.MessageRead(
                        id="1",
                        chat_id="1",
                        parent_id=None,
                        content="Hello, my name is Open Assistant, how i can help you today?",
                        created_at=datetime.datetime.now(),
                        role="assistant",
                        state=inference.MessageState.complete,
                        score=0,
                        work_parameters=work_parameters,
                        reports=[],
                    ),
                    inference.MessageRead(
                        id="1",
                        chat_id="1",
                        parent_id=None,
                        content=input_,
                        created_at=datetime.datetime.now(),
                        role="prompter",
                        state=inference.MessageState.in_progress,
                        score=0,
                        work_parameters=work_parameters,
                        reports=[],
                    ),
                ]
            ),
        )
        tokenizer = transformers.LlamaTokenizer.from_pretrained(model_config.model_id)
        final_out, used_plugin = handle_conversation(work_request, worker_config, parameters, tokenizer)
        print(f"Used_plugin: {used_plugin}")
        print(final_out)
