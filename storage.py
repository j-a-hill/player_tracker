"""
Backend storage using Google Sheets for player data.
"""
import gspread
from google.oauth2.service_account import Credentials
import json
from typing import Dict, List, Optional


class PlayerStorage:
    """Manages player data in Google Sheets."""
    
    def __init__(self, sheet_id: str, credentials_file: str = 'credentials.json'):
        """
        Initialize the storage backend.
        
        Args:
            sheet_id: Google Sheets ID
            credentials_file: Path to Google service account credentials
        """
        self.sheet_id = sheet_id
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        try:
            creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(sheet_id)
            self._ensure_worksheets()
        except Exception as e:
            print(f"Warning: Could not connect to Google Sheets: {e}")
            self.client = None
            self.spreadsheet = None
    
    def _ensure_worksheets(self):
        """Ensure required worksheets exist."""
        if not self.spreadsheet:
            return
            
        try:
            self.players_sheet = self.spreadsheet.worksheet('Players')
            # Check if headers exist, if not add them
            existing_data = self.players_sheet.get_all_values()
            if not existing_data or len(existing_data) == 0:
                self.players_sheet.append_row(['Player ID', 'Name', 'XP', 'Copper', 'Inventory'])
            elif existing_data[0] != ['Player ID', 'Name', 'XP', 'Copper', 'Inventory']:
                # Headers exist but are incorrect, insert them at the top
                self.players_sheet.insert_row(['Player ID', 'Name', 'XP', 'Copper', 'Inventory'], 1)
        except gspread.exceptions.WorksheetNotFound:
            self.players_sheet = self.spreadsheet.add_worksheet('Players', 100, 10)
            self.players_sheet.append_row(['Player ID', 'Name', 'XP', 'Copper', 'Inventory'])
        
        # Training sheet for skills and languages
        try:
            self.training_sheet = self.spreadsheet.worksheet('Training')
            existing_data = self.training_sheet.get_all_values()
            if not existing_data or len(existing_data) == 0:
                self.training_sheet.append_row(['Player ID', 'Training Type', 'Skill/Language', 'Days Spent', 'Days Required', 'Status'])
        except gspread.exceptions.WorksheetNotFound:
            self.training_sheet = self.spreadsheet.add_worksheet('Training', 100, 10)
            self.training_sheet.append_row(['Player ID', 'Training Type', 'Skill/Language', 'Days Spent', 'Days Required', 'Status'])
        
        # Training options sheet
        # Define default training options once
        default_skills = [
            ['Skill', 'Acrobatics', 'Dexterity-based physical agility'],
            ['Skill', 'Animal Handling', 'Wisdom-based creature interaction'],
            ['Skill', 'Arcana', 'Intelligence-based magical knowledge'],
            ['Skill', 'Athletics', 'Strength-based physical prowess'],
            ['Skill', 'Deception', 'Charisma-based lying and misdirection'],
            ['Skill', 'History', 'Intelligence-based historical knowledge'],
            ['Skill', 'Insight', 'Wisdom-based reading people'],
            ['Skill', 'Intimidation', 'Charisma-based threats and fear'],
            ['Skill', 'Investigation', 'Intelligence-based searching and deduction'],
            ['Skill', 'Medicine', 'Wisdom-based healing knowledge'],
            ['Skill', 'Nature', 'Intelligence-based natural world knowledge'],
            ['Skill', 'Perception', 'Wisdom-based awareness'],
            ['Skill', 'Performance', 'Charisma-based entertainment'],
            ['Skill', 'Persuasion', 'Charisma-based convincing others'],
            ['Skill', 'Religion', 'Intelligence-based religious knowledge'],
            ['Skill', 'Sleight of Hand', 'Dexterity-based manual tricks'],
            ['Skill', 'Stealth', 'Dexterity-based hiding and sneaking'],
            ['Skill', 'Survival', 'Wisdom-based wilderness skills'],
        ]
        default_languages = [
            ['Language', 'Common', 'Standard language'],
            ['Language', 'Dwarvish', 'Language of dwarves'],
            ['Language', 'Elvish', 'Language of elves'],
            ['Language', 'Giant', 'Language of giants'],
            ['Language', 'Gnomish', 'Language of gnomes'],
            ['Language', 'Goblin', 'Language of goblinoids'],
            ['Language', 'Halfling', 'Language of halflings'],
            ['Language', 'Orc', 'Language of orcs'],
            ['Language', 'Abyssal', 'Language of demons'],
            ['Language', 'Celestial', 'Language of celestials'],
            ['Language', 'Draconic', 'Language of dragons'],
            ['Language', 'Deep Speech', 'Language of aberrations'],
            ['Language', 'Infernal', 'Language of devils'],
            ['Language', 'Primordial', 'Language of elementals'],
            ['Language', 'Sylvan', 'Language of fey'],
            ['Language', 'Undercommon', 'Language of the Underdark'],
        ]
        
        try:
            self.training_options_sheet = self.spreadsheet.worksheet('TrainingOptions')
            existing_data = self.training_options_sheet.get_all_values()
            if not existing_data or len(existing_data) == 0:
                self.training_options_sheet.append_row(['Type', 'Name', 'Description'])
                for skill in default_skills:
                    self.training_options_sheet.append_row(skill)
                for lang in default_languages:
                    self.training_options_sheet.append_row(lang)
        except gspread.exceptions.WorksheetNotFound:
            self.training_options_sheet = self.spreadsheet.add_worksheet('TrainingOptions', 100, 10)
            self.training_options_sheet.append_row(['Type', 'Name', 'Description'])
            for skill in default_skills:
                self.training_options_sheet.append_row(skill)
            for lang in default_languages:
                self.training_options_sheet.append_row(lang)
        
        # Timekeeper data sheet
        try:
            self.timekeeper_sheet = self.spreadsheet.worksheet('Timekeeper')
            existing_data = self.timekeeper_sheet.get_all_values()
            if not existing_data or len(existing_data) == 0:
                self.timekeeper_sheet.append_row(['Key', 'Value'])
                self.timekeeper_sheet.append_row(['current_game_time', ''])
                self.timekeeper_sheet.append_row(['last_real_time', ''])
        except gspread.exceptions.WorksheetNotFound:
            self.timekeeper_sheet = self.spreadsheet.add_worksheet('Timekeeper', 100, 10)
            self.timekeeper_sheet.append_row(['Key', 'Value'])
            self.timekeeper_sheet.append_row(['current_game_time', ''])
            self.timekeeper_sheet.append_row(['last_real_time', ''])
        
        # Inn configuration sheet
        try:
            self.inn_sheet = self.spreadsheet.worksheet('Inn')
            existing_data = self.inn_sheet.get_all_values()
            if not existing_data or len(existing_data) == 0:
                self.inn_sheet.append_row(['Player ID', 'Exempt', 'Custom Cost'])
        except gspread.exceptions.WorksheetNotFound:
            self.inn_sheet = self.spreadsheet.add_worksheet('Inn', 100, 10)
            self.inn_sheet.append_row(['Player ID', 'Exempt', 'Custom Cost'])
        
        try:
            self.shop_sheet = self.spreadsheet.worksheet('Shop')
            # Check if headers exist, if not add them
            existing_data = self.shop_sheet.get_all_values()
            if not existing_data or len(existing_data) == 0:
                self.shop_sheet.append_row(['Item Name', 'Price', 'Currency', 'Description', 'Stock'])
                # Add some default items
                self.shop_sheet.append_row(['Health Potion', '50', 'gp', 'Restores 50 HP', '10'])
                self.shop_sheet.append_row(['Mana Potion', '40', 'gp', 'Restores 30 MP', '10'])
                self.shop_sheet.append_row(['Sword', '100', 'gp', 'A basic sword', '5'])
                self.shop_sheet.append_row(['Shield', '80', 'gp', 'A basic shield', '5'])
            elif existing_data[0] != ['Item Name', 'Price', 'Currency', 'Description', 'Stock']:
                # Headers exist but are incorrect, insert them at the top
                self.shop_sheet.insert_row(['Item Name', 'Price', 'Currency', 'Description', 'Stock'], 1)
        except gspread.exceptions.WorksheetNotFound:
            self.shop_sheet = self.spreadsheet.add_worksheet('Shop', 100, 10)
            self.shop_sheet.append_row(['Item Name', 'Price', 'Currency', 'Description', 'Stock'])
            # Add some default items
            self.shop_sheet.append_row(['Health Potion', '50', 'gp', 'Restores 50 HP', '10'])
            self.shop_sheet.append_row(['Mana Potion', '40', 'gp', 'Restores 30 MP', '10'])
            self.shop_sheet.append_row(['Sword', '100', 'gp', 'A basic sword', '5'])
            self.shop_sheet.append_row(['Shield', '80', 'gp', 'A basic shield', '5'])
    
    def get_player(self, player_id: str) -> Optional[Dict]:
        """Get player data by Discord ID."""
        if not self.players_sheet:
            return None
            
        try:
            records = self.players_sheet.get_all_records()
            for idx, record in enumerate(records, start=2):  # Start at 2 (header is row 1)
                if str(record.get('Player ID')) == str(player_id):
                    inventory = record.get('Inventory', '[]')
                    if isinstance(inventory, str):
                        try:
                            inventory = json.loads(inventory) if inventory else []
                        except json.JSONDecodeError:
                            inventory = []
                    
                    try:
                        xp = int(record.get('XP', 0))
                    except (ValueError, TypeError):
                        xp = 0
                    
                    # Get copper value (single currency field)
                    try:
                        copper = int(record.get('Copper', 0))
                    except (ValueError, TypeError):
                        copper = 0
                    
                    return {
                        'player_id': str(record.get('Player ID')),
                        'name': record.get('Name', ''),
                        'xp': xp,
                        'copper': copper,
                        'inventory': inventory,
                        'row': idx
                    }
            return None
        except Exception as e:
            print(f"Error getting player: {e}")
            return None
    
    def create_player(self, player_id: str, name: str) -> Dict:
        """Create a new player."""
        if not self.players_sheet:
            return {
                'player_id': player_id,
                'name': name,
                'xp': 0,
                'copper': 0,
                'inventory': []
            }
            
        try:
            # Append the new player row - this is an atomic operation
            self.players_sheet.append_row([str(player_id), name, 0, 0, '[]'])
            
            # Get the actual row number by counting existing rows after append
            # This is more reliable than using row_count which includes empty rows
            # Note: We get the row count AFTER appending to ensure we capture the row
            # where our data was actually placed. This approach is safe because:
            # 1. append_row is atomic and places data in the first empty row
            # 2. get_all_values() returns all rows up to the last row with data
            # 3. Since we just appended, our row is the last row with data
            next_row = len(self.players_sheet.get_all_values())
            
            return {
                'player_id': str(player_id),
                'name': name,
                'xp': 0,
                'copper': 0,
                'inventory': [],
                'row': next_row  # Include row number for immediate updates
            }
        except Exception as e:
            print(f"Error creating player: {e}")
            return {
                'player_id': player_id,
                'name': name,
                'xp': 0,
                'copper': 0,
                'inventory': []
            }
    
    def update_player(self, player_id: str, player_data: Optional[Dict] = None, **kwargs):
        """
        Update player data.
        
        Args:
            player_id: Discord ID of the player
            player_data: Optional cached player data (from recent get_player or create_player)
            **kwargs: Fields to update (xp, copper, inventory)
        """
        if not self.players_sheet:
            return
            
        try:
            # Use provided player_data if available, otherwise fetch it
            player = player_data if player_data else self.get_player(player_id)
            if not player:
                print(f"Warning: Player {player_id} not found for update")
                return
            
            row = player.get('row')
            if not row:
                print(f"Warning: No row number for player {player_id}")
                return
            
            # Collect all updates to do them in a single batch
            updates = []
            
            if 'xp' in kwargs:
                updates.append({'range': f'C{row}', 'values': [[kwargs['xp']]]})
            if 'copper' in kwargs:
                updates.append({'range': f'D{row}', 'values': [[kwargs['copper']]]})
            if 'inventory' in kwargs:
                inventory_json = json.dumps(kwargs['inventory'])
                updates.append({'range': f'E{row}', 'values': [[inventory_json]]})
            
            # Perform batch update if there are any updates
            if updates:
                self.players_sheet.batch_update(updates)
        except Exception as e:
            print(f"Error updating player: {e}")
    
    def get_shop_items(self) -> List[Dict]:
        """Get all shop items."""
        if not self.shop_sheet:
            return []
            
        try:
            records = self.shop_sheet.get_all_records()
            items = []
            for idx, record in enumerate(records, start=2):  # Start at 2 (header is row 1)
                # Skip items with empty or missing name
                item_name = record.get('Item Name', '').strip()
                if not item_name:
                    continue
                
                try:
                    price = int(record.get('Price', 0))
                except (ValueError, TypeError):
                    price = 0
                
                # Get currency type (default to 'gp' for backwards compatibility)
                currency = str(record.get('Currency') or 'gp').strip().lower()
                if currency not in ['cp', 'sp', 'gp']:
                    currency = 'gp'
                
                try:
                    stock = int(record.get('Stock', -1))  # -1 means unlimited
                except (ValueError, TypeError):
                    stock = -1
                
                items.append({
                    'name': item_name,
                    'price': price,
                    'currency': currency,
                    'description': record.get('Description', '').strip(),
                    'stock': stock,
                    'row': idx
                })
            return items
        except Exception as e:
            print(f"Error getting shop items: {e}")
            return []
    
    def update_item_stock(self, item_name: str, new_stock: int):
        """Update stock for a shop item."""
        if not self.shop_sheet:
            return False
            
        try:
            items = self.get_shop_items()
            for item in items:
                if item['name'].lower() == item_name.lower():
                    self.shop_sheet.update_cell(item['row'], 5, new_stock)
                    return True
            return False
        except Exception as e:
            print(f"Error updating stock: {e}")
            return False
    
    def add_shop_item(self, name: str, price: int, currency: str, description: str, stock: int = -1):
        """Add a new item to the shop."""
        if not self.shop_sheet:
            return False
            
        try:
            self.shop_sheet.append_row([name, price, currency, description, stock])
            return True
        except Exception as e:
            print(f"Error adding shop item: {e}")
            return False
    
    def remove_shop_item(self, item_name: str):
        """Remove an item from the shop."""
        if not self.shop_sheet:
            return False
            
        try:
            items = self.get_shop_items()
            for item in items:
                if item['name'].lower() == item_name.lower():
                    self.shop_sheet.delete_rows(item['row'])
                    return True
            return False
        except Exception as e:
            print(f"Error removing shop item: {e}")
            return False
    
    def clear_shop(self):
        """Clear all shop items (keeping headers)."""
        if not self.shop_sheet:
            return False
            
        try:
            # Get all rows except header
            num_rows = len(self.shop_sheet.get_all_values())
            if num_rows > 1:
                self.shop_sheet.delete_rows(2, num_rows)
            return True
        except Exception as e:
            print(f"Error clearing shop: {e}")
            return False
    
    # Training methods
    def get_training_options(self, training_type: Optional[str] = None) -> List[Dict]:
        """Get available training options (skills or languages)."""
        if not hasattr(self, 'training_options_sheet') or not self.training_options_sheet:
            return []
        
        try:
            records = self.training_options_sheet.get_all_records()
            options = []
            for record in records:
                option_type = record.get('Type', '').strip()
                if training_type and option_type.lower() != training_type.lower():
                    continue
                options.append({
                    'type': option_type,
                    'name': record.get('Name', '').strip(),
                    'description': record.get('Description', '').strip()
                })
            return options
        except Exception as e:
            print(f"Error getting training options: {e}")
            return []
    
    def get_player_training(self, player_id: str) -> List[Dict]:
        """Get player's current training progress."""
        if not hasattr(self, 'training_sheet') or not self.training_sheet:
            return []
        
        try:
            records = self.training_sheet.get_all_records()
            training = []
            for idx, record in enumerate(records, start=2):
                if str(record.get('Player ID')) == str(player_id):
                    training.append({
                        'training_type': record.get('Training Type', ''),
                        'skill_or_language': record.get('Skill/Language', ''),
                        'days_spent': int(record.get('Days Spent', 0)),
                        'days_required': int(record.get('Days Required', 250)),
                        'status': record.get('Status', 'In Progress'),
                        'row': idx
                    })
            return training
        except Exception as e:
            print(f"Error getting player training: {e}")
            return []
    
    def start_training(self, player_id: str, training_type: str, skill_or_language: str, days_required: int = 250):
        """Start training for a player."""
        if not hasattr(self, 'training_sheet') or not self.training_sheet:
            return False
        
        try:
            self.training_sheet.append_row([
                str(player_id),
                training_type,
                skill_or_language,
                0,  # days_spent
                days_required,
                'In Progress'
            ])
            return True
        except Exception as e:
            print(f"Error starting training: {e}")
            return False
    
    def update_training_progress(self, player_id: str, skill_or_language: str, days_to_add: int):
        """Update training progress for a player."""
        if not hasattr(self, 'training_sheet') or not self.training_sheet:
            return False
        
        try:
            training_list = self.get_player_training(player_id)
            for training in training_list:
                if training['skill_or_language'].lower() == skill_or_language.lower():
                    new_days = training['days_spent'] + days_to_add
                    row = training['row']
                    
                    # Check if training is complete
                    if new_days >= training['days_required']:
                        new_days = training['days_required']
                        status = 'Complete'
                    else:
                        status = 'In Progress'
                    
                    self.training_sheet.update_cell(row, 4, new_days)  # Days Spent
                    self.training_sheet.update_cell(row, 6, status)  # Status
                    return True
            return False
        except Exception as e:
            print(f"Error updating training progress: {e}")
            return False
    
    # Timekeeper methods
    def get_game_time(self) -> Optional[str]:
        """Get current in-game time."""
        if not hasattr(self, 'timekeeper_sheet') or not self.timekeeper_sheet:
            return None
        
        try:
            records = self.timekeeper_sheet.get_all_records()
            for record in records:
                if record.get('Key') == 'current_game_time':
                    return record.get('Value', '')
            return None
        except Exception as e:
            print(f"Error getting game time: {e}")
            return None
    
    def set_game_time(self, game_time: str):
        """Set current in-game time."""
        if not hasattr(self, 'timekeeper_sheet') or not self.timekeeper_sheet:
            return False
        
        try:
            records = self.timekeeper_sheet.get_all_records()
            for idx, record in enumerate(records, start=2):
                if record.get('Key') == 'current_game_time':
                    self.timekeeper_sheet.update_cell(idx, 2, game_time)
                    return True
            # If not found, add it
            self.timekeeper_sheet.append_row(['current_game_time', game_time])
            return True
        except Exception as e:
            print(f"Error setting game time: {e}")
            return False
    
    def get_last_real_time(self) -> Optional[str]:
        """Get last recorded real time."""
        if not hasattr(self, 'timekeeper_sheet') or not self.timekeeper_sheet:
            return None
        
        try:
            records = self.timekeeper_sheet.get_all_records()
            for record in records:
                if record.get('Key') == 'last_real_time':
                    return record.get('Value', '')
            return None
        except Exception as e:
            print(f"Error getting last real time: {e}")
            return None
    
    def set_last_real_time(self, real_time: str):
        """Set last recorded real time."""
        if not hasattr(self, 'timekeeper_sheet') or not self.timekeeper_sheet:
            return False
        
        try:
            records = self.timekeeper_sheet.get_all_records()
            for idx, record in enumerate(records, start=2):
                if record.get('Key') == 'last_real_time':
                    self.timekeeper_sheet.update_cell(idx, 2, real_time)
                    return True
            # If not found, add it
            self.timekeeper_sheet.append_row(['last_real_time', real_time])
            return True
        except Exception as e:
            print(f"Error setting last real time: {e}")
            return False
    
    # Inn methods
    def get_inn_config(self, player_id: str) -> Dict:
        """Get inn configuration for a player."""
        if not hasattr(self, 'inn_sheet') or not self.inn_sheet:
            return {'exempt': False, 'custom_cost': None}
        
        try:
            records = self.inn_sheet.get_all_records()
            for idx, record in enumerate(records, start=2):
                if str(record.get('Player ID')) == str(player_id):
                    exempt = str(record.get('Exempt', 'FALSE')).upper() == 'TRUE'
                    custom_cost = record.get('Custom Cost', '')
                    try:
                        custom_cost = int(custom_cost) if custom_cost else None
                    except (ValueError, TypeError):
                        custom_cost = None
                    return {
                        'exempt': exempt,
                        'custom_cost': custom_cost,
                        'row': idx
                    }
            return {'exempt': False, 'custom_cost': None}
        except Exception as e:
            print(f"Error getting inn config: {e}")
            return {'exempt': False, 'custom_cost': None}
    
    def set_inn_exempt(self, player_id: str, exempt: bool):
        """Set inn exemption for a player."""
        if not hasattr(self, 'inn_sheet') or not self.inn_sheet:
            return False
        
        try:
            config = self.get_inn_config(player_id)
            if 'row' in config:
                # Update existing
                self.inn_sheet.update_cell(config['row'], 2, 'TRUE' if exempt else 'FALSE')
            else:
                # Create new
                self.inn_sheet.append_row([str(player_id), 'TRUE' if exempt else 'FALSE', ''])
            return True
        except Exception as e:
            print(f"Error setting inn exempt: {e}")
            return False
    
    def set_inn_custom_cost(self, player_id: str, cost: Optional[int]):
        """Set custom inn cost for a player."""
        if not hasattr(self, 'inn_sheet') or not self.inn_sheet:
            return False
        
        try:
            config = self.get_inn_config(player_id)
            cost_value = str(cost) if cost is not None else ''
            if 'row' in config:
                # Update existing
                self.inn_sheet.update_cell(config['row'], 3, cost_value)
            else:
                # Create new
                self.inn_sheet.append_row([str(player_id), 'FALSE', cost_value])
            return True
        except Exception as e:
            print(f"Error setting inn custom cost: {e}")
            return False
    
    def get_all_players(self) -> List[Dict]:
        """Get all players."""
        if not self.players_sheet:
            return []
        
        try:
            records = self.players_sheet.get_all_records()
            players = []
            for idx, record in enumerate(records, start=2):
                inventory = record.get('Inventory', '[]')
                if isinstance(inventory, str):
                    try:
                        inventory = json.loads(inventory) if inventory else []
                    except json.JSONDecodeError:
                        inventory = []
                
                try:
                    xp = int(record.get('XP', 0))
                except (ValueError, TypeError):
                    xp = 0
                
                try:
                    copper = int(record.get('Copper', 0))
                except (ValueError, TypeError):
                    copper = 0
                
                players.append({
                    'player_id': str(record.get('Player ID')),
                    'name': record.get('Name', ''),
                    'xp': xp,
                    'copper': copper,
                    'inventory': inventory,
                    'row': idx
                })
            return players
        except Exception as e:
            print(f"Error getting all players: {e}")
            return []
