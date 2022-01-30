import os
from typing import Union

import requests
from _pytest.config import ExitCode
from _pytest.main import Session


def send_message(session: Session, exitstatus: Union[int, ExitCode]):
    # https://zulip.com/api/send-message
    # https://zulip.com/help/format-your-message-using-markdown#status-messages
    status = "succeeded"
    if exitstatus != 0:
        status = "failed"
    topic = f"{os.environ.get('ZULIP_TOPIC')} {status}"
    content = session.config.hook.zulip_create_content(session=session, exitstatus=exitstatus)
    if not content:
        reporter = session.config.pluginmanager.get_plugin('terminalreporter')
        content = (
            f"Passed={len(reporter.stats.get('passed', []))} Failed={len(reporter.stats.get('failed', []))} "
            f"Skipped={len(reporter.stats.get('skipped', []))} Error={len(reporter.stats.get('error', []))}"
        )
    payload = {
        "type": "stream",
        "to": os.environ.get("ZULIP_STREAM"),
        "topic": topic,
        "content": content,
    }
    requests.post(
        url=os.environ.get("ZULIP_URL"),
        auth=(
            os.environ.get("ZULIP_BOT_EMAIL_ADDRESS"),
            os.environ.get("ZULIP_BOT_API_KEY"),
        ),
        data=payload,
    )
