"""All user-facing messages and embeds."""

from datetime import datetime

import hikari
from oasst_shared.schemas import protocol as protocol_schema

NUMBER_EMOJIS = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":ten:"]
NL = "\n"

###
# Reusable 'components'
###


def _h1(text: str) -> str:
    return f"\n:small_blue_diamond: __**{text}**__ :small_blue_diamond:"


def _h2(text: str) -> str:
    return f"__**{text}**__"


def _h3(text: str) -> str:
    return f"__{text}__"


def _writing_prompt(text: str) -> str:
    return f":pencil: _{text}_"


def _ranking_prompt(text: str) -> str:
    return f":trophy: _{text}_"


def _response_prompt(text: str) -> str:
    return f":speech_balloon: _{text}_"


def _summarize_prompt(text: str) -> str:
    return f":notepad_spiral: _{text}_"


def _user(text: str | None) -> str:
    return f"""\
:person_red_hair: {_h3("User")}:{f"{NL}> **{text}**" if text is not None else ""}
"""


def _assistant(text: str | None) -> str:
    return f"""\
:robot: {_h3("Assistant")}:{f"{NL}> {text}" if text is not None else ""}
"""


def _make_ordered_list(items: list[str]) -> list[str]:
    return [f"{num} {item}" for num, item in zip(NUMBER_EMOJIS, items)]


def _ordered_list(items: list[str]) -> str:
    return "\n\n".join(_make_ordered_list(items))


def _conversation(conv: protocol_schema.Conversation) -> str:
    return "\n".join([_assistant(msg.text) if msg.is_assistant else _user(msg.text) for msg in conv.messages])


def _hint(hint: str | None) -> str:
    return f"{NL}Hint: {hint}" if hint else ""


###
# Messages
###


def initial_prompt_message(task: protocol_schema.InitialPromptTask) -> str:
    """Creates the message that gets sent to users when they request an `initial_prompt` task."""
    return f"""\

{_h1("INITIAL PROMPT")}


{_writing_prompt("Please provide an initial prompt to the assistant.")}
{_hint(task.hint)}
"""


def rank_initial_prompts_message(task: protocol_schema.RankInitialPromptsTask) -> str:
    """Creates the message that gets sent to users when they request a `rank_initial_prompts` task."""
    return f"""\

{_h1("RANK INITIAL PROMPTS")}


{_ordered_list(task.prompts)}

{_ranking_prompt("Reply with the numbers of best to worst prompts separated by commas (example: '4,1,3,2')")}
"""


def rank_prompter_reply_message(task: protocol_schema.RankPrompterRepliesTask) -> str:
    """Creates the message that gets sent to users when they request a `rank_prompter_replies` task."""
    return f"""\

{_h1("RANK PROMPTER REPLIES")}


{_conversation(task.conversation)}
{_user(None)}
{_ordered_list(task.replies)}

{_ranking_prompt("Reply with the numbers of best to worst replies separated by commas (example: '4,1,3,2')")}
"""


def rank_assistant_reply_message(task: protocol_schema.RankAssistantRepliesTask) -> str:
    """Creates the message that gets sent to users when they request a `rank_assistant_replies` task."""
    return f"""\

{_h1("RANK ASSISTANT REPLIES")}


{_conversation(task.conversation)}
{_assistant(None)}
{_ordered_list(task.replies)}

{_ranking_prompt("Reply with the numbers of best to worst replies separated by commas (example: '4,1,3,2')")}
"""


def prompter_reply_message(task: protocol_schema.PrompterReplyTask) -> str:
    """Creates the message that gets sent to users when they request a `prompter_reply` task."""
    return f"""\

{_h1("PROMPTER REPLY")}


{_conversation(task.conversation)}
{_hint(task.hint)}

{_response_prompt("Please provide a reply to the assistant.")}
"""


def assistant_reply_message(task: protocol_schema.AssistantReplyTask) -> str:
    """Creates the message that gets sent to users when they request a `assistant_reply` task."""
    return f"""\
{_h1("ASSISTANT REPLY")}


{_conversation(task.conversation)}

{_response_prompt("Please provide an assistant reply to the prompter.")}
"""


def confirm_text_response_message(content: str) -> str:
    return f"""\
{_h2("CONFIRM RESPONSE")}

> {content}
"""


def confirm_ranking_response_message(content: str, items: list[str]) -> str:
    user_rankings = [int(r) for r in content.replace(" ", "").split(",")]
    original_list = _make_ordered_list(items)
    user_ranked_list = "\n\n".join([original_list[r - 1] for r in user_rankings])

    return f"""\
{_h2("CONFIRM RESPONSE")}

{user_ranked_list}
"""


###
# Embeds
###


def task_complete_embed(task: protocol_schema.Task, mention: str) -> hikari.Embed:
    return (
        hikari.Embed(
            title="Task Completion",
            description=f"`{task.type}` completed by {mention}",
            color=hikari.Color(0x00FF00),
            timestamp=datetime.now().astimezone(),
        )
        .add_field("Total Tasks", "0", inline=True)
        .add_field("Server Ranking", "0/0", inline=True)
        .add_field("Global Ranking", "0/0", inline=True)
        .set_footer(f"Task ID: {task.id}")
    )


def invalid_user_input_embed(error_message: str) -> hikari.Embed:
    return hikari.Embed(
        title="Invalid User Input",
        description=error_message,
        color=hikari.Color(0xFF0000),
        timestamp=datetime.now().astimezone(),
    )


def plain_embed(text: str) -> hikari.Embed:
    return hikari.Embed(color=0x36393F, description=text)
