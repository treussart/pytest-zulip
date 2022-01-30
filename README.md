# pytest-zulip

## installation

    pip install pytest-zulip

## Configure via env var

    ZULIP_URL="https://x.zulipchat.com/api/v1/messages"
    ZULIP_BOT_EMAIL_ADDRESS="bot@x.zulipchat.com"
    ZULIP_BOT_API_KEY="API_KEY"
    ZULIP_TOPIC="TOPIC"
    ZULIP_STREAM="STREAM"

## Add option to send message

    pytest --notify

## Modify content via hook

    def pytest_zulip_create_content(session: Session, exitstatus: Union[int, ExitCode]) -> str:
        reporter = session.config.pluginmanager.get_plugin('terminalreporter')
        return str(reporter.stats.get('passed', []))
