from typing import Union

from _pytest.config import ExitCode
from _pytest.main import Session


def pytest_zulip_create_content(
    session: Session, exitstatus: Union[int, ExitCode]
) -> str:
    """Called to create content"""
