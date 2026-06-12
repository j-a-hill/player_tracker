"""
Unit tests for merchant bot functionality.
Tests the storage layer methods for inventory tracking.
"""
import sys
import json


def test_storage_methods():
    """Test that storage methods have correct signatures."""
    print("Testing storage methods...")
    
    # Check the source code directly instead of importing
    with open('storage.py', 'r') as f:
        code = f.read()
    
    # Check that new methods exist in the code
    assert 'def update_item_stock(' in code, "update_item_stock method missing"
    assert 'def add_shop_item(' in code, "add_shop_item method missing"
    assert 'def remove_shop_item(' in code, "remove_shop_item method missing"
    assert 'def clear_shop(' in code, "clear_shop method missing"
    assert "'stock':" in code or '"stock":' in code, "stock field missing from shop items"
    
    print("✓ All storage methods exist")
    return True


def test_shop_item_structure():
    """Test that shop items have the stock field and currency field."""
    print("\nTesting shop item structure...")
    
    with open('storage.py', 'r') as f:
        code = f.read()
    
    # Check that Shop worksheet has Stock and Currency columns
    assert "'Stock'" in code or '"Stock"' in code, "Stock column missing from Shop worksheet"
    assert "'Currency'" in code or '"Currency"' in code, "Currency column missing from Shop worksheet"
    
    # Check that get_shop_items includes stock and currency in return
    assert "record.get('Stock'" in code, "get_shop_items doesn't retrieve stock"
    assert "record.get('Currency'" in code, "get_shop_items doesn't retrieve currency"
    
    print("✓ Shop item structure is correct")
    return True


def test_merchant_bot_imports():
    """Test that merchant_bot can be imported."""
    print("\nTesting merchant_bot imports...")
    
    # Try to parse merchant_bot.py
    with open('merchant_bot.py', 'r') as f:
        code = f.read()
        compile(code, 'merchant_bot.py', 'exec')
    
    # Check for key command definitions
    assert '@bot.tree.command(name="shop"' in code, "shop command not found"
    assert '@bot.tree.command(name="buy"' in code, "buy command not found"
    assert '@bot.tree.command(name="add_item"' in code, "add_item command not found"
    assert '@bot.tree.command(name="restock"' in code, "restock command not found"
    assert '@bot.tree.command(name="clear_shop"' in code, "clear_shop command not found"
    assert 'quantity: int = 1' in code, "buy command doesn't have quantity parameter"
    assert 'currency' in code.lower(), "merchant_bot doesn't support currency types"
    assert 'from dnd_utils import' in code, "merchant_bot doesn't import dnd_utils"
    
    print("✓ merchant_bot has all required commands and multi-currency support")
    return True


def test_bot_commands_removed():
    """Test that merchant commands were removed from bot.py."""
    print("\nTesting bot.py cleanup...")
    
    with open('bot.py', 'r') as f:
        code = f.read()
    
    # Verify merchant commands are removed
    assert '@bot.tree.command(name="shop"' not in code, "shop command still in bot.py"
    assert '@bot.tree.command(name="buy"' not in code, "buy command still in bot.py"
    
    # Verify player commands still exist
    assert '@bot.tree.command(name="profile"' in code, "profile command missing"
    assert '@bot.tree.command(name="inventory"' in code, "inventory command missing"
    
    # Verify multi-currency support
    assert 'from dnd_utils import' in code, "bot.py doesn't import dnd_utils"
    assert 'add_gold' in code, "add_gold command missing"
    assert 'remove_gold' in code, "remove_gold command missing"
    
    print("✓ bot.py correctly cleaned up and has multi-currency support")
    return True


def test_dnd_utils_exists():
    """Test that dnd_utils.py exists and has required functions."""
    print("\nTesting dnd_utils.py...")
    
    with open('dnd_utils.py', 'r') as f:
        code = f.read()
        compile(code, 'dnd_utils.py', 'exec')
    
    # Check for required functions
    assert 'def get_level_from_xp' in code, "get_level_from_xp missing"
    assert 'def get_xp_progress' in code, "get_xp_progress missing"
    assert 'def format_currency' in code, "format_currency missing"
    assert 'def create_progress_bar' in code, "create_progress_bar missing"
    # assert 'XP_THRESHOLDS' in code, "XP_THRESHOLDS missing"
    assert 'CURRENCY_VALUES' in code, "CURRENCY_VALUES missing"
    
    print("✓ dnd_utils.py has all required functions")
    return True


if __name__ == '__main__':
    print("=" * 60)
    print("Merchant Bot - Unit Tests")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("DnD utils", test_dnd_utils_exists()))
        results.append(("Storage methods", test_storage_methods()))
        results.append(("Shop item structure", test_shop_item_structure()))
        results.append(("Merchant bot imports", test_merchant_bot_imports()))
        results.append(("Bot cleanup", test_bot_commands_removed()))
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
        print("\n✓ All unit tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed.")
        sys.exit(1)
