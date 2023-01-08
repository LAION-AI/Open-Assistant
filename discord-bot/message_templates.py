"""Message templates for the discord bot."""
import typing

import jinja2
from loguru import logger


class MessageTemplates:
    """
    The MessageTemplates class is used to create message templates for the Discord bot. It uses Jinja2 template engine to render the templates with the provided arguments.

    Attributes:
    env (jinja2.Environment): The Jinja2 environment object used to load templates from the specified directory.

    Methods:
    render(template_name: str, **kwargs) -> str: Renders the specified template with the provided keyword arguments and returns the rendered template as a string.
    """
    def __init__(self, template_dir: str = "./templates"):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(
                disabled_extensions=("msg",),
                default=False,
                default_for_string=False,
            ),
        )

    def render(self, template_name: str, **kwargs):
        template = self.env.get_template(template_name)
        txt = template.render(kwargs)
        logger.debug(txt)

        return txt
