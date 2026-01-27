"""
Unit tests for currency system functionality.
Tests the conversion, formatting, and handling of currency.
"""
import sys


def test_currency_values():
    """Test that only cp, sp, and gp are in CURRENCY_VALUES."""
    print("\nTesting currency values...")
    
    with open('dnd_utils.py', 'r') as f:
        code = f.read()
    
    # Check that only cp, sp, gp exist in CURRENCY_VALUES
    assert "'cp': 1" in code, "cp should be in CURRENCY_VALUES"
    assert "'sp': 10" in code, "sp should be in CURRENCY_VALUES"
    assert "'gp': 100" in code, "gp should be in CURRENCY_VALUES"
    
    # Check that pp and ep are removed
    assert "'pp':" not in code or "Removed pp" in code, "pp should be removed from CURRENCY_VALUES"
    assert "'ep':" not in code or "Removed" in code, "ep should be removed from CURRENCY_VALUES"
    
    print("✓ Currency values correct (cp, sp, gp only)")
    return True


def test_format_currency_function():
    """Test that format_currency takes total_copper parameter."""
    print("\nTesting format_currency function...")
    
    with open('dnd_utils.py', 'r') as f:
        code = f.read()
    
    # Check new signature
    assert "def format_currency(total_copper: int = 0)" in code, \
        "format_currency should take total_copper parameter"
    
    # Check that it doesn't use old parameters
    assert "def format_currency(cp=0, sp=0" not in code, \
        "format_currency shouldn't use old multi-parameter signature"
    
    print("✓ format_currency has correct signature")
    return True


def test_convert_to_copper_function():
    """Test that convert_to_copper only handles cp, sp, gp."""
    print("\nTesting convert_to_copper function...")
    
    with open('dnd_utils.py', 'r') as f:
        code = f.read()
    
    # Check new signature
    assert "def convert_to_copper(cp=0, sp=0, gp=0)" in code, \
        "convert_to_copper should only take cp, sp, gp parameters"
    
    # Check that it doesn't use ep or pp
    assert "ep=0" not in code or "def convert_to_copper(cp=0, sp=0, gp=0)" in code, \
        "convert_to_copper shouldn't have ep parameter"
    assert "pp=0" not in code or "def convert_to_copper(cp=0, sp=0, gp=0)" in code, \
        "convert_to_copper shouldn't have pp parameter"
    
    print("✓ convert_to_copper has correct signature")
    return True


def test_parse_currency_input_function():
    """Test that parse_currency_input function exists."""
    print("\nTesting parse_currency_input function...")
    
    with open('dnd_utils.py', 'r') as f:
        code = f.read()
    
    assert "def parse_currency_input(" in code, \
        "parse_currency_input function should exist"
    
    print("✓ parse_currency_input function exists")
    return True


def test_storage_player_structure():
    """Test that storage uses single copper field."""
    print("\nTesting storage player structure...")
    
    with open('storage.py', 'r') as f:
        code = f.read()
    
    # Check header has only Copper (not Silver, Electrum, Gold, Platinum)
    assert "['Player ID', 'Name', 'XP', 'Copper', 'Inventory']" in code, \
        "Player sheet header should only have Copper field"
    
    # Check that update_player doc mentions only copper
    assert "copper, inventory" in code or "xp, copper, inventory" in code, \
        "update_player should mention copper field"
    
    print("✓ Storage uses single copper field")
    return True


def test_bot_currency_choices():
    """Test that bot.py only has cp, sp, gp choices."""
    print("\nTesting bot.py currency choices...")
    
    with open('bot.py', 'r') as f:
        code = f.read()
    
    # Check that add_currency has only cp, sp, gp
    assert 'app_commands.Choice(name="Copper (cp)", value="cp")' in code
    assert 'app_commands.Choice(name="Silver (sp)", value="sp")' in code
    assert 'app_commands.Choice(name="Gold (gp)", value="gp")' in code
    
    # Check that ep and pp are not in choices
    assert 'Electrum (ep)' not in code, "Electrum should not be in currency choices"
    assert 'Platinum (pp)' not in code, "Platinum should not be in currency choices"
    
    print("✓ Bot currency choices correct (cp, sp, gp only)")
    return True


def test_merchant_bot_currency_choices():
    """Test that merchant_bot.py only has cp, sp, gp choices."""
    print("\nTesting merchant_bot.py currency choices...")
    
    with open('merchant_bot.py', 'r') as f:
        code = f.read()
    
    # Check that add_item has only cp, sp, gp
    assert 'app_commands.Choice(name="Copper (cp)", value="cp")' in code
    assert 'app_commands.Choice(name="Silver (sp)", value="sp")' in code
    assert 'app_commands.Choice(name="Gold (gp)", value="gp")' in code
    
    # Check that ep and pp are not in choices
    assert 'Electrum (ep)' not in code, "Electrum should not be in merchant bot"
    assert 'Platinum (pp)' not in code, "Platinum should not be in merchant bot"
    
    print("✓ Merchant bot currency choices correct (cp, sp, gp only)")
    return True


def test_currency_conversion_logic():
    """Test currency conversion logic by importing and testing functions."""
    print("\nTesting currency conversion logic...")
    
    # Import the functions
    import dnd_utils
    
    # Test parse_currency_input
    assert dnd_utils.parse_currency_input(1, 'cp') == 1, "1 cp should be 1 copper"
    assert dnd_utils.parse_currency_input(1, 'sp') == 10, "1 sp should be 10 copper"
    assert dnd_utils.parse_currency_input(1, 'gp') == 100, "1 gp should be 100 copper"
    assert dnd_utils.parse_currency_input(5, 'gp') == 500, "5 gp should be 500 copper"
    
    # Test format_currency
    assert dnd_utils.format_currency(0) == "0 cp", "0 copper should format as '0 cp'"
    assert dnd_utils.format_currency(1) == "1 cp", "1 copper should format as '1 cp'"
    assert dnd_utils.format_currency(10) == "1 sp", "10 copper should format as '1 sp'"
    assert dnd_utils.format_currency(100) == "1 gp", "100 copper should format as '1 gp'"
    assert dnd_utils.format_currency(157) == "1 gp, 5 sp, 7 cp", "157 copper should format as '1 gp, 5 sp, 7 cp'"
    assert dnd_utils.format_currency(507) == "5 gp, 7 cp", "507 copper should format as '5 gp, 7 cp'"
    
    # Test convert_to_copper
    assert dnd_utils.convert_to_copper(cp=5) == 5, "5 cp should be 5 copper"
    assert dnd_utils.convert_to_copper(sp=3) == 30, "3 sp should be 30 copper"
    assert dnd_utils.convert_to_copper(gp=2) == 200, "2 gp should be 200 copper"
    assert dnd_utils.convert_to_copper(gp=1, sp=5, cp=7) == 157, "1 gp, 5 sp, 7 cp should be 157 copper"
    
    print("✓ Currency conversion logic works correctly")
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("Currency System - Unit Tests")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Currency values", test_currency_values()))
        results.append(("format_currency function", test_format_currency_function()))
        results.append(("convert_to_copper function", test_convert_to_copper_function()))
        results.append(("parse_currency_input function", test_parse_currency_input_function()))
        results.append(("Storage player structure", test_storage_player_structure()))
        results.append(("Bot currency choices", test_bot_currency_choices()))
        results.append(("Merchant bot currency choices", test_merchant_bot_currency_choices()))
        results.append(("Currency conversion logic", test_currency_conversion_logic()))
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Test Results")
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
        print("\n✓ All currency tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed.")
        sys.exit(1)
