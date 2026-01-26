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
        except gspread.exceptions.WorksheetNotFound:
            self.players_sheet = self.spreadsheet.add_worksheet('Players', 100, 10)
            self.players_sheet.append_row(['Player ID', 'Name', 'XP', 'Gold', 'Inventory'])
        
        try:
            self.shop_sheet = self.spreadsheet.worksheet('Shop')
        except gspread.exceptions.WorksheetNotFound:
            self.shop_sheet = self.spreadsheet.add_worksheet('Shop', 100, 10)
            self.shop_sheet.append_row(['Item Name', 'Price', 'Description'])
            # Add some default items
            self.shop_sheet.append_row(['Health Potion', '50', 'Restores 50 HP'])
            self.shop_sheet.append_row(['Mana Potion', '40', 'Restores 30 MP'])
            self.shop_sheet.append_row(['Sword', '100', 'A basic sword'])
            self.shop_sheet.append_row(['Shield', '80', 'A basic shield'])
    
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
                    
                    return {
                        'player_id': str(record.get('Player ID')),
                        'name': record.get('Name', ''),
                        'xp': int(record.get('XP', 0)),
                        'gold': int(record.get('Gold', 0)),
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
            return {'player_id': player_id, 'name': name, 'xp': 0, 'gold': 0, 'inventory': []}
            
        try:
            self.players_sheet.append_row([str(player_id), name, 0, 0, '[]'])
            return {
                'player_id': str(player_id),
                'name': name,
                'xp': 0,
                'gold': 0,
                'inventory': []
            }
        except Exception as e:
            print(f"Error creating player: {e}")
            return {'player_id': player_id, 'name': name, 'xp': 0, 'gold': 0, 'inventory': []}
    
    def update_player(self, player_id: str, **kwargs):
        """Update player data."""
        if not self.players_sheet:
            return
            
        try:
            player = self.get_player(player_id)
            if not player:
                return
            
            row = player['row']
            
            if 'xp' in kwargs:
                self.players_sheet.update_cell(row, 3, kwargs['xp'])
            if 'gold' in kwargs:
                self.players_sheet.update_cell(row, 4, kwargs['gold'])
            if 'inventory' in kwargs:
                inventory_json = json.dumps(kwargs['inventory'])
                self.players_sheet.update_cell(row, 5, inventory_json)
        except Exception as e:
            print(f"Error updating player: {e}")
    
    def get_shop_items(self) -> List[Dict]:
        """Get all shop items."""
        if not self.shop_sheet:
            return []
            
        try:
            records = self.shop_sheet.get_all_records()
            return [
                {
                    'name': record.get('Item Name', ''),
                    'price': int(record.get('Price', 0)),
                    'description': record.get('Description', '')
                }
                for record in records
            ]
        except Exception as e:
            print(f"Error getting shop items: {e}")
            return []
