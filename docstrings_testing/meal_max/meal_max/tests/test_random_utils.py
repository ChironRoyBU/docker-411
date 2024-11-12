import pytest
import requests

from meal_max.utils.random_utils import get_random

# Constants for testing
MOCK_RANDOM_NUMBER = 0.42

@pytest.fixture
def mock_random_org(mocker):
    """Fixture to mock the response from random.org."""
    mock_response = mocker.Mock()
    mock_response.text = f"{MOCK_RANDOM_NUMBER:.2f}"  # Mock response as a string formatted to two decimal places
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

def test_get_random_success(mock_random_org):
    """Test retrieving a random float from random.org successfully."""
    result = get_random()

    # Assert that the result matches the mocked random number
    assert result == MOCK_RANDOM_NUMBER, f"Expected random number {MOCK_RANDOM_NUMBER}, but got {result}"

    # Ensure that the correct URL was called
    requests.get.assert_called_once_with(
        "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new",
        timeout=5
    )

def test_get_random_request_failure(mocker):
    """Simulate a request failure."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))

    with pytest.raises(RuntimeError, match="Request to random.org failed: Connection error"):
        get_random()

def test_get_random_timeout(mocker):
    """Simulate a timeout."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()

def test_get_random_invalid_response(mocker):
    """Simulate an invalid response from random.org."""
    mock_response = mocker.Mock()
    mock_response.text = "invalid_response"
    mocker.patch("requests.get", return_value=mock_response)

    with pytest.raises(ValueError, match="Invalid response from random.org: invalid_response"):
        get_random()
