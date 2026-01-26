"""
Test script to verify bot components work correctly.
This script tests the basic functionality without requiring actual Discord/Google credentials.
"""
import sys
import os

def test_imports():
    """Test that all files can be parsed as valid Python."""
    print("Testing Python syntax...")
    
    # Test bot.py syntax
    try:
        with open('bot.py', 'r') as f:
            compile(f.read(), 'bot.py', 'exec')
        print("✓ bot.py syntax is valid")
    except SyntaxError as e:
        print(f"✗ bot.py has syntax error: {e}")
        return False
    
    # Test merchant_bot.py syntax
    try:
        with open('merchant_bot.py', 'r') as f:
            compile(f.read(), 'merchant_bot.py', 'exec')
        print("✓ merchant_bot.py syntax is valid")
    except SyntaxError as e:
        print(f"✗ merchant_bot.py has syntax error: {e}")
        return False
    
    # Test storage.py syntax
    try:
        with open('storage.py', 'r') as f:
            compile(f.read(), 'storage.py', 'exec')
        print("✓ storage.py syntax is valid")
    except SyntaxError as e:
        print(f"✗ storage.py has syntax error: {e}")
        return False
    
    # Test dnd_utils.py syntax
    try:
        with open('dnd_utils.py', 'r') as f:
            compile(f.read(), 'dnd_utils.py', 'exec')
        print("✓ dnd_utils.py syntax is valid")
    except SyntaxError as e:
        print(f"✗ dnd_utils.py has syntax error: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    
    required_files = [
        'bot.py',
        'merchant_bot.py',
        'storage.py',
        'dnd_utils.py',
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'credentials.json.example',
        'README.md'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} is missing")
            all_exist = False
    
    return all_exist

def test_env_example():
    """Test that .env.example has required variables."""
    print("\nTesting .env.example...")
    
    required_vars = ['DISCORD_TOKEN', 'MERCHANT_BOT_TOKEN', 'GOOGLE_SHEET_ID', 'GM_ROLE_ID']
    
    with open('.env.example', 'r') as f:
        content = f.read()
    
    all_present = True
    for var in required_vars:
        if var in content:
            print(f"✓ {var} is defined")
        else:
            print(f"✗ {var} is missing")
            all_present = False
    
    return all_present

def test_requirements():
    """Test that requirements.txt has necessary packages."""
    print("\nTesting requirements.txt...")
    
    required_packages = ['discord.py', 'python-dotenv', 'gspread', 'google-auth']
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    all_present = True
    for package in required_packages:
        if package in content:
            print(f"✓ {package} is listed")
        else:
            print(f"✗ {package} is missing")
            all_present = False
    
    return all_present

def test_readme():
    """Test that README has essential sections."""
    print("\nTesting README.md...")
    
    required_sections = ['Setup', 'Usage', 'Features', 'Installation']
    
    with open('README.md', 'r') as f:
        content = f.read()
    
    all_present = True
    for section in required_sections:
        if section in content:
            print(f"✓ {section} section exists")
        else:
            print(f"✗ {section} section is missing")
            all_present = False
    
    return all_present


def test_dnd_utils():
    """Test D&D 5e utility functions."""
    print("\nTesting D&D 5e utilities...")
    
    try:
        from dnd_utils import (
            get_level_from_xp,
            get_xp_for_level,
            get_xp_progress,
            format_currency,
            create_progress_bar
        )
        
        # Test level calculation
        level = get_level_from_xp(0)
        if level == 1:
            print("✓ Level 1 at 0 XP")
        else:
            print(f"✗ Expected level 1, got {level}")
            return False
        
        level = get_level_from_xp(300)
        if level == 2:
            print("✓ Level 2 at 300 XP")
        else:
            print(f"✗ Expected level 2, got {level}")
            return False
        
        level = get_level_from_xp(355000)
        if level == 20:
            print("✓ Level 20 at 355000 XP")
        else:
            print(f"✗ Expected level 20, got {level}")
            return False
        
        # Test XP threshold
        xp = get_xp_for_level(5)
        if xp == 6500:
            print("✓ Level 5 requires 6500 XP")
        else:
            print(f"✗ Expected 6500 XP for level 5, got {xp}")
            return False
        
        # Test currency formatting
        currency_str = format_currency(gp=10, sp=5)
        if "10 gp" in currency_str and "5 sp" in currency_str:
            print("✓ Currency formatting works")
        else:
            print(f"✗ Currency formatting failed: {currency_str}")
            return False
        
        # Test progress bar
        bar = create_progress_bar(50.0)
        if "50.0%" in bar:
            print("✓ Progress bar creation works")
        else:
            print(f"✗ Progress bar failed: {bar}")
            return False
        
        print("✓ All D&D utility tests passed")
        return True
    except Exception as e:
        print(f"✗ D&D utils test failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Player Tracker Bot - Component Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Syntax validation", test_imports()))
    results.append(("File structure", test_file_structure()))
    results.append((".env.example", test_env_example()))
    results.append(("requirements.txt", test_requirements()))
    results.append(("README.md", test_readme()))
    results.append(("D&D 5e utilities", test_dnd_utils()))
    
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
        print("\n✓ All tests passed! The bot is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up Google Sheets and get credentials.json")
        print("3. Create Discord bot and get token")
        print("4. Copy .env.example to .env and fill in your credentials")
        print("5. Run: python bot.py")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)
