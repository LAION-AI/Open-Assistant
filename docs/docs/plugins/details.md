# Plugins Technical Details

OpenAssistant incorporates a basic implementation of support for external
augmentation using AI plugins of the OpenAI spec. In the current state, this is
more of a proof-of-concept and should be considered experimental.

## Architecture

There is now middleware between `work.py` (in the worker) and the final prompt
that is passed to the inference model server for generation. That middleware is
responsible for checking if there is an enabled plugin in the UI. If so, it will
add curated pre-prompts for plugin usage and generate subsequent calls to the
LLM (inner monologues) to generate the final externally **augmented** prompt,
that will be passed back to the inference model server, for final LLM generation
and streaming of tokens to the frontend.

## Plugins

Plugins are in essence just wrappers around APIs to help LLM utilize an API more
precisely and reliably. They can be quite useful and powerful augmentation tools
for OpenAssistant. The two main parts of a plugin are the `ai-plugin.json` file,
which is just the main descriptor of a plugin, and the OpenAPI specification of
the plugin APIs.

Here is the OpenAI plugin
[specification](https://platform.openai.com/docs/plugins/getting-started) that
is currently _partially_ supported by OpenAssistant. Instructions for creating
and hosting a plugin as well as a template for basic plugins can be found
[here](https://github.com/someone13574/oasst-plugin-template).

For now, only non-authentication-based and only (**GET** request) plugins are
supported. Some of them are:

- https://www.klarna.com/.well-known/ai-plugin.json
- https://www.joinmilo.com/.well-known/ai-plugin.json

And quite a few of them can be found on the
[plugin "store" at wellknown.ai](https://www.wellknown.ai/)

Adding support for all other request types is tricky with the current approach.
It would be best to drop current prompts explaining in-depth the API to the LLM
and instead just show it complete JSON/YAML content. But for that to work as
well as the current approach we would need larger context size and more capable
models, which are still in development.

We provide a few official OA plugins, and any community member can develop a
plugin.

### Notes on reliability, performance, and limitations of the system

- Performance can vary a lot depending on the models and plugins used.

- Performance and consistency should improve as we get better and better models.
  One of the biggest limitations at the moment is context size and instruction
  following capabilities.

- We combat model limitations with prompt tricks, truncations of plugin OpenAPI
  descriptions and dynamically including/excluding parts of prompts in internal
  processing of subsequent generations of intermediate texts (inner monologues).

- The current approach is somewhat hybrid and relies on the zero-shot
  capabilities of a model.

## Relevant files for the inference side of the plugin system

- chat_chain.py
- chat*chain_utils.py *(tweaking tools/plugin description string generation can
  help for some models)\_
- chat*chain_prompts.py *(tweaking prompts can help also)\_
