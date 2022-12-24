# -*- coding: utf-8 -*-
import jinja2
from loguru import logger


class MessageTemplates:
    def __init__(self, template_dir="./templates"):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(disabled_extensions=("msg",), default=False, default_for_string=False),
        )

    def render(self, template_name, **kwargs):
        template = self.env.get_template(template_name)
        txt = template.render(kwargs)
        logger.debug(txt)

        return txt
