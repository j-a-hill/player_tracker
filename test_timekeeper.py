"""
Tests for timekeeper, inn, and training features.
"""
import sys
import os
from datetime import datetime, timedelta

# Mock gspread for testing
class MockWorksheet:
    def __init__(self, name):
        self.name = name
        self.rows = []
        
    def append_row(self, values):
        """Simulate append_row - adds to next available row."""
        self.rows.append(values)
    
    def get_all_records(self):
        """Return all rows as dictionaries."""
        if not self.rows:
            return []
        headers = self.rows[0]
        records = []
        for row in self.rows[1:]:
            record = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    record[header] = row[i]
                else:
                    record[header] = ''
            records.append(record)
        return records
    
    def get_all_values(self):
        """Return all rows as lists."""
        return self.rows
    
    def update_cell(self, row, col, value):
        """Update a cell."""
        while len(self.rows) < row:
            self.rows.append([])
        row_data = self.rows[row - 1]
        while len(row_data) < col:
            row_data.append('')
        row_data[col - 1] = value
    
    def batch_update(self, updates):
        """Batch update cells."""
        for update in updates:
            # Parse range like 'C2'
            range_str = update['range']
            col_letter = ''.join(c for c in range_str if c.isalpha())
            row_num = int(''.join(c for c in range_str if c.isdigit()))
            
            # Convert column letter to number
            col_num = ord(col_letter.upper()) - ord('A') + 1
            
            value = update['values'][0][0]
            self.update_cell(row_num, col_num, value)

class MockSpreadsheet:
    def __init__(self):
        self.worksheets = {}
    
    def worksheet(self, name):
        if name not in self.worksheets:
            raise Exception(f"WorksheetNotFound: {name}")
        return self.worksheets[name]
    
    def add_worksheet(self, name, rows, cols):
        worksheet = MockWorksheet(name)
        self.worksheets[name] = worksheet
        return worksheet

class MockClient:
    def open_by_key(self, sheet_id):
        return MockSpreadsheet()

# Mock gspread module
class MockGspread:
    class exceptions:
        class WorksheetNotFound(Exception):
            pass
    
    @staticmethod
    def authorize(creds):
        return MockClient()

sys.modules['gspread'] = MockGspread()
sys.modules['gspread.exceptions'] = MockGspread.exceptions

# Mock google auth
class MockCredentials:
    @staticmethod
    def from_service_account_file(filename, scopes):
        return None

class MockServiceAccount:
    Credentials = MockCredentials

sys.modules['google.oauth2.service_account'] = MockServiceAccount()

# Now import our storage module
from storage import PlayerStorage


def test_training_options():
    """Test getting training options."""
    print("Testing training options...")
    
    # Create mock storage
    storage = PlayerStorage.__new__(PlayerStorage)
    storage.spreadsheet = MockSpreadsheet()
    
    # Manually create worksheets
    storage.training_options_sheet = storage.spreadsheet.add_worksheet('TrainingOptions', 100, 10)
    storage.training_options_sheet.append_row(['Type', 'Name', 'Description'])
    storage.training_options_sheet.append_row(['Skill', 'Acrobatics', 'Dex-based agility'])
    storage.training_options_sheet.append_row(['Skill', 'Athletics', 'Str-based prowess'])
    storage.training_options_sheet.append_row(['Language', 'Elvish', 'Language of elves'])
    
    # Get all options
    options = storage.get_training_options()
    assert len(options) == 3, f"Expected 3 options, got {len(options)}"
    
    # Get only skills
    skills = storage.get_training_options('skill')
    assert len(skills) == 2, f"Expected 2 skills, got {len(skills)}"
    
    # Get only languages
    languages = storage.get_training_options('language')
    assert len(languages) == 1, f"Expected 1 language, got {len(languages)}"
    
    print("✓ Training options test passed")


