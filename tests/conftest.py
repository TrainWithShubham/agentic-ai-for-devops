from pathlib import Path

import pytest

from runbookops.config import Settings


@pytest.fixture
def settings(tmp_path):
    return Settings(root=Path(__file__).resolve().parents[1], data=tmp_path / "state")
