"""
Integration test to demonstrate the currency system working end-to-end.
Tests player creation, currency transactions, and purchases with the new system.
"""
import sys
import json


# Mock classes for testing (same as in test_bug_fixes.py)
class MockWorksheet:
    def __init__(self, name):
        self.name = name
        self.rows = []
        self.row_count = 1000
        
    def append_row(self, values):
        self.rows.append(list(values))
    
    def insert_row(self, values, index):
        self.rows.insert(index - 1, list(values))
    
    def get_all_values(self):
        return self.rows
    
    def get_all_records(self):
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
    
    def update_cell(self, row, col, value):
        while len(self.rows) < row:
            self.rows.append([])
        while len(self.rows[row - 1]) < col:
            self.rows[row - 1].append('')
        self.rows[row - 1][col - 1] = str(value)
    
    def batch_update(self, updates):
        import re
        for update in updates:
            range_str = update['range']
            values = update['values']
            match = re.match(r'([A-Z]+)(\d+)', range_str)
            if match:
                col_letter = match.group(1)
                row_num = int(match.group(2))
                col_num = ord(col_letter) - ord('A') + 1
                self.update_cell(row_num, col_num, values[0][0])
    
    def delete_rows(self, start, end=None):
        if end is None:
            end = start
        del self.rows[start-1:end]


def test_currency_storage_integration():
    """Test that the currency system works with storage layer."""
    print("\n" + "=" * 60)
    print("TEST: Currency Storage Integration")
    print("=" * 60)
    
    import dnd_utils
    
    # Create mock worksheet with new format (single Copper column)
    ws = MockWorksheet('Players')
    ws.append_row(['Player ID', 'Name', 'XP', 'Copper', 'Inventory'])
    
    # Simulate creating a player
    player_id = "123456789"
    name = "TestPlayer"
    ws.append_row([player_id, name, 0, 0, '[]'])
    
    print("\n1. Player created with 0 copper")
    records = ws.get_all_records()
    assert records[0]['Copper'] == 0, "New player should have 0 copper"
    print(f"   ✓ Player copper: {records[0]['Copper']}")
    
    # Add some gold (converting to copper)
    gold_to_add = 5
    copper_to_add = dnd_utils.parse_currency_input(gold_to_add, 'gp')
    new_copper = int(records[0]['Copper']) + copper_to_add
    
    # Update the player's copper
    updates = [{'range': 'D2', 'values': [[new_copper]]}]
    ws.batch_update(updates)
    
    print(f"\n2. Added {gold_to_add} gold ({copper_to_add} copper)")
    records = ws.get_all_records()
    assert int(records[0]['Copper']) == 500, "Player should have 500 copper"
    currency_display = dnd_utils.format_currency(int(records[0]['Copper']))
    print(f"   ✓ Player now has: {currency_display}")
    
    # Simulate a purchase
    item_price_gp = 2
    item_price_copper = dnd_utils.parse_currency_input(item_price_gp, 'gp')
    current_copper = int(records[0]['Copper'])
    
    print(f"\n3. Purchasing item for {item_price_gp} gp ({item_price_copper} copper)")
    
    if current_copper >= item_price_copper:
        new_copper = current_copper - item_price_copper
        updates = [{'range': 'D2', 'values': [[new_copper]]}]
        ws.batch_update(updates)
        print(f"   ✓ Purchase successful!")
        
        records = ws.get_all_records()
        currency_display = dnd_utils.format_currency(int(records[0]['Copper']))
        print(f"   ✓ Remaining: {currency_display}")
        assert int(records[0]['Copper']) == 300, "Player should have 300 copper remaining"
    else:
        print(f"   ✗ Not enough currency!")
        assert False, "Player should have enough currency"
    
    # Add mixed currency
    print("\n4. Adding mixed currency: 1 gp, 3 sp, 7 cp")
    copper_to_add = dnd_utils.convert_to_copper(gp=1, sp=3, cp=7)
    current_copper = int(records[0]['Copper'])
    new_copper = current_copper + copper_to_add
    
    updates = [{'range': 'D2', 'values': [[new_copper]]}]
    ws.batch_update(updates)
    
    records = ws.get_all_records()
    currency_display = dnd_utils.format_currency(int(records[0]['Copper']))
    print(f"   ✓ Added {copper_to_add} copper")
    print(f"   ✓ Total now: {currency_display}")
    assert int(records[0]['Copper']) == 437, "Player should have 437 copper"
    
    print("\n✓ Currency Storage Integration Test PASSED")
    return True


