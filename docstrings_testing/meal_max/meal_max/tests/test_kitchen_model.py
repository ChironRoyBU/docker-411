import pytest
import sqlite3
from contextlib import contextmanager
from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)

######################################################
#
#    Fixtures and Mocks
#
######################################################

@pytest.fixture
def mock_db_connection(mocker):
    """Fixture to mock the database connection."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None  # Simulate commit behavior

    # Patch `get_db_connection` where it is imported in `kitchen_model`
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection instead of the cursor

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_conn  # Return mock_conn for assertions in tests

######################################################
#
#    Test Cases
#
######################################################

def test_create_meal(mock_db_connection):
    """Test creating a new meal."""
    create_meal(meal="Pasta", cuisine="Italian", price=12.5, difficulty="MED")
    assert mock_db_connection.cursor().execute.called, "Expected SQL execute to be called."
    assert mock_db_connection.commit.called, "Expected connection commit to be called."

def test_create_meal_duplicate(mock_db_connection):
    """Test creating a meal that already exists."""
    mock_db_connection.cursor().execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal")

    with pytest.raises(ValueError, match="Meal with name 'Pasta' already exists"):
        create_meal(meal="Pasta", cuisine="Italian", price=12.5, difficulty="MED")


def test_clear_meals(mock_db_connection, mocker):
    """Test clearing all meals from the database."""
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': '/app/sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="CREATE TABLE meals ..."))

    clear_meals()
    mock_open.assert_called_once_with('/app/sql/create_meal_table.sql', 'r')
    assert mock_db_connection.cursor().executescript.called, "Expected SQL executescript to be called."
    assert mock_db_connection.commit.called, "Expected connection commit to be called."


def test_delete_meal(mock_db_connection):
    """Test deleting a meal by ID."""
    mock_db_connection.cursor().fetchone.return_value = (False,)  # Simulate meal not being deleted

    delete_meal(1)
    assert mock_db_connection.cursor().execute.called, "Expected SQL execute to be called."
    assert mock_db_connection.commit.called, "Expected connection commit to be called."

def test_delete_meal_already_deleted(mock_db_connection):
    """Test deleting a meal that has already been marked as deleted."""
    mock_db_connection.cursor().fetchone.return_value = (True,)  # Simulate meal already deleted

    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        delete_meal(1)

def test_delete_meal_not_found(mock_db_connection):
    """Test deleting a meal that does not exist."""
    mock_db_connection.cursor().fetchone.return_value = None  # Simulate meal not found

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)


def test_get_meal_by_id(mock_db_connection):
    """Test retrieving a meal by ID."""
    mock_db_connection.cursor().fetchone.return_value = (1, "Pasta", "Italian", 12.5, "MED", False)

    meal = get_meal_by_id(1)
    expected_meal = Meal(id=1, meal="Pasta", cuisine="Italian", price=12.5, difficulty="MED")
    assert meal == expected_meal, f"Expected {expected_meal}, got {meal}."


def test_get_meal_by_id_not_found(mock_db_connection):
    """Test retrieving a meal by ID that does not exist."""
    mock_db_connection.cursor().fetchone.return_value = None  # Simulate meal not found

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)


def test_get_meal_by_name(mock_db_connection):
    """Test retrieving a meal by name."""
    mock_db_connection.cursor().fetchone.return_value = (1, "Pasta", "Italian", 12.5, "MED", False)

    meal = get_meal_by_name("Pasta")
    expected_meal = Meal(id=1, meal="Pasta", cuisine="Italian", price=12.5, difficulty="MED")
    assert meal == expected_meal, f"Expected {expected_meal}, got {meal}."


def test_get_meal_by_name_not_found(mock_db_connection):
    """Test retrieving a meal by name that does not exist."""
    mock_db_connection.cursor().fetchone.return_value = None  # Simulate meal not found

    # Adjusted the regex to match the exact message
    with pytest.raises(ValueError, match="Meal with name Pizza not found"):
        get_meal_by_name("Pizza")


def test_get_leaderboard(mock_db_connection):
    """Test retrieving the leaderboard."""
    mock_db_connection.cursor().fetchall.return_value = [
        (1, "Pasta", "Italian", 12.5, "MED", 10, 8, 0.8)
    ]

    leaderboard = get_leaderboard()
    assert len(leaderboard) == 1, "Expected leaderboard to contain 1 entry."
    assert leaderboard[0]['meal'] == "Pasta", "Expected meal to be 'Pasta'."
    assert leaderboard[0]['win_pct'] == 80.0, "Expected win percentage to be 80.0."


def test_update_meal_stats_win(mock_db_connection):
     """Test updating meal stats with a win."""
     mock_db_connection.cursor().fetchone.return_value = (False,)  # Simulate meal not deleted

     update_meal_stats(1, "win")
     assert mock_db_connection.cursor().execute.called, "Expected SQL execute to be called for update."
     assert mock_db_connection.commit.called, "Expected connection commit to be called."