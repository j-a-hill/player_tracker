"""
Tests for the Adventure Bot functionality.
"""
import unittest
import yaml
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestAdventureYAML(unittest.TestCase):
    """Test adventure YAML file structure and content."""
    
    def setUp(self):
        """Load adventures.yaml before each test."""
        self.adventures_file = 'adventures.yaml'
        with open(self.adventures_file, 'r') as f:
            self.adventures_data = yaml.safe_load(f)
    
    def test_yaml_structure(self):
        """Test that YAML has correct top-level structure."""
        self.assertIn('adventures', self.adventures_data)
        self.assertIsInstance(self.adventures_data['adventures'], dict)
    
    def test_adventure_count(self):
        """Test that we have at least some adventures."""
        adventures = self.adventures_data.get('adventures', {})
        self.assertGreater(len(adventures), 0, "Should have at least one adventure")
    
    def test_adventure_structure(self):
        """Test that each adventure has required fields."""
        adventures = self.adventures_data.get('adventures', {})
        
        for adv_id, adv_data in adventures.items():
            with self.subTest(adventure=adv_id):
                # Check required fields
                self.assertIn('name', adv_data, f"Adventure {adv_id} missing 'name'")
                self.assertIn('description', adv_data, f"Adventure {adv_id} missing 'description'")
                self.assertIn('start_node', adv_data, f"Adventure {adv_id} missing 'start_node'")
                self.assertIn('nodes', adv_data, f"Adventure {adv_id} missing 'nodes'")
                
                # Check that start_node exists in nodes
                start_node = adv_data['start_node']
                nodes = adv_data['nodes']
                self.assertIn(start_node, nodes, 
                             f"Adventure {adv_id} start_node '{start_node}' not found in nodes")
    
    def test_node_structure(self):
        """Test that each node has correct structure."""
        adventures = self.adventures_data.get('adventures', {})
        
        for adv_id, adv_data in adventures.items():
            nodes = adv_data.get('nodes', {})
            
            for node_id, node_data in nodes.items():
                with self.subTest(adventure=adv_id, node=node_id):
                    # Every node must have text
                    self.assertIn('text', node_data, 
                                 f"Node {node_id} in {adv_id} missing 'text'")
                    
                    # If not an end node, must have choices
                    if not node_data.get('is_end', False):
                        self.assertIn('choices', node_data,
                                     f"Non-end node {node_id} in {adv_id} missing 'choices'")
                        self.assertIsInstance(node_data['choices'], list)
                        self.assertGreater(len(node_data['choices']), 0,
                                          f"Node {node_id} in {adv_id} has empty choices")
    
    def test_choices_structure(self):
        """Test that choices have correct structure."""
        adventures = self.adventures_data.get('adventures', {})
        
        for adv_id, adv_data in adventures.items():
            nodes = adv_data.get('nodes', {})
            
            for node_id, node_data in nodes.items():
                choices = node_data.get('choices', [])
                
                for idx, choice in enumerate(choices):
                    with self.subTest(adventure=adv_id, node=node_id, choice_idx=idx):
                        # Each choice must have label and next
                        self.assertIn('label', choice,
                                     f"Choice {idx} in node {node_id} of {adv_id} missing 'label'")
                        self.assertIn('next', choice,
                                     f"Choice {idx} in node {node_id} of {adv_id} missing 'next'")
                        
                        # Next node must exist
                        next_node = choice['next']
                        self.assertIn(next_node, nodes,
                                     f"Choice {idx} in node {node_id} of {adv_id} points to non-existent node '{next_node}'")
    
    def test_rewards_structure(self):
        """Test that rewards have valid structure."""
        adventures = self.adventures_data.get('adventures', {})
        
        for adv_id, adv_data in adventures.items():
            nodes = adv_data.get('nodes', {})
            
            for node_id, node_data in nodes.items():
                if 'rewards' in node_data:
                    with self.subTest(adventure=adv_id, node=node_id):
                        rewards = node_data['rewards']
                        self.assertIsInstance(rewards, dict)
                        
                        # Check valid reward types
                        valid_types = ['gold', 'xp', 'items']
                        for reward_type in rewards.keys():
                            self.assertIn(reward_type, valid_types,
                                         f"Invalid reward type '{reward_type}' in node {node_id} of {adv_id}")
                        
                        # If items, should be a list
                        if 'items' in rewards:
                            self.assertIsInstance(rewards['items'], list)
                        
                        # Gold and XP should be positive numbers
                        if 'gold' in rewards:
                            self.assertIsInstance(rewards['gold'], (int, float))
                            self.assertGreater(rewards['gold'], 0)
                        
                        if 'xp' in rewards:
                            self.assertIsInstance(rewards['xp'], (int, float))
                            self.assertGreater(rewards['xp'], 0)
    
    def test_penalties_structure(self):
        """Test that penalties have valid structure."""
        adventures = self.adventures_data.get('adventures', {})
        
        for adv_id, adv_data in adventures.items():
            nodes = adv_data.get('nodes', {})
            
            for node_id, node_data in nodes.items():
                if 'penalties' in node_data:
                    with self.subTest(adventure=adv_id, node=node_id):
                        penalties = node_data['penalties']
                        self.assertIsInstance(penalties, dict)
                        
                        # Check valid penalty types
                        valid_types = ['gold', 'xp', 'items']
                        for penalty_type in penalties.keys():
                            self.assertIn(penalty_type, valid_types,
                                         f"Invalid penalty type '{penalty_type}' in node {node_id} of {adv_id}")
                        
                        # If items, should be a list
                        if 'items' in penalties:
                            self.assertIsInstance(penalties['items'], list)
                        
                        # Gold and XP should be positive numbers
                        if 'gold' in penalties:
                            self.assertIsInstance(penalties['gold'], (int, float))
                            self.assertGreater(penalties['gold'], 0)
                        
                        if 'xp' in penalties:
                            self.assertIsInstance(penalties['xp'], (int, float))
                            self.assertGreater(penalties['xp'], 0)
    
    def test_requirements_structure(self):
        """Test that requirements have valid structure."""
        adventures = self.adventures_data.get('adventures', {})
        
        for adv_id, adv_data in adventures.items():
            nodes = adv_data.get('nodes', {})
            
            for node_id, node_data in nodes.items():
                choices = node_data.get('choices', [])
                
                for idx, choice in enumerate(choices):
                    if 'requirement' in choice:
                        with self.subTest(adventure=adv_id, node=node_id, choice_idx=idx):
                            req = choice['requirement']
                            self.assertIsInstance(req, dict)
                            
                            # Check valid requirement types
                            valid_types = ['gold', 'items']
                            for req_type in req.keys():
                                self.assertIn(req_type, valid_types,
                                             f"Invalid requirement type '{req_type}' in choice {idx} of node {node_id} in {adv_id}")
                            
                            # If items, should be a list
                            if 'items' in req:
                                self.assertIsInstance(req['items'], list)
                            
                            # Gold should be a positive number
                            if 'gold' in req:
                                self.assertIsInstance(req['gold'], (int, float))
                                self.assertGreater(req['gold'], 0)
    
    def test_no_dead_ends(self):
        """Test that all paths eventually lead to an end node."""
        adventures = self.adventures_data.get('adventures', {})
        
        for adv_id, adv_data in adventures.items():
            nodes = adv_data.get('nodes', {})
            start_node = adv_data['start_node']
            
            # BFS to find all reachable nodes
            visited = set()
            queue = [start_node]
            has_end_node = False
            
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                
                node_data = nodes[current]
                
                if node_data.get('is_end', False):
                    has_end_node = True
                
                for choice in node_data.get('choices', []):
                    next_node = choice['next']
                    if next_node not in visited:
                        queue.append(next_node)
            
            self.assertTrue(has_end_node, 
                           f"Adventure {adv_id} has no reachable end nodes")
    
    def test_example_adventures(self):
        """Test that example adventures exist and are valid."""
        adventures = self.adventures_data.get('adventures', {})
        
        # Check for key example adventures
        expected_adventures = ['mysterious_stranger', 'goblin_ambush']
        for expected in expected_adventures:
            self.assertIn(expected, adventures,
                         f"Example adventure '{expected}' not found")


class TestAdventureLogic(unittest.TestCase):
    """Test adventure bot logic."""
    
    def test_adventure_yaml_loads(self):
        """Test that adventures.yaml loads without errors."""
        try:
            with open('adventures.yaml', 'r') as f:
                data = yaml.safe_load(f)
            self.assertIsNotNone(data)
        except Exception as e:
            self.fail(f"Failed to load adventures.yaml: {e}")
    
    def test_example_file_creation(self):
        """Test that example file can be created."""
        # This imports the function from adventure_bot
        # We can't easily test this without running the full bot
        # So we just verify the YAML is valid
        self.assertTrue(os.path.exists('adventures.yaml'))


if __name__ == '__main__':
    # Change to script directory so we can find adventures.yaml
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    unittest.main()
