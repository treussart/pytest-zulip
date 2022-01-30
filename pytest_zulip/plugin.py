import os
from typing import Union

import pytest
from _pytest.config import ExitCode, Config, PytestPluginManager
from _pytest.config.argparsing import Parser
from _pytest.main import Session
from _pytest.terminal import TerminalReporter

from pytest_zulip.zulip import send_message


def pytest_addhooks(pluginmanager: PytestPluginManager):
    from . import hooks

    pluginmanager.add_hookspecs(hooks)


def pytest_addoption(parser: Parser):
    parser.addoption("--notify", action="store_true", help="Notify via Zulip")


def pytest_sessionfinish(session: Session, exitstatus: Union[int, ExitCode]):
    if session.config.getoption("--notify"):
        send_message(session, exitstatus)


@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(
    terminalreporter: TerminalReporter, exitstatus: int, config: Config
):
    yield
    # special check for pytest-xdist plugin, cause we do not want to send report for each worker.
    if hasattr(terminalreporter.config, "workerinput"):
        return
    if config.getoption("--notify"):
        terminalreporter.write_sep("-", "notification sent on Zulip")


def pytest_configure(config: Config):
    if config.getoption("--notify") and (
        not os.environ.get("ZULIP_URL")
        or not os.environ.get("ZULIP_STREAM")
        or not os.environ.get("ZULIP_TOPIC")
        or not os.environ.get("ZULIP_BOT_EMAIL_ADDRESS")
        or not os.environ.get("ZULIP_BOT_API_KEY")
    ):
        raise Exception("You must set the environment variables for Zulip plugin")
