import os

import pytest

pytest_plugins = ["pytester"]


@pytest.fixture
def set_env():
    os.environ["ZULIP_URL"] = "https://x.zulipchat.com/api/v1/messages"
    os.environ["ZULIP_BOT_EMAIL_ADDRESS"]="bot@x.zulipchat.com"
    os.environ["ZULIP_BOT_API_KEY"]="API_KEY"
    os.environ["ZULIP_TOPIC"]="TOPIC"
    os.environ["ZULIP_STREAM"]="STREAM"
    yield
    del os.environ["ZULIP_URL"]
    del os.environ["ZULIP_BOT_EMAIL_ADDRESS"]
    del os.environ["ZULIP_BOT_API_KEY"]
    del os.environ["ZULIP_TOPIC"]
    del os.environ["ZULIP_STREAM"]
