from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def shared_tmp_path(
    tmp_path_factory: Path
) -> Path:

    return tmp_path_factory.mktemp("app_test")