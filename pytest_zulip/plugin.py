import os
from _pytest.config import Config, PytestPluginManager
from _pytest.config.argparsing import Parser

from pytest_zulip.zulip import Zulip


def pytest_addhooks(pluginmanager: PytestPluginManager):
    from . import hooks

    pluginmanager.add_hookspecs(hooks)


def pytest_addoption(parser: Parser):
    parser.addoption("--notify", action="store_true", help="Notify via Zulip")


def pytest_configure(config: Config):
    if config.getoption("--notify") and not hasattr(config, "workerinput"):
        if (
            not os.environ.get("ZULIP_URL")
            or not os.environ.get("ZULIP_STREAM")
            or not os.environ.get("ZULIP_TOPIC")
            or not os.environ.get("ZULIP_BOT_EMAIL_ADDRESS")
            or not os.environ.get("ZULIP_BOT_API_KEY")
        ):
            raise Exception("You must set the environment variables for Zulip plugin")
        config._zulip = Zulip(config)
        config.pluginmanager.register(config._zulip)


def pytest_unconfigure(config: Config):
    zulip = getattr(config, "_zulip", None)
    if zulip:
        del config._zulip
        config.pluginmanager.unregister(zulip)
