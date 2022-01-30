from typing import Union

import pytest
from _pytest.config import ExitCode, Config
from _pytest.main import Session
from _pytest.terminal import TerminalReporter

from pytest_zulip.zulip import send_message


def pytest_addhooks(pluginmanager):
    from . import hooks

    pluginmanager.add_hookspecs(hooks)


def pytest_addoption(parser):
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
