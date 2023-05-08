import datetime

import interface
import transformers
import utils
from chat_chain_prompts import (
    ASSISTANT_PREFIX,
    HUMAN_PREFIX,
    JSON_FORMAT_NO_PAYLOAD,
    JSON_FORMAT_PAYLOAD,
    OBSERVATION_SEQ,
    PREFIX,
    SUFFIX,
    THOUGHT_SEQ,
    V2_ASST_PREFIX,
    V2_PROMPTER_PREFIX,
)
from chat_chain_utils import compose_tools_from_plugins, extract_tool_and_input, prepare_prompt, use_tool
from hf_langchain_inference import HFInference
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from loguru import logger
from oasst_shared.model_configs import ModelConfig
from oasst_shared.schemas import inference
from settings import settings

# NOTE: Max depth of retries for tool usage
MAX_DEPTH = 6

# NOTE: If we want to exclude tools description from final prompt,
# to save ctx token space, but it can hurt output quality, especially if
# truncation kicks in!
# I keep switching this on/off, depending on the model used.
REMOVE_TOOLS_FROM_FINAL_PROMPT = False

current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

llm = HFInference(
    inference_server_url=settings.inference_server_url,
    max_new_tokens=512,
    stop_sequences=[],
    top_k=50,
    temperature=0.20,
    # NOTE: It seems to me like it's better without repetition_penalty for
    # llama-sft7e3 model
    seed=43,
    repetition_penalty=(1 / 0.92),  # works with good with > 0.88
)


def populate_memory(memory: ConversationBufferMemory, work_request: inference.WorkRequest) -> None:
    for message in work_request.thread.messages[:-1]:
        if message.role == "prompter" and message.state == inference.MessageState.manual and message.content:
            memory.chat_memory.add_user_message(message.content)
        elif message.role == "assistant" and message.state == inference.MessageState.complete and message.content:
            memory.chat_memory.add_ai_message(message.content)


