import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import unittest
import calc

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(calc.add(2, 3), 5)
