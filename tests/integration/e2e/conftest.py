from collections.abc import Iterator
from pathlib import Path 
import shutil

import pytest

@pytest.fixture
def  e2e_test_ticker() -> Iterator[str]:
    """
    Make deterministic E2E market data avaliable through
    the same data/raw path used by the production enge
    """
    ticker = "E2E_TEST"

    source = Path("tests/integration/e2e/fixtures/E2E_TEST.csv")

    target = Path(f"data/raw/{ticker}.csv")

    target.parent.mkdir(parents=True,exist_ok=True)

    shutil.copyfile(source,target)

    try:
        yield ticker
    finally:
        target.unlink(missing_ok=True)