import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from app.classify import HEADINGS  # noqa: E402
from app.reference_content import REFERENCE_ITEMS  # noqa: E402


class TestReferenceCategories(unittest.TestCase):
    def test_every_reference_item_lands_in_a_heading_panel(self):
        hidden = [r["label"] for r in REFERENCE_ITEMS if r["category"] not in HEADINGS]
        self.assertEqual(hidden, [], "these reference items would never show in any panel")


if __name__ == "__main__":
    unittest.main()
