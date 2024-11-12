import pytest
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal, update_meal_stats
from contextlib import contextmanager
import sqlite3

######################################################
#
#    Fixtures and Mocks
#
######################################################

@pytest.fixture
def battle_model():
    """Fixture to create a BattleModel instance."""
    return BattleModel()

@pytest.fixture
def sample_meal_1():
    """Fixture to create a sample meal."""
    return Meal(id=1, meal="Spaghetti", cuisine="Italian", price=15.0, difficulty="MED")

@pytest.fixture
def sample_meal_2():
    """Fixture to create another sample meal."""
    return Meal(id=2, meal="Sushi", cuisine="Japanese", price=20.0, difficulty="HIGH")


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
#    Test Battle Preparation and Execution
#
######################################################

def test_prep_combatant(battle_model, sample_meal_1):
    """Test prepping a combatant."""
    battle_model.prep_combatant(sample_meal_1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0] == sample_meal_1

def test_prep_combatant_full(battle_model, sample_meal_1, sample_meal_2):
    """Test prepping combatants when the list is already full."""
    battle_model.prep_combatant(sample_meal_1)
    battle_model.prep_combatant(sample_meal_2)
    
    with pytest.raises(ValueError, match="Combatant list is full"):
        battle_model.prep_combatant(sample_meal_1)

def test_battle_not_enough_combatants(battle_model, sample_meal_1):
    """Test that an error is raised when there aren't enough combatants."""
    battle_model.prep_combatant(sample_meal_1)
    
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle"):
        battle_model.battle()

def test_battle_execution(mocker, mock_db_connection, battle_model, sample_meal_1, sample_meal_2):
    """Test a successful battle execution."""
    mocker.patch('meal_max.models.battle_model.get_random', return_value=0.1)
    mocker.patch('meal_max.models.kitchen_model.update_meal_stats')

    battle_model.prep_combatant(sample_meal_1)
    battle_model.prep_combatant(sample_meal_2)

    winner = battle_model.battle(),

    assert winner in [sample_meal_1.meal, sample_meal_2.meal]
    assert len(battle_model.combatants) == 1

######################################################
#
#    Test Utility Functions
#
######################################################

def test_clear_combatants(battle_model, sample_meal_1, sample_meal_2):
    """Test clearing the combatants list."""
    battle_model.prep_combatant(sample_meal_1)
    battle_model.prep_combatant(sample_meal_2)
    battle_model.clear_combatants()
    
    assert len(battle_model.combatants) == 0

def test_get_battle_score(battle_model, sample_meal_1):
    """Test getting the battle score for a combatant."""
    score = battle_model.get_battle_score(sample_meal_1)
    expected_score = (sample_meal_1.price * len(sample_meal_1.cuisine)) - 2  # 'MED' has modifier 2
    assert score == expected_score

def test_get_combatants(battle_model, sample_meal_1):
    """Test retrieving the current list of combatants."""
    battle_model.prep_combatant(sample_meal_1)
    combatants = battle_model.get_combatants()
    assert combatants == [sample_meal_1]
