"""All user-facing messages and embeds.

When sending a conversation
- The function will return a list of strings
    - use asyncio.gather to send all messages

-
"""

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


def _label_prompt(text: str, mandatory_label: list[str] | None, valid_labels: list[str]) -> str:
    return f""":question: _{text}_
Mandatory labels: {", ".join(mandatory_label) if mandatory_label is not None else "None"}
Valid labels: {", ".join(valid_labels)}
"""


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


def _make_ordered_list(items: list[protocol_schema.ConversationMessage]) -> list[str]:
    return [f"{num} {item.text}" for num, item in zip(NUMBER_EMOJIS, items)]


def _ordered_list(items: list[protocol_schema.ConversationMessage]) -> str:
    return "\n\n".join(_make_ordered_list(items))


def _conversation(conv: protocol_schema.Conversation) -> list[str]:
    # return "\n".join([_assistant(msg.text) if msg.is_assistant else _user(msg.text) for msg in conv.messages])
    messages = map(
        lambda m: f"""\
:robot: __Assistant__:
{m.text}
"""
        if m.is_assistant
        else f"""\
:person_red_hair: __User__:
{m.text}
""",
        conv.messages,
    )
    return list(messages)


def _li(text: str) -> str:
    return f":small_blue_diamond: {text}"


###
# Messages
###


def initial_prompt_messages(task: protocol_schema.InitialPromptTask) -> list[str]:
    """Creates the message that gets sent to users when they request an `initial_prompt` task."""
    return [
        f"""\

:small_blue_diamond: __**INITIAL PROMPT**__ :small_blue_diamond:


:pencil: _Please provide an initial prompt to the assistant._{f"{NL}Hint: {task.hint}" if task.hint else ""}
"""
    ]


def rank_initial_prompts_messages(task: protocol_schema.RankInitialPromptsTask) -> list[str]:
    """Creates the message that gets sent to users when they request a `rank_initial_prompts` task."""
    return [
        f"""\

:small_blue_diamond: __**RANK INITIAL PROMPTS**__ :small_blue_diamond:


{_ordered_list(task.prompt_messages)}

:trophy: _Reply with the numbers of best to worst prompts separated by commas (example: '4,1,3,2')_
"""
    ]


def rank_prompter_reply_messages(task: protocol_schema.RankPrompterRepliesTask) -> list[str]:
    """Creates the message that gets sent to users when they request a `rank_prompter_replies` task."""
    return [
        """\

:small_blue_diamond: __**RANK PROMPTER REPLIES**__ :small_blue_diamond:

""",
        *_conversation(task.conversation),
        f""":person_red_hair: __User__:
{_ordered_list(task.reply_messages)}

:trophy: _Reply with the numbers of best to worst replies separated by commas (example: '4,1,3,2')_
""",
    ]


def rank_assistant_reply_message(task: protocol_schema.RankAssistantRepliesTask) -> list[str]:
    """Creates the message that gets sent to users when they request a `rank_assistant_replies` task."""
    return [
        """\

:small_blue_diamond: __**RANK ASSISTANT REPLIES**__ :small_blue_diamond:

""",
        *_conversation(task.conversation),
        f""":robot: __Assistant__:,
{_ordered_list(task.reply_messages)}
:trophy: _Reply with the numbers of best to worst replies separated by commas (example: '4,1,3,2')_
""",
    ]


def rank_conversation_reply_messages(task: protocol_schema.RankConversationRepliesTask) -> list[str]:
    """Creates the message that gets sent to users when they request a `rank_conversation_replies` task."""
    return [
        """\

:small_blue_diamond: __**RANK CONVERSATION REPLIES**__ :small_blue_diamond:

""",
        *_conversation(task.conversation),
        f""":person_red_hair: __User__:
{_ordered_list(task.reply_messages)}
""",
    ]


def label_initial_prompt_message(task: protocol_schema.LabelInitialPromptTask) -> str:
    """Creates the message that gets sent to users when they request a `label_initial_prompt` task."""
    return f"""\

{_h1("LABEL INITIAL PROMPT")}


{task.prompt}

{_label_prompt("Reply with labels for the prompt separated by commas (example: 'profanity,misleading')", task.mandatory_labels, task.valid_labels)}
"""


def label_prompter_reply_messages(task: protocol_schema.LabelPrompterReplyTask) -> list[str]:
    """Creates the message that gets sent to users when they request a `label_prompter_reply` task."""
    return [
        f"""\

{_h1("LABEL PROMPTER REPLY")}


""",
        *_conversation(task.conversation),
        f"""{_user(None)}
{task.reply}

{_label_prompt("Reply with labels for the reply separated by commas (example: 'profanity,misleading')", task.mandatory_labels, task.valid_labels)}
""",
    ]


