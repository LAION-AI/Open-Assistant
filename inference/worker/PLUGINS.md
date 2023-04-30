# Plugin system for OA

This is a basic implementation of support for external augmentation and
OpenAI/ChatGPT plugins into the Open-Assistant. In the current state, this is
more of a proof-of-concept and should be considered to be used behind some
experimental flag.

## Architecture

There is now some kind of middleware between work.py(worker) and the final
prompt that is passed to the inference server for generation and streaming. That
middleware is responsible for checking if there is an enabled plugin in the
userland/UI and if so, it will take over the job of creating curated pre-prompts
for plugin usage, as well as generating subsequent calls to LLM(inner
monologues) in order to generate the final externally **augmented** prompt, that
will be passed back to the worker and next to the inference, for final LLM
generation/streaming tokens to the frontend.

## Plugins

Plugins are in essence just pretty wrappers around some kind of API-s and serve
a purpose to help LLM utilize it more precisely and reliably, so they can be
quite useful and powerful augmentation tools for Open-Assistant. Two main parts
of a plugin are the ai-plugin.json file, which is just the main descriptor of a
plugin, and the second part is OpenAPI specification of the plugin API-s.

Here is OpenAI plugins
[specification](https://platform.openai.com/docs/plugins/getting-started) that
is currently partially supported with this system.

For now, only non-authentication-based and only (**GET** request) plugins are
supported. Some of them are:

- https://www.klarna.com/.well-known/ai-plugin.json
- https://www.joinmilo.com/.well-known/ai-plugin.json

Adding support for all other request types would be quite tricky with the
current approach. It would be best to drop current “mansplaining” of the API to
LLM and just show it complete json/yaml content. But unfortunately for that to
be reliable and to work as close as current approach we would need larger
context size and a bit more capable models.

And quite a few of them can be found on this website
[plugin "store" wellknown.ai](https://www.wellknown.ai/)

One of the ideas of the plugin system is that we can have some internal OA
plugins, which will be like out-of-the-box plugins, and there could be endless
third-party community-developed plugins as well.

### Notes regarding the reliability and performance and the limitations of the plugin system

Performance can vary a lot depending on the models and plugins used. Some of
them work better some worse, but that aspect should improve as we get better and
better models. One of the biggest limitations at the moment is context size and
instruction following capabilities. And that is combated with some prompt
tricks, truncations of the plugin OpenAPI descriptions and dynamically
including/excluding parts of the prompts in the internal processing of the
subsequent generations of intermediate texts (inner monologues). More of the
limitations and possible alternatives are explained in code comments.

The current approach is somewhat hybrid I would say, and relies on the zero-shot
capabilities of a model. There will be one more branch with the plugin system
that will be a bit different approach than this one as it will be utilizing
other smaller embedding transformer models and vector stores, so we can do A/B
testing of the system alongside new OA model releases.

## Relevant files for the inference side of the plugin system

- chat_chain.py
- chat*chain_utils.py *(tweaking tools/plugin description string generation can
  help for some models)\_
- chat*chain_prompts.py *(tweaking prompts can help also)\_
