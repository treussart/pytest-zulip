from _pytest.config import ExitCode
from _pytest.pytester import RunResult

from pytest_zulip.zulip import _trim_string


def test_trim_string():
    result = _trim_string("01234", 4, "…")
    assert result == "0…"
    assert len(result.encode("utf-8")) == 4

    result = _trim_string("01234", 4)
    assert result == "0…"
    assert len(result.encode("utf-8")) == 4

    result = _trim_string("01234", 4, ".")
    assert result == "012."
    assert len(result.encode("utf-8")) == 4

    result = _trim_string("01234", 4, None)
    assert result == "0…"
    assert len(result.encode("utf-8")) == 4


def run(pytester, *args):
    return pytester.runpytest("--notify-zulip", *args)


class TestZulip:
    def test_pass(self, pytester, set_env):
        pytester.makepyfile("def test_pass(): pass")
        result: RunResult = run(pytester)
        assert result.ret == 0
        assert "notification sent on Zulip" in result.stdout.str()

    def test_no_config(self, pytester):
        pytester.makepyfile("def test_no_config(): pass")
        result: RunResult = run(pytester)
        assert result.ret == ExitCode.INTERNAL_ERROR

    def test_pass_hook(self, pytester, set_env):
        pytester.makepyfile("def test_pass(): pass")
        # create a temporary conftest.py file
        pytester.makeconftest(
            """
                def pytest_zulip_create_content(session, exitstatus):
                    reporter = session.config.pluginmanager.get_plugin('terminalreporter')
                    return f"passed: {len(reporter.stats.get('passed', []))}"
        """
        )
        result: RunResult = run(pytester)
        assert result.ret == 0
        assert "notification sent on Zulip" in result.stdout.str()