def label_assistant_reply_messages(task: protocol_schema.LabelAssistantReplyTask) -> list[str]:
    """Creates the message that gets sent to users when they request a `label_assistant_reply` task."""
    return [
        f"""\

{_h1("LABEL ASSISTANT REPLY")}


""",
        *_conversation(task.conversation),
        f"""
{_assistant(None)}
{task.reply}

{_label_prompt("Reply with labels for the reply separated by commas (example: 'profanity,misleading')", task.mandatory_labels, task.valid_labels)}
""",
    ]


def prompter_reply_messages(task: protocol_schema.PrompterReplyTask) -> list[str]:
    """Creates the message that gets sent to users when they request a `prompter_reply` task."""
    return [
        """\
:small_blue_diamond: __**PROMPTER REPLY**__ :small_blue_diamond:

""",
        *_conversation(task.conversation),
        f"""{f"{NL}Hint: {task.hint}" if task.hint else ""}

:speech_balloon: _Please provide a reply to the assistant._
""",
    ]


# def prompter_reply_messages2(task: protocol_schema.PrompterReplyTask) -> list[str]:
#     """Creates the message that gets sent to users when they request a `prompter_reply` task."""
#     return [
#         message_templates.render("title.msg", "PROMPTER REPLY"),
#         *[message_templates.render("conversation_message.msg", conv) for conv in task.conversation],
#         message_templates.render("prompter_reply_task.msg", task.hint),
#     ]


def assistant_reply_messages(task: protocol_schema.AssistantReplyTask) -> list[str]:
    """Creates the message that gets sent to users when they request a `assistant_reply` task."""
    return [
        """\
:small_blue_diamond: __**ASSISTANT REPLY**__ :small_blue_diamond:

""",
        *_conversation(task.conversation),
        """\

:speech_balloon: _Please provide a reply to the user as the assistant._
""",
    ]


def confirm_text_response_message(content: str) -> str:
    return f"""\
{_h2("CONFIRM RESPONSE")}

> {content}
"""


def confirm_ranking_response_message(content: str, items: list[protocol_schema.ConversationMessage]) -> str:
    user_rankings = [int(r) for r in content.replace(" ", "").split(",")]
    original_list = _make_ordered_list(items)
    user_ranked_list = "\n\n".join([original_list[r - 1] for r in user_rankings])

    return f"""\
{_h2("CONFIRM RESPONSE")}

{user_ranked_list}
"""


def help_message(can_manage_guild: bool, is_dev: bool) -> str:
    """The /help command message."""
    content = f"""\
{_h1("HELP")}

{_li("**`/help`**")}
Show this message.

{_li("**`/work [type]`**")}
Start a new task.
**`[type]`**:
The type of task to start. If not provided, a random task will be selected. The different types are
:small_orange_diamond: `random`: A random task type
:small_orange_diamond: ~~`summarize_story`~~ (coming soon)
:small_orange_diamond: ~~`rate_summary`~~ (coming soon)
:small_orange_diamond: `initial_prompt`: Ask the assistant something
:small_orange_diamond: `prompter_reply`: Reply to the assistant
:small_orange_diamond: `assistant_reply`: Reply to the user
:small_orange_diamond: `rank_initial_prompts`: Rank some initial prompts
:small_orange_diamond: `rank_prompter_replies`: Rank some prompter replies
:small_orange_diamond: `rank_assistant_replies`: Rank some assistant replies

To learn how to complete tasks, run `/tutorial`.
"""
    if can_manage_guild:
        content += f"""\

{_li("**`/settings log_channel <channel>`**")}
Set the channel that the bot logs completed task messages in.
**`<channel>`**: The channel to log completed tasks in. The bot needs to be able to send messages in this channel.

{_li("**`/settings get`**")}
Get the current settings.
"""
    if is_dev:
        content += f"""\

{_li("**`/reload [plugin]`**")}
Hot-reload a plugin. Only code *inside* of function bodies will be updated.
Any changes to __function signatures__, __other files__, __decorators__, or __imports__ will require a restart.
**`[plugin]`**:
The plugin to hot-reload. If no plugin is provided, all plugins are hot-reload.
"""
    return content


def tutorial_message() -> str:
    """The /tutorial command message."""
    # TODO: Finish message
    return f"""\
{_h1("TUTORIAL")}
"""


def confirm_label_response_message(content: str) -> str:
    user_labels = content.lower().replace(" ", "").split(",")
    user_labels_str = ", ".join(user_labels)

    return f"""\
{_h2("CONFIRM RESPONSE")}

{user_labels_str}
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
