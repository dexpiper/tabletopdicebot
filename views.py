from jinja2 import Environment, PackageLoader, select_autoescape

from models import User
from common.unicode import emoji


# setting Jinja2-specified params
env = Environment(
        loader=PackageLoader("views"),
        autoescape=select_autoescape()
    )
env.trim_blocks = True
env.lstrip_blocks = True


def hello(username: str):
    """
    Render basic hello template
    """
    template = env.get_template("hello.jinja2")
    return template.render(username=username, emoji=emoji)


def charlist(user: User):
    """
    Render list of user's characters, their throws and attributes.
    """
    template = env.get_template("charlist.jinja2")
    return template.render(user=user, emoji=emoji)


def error(error_text: str):
    """
    Render error_text into a standard error template
    """
    template = env.get_template("error.jinja2")
    return template.render(error_text=error_text, emoji=emoji)


def roll(roller: object, hand: object):
    """
    Render roll template
    """
    template = env.get_template("roll.jinja2")
    return template.render(roller=roller, emoji=emoji)