def test_player_training():
    """Test player training tracking."""
    print("Testing player training...")
    
    # Create mock storage
    storage = PlayerStorage.__new__(PlayerStorage)
    storage.spreadsheet = MockSpreadsheet()
    
    # Manually create worksheets
    storage.training_sheet = storage.spreadsheet.add_worksheet('Training', 100, 10)
    storage.training_sheet.append_row(['Player ID', 'Training Type', 'Skill/Language', 'Days Spent', 'Days Required', 'Status'])
    
    # Start training
    player_id = '123456'
    success = storage.start_training(player_id, 'Skill', 'Acrobatics', 250)
    assert success, "Failed to start training"
    
    # Get training
    training = storage.get_player_training(player_id)
    assert len(training) == 1, f"Expected 1 training, got {len(training)}"
    assert training[0]['skill_or_language'] == 'Acrobatics'
    assert training[0]['days_spent'] == 0
    assert training[0]['status'] == 'In Progress'
    
    # Update progress
    success = storage.update_training_progress(player_id, 'Acrobatics', 50)
    assert success, "Failed to update training progress"
    
    # Check updated progress
    training = storage.get_player_training(player_id)
    assert training[0]['days_spent'] == 50
    assert training[0]['status'] == 'In Progress'
    
    # Complete training
    success = storage.update_training_progress(player_id, 'Acrobatics', 200)
    assert success, "Failed to complete training"
    
    training = storage.get_player_training(player_id)
    assert training[0]['days_spent'] == 250
    assert training[0]['status'] == 'Complete'
    
    print("✓ Player training test passed")


def test_timekeeper_data():
    """Test timekeeper time tracking."""
    print("Testing timekeeper data...")
    
    # Create mock storage
    storage = PlayerStorage.__new__(PlayerStorage)
    storage.spreadsheet = MockSpreadsheet()
    
    # Manually create worksheets
    storage.timekeeper_sheet = storage.spreadsheet.add_worksheet('Timekeeper', 100, 10)
    storage.timekeeper_sheet.append_row(['Key', 'Value'])
    
    # Set game time
    game_time = '1492-01-01 08:00:00'
    success = storage.set_game_time(game_time)
    assert success, "Failed to set game time"
    
    # Get game time
    retrieved_time = storage.get_game_time()
    assert retrieved_time == game_time, f"Expected {game_time}, got {retrieved_time}"
    
    # Set real time
    real_time = '2024-01-01 12:00:00'
    success = storage.set_last_real_time(real_time)
    assert success, "Failed to set real time"
    
    # Get real time
    retrieved_real = storage.get_last_real_time()
    assert retrieved_real == real_time, f"Expected {real_time}, got {retrieved_real}"
    
    # Update game time
    new_game_time = '1492-01-08 08:00:00'
    success = storage.set_game_time(new_game_time)
    assert success, "Failed to update game time"
    
    retrieved_time = storage.get_game_time()
    assert retrieved_time == new_game_time, f"Expected {new_game_time}, got {retrieved_time}"
    
    print("✓ Timekeeper data test passed")


def test_inn_configuration():
    """Test inn configuration."""
    print("Testing inn configuration...")
    
    # Create mock storage
    storage = PlayerStorage.__new__(PlayerStorage)
    storage.spreadsheet = MockSpreadsheet()
    
    # Manually create worksheets
    storage.inn_sheet = storage.spreadsheet.add_worksheet('Inn', 100, 10)
    storage.inn_sheet.append_row(['Player ID', 'Exempt', 'Custom Cost'])
    
    player_id = '123456'
    
    # Get default config (not in sheet yet)
    config = storage.get_inn_config(player_id)
    assert config['exempt'] == True, "Default should be exempt (checked out)"
    assert config['custom_cost'] is None, "Default should have no custom cost"
    
    # Set exemption
    success = storage.set_inn_exempt(player_id, True)
    assert success, "Failed to set exemption"
    
    config = storage.get_inn_config(player_id)
    assert config['exempt'] == True, "Should be exempt"
    
    # Remove exemption
    success = storage.set_inn_exempt(player_id, False)
    assert success, "Failed to remove exemption"
    
    config = storage.get_inn_config(player_id)
    assert config['exempt'] == False, "Should not be exempt"
    
    # Set custom cost
    success = storage.set_inn_custom_cost(player_id, 500)
    assert success, "Failed to set custom cost"
    
    config = storage.get_inn_config(player_id)
    assert config['custom_cost'] == 500, f"Expected custom cost 500, got {config['custom_cost']}"
    
    # Clear custom cost
    success = storage.set_inn_custom_cost(player_id, None)
    assert success, "Failed to clear custom cost"
    
    config = storage.get_inn_config(player_id)
    assert config['custom_cost'] is None, "Custom cost should be None"
    
    print("✓ Inn configuration test passed")


