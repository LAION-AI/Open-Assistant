# -*- coding: utf-8 -*-
# TODO: Convert file to markdown
# -*- coding: utf-8 -*-
"""Example plugin for reference.

Because this file starts with an `_`, it cannot be loaded by the bot.
To see the example plugin in action, rename this file to `example.py`.
"""
import asyncio

import hikari
import lightbulb
import lightbulb.decorators
import miru
from miru.ext import nav

plugin = lightbulb.Plugin("ExamplePlugin")

# To add checks to a plugin, you can use the `@plugin.check` decorator
# or the `plugin.add_check` method. Lightbulb has some built-in checks.
# The check will be called before any command in the plugin is called.
plugin.add_checks(lightbulb.guild_only)


# To create a slash command, use the template below
@plugin.command
@lightbulb.command("example", "Example command.")
@lightbulb.implements(lightbulb.SlashCommand)
async def example(ctx: lightbulb.SlashContext):
    """Example command."""
    # To send a message, use the `respond` method on `ctx`.
    # !!! Be sure to use `await` when calling `respond` !!!
    await ctx.respond("Hello, world!")


# To add arguments, use the `@lightbulb.option` decorator.
@plugin.command
@lightbulb.option(
    "name",  # The name of the option. This is what you will use to access the value in `ctx.options.name`
    "Your name.",  # The description of the option. This will be shown in the slash command menu.
    # Whether or not the option is required.
    # If `required` is `True`, the user will not be able to use the command without providing a value for this option.
    required=False,
    default=None,  # The default value for the option. If `required` is `True`, this will be ignored.
    type=str | None,  # The type of the option. This is used to convert the value to the correct type.
    # https://hikari-lightbulb.readthedocs.io/en/latest/guides/commands.html#converters-and-slash-command-option-types
)
@lightbulb.option(
    "age",
    "Your age.",
    type=int,
    # These are enforced on the client side, so the user won't be able to enter a value outside of the range.
    min_value=0,
    max_value=100,
)
@lightbulb.option(
    "gender",
    "Your gender.",
    # You can also use `choices` to limit the user to a specific set of values.
    # This can be a list of `str`, `int, or `float`
    # choices=["Male", "Female", "Other"],
    # or a list of `hikari.CommandChoice` objects to have separate option names and values
    choices=[
        hikari.CommandChoice(name="male", value="M"),
        hikari.CommandChoice(name="female", value="F"),
        hikari.CommandChoice(name="other", value="Other"),
    ],
    type=str,
)
@lightbulb.command("args_example", "Example command with arguments.")
@lightbulb.implements(lightbulb.SlashCommand)
async def args_example(ctx: lightbulb.SlashContext):
    """Example command with arguments."""
    name: str | None = ctx.options.name
    if name is None:
        name = ctx.author.username
    age: int = ctx.options.age
    gender: str = ctx.options.gender

    await ctx.respond(
        f"Hello {ctx.author.mention}! Your name is {name}, you are {age} years old, and your gender is {gender}.",
        # in order to actually mention the user, you must pass `user_mentions=True`
        # otherwise, the user won't get a notification
        user_mentions=True,
    )


# To have autocomplete options, add the
# pass `autocomplete=function` to `@lightbulb.option`
# or `autocomplete=True` and mark the function with `@command.autocomplete("option_name")`.
# @autocomplete_example.autocomplete("language")
async def _programming_language_autocomplete(
    option: hikari.CommandInteractionOption, interaction: hikari.AutocompleteInteraction
) -> list[str]:
    # The `option` argument is the current text that the user typed in.
    if not isinstance(option.value, str):
        # This will raise a TypeError if `option.value` cannot be converted
        option.value = str(option.value)

    # You can query a database, fetch an api, or return any list of strings
    # !!! You can return a max of 25 options !!!
    langs = [
        "C",
        "C++",
        "C#",
        "CSS",
        "Go",
        "HTML",
        "Java",
        "Javascript",
        "Kotlin",
        "Matlab",
        "NoSQL",
        "PHP",
        "Perl",
        "Python",
        "R",
        "Ruby",
        "Rust",
        "SQL",
        "Scala",
        "Swift",
        "TypeScript",
        "Zig",
    ]
    return [lang for lang in langs if option.value.lower() in lang.lower()]


@plugin.command
@lightbulb.option(
    "language",
    "Your favorite programming language.",
    autocomplete=_programming_language_autocomplete,
)
@lightbulb.command("autocomplete_example", "Autocomplete example.")
@lightbulb.implements(lightbulb.SlashCommand)
async def autocomplete_example(ctx: lightbulb.SlashContext):
    """Autocomplete example."""
    await ctx.respond("Your favorite programming language is " + ctx.options.language)


# Command groups are like trees
# You can have subcommands, subcommand groups, and subcommand groups with subcommands
# Here is an example diagram:
# /group_example        (group)
#   subcommand          (executable)
#   subcommand_group    (group)
#     subsubcommand     (executable)

