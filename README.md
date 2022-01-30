# pytest-zulip

Pytest report plugin for [Zulip](https://zulip.com/)

Allow to send notification on Zulip chat product.

## installation

    pip install pytest-zulip

## Configure via env var

    ZULIP_URL="https://x.zulipchat.com/api/v1/messages"
    ZULIP_BOT_EMAIL_ADDRESS="bot@x.zulipchat.com"
    ZULIP_BOT_API_KEY="API_KEY"
    ZULIP_TOPIC="TOPIC"
    ZULIP_STREAM="STREAM"

Optional:

    ZULIP_ELLIPSIS_CHAR="…"

## Add option to send message

    pytest --notify

## Modify content via hook

    def pytest_zulip_create_content(session: Session, exitstatus: Union[int, ExitCode]) -> str:
        reporter = session.config.pluginmanager.get_plugin('terminalreporter')
        return str(reporter.stats.get('passed', []))

## Dev

### Change version

edit

    pytest_zulip/__init__.py

commit

    git commit -m "v0.1.0"

tag

    git tag v0.1.0

### Build package

    python -m build
    twine upload dist/*