def test_get_all_players():
    """Test getting all players."""
    print("Testing get all players...")
    
    # Create mock storage
    storage = PlayerStorage.__new__(PlayerStorage)
    storage.spreadsheet = MockSpreadsheet()
    
    # Manually create worksheets
    storage.players_sheet = storage.spreadsheet.add_worksheet('Players', 100, 10)
    storage.players_sheet.append_row(['Player ID', 'Name', 'XP', 'Copper', 'Inventory'])
    storage.players_sheet.append_row(['123', 'Alice', 1000, 5000, '["Sword", "Shield"]'])
    storage.players_sheet.append_row(['456', 'Bob', 2000, 10000, '["Potion"]'])
    
    # Get all players
    players = storage.get_all_players()
    assert len(players) == 2, f"Expected 2 players, got {len(players)}"
    
    # Check first player
    assert players[0]['player_id'] == '123'
    assert players[0]['name'] == 'Alice'
    assert players[0]['xp'] == 1000
    assert players[0]['copper'] == 5000
    assert len(players[0]['inventory']) == 2
    
    # Check second player
    assert players[1]['player_id'] == '456'
    assert players[1]['name'] == 'Bob'
    
    print("✓ Get all players test passed")


def test_weekly_schedule():
    """Test real-world weekly schedule (Sunday 19:00 UK time)."""
    print("Testing weekly schedule...")
    from datetime import timezone, time as dtime
    from weekly_schedule import weekly_events_between, parse_notification_time
    
    at = parse_notification_time("19:00")
    assert at == dtime(19, 0)
    utc = timezone.utc
    
    # Winter (GMT): Sunday 2026-01-04 19:00 London == 19:00 UTC
    events = weekly_events_between(
        datetime(2026, 1, 4, 18, 58, tzinfo=utc), datetime(2026, 1, 4, 19, 3, tzinfo=utc), 0, at)
    assert len(events) == 1, f"Expected 1 event in GMT, got {events}"
    
    # Summer (BST): Sunday 2026-07-05 19:00 London == 18:00 UTC
    events = weekly_events_between(
        datetime(2026, 7, 5, 17, 58, tzinfo=utc), datetime(2026, 7, 5, 18, 3, tzinfo=utc), 0, at)
    assert len(events) == 1, f"Expected 1 event in BST, got {events}"
    events = weekly_events_between(
        datetime(2026, 7, 5, 18, 58, tzinfo=utc), datetime(2026, 7, 5, 19, 3, tzinfo=utc), 0, at)
    assert events == [], f"19:00 UTC in summer is 20:00 UK, got {events}"
    
    # Old behaviour (midnight) no longer fires
    events = weekly_events_between(
        datetime(2026, 1, 4, 23, 58, tzinfo=utc), datetime(2026, 1, 5, 0, 3, tzinfo=utc), 0, at)
    assert events == [], f"Should not fire at midnight, got {events}"
    
    # Exactly on the boundary fires once across consecutive checks
    boundary = datetime(2026, 1, 4, 19, 0, tzinfo=utc)
    first = weekly_events_between(boundary - timedelta(minutes=5), boundary, 0, at)
    second = weekly_events_between(boundary, boundary + timedelta(minutes=5), 0, at)
    assert len(first) + len(second) == 1, "Boundary should fire exactly once"
    
    # Bot offline for 2 weeks catches up on both Sundays
    events = weekly_events_between(
        datetime(2026, 1, 1, 12, 0, tzinfo=utc), datetime(2026, 1, 15, 12, 0, tzinfo=utc), 0, at)
    assert len(events) == 2, f"Expected 2 missed events, got {events}"
    assert all(e.weekday() == 6 and e.hour == 19 for e in events)
    
    # Caught-up events each get their own week's in-game time
    from weekly_schedule import game_time_at
    now = datetime(2026, 1, 15, 12, 0, tzinfo=utc)
    game_now = datetime(1492, 3, 1, 12, 0)
    game_times = [game_time_at(e, now, game_now, 1.0) for e in events]
    assert game_times[1] - game_times[0] == timedelta(days=7), game_times
    assert game_times[1] == game_now - (now - events[1]), game_times
    assert game_time_at(now, now, game_now, 1.0) == game_now
    
    print("✓ Weekly schedule test passed")


def run_tests():
    """Run all tests."""
    print("Running timekeeper, inn, and training tests...\n")
    
    test_training_options()
    test_player_training()
    test_timekeeper_data()
    test_inn_configuration()
    test_get_all_players()
    test_weekly_schedule()
    
    print("\n✅ All tests passed!")


if __name__ == '__main__':
    run_tests()
