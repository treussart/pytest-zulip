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
        self.url = os.environ.get("ZULIP_URL")
        self.only_on_failed = os.getenv("ZULIP_ONLY_ON_FAILED", False)

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session: Session, exitstatus: Union[int, ExitCode]):
        try:
            if not self.only_on_failed:
                self.send_message(session, exitstatus)
            elif self.only_on_failed and exitstatus != 0:
                self.send_message(session, exitstatus)
        except Exception as e:
            log.error(
                f"Zulip send_message error: {self.url} - {e}"
            )

    @pytest.hookimpl(trylast=True)
    def pytest_terminal_summary(
        self,
        terminalreporter: TerminalReporter,
        exitstatus: Union[int, ExitCode],
        config: Config,
    ):
        terminalreporter.write_sep("-", "notification sent on Zulip")

    def send_message(self, session: Session, exitstatus: Union[int, ExitCode]):
        # https://zulip.com/api/send-message
        # https://zulip.com/help/format-your-message-using-markdown#status-messages
        status = "succeeded"
        if exitstatus != 0:
            status = "failed"
        topic = session.config.hook.pytest_zulip_rename_topic(
            session=session, exitstatus=exitstatus, topic=os.environ.get('ZULIP_TOPIC')
        )
        if not topic:
            topic = os.environ.get('ZULIP_TOPIC')
        else:
            topic = topic[0]
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
        requests.post(
            url=self.url,
            auth=(
                os.environ.get("ZULIP_BOT_EMAIL_ADDRESS"),
                os.environ.get("ZULIP_BOT_API_KEY"),
            ),
            data=payload,
        )


def _trim_string(s: str, limit: int, ellipsis_char: Optional[str] = "???") -> str:
    s = s.strip()
    sb = s.encode("utf-8")
    if not ellipsis_char:
        ellipsis_char = "???"
    limit = limit - len(ellipsis_char.encode("utf-8"))
    if len(sb) > limit:
        sb_limited = sb[:limit]
        return sb_limited.decode("utf-8").strip() + ellipsis_char
    return s