def test_shop_item_pricing():
    """Test that shop items work with the new currency system."""
    print("\n" + "=" * 60)
    print("TEST: Shop Item Pricing")
    print("=" * 60)
    
    import dnd_utils
    
    # Create mock shop worksheet
    ws = MockWorksheet('Shop')
    ws.append_row(['Item Name', 'Price', 'Currency', 'Description', 'Stock'])
    ws.append_row(['Health Potion', '50', 'gp', 'Restores 50 HP', '10'])
    ws.append_row(['Torch', '1', 'sp', 'Provides light', '20'])
    ws.append_row(['Rations', '5', 'cp', 'One day of food', '50'])
    
    records = ws.get_all_records()
    
    print("\n1. Shop items with different currency types:")
    for record in records:
        item_name = record['Item Name']
        price = int(record['Price'])
        currency = record['Currency']
        price_in_copper = dnd_utils.parse_currency_input(price, currency)
        display = dnd_utils.format_currency(price_in_copper)
        print(f"   - {item_name}: {price} {currency} = {display}")
    
    # Simulate player buying items
    print("\n2. Player purchases:")
    player_copper = 10000  # Player has 100 gp
    print(f"   Player starts with: {dnd_utils.format_currency(player_copper)}")
    
    # Buy 2 health potions
    item = records[0]
    quantity = 2
    total_cost = int(item['Price']) * quantity
    cost_in_copper = dnd_utils.parse_currency_input(total_cost, item['Currency'])
    
    print(f"\n   Buying {quantity}x {item['Item Name']} for {total_cost} {item['Currency']}")
    
    if player_copper >= cost_in_copper:
        player_copper -= cost_in_copper
        print(f"   ✓ Purchase successful!")
        print(f"   ✓ Remaining: {dnd_utils.format_currency(player_copper)}")
        assert player_copper == 0, "Player should have 0 copper after buying 2x 50gp items with 100gp"
    else:
        print(f"   ✗ Not enough currency!")
        assert False, "Player should have enough currency"
    
    print("\n✓ Shop Item Pricing Test PASSED")
    return True


def test_currency_conversions():
    """Test various currency conversion scenarios."""
    print("\n" + "=" * 60)
    print("TEST: Currency Conversion Scenarios")
    print("=" * 60)
    
    import dnd_utils
    
    scenarios = [
        {"name": "Exact gold", "copper": 500, "expected": "5 gp"},
        {"name": "Exact silver", "copper": 70, "expected": "7 sp"},
        {"name": "Exact copper", "copper": 7, "expected": "7 cp"},
        {"name": "Mixed 1", "copper": 157, "expected": "1 gp, 5 sp, 7 cp"},
        {"name": "Mixed 2", "copper": 537, "expected": "5 gp, 3 sp, 7 cp"},
        {"name": "No silver", "copper": 507, "expected": "5 gp, 7 cp"},
        {"name": "No copper", "copper": 530, "expected": "5 gp, 3 sp"},
        {"name": "Large amount", "copper": 12345, "expected": "123 gp, 4 sp, 5 cp"},
    ]
    
    print("\nTesting currency formatting:")
    for scenario in scenarios:
        result = dnd_utils.format_currency(scenario['copper'])
        expected = scenario['expected']
        status = "✓" if result == expected else "✗"
        print(f"   {status} {scenario['name']}: {scenario['copper']} cp → {result}")
        assert result == expected, f"Expected '{expected}' but got '{result}'"
    
    print("\n✓ Currency Conversion Scenarios Test PASSED")
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("Currency System - Integration Tests")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Currency Storage Integration", test_currency_storage_integration()))
        results.append(("Shop Item Pricing", test_shop_item_pricing()))
        results.append(("Currency Conversion Scenarios", test_currency_conversions()))
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Integration Test Results")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All integration tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed.")
        sys.exit(1)
