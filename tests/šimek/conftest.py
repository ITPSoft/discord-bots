from collections.abc import Generator
from typing import Any
from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture()
def first_rand_answer() -> Generator[MagicMock, Any, None]:
    # Use the same mock object for both patches
    with patch("random.choice") as mock_choice:
        mock_choice.side_effect = lambda x: x[0]  # force random to return first element
        yield mock_choice


@pytest.fixture()
def always_answer() -> Generator[MagicMock, Any, None]:
    # Create a single mock object
    # Use the same mock object for both patches
    with patch("random.randint") as mock_randint:
        mock_randint.return_value = 1  # so the probability triggers always in tests
        yield mock_randint