# Because those are slash commands, only the leaves (/subcommand and /subsubcommand) are callable.

# To create a group, use the template below
# 1. Create the command group
@plugin.command
@lightbulb.command("group_example", "Example command group.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def group_example(_: lightbulb.SlashContext) -> None:
    """Group example."""
    # This will never execute because it is a group
    pass


# 2. Add a child command
@group_example.child
@lightbulb.command("subcommand", "Example subcommand.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def subcommand(ctx: lightbulb.SlashContext) -> None:
    """An example subcommand."""
    await ctx.respond("invoked `/group_example subcommand`")


# 3. Add a sub-group
@group_example.child
@lightbulb.command("subcommand_group", "Example subcommand group.")
@lightbulb.implements(lightbulb.SlashSubGroup)
async def subcommand_group(_: lightbulb.SlashContext) -> None:
    """Subcommand group example."""
    # This will never execute because it is a sub-group
    pass


# 4. Add a child to the sub-group
@subcommand_group.child
@lightbulb.command("subsubcommand", "Example subsubcommand.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def subsubcommand(ctx: lightbulb.SlashContext) -> None:
    """An example subsubcommand."""
    await ctx.respond("invoked `/group_example subcommand_group subsubcommand`")


# Event listeners are a way to listen to events from the gateway.
# You can have stand alone event listeners or use `wait_for` to wait for a specific event inside a command / listener.
@plugin.listener(hikari.MemberCreateEvent)
async def on_member_join(event: hikari.MemberCreateEvent) -> None:
    """Event listener to welcome new members."""
    guild = event.get_guild()
    await event.member.send(f"Welcome to {guild.name if guild else 'the server'}!")


# You can also use `wait_for` to wait for a specific event
@plugin.command
@lightbulb.command("wait_for_example", "Example command with `wait_for` and `stream`.")
@lightbulb.implements(lightbulb.SlashCommand)
async def wait_for_example(ctx: lightbulb.SlashContext) -> None:
    """Wait for example."""
    await ctx.respond("Send a message!")

    # We can add a predicate to `wait_for` to filter out events
    def author_check(e: hikari.MessageCreateEvent) -> bool:
        return e.author_id == ctx.author.id

    # You need to wrap wait_for in a try/catch block because it can raise `asyncio.TimeoutError`
    try:
        event = await ctx.bot.wait_for(hikari.MessageCreateEvent, timeout=10, predicate=author_check)
        await ctx.respond(f"You sent: {event.message.content}")
    except asyncio.TimeoutError:
        await ctx.respond("Too slow!")
    # remember to use try/except/finally if you need to clean up any resources

    # You can also use `stream` to listen for events
    await ctx.respond("Waiting for guild events...")
    with ctx.bot.stream(hikari.Event, timeout=5).filter(
        # Only listen for events that have a guild_id and are not bots
        lambda e: getattr(e, "guild_id", None) == ctx.guild_id
        and getattr(e, "is_human", False)
    ) as stream:
        async for event in stream:
            await ctx.respond(f"New `{event.__class__.__name__}`")

    await ctx.respond("Done!")


# You can interact with discord's API using the `rest` attribute on the bot
# This allows you to
# - fetch information about users, channels, guilds, etc.
# - create, edit, and delete messages, channels, threads, roles, categories, etc.
# - add, remove, and edit reactions
@plugin.command
@lightbulb.command("rest_example", "Example command using the `rest` attribute.")
@lightbulb.implements(lightbulb.SlashCommand)
async def rest_example(ctx: lightbulb.SlashContext) -> None:
    """Example command using the `rest` attribute."""
    rest = ctx.bot.rest
    your_messages = await rest.fetch_messages(ctx.channel_id).filter(lambda m: m.author.id == ctx.author.id).count()
    await ctx.respond(f"{your_messages} out of the last 10 messages in this channel were sent by you.")


# Context Menus are a way to attach a command to a user or a message.
# By right clicking a user or a User, you can select to execute a command under the "Apps" menu item.
@plugin.command
@lightbulb.command("user_context_menu_example", "Example context menu on a user.")
@lightbulb.implements(lightbulb.UserCommand)
async def user_context_menu_example(ctx: lightbulb.UserContext) -> None:
    """User context menu example."""
    user: hikari.Member = ctx.options.target
    await ctx.respond(f"Hello {user.mention}!", user_mentions=True)


# Same with messages
@plugin.command
@lightbulb.command("message_context_menu_example", "Example context menu on a message.")
@lightbulb.implements(lightbulb.MessageCommand)
async def message_context_menu_example(ctx: lightbulb.MessageContext) -> None:
    """Message context menu example."""
    message: hikari.Message = ctx.options.target
    await ctx.respond(f"The message length is: {len(message.content or '')}", flags=hikari.MessageFlag.EPHEMERAL)


# Components are a way to add interactive buttons to your slash commands.
# We use `miru` to manage components and their callbacks.

# To create a component, use the template below
# 1. Create the view
class MyView(miru.View):
    """An example view with buttons."""

    @miru.button(label="Rock", emoji="\N{ROCK}", style=hikari.ButtonStyle.PRIMARY)
    async def rock_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        await ctx.respond("Paper!")

    @miru.button(label="Paper", emoji="\N{SCROLL}", style=hikari.ButtonStyle.PRIMARY)
    async def paper_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        await ctx.respond("Scissors!")

    @miru.button(label="Scissors", emoji="\N{BLACK SCISSORS}", style=hikari.ButtonStyle.PRIMARY)
    async def scissors_button(self, button: miru.Button, ctx: miru.ViewContext):
        await ctx.respond("Rock!")

    @miru.button(emoji="\N{BLACK SQUARE FOR STOP}", style=hikari.ButtonStyle.DANGER, row=2)
    async def stop_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        self.stop()  # Stop listening for interactions

    @miru.select(
        options=[
            hikari.SelectMenuOption(
                label="Thing 1",
                value="1",
                description="This is a thing",
                emoji=hikari.UnicodeEmoji("🗿"),
                is_default=True,
            ),
            hikari.SelectMenuOption(
                label="Thing 2",
                value="2",
                description="This is another thing",
                emoji=hikari.UnicodeEmoji("🗿"),
                is_default=False,
            ),
            hikari.SelectMenuOption(
                label="Thing 3",
                value="3",
                description="This is a different thing",
                emoji=hikari.UnicodeEmoji("🗿"),
                is_default=False,
            ),
        ],
        placeholder="Select some stuff!",
        min_values=0,
        max_values=2,
        row=3,
    )
    async def select(self, select: miru.Select, ctx: miru.ViewContext) -> None:
        await ctx.respond(f"You selected {select.values}")


# 2. Create a command to use the view
@plugin.command
@lightbulb.command("button_example", "Example command with buttons.")
@lightbulb.implements(lightbulb.SlashCommand)
async def button_example(ctx: lightbulb.SlashContext) -> None:
    """Wait for example."""
    # 3. Create an instance of the view and start it
    view = MyView(timeout=60)
    resp = await ctx.respond("Rock Paper Scissors!", components=view)
    msg = await resp.message()
    await view.start(msg)
    await view.wait()

    await ctx.respond("Thank you for playing!")


# You can use buttons to create a navigation menu
@plugin.command
@lightbulb.command("nav_example", "Example command with button navigation.", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def navigation_example(ctx: lightbulb.SlashContext) -> None:
    """Navigation example."""
    # await ctx.respond(response_type=hikari.ResponseType.DEFERRED_MESSAGE_UPDATE)
    embed = hikari.Embed(title="I'm the second page!", description="Also an embed!")
    pages = ["I'm the first page!", embed, "I'm the last page!"]

    navigator = nav.NavigatorView(pages=pages, timeout=10)
    # You may also pass an interaction object to this function
    await navigator.send(ctx.channel_id)

    await navigator.wait()  # This is not necessary, but we want to wait anyway
    await ctx.respond("Done!")


# Miru also has modal support
class MyModal(miru.Modal):
    """An example modal."""

    # Define our modal items
    # You can also use Modal.add_item() to add items to the modal after instantiation, just like with views.
    name = miru.TextInput(label="Name", placeholder="Enter your name!", required=True)
    bio = miru.TextInput(label="Biography", value="Pre-filled content!", style=hikari.TextInputStyle.PARAGRAPH)

    # You can currently only use TextInputs
    # https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-response-object-modal

    # The callback function is called after the user hits 'Submit'
    async def callback(self, context: miru.ModalContext) -> None:
        # You can also access the values using ctx.values, Modal.values, or use ctx.get_value_by_id()
        await context.respond(f"Your name: `{self.name.value}`\nYour bio: ```{self.bio.value}```")


class ModalView(miru.View):
    """An example view that opens a modal."""

    # Create a new button that will invoke our modal
    @miru.button(label="Click me!", style=hikari.ButtonStyle.PRIMARY)
    async def modal_button(self, button: miru.Button, ctx: miru.ViewContext) -> None:
        modal = MyModal(title="Example Title")
        # You may also use Modal.send(interaction) if not working with a miru context object. (e.g. slash commands)
        # Keep in mind that modals can only be sent in response to interactions.
        await ctx.respond_with_modal(modal)
        # OR
        # await modal.send(ctx.interaction)


@plugin.command
@lightbulb.command("modal_example", "Example command with a modal.")
@lightbulb.implements(lightbulb.SlashCommand)
async def modal_example(ctx: lightbulb.SlashContext) -> None:
    """Navigation example."""
    view = ModalView()
    resp = await ctx.respond("This button triggers a modal!", components=view)
    await view.start(await resp.message())


# TODO: Database example
# TODO: Rest client example


def load(bot: lightbulb.BotApp):
    """Add the plugin to the bot."""
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    """Remove the plugin to the bot."""
    bot.remove_plugin(plugin)
