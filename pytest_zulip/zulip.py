import logging
import os
from typing import Union, Optional

import pytest
import requests
from _pytest.config import ExitCode, Config
from _pytest.main import Session
from _pytest.terminal import TerminalReporter


log = logging.getLogger(__name__)


class Zulip:
    def __init__(self, config: Config):
        self.config = config

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session: Session, exitstatus: Union[int, ExitCode]):
        self.send_message(session, exitstatus)

    @pytest.hookimpl(trylast=True)
    def pytest_terminal_summary(
        self,
        terminalreporter: TerminalReporter,
        exitstatus: Union[int, ExitCode],
        config: Config,
    ):
        terminalreporter.write_sep("-", "notification sent on Zulip")

    @staticmethod
    def send_message(session: Session, exitstatus: Union[int, ExitCode]):
        # https://zulip.com/api/send-message
        # https://zulip.com/help/format-your-message-using-markdown#status-messages
        status = "succeeded"
        if exitstatus != 0:
            status = "failed"
        topic = f"{os.environ.get('ZULIP_TOPIC')} {status}"
        content = session.config.hook.pytest_zulip_create_content(
            session=session, exitstatus=exitstatus
        )
        if not content:
            reporter: TerminalReporter = session.config.pluginmanager.get_plugin(
                "terminalreporter"
            )
            content = (
                f"# Test {session.nodeid} {status}\n"
                f"Passed={len(reporter.stats.get('passed', []))} Failed={len(reporter.stats.get('failed', []))} "
                f"Skipped={len(reporter.stats.get('skipped', []))} Error={len(reporter.stats.get('error', []))}"
            )
        else:
            content = content[0]
        payload = {
            "type": "stream",
            "to": os.environ.get("ZULIP_STREAM"),
            "topic": topic,
            "content": _trim_string(
                content, 1000, os.environ.get("ZULIP_ELLIPSIS_CHAR")
            ),
        }
        try:
            requests.post(
                url=os.environ.get("ZULIP_URL"),
                auth=(
                    os.environ.get("ZULIP_BOT_EMAIL_ADDRESS"),
                    os.environ.get("ZULIP_BOT_API_KEY"),
                ),
                data=payload,
            )
        except Exception as e:
            log.error(
                f"Zulip requests.post error: {os.environ.get('ZULIP_URL')} - {e}"
            )


def _trim_string(s: str, limit: int, ellipsis_char: Optional[str] = "…") -> str:
    s = s.strip()
    sb = s.encode("utf-8")
    if not ellipsis_char:
        ellipsis_char = "…"
    limit = limit - len(ellipsis_char.encode("utf-8"))
    if len(sb) > limit:
        sb_limited = sb[:limit]
        return sb_limited.decode("utf-8").strip() + ellipsis_char
    return s
