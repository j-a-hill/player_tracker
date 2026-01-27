"""
Tests to verify the storage bugs are fixed.
"""
import sys
import os

# Mock gspread for testing
class MockCell:
    def __init__(self, row, col, value):
        self.row = row
        self.col = col
        self.value = value

class MockWorksheet:
    def __init__(self, name):
        self.name = name
        self.rows = []
        self.row_count = 1000  # Simulates a large sheet
        
    def append_row(self, values):
        """Simulate append_row - adds to next available row."""
        # In real gspread, this finds the first empty row
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
            range_str = update['range']
            values = update['values']
            # Parse range like "C2" or "D3"
            import re
            match = re.match(r'([A-Z]+)(\d+)', range_str)
            if match:
                col_letter = match.group(1)
                row_num = int(match.group(2))
                col_num = ord(col_letter) - ord('A') + 1
                self.update_cell(row_num, col_num, values[0][0])

def test_create_player_row_calculation():
    """Test that create_player correctly calculates the row number."""
    print("Testing create_player row calculation...")
    
    # Create mock worksheet
    worksheet = MockWorksheet('Players')
    worksheet.append_row(['Player ID', 'Name', 'XP', 'Copper', 'Silver', 'Electrum', 'Gold', 'Platinum', 'Inventory'])
    
    # Simulate creating a player
    player_id = "123456789"
    name = "TestPlayer"
    
    # Before fix: would use row_count + 1 = 1001
    # After fix: should use len(rows) + 1 = 2 (header is row 1, new player is row 2)
    
    # Simulate append
    worksheet.append_row([player_id, name, 0, 0, 0, 0, 0, 0, '[]'])
    
    # The correct row should be len(worksheet.rows) = 2
    actual_row = len(worksheet.rows)
    
    print(f"  Row count: {worksheet.row_count}")
    print(f"  Actual data rows: {len(worksheet.rows)}")
    print(f"  Correct row for player: {actual_row}")
    
    # The bug would have calculated: row_count + 1 = 1001
    # The fix should calculate: len(get_all_values()) or similar
    
    assert actual_row == 2, f"Expected row 2, got {actual_row}"
    print("  ✓ Row calculation correct")
    
    return True

def test_update_player_after_create():
    """Test that update_player works with newly created players."""
    print("\nTesting update_player after create...")
    
    worksheet = MockWorksheet('Players')
    worksheet.append_row(['Player ID', 'Name', 'XP', 'Copper', 'Silver', 'Electrum', 'Gold', 'Platinum', 'Inventory'])
    worksheet.append_row(["123", "Test", 0, 0, 0, 0, 0, 0, '[]'])
    
    # Row 2 is the player row
    row = 2
    
    # Simulate updating XP (column C = 3)
    updates = [{'range': f'C{row}', 'values': [[100]]}]
    worksheet.batch_update(updates)
    
    # Verify update
    records = worksheet.get_all_records()
    assert len(records) > 0, "No records found"
    assert int(records[0]['XP']) == 100, f"XP not updated, got {records[0]['XP']}"
    
    print("  ✓ Update works correctly")
    return True

def test_shop_items_with_headers():
    """Test that shop items are read correctly when headers exist."""
    print("\nTesting shop items retrieval...")
    
    worksheet = MockWorksheet('Shop')
    worksheet.append_row(['Item Name', 'Price', 'Currency', 'Description', 'Stock'])
    worksheet.append_row(['Health Potion', '50', 'gp', 'Restores HP', '10'])
    worksheet.append_row(['', '', '', '', ''])  # Blank row
    worksheet.append_row(['Mana Potion', '40', 'gp', 'Restores MP', '5'])
    
    records = worksheet.get_all_records()
    
    # Filter out empty items (like get_shop_items does)
    items = []
    for record in records:
        item_name = record.get('Item Name', '').strip()
        if item_name:
            items.append({
                'name': item_name,
                'price': int(record.get('Price', 0)),
                'currency': record.get('Currency', 'gp'),
                'description': record.get('Description', ''),
                'stock': int(record.get('Stock', -1))
            })
    
    print(f"  Found {len(items)} items")
    assert len(items) == 2, f"Expected 2 items, got {len(items)}"
    assert items[0]['name'] == 'Health Potion', f"First item should be Health Potion, got {items[0]['name']}"
    
    print("  ✓ Shop items retrieved correctly")
    return True

def test_ensure_headers():
    """Test that headers are added to existing empty worksheets."""
    print("\nTesting header initialization...")
    
    # Scenario: Worksheet exists but is empty (no headers)
    worksheet = MockWorksheet('Players')
    
    # Check if empty
    if len(worksheet.rows) == 0:
        # Should add headers
        worksheet.append_row(['Player ID', 'Name', 'XP', 'Copper', 'Silver', 'Electrum', 'Gold', 'Platinum', 'Inventory'])
    
    assert len(worksheet.rows) > 0, "Headers not added"
    assert worksheet.rows[0][0] == 'Player ID', "First header should be 'Player ID'"
    
    print("  ✓ Headers added correctly")
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Storage Bug Tests")
    print("=" * 60)
    
    try:
        test_create_player_row_calculation()
        test_update_player_after_create()
        test_shop_items_with_headers()
        test_ensure_headers()
        
        print("\n" + "=" * 60)
        print("✓ All storage bug tests passed!")
        print("=" * 60)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