def handle_plugin_usage(
    input_prompt: str,
    prompt_template: PromptTemplate,
    language: str,
    tools: list[Tool],
    memory: ConversationBufferMemory,
    plugins: list[inference.PluginEntry],
    worker_config: inference.WorkerConfig,
    tokenizer: transformers.PreTrainedTokenizer,
    parameters: interface.GenerateStreamParameters,
) -> tuple[str, inference.PluginsUsed]:
    execution_details = inference.PluginExecutionDetails(
        inner_monologue=[],
        final_tool_output="",
        final_prompt="",
        final_generation_assisted=False,
        error_message="",
        status="failure",
    )
    plugins_used = inference.PluginsUsed()

    if len(plugins) == 0:
        return input_prompt, plugins_used

    chain_finished = False
    achieved_depth = 0
    assisted = False
    inner_prompt = ""
    inner_monologue = []

    action_input_format = (
        JSON_FORMAT_PAYLOAD if prompt_template.template.find("payload") != -1 else JSON_FORMAT_NO_PAYLOAD
    )

    eos_token = ""
    if hasattr(tokenizer, "eos_token"):
        eos_token = tokenizer.eos_token

    tools_names = [tool.name for tool in tools]

    init_prompt = f"{input_prompt}{eos_token}{V2_ASST_PREFIX}"
    memory, init_prompt = prepare_prompt(
        init_prompt,
        prompt_template,
        memory,
        tools_names,
        current_time,
        language,
        tokenizer,
        worker_config,
        action_input_format,
    )

    # NOTE: Do not strip() any of the outputs ever, as it will degrade the
    # instruction following performance, at least with
    # `OpenAssistant/oasst-sft-6-llama-30b-epoch-1 model`

    init_prompt = utils.truncate_prompt(tokenizer, worker_config, parameters, init_prompt, True)
    chain_response = (
        llm.generate(prompts=[init_prompt], stop=[ASSISTANT_PREFIX, OBSERVATION_SEQ, f"\n{OBSERVATION_SEQ}"])
        .generations[0][0]
        .text
    )
    if chain_response is not None and chain_response != "":
        chain_response = chain_response.replace("\n\n", "\n")
        if chain_response[0] != "\n":
            chain_response = f"\n{chain_response}"

    inner_monologue.append("In: " + str(init_prompt))
    inner_monologue.append("Out: " + str(chain_response))

    # out_1 -> tool name/assistant prefix
    # out_2 -> tool input/assistant response
    out_1, out_2 = extract_tool_and_input(llm_output=chain_response, ai_prefix=ASSISTANT_PREFIX)

    # whether model decided to use Plugin or not
    assisted = False if ASSISTANT_PREFIX in out_1 else True
    chain_finished = not assisted

    all_responses = ""

    # Check if there is need to go deeper
    while not chain_finished and assisted and achieved_depth < MAX_DEPTH:
        tool_response, used_plugin_name = use_tool(out_1, out_2, tools)

        all_responses += f"{chain_response}{OBSERVATION_SEQ} {tool_response}\n"

        # Save previous chain response, that we will use for the final prompt
        prev_chain_response = chain_response

        new_prompt = f"{input_prompt}{eos_token}{V2_ASST_PREFIX}{all_responses}"
        memory, new_prompt = prepare_prompt(
            new_prompt,
            prompt_template,
            memory,
            tools_names,
            current_time,
            language,
            tokenizer,
            worker_config,
            action_input_format,
        )

        # NOTE: Do not strip() any of the outputs ever, as it will degrade the
        # instruction following performance, at least with
        # `OpenAssistant/oasst-sft-6-llama-30b-epoch-1 model`
        new_prompt = utils.truncate_prompt(tokenizer, worker_config, parameters, new_prompt, True)
        chain_response = (
            llm.generate(prompts=[new_prompt], stop=[ASSISTANT_PREFIX, OBSERVATION_SEQ, f"\n{OBSERVATION_SEQ}"])
            .generations[0][0]
            .text
        )

        if chain_response is not None and chain_response != "":
            chain_response = chain_response.replace("\n\n", "\n")
            if chain_response[0] != "\n":
                chain_response = f"\n{chain_response}"

        inner_monologue.append("In: " + str(new_prompt))
        inner_monologue.append("Out: " + str(chain_response))

        out_1, out_2 = extract_tool_and_input(llm_output=chain_response, ai_prefix=ASSISTANT_PREFIX)
        # Did model decided to use Plugin again or not?
        assisted = False if ASSISTANT_PREFIX in out_1 else True

        # NOTE: Check if tool response contains ERROR string, this is something
        # that we would like to avoid, but until models are better, we will
        # help them with this...
        # for now models, sometime decides to retry, when tool usage reports
        # error, but sometime it just ignore error...
        if tool_response.find("ERROR") != -1 and assisted is False:
            chain_response = prev_chain_response
            assisted = True

        the_plugin: inference.PluginEntry | None = None
        for plugin_ in plugins:
            if getattr(plugin_.plugin_config, "name_for_human", None) == used_plugin_name:
                the_plugin = plugin_
                break

        if isinstance(the_plugin, inference.PluginEntry) and used_plugin_name not in plugins_used.name:
            plugins_used.names.append(getattr(the_plugin.plugin_config, "name_for_human", None))
            plugins_used.trusted.append(getattr(the_plugin, "trusted", None))
            plugins_used.urls.append(getattr(the_plugin, "url", None))

        # Now LLM is done with using the plugin,
        # so we need to generate the final prompt
        if not assisted:
            chain_finished = True

            if REMOVE_TOOLS_FROM_FINAL_PROMPT:
                TEMPLATE = f"""{V2_PROMPTER_PREFIX}{PREFIX}{SUFFIX}"""
                input_variables = ["input", "chat_history", "language", "current_time"]

                prompt_template = PromptTemplate(input_variables=input_variables, template=TEMPLATE)
                tools_names = []

            final_input = f"{input_prompt}{eos_token}{V2_ASST_PREFIX}\n{all_responses}"
            memory, inner_prompt = prepare_prompt(
                final_input,
                prompt_template,
                memory,
                tools_names,
                current_time,
                language,
                tokenizer,
                worker_config,
                action_input_format,
            )

            inner_prompt = f"{inner_prompt}\n{THOUGHT_SEQ} I now know the final answer\n{ASSISTANT_PREFIX}:  "

            plugins_used.execution_details.inner_monologue = inner_monologue
            plugins_used.execution_details.final_tool_output = tool_response
            plugins_used.execution_details.final_prompt = inner_prompt
            plugins_used.execution_details.final_generation_assisted = True
            plugins_used.execution_details.achieved_depth = achieved_depth + 1
            plugins_used.execution_details.status = "success"

            return inner_prompt, plugins_used
        achieved_depth += 1

    if not plugins_used[used_plugin_name]:
        for plugin_ in plugins:
            if getattr(plugin_.plugin_config, "name_for_human", None) == used_plugin_name:
                the_plugin = plugin_
        plugins_used[used_plugin_name] = (
            inference.PluginUsed(
                name=used_plugin_name,
                url=getattr(the_plugin, "url", None),
                execution_details=execution_details,
            ),
            the_plugin,
        )
    plugin_used, the_plugin = plugins_used[used_plugin_name]

    plugin_used.name = getattr(the_plugin.plugin_config, "name_for_human", None)
    plugin_used.trusted = getattr(the_plugin, "trusted", None)
    plugin_used.url = getattr(the_plugin, "url", None)
    plugin_used.execution_details.inner_monologue += inner_monologue

    # bring back ASSISTANT_PREFIX to chain_response,
    # that was omitted with stop=[ASSISTANT_PREFIX]
    chain_response = f"{chain_response}{ASSISTANT_PREFIX}:  "

    # Return non-assisted response
    if chain_finished:
        # Malformed non-assisted LLM output
        if not out_2 or out_2 == "":
            plugin_used.execution_details.status = "failure"
            plugin_used.execution_details.error_message = "Malformed LLM output"
            return init_prompt, plugins_used

        plugin_used.execution_details.status = "success"
        return f"{init_prompt}{THOUGHT_SEQ} I now know the final answer\n{ASSISTANT_PREFIX}:  ", plugins_used
    else:
        # Max depth reached, just try to answer without using a tool
        plugin_used.execution_details.final_prompt = init_prompt
        plugin_used.execution_details.achieved_depth = achieved_depth
        plugin_used.execution_details.status = "failure"
        plugin_used.execution_details.error_message = f"Max depth reached: {MAX_DEPTH}"
        init_prompt = f"{init_prompt}{THOUGHT_SEQ} I now know the final answer\n{ASSISTANT_PREFIX}:  "
        return init_prompt, plugins_used


