"""Functional shop regression contracts (not a replacement for Godot runtime QA)."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "scripts" / "main.gd").read_text(encoding="utf-8")
RUNTIME = (ROOT / "tests" / "runtime_wave_qa.gd").read_text(encoding="utf-8")


def body(name):
    return MAIN.split(f"func {name}(", 1)[1].split("\nfunc ", 1)[0]


class ShopConsumablesContractTests(unittest.TestCase):
    def test_full_resources_have_one_shared_guard(self):
        check = body("_shop_resource_full_reason")
        for key in ('"ammo":', '"armor":', '"medkit":'):
            self.assertIn(key, check)
        self.assertIn('stats["mag"]', check)
        self.assertIn('stats["reserve"]', check)
        self.assertIn("player.health >= 100.0", check)
        self.assertIn("player.armor >= 100.0", check)

    def test_ui_indicates_full_and_disables_button(self):
        render = body("_render_shop")
        self.assertIn("_shop_resource_full_reason(item_id)", render)
        self.assertIn("resource_full_reason != \"\"", render)
        self.assertIn("CHEIO", render)
        self.assertIn("button.disabled = already_equipped or resource_full_reason", render)

    def test_keyboard_buy_checks_resources_before_debit(self):
        buy = body("_buy")
        self.assertIn("if not shop_open or not SHOP_OPTIONS.has(shop_id):", buy)
        self.assertIn("var full_reason: String = _shop_resource_full_reason(id)", buy)
        self.assertLess(buy.index('if full_reason != "":'), buy.index("wallet -= price"))

    def test_live_regression_covers_partial_full_repeat_and_closed(self):
        for marker in (
            "full ammo, armor, or health incorrectly charged credits",
            "partially empty consumables must be enabled in the shop",
            "partial consumable purchases charged the wrong total",
            "repeated full consumable purchases must not charge again",
            "stale shop callback charged money after the store closed",
        ):
            self.assertIn(marker, RUNTIME)


if __name__ == "__main__":
    unittest.main()
