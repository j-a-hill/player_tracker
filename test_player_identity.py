"""
Players are keyed on Discord ID only. A changed display name, or a failed
sheet read, must never add a second row for the same ID.
"""
import sys
import types

# storage.py imports gspread and google auth at module level; stub them so the
# test runs without those packages or any credentials.
for mod in ['gspread', 'google', 'google.oauth2', 'google.oauth2.service_account']:
    sys.modules.setdefault(mod, types.ModuleType(mod))
sys.modules['google.oauth2.service_account'].Credentials = object

from storage import PlayerStorage, PlayerLookupError  # noqa: E402

HEADERS = ['Player ID', 'Name', 'Sessions', 'Copper', 'Inventory']


class FakeSheet:
    def __init__(self, rows):
        self.rows = [list(r) for r in rows]
        self.fail_reads = False
        self.appends = 0

    def get_all_values(self):
        if self.fail_reads:
            raise RuntimeError("APIError: [429] Quota exceeded")
        return [list(r) for r in self.rows]

    def append_row(self, values):
        self.appends += 1
        self.rows.append([str(v) for v in values])

    def update_cell(self, row, col, value):
        self.rows[row - 1][col - 1] = value


def make_storage(rows):
    storage = PlayerStorage.__new__(PlayerStorage)  # skip Google auth
    storage.players_sheet = FakeSheet([HEADERS] + rows)
    return storage


LOBSTREX = ['177500483500376064', 'Lobstrex', '0', '5700', '["Lantern, Hooded"]']


def test_name_change_updates_existing_row():
    s = make_storage([LOBSTREX])
    player = s.get_or_create_player('177500483500376064', 'Sylphiette')
    assert s.players_sheet.appends == 0
    assert len(s.players_sheet.rows) == 2
    assert player['row'] == 2
    assert player['copper'] == 5700
    assert player['inventory'] == ['Lantern, Hooded']
    assert player['name'] == 'Sylphiette'
    assert s.players_sheet.rows[1][1] == 'Sylphiette'


def test_read_failure_raises_and_writes_nothing():
    s = make_storage([LOBSTREX])
    s.players_sheet.fail_reads = True
    try:
        s.get_or_create_player('177500483500376064', 'Sylphiette')
    except PlayerLookupError:
        pass
    else:
        raise AssertionError("expected PlayerLookupError")
    assert s.players_sheet.appends == 0


def test_old_get_then_create_pattern_cannot_duplicate():
    s = make_storage([LOBSTREX])
    s.players_sheet.fail_reads = True
    assert s.get_player('177500483500376064') is None  # read failed, logged
    s.players_sheet.fail_reads = False
    player = s.create_player('177500483500376064', 'Sylphiette')
    assert s.players_sheet.appends == 0
    assert player['row'] == 2


def test_ids_with_whitespace_or_float_suffix_match():
    s = make_storage([[' 279996223983976448 ', 'Bridgedogg', '0', '5700', '[]'],
                      ['539463525572149248.0', 'T', '0', '3400', '[]']])
    assert s.get_player('279996223983976448')['row'] == 2
    assert s.get_player(539463525572149248)['row'] == 3
    s.get_or_create_player('539463525572149248', 'T')
    assert s.players_sheet.appends == 0


def test_existing_duplicates_use_first_row():
    s = make_storage([LOBSTREX, ['177500483500376064', 'Sylphiette', '0', '0', '[]']])
    player = s.get_or_create_player('177500483500376064', 'Lobstrex')
    assert player['row'] == 2
    assert player['copper'] == 5700
    assert s.players_sheet.appends == 0


def test_new_player_added_once():
    s = make_storage([LOBSTREX])
    player = s.get_or_create_player('1327353808107475025', 'abi')
    assert s.players_sheet.appends == 1
    assert player['row'] == 3
    again = s.get_or_create_player('1327353808107475025', 'abi')
    assert s.players_sheet.appends == 1
    assert again['row'] == 3


if __name__ == '__main__':
    tests = [v for k, v in sorted(globals().items()) if k.startswith('test_')]
    for t in tests:
        t()
        print(f"✓ {t.__name__}")
    print(f"All {len(tests)} player identity tests passed")