def handle_conversation(
    work_request: inference.WorkRequest,
    worker_config: inference.WorkerConfig,
    parameters: interface.GenerateStreamParameters,
    tokenizer: transformers.PreTrainedTokenizer,
) -> tuple[str, inference.PluginsUsed | None]:
    try:
        original_prompt = work_request.thread.messages[-1].content
        if not original_prompt:
            raise ValueError("Prompt is empty")

        language = "English"

        # Get one and only one enabled plugin
        # TODO: Add support for multiple plugins at once
        # maybe... should be explored
        plugins = list(p for p in parameters.plugins if p.enabled)

        # Compose tools from plugin, where every endpoint of plugin will become
        # one tool, and return prepared prompt with instructions
        tools_instructions_template, tools = compose_tools_from_plugins(plugins)
        plugin_enabled = len(tools) > 0

        eos_token = ""
        if hasattr(tokenizer, "eos_token"):
            eos_token = tokenizer.eos_token

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="input",
            output_key="output",
            ai_prefix=ASSISTANT_PREFIX,
            human_prefix=HUMAN_PREFIX,
        )

        populate_memory(memory, work_request)

        TEMPLATE = f"""{V2_PROMPTER_PREFIX}{PREFIX}{tools_instructions_template}{SUFFIX}"""
        input_variables = [
            "input",
            "chat_history",
            "language",
            "current_time",
            "action_input_format",
        ] + (["tools_names"] if plugin_enabled else [])

        # NOTE: Should we pass language from the UI here?
        prompt_template = PromptTemplate(input_variables=input_variables, template=TEMPLATE)

        # Run trough plugin chain. Returns PluginUsed and final prompt
        # that will be passed to worker for final completion with LLM
        # using sampling settings derived from frontend UI
        if plugin_enabled:
            return handle_plugin_usage(
                original_prompt, prompt_template, language, tools, memory, plugins, worker_config, tokenizer, parameters
            )

        # Just regular prompt template without plugin chain.
        # Here is prompt in format of a template, that includes some
        # external/ "realtime" data, such as current date&time and language
        # that can be passed from frontend here.
        action_input_format = (
            JSON_FORMAT_PAYLOAD if prompt_template.template.find("payload") != -1 else JSON_FORMAT_NO_PAYLOAD
        )
        input = f"{original_prompt}{eos_token}{V2_ASST_PREFIX}"
        memory, init_prompt = prepare_prompt(
            input, prompt_template, memory, None, current_time, language, tokenizer, worker_config, action_input_format
        )
        return init_prompt, None

    except Exception as e:
        logger.error(f"Error while handling conversation: {e}")
        return "", None


# NOTE: Only for local DEV and prompt "engineering"
# some of the plugins that can be used for testing:
# - https://www.klarna.com/.well-known/ai-plugin.json
# - https://nla.zapier.com/.well-known/ai-plugin.json (this one is behind auth)
# - https://chat-calculator-plugin.supportmirage.repl.co/.well-known/ai-plugin.json (error responses seems to be html)
# - https://www.joinmilo.com/.well-known/ai-plugin.json (works quite well, but
#   is very simple, so it's not very useful for testing)
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
                        content="Hello, my name is Open Assisstant, how i can help you today?",
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
