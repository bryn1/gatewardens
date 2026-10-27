import re
# I1 regex as written in DESIGN-draft.md lines 191-192, two readings:
as_wrapped = re.compile(r"(?i)shop\b|price|buy_|gem|coin_store|premium|battle.?pass|gacha|loot.?box|key_count|real.?\nmoney|cooldown_unlock|time.?gate|timer_unlock")
as_intended = re.compile(r"(?i)shop\b|price|buy_|gem|coin_store|premium|battle.?pass|gacha|loot.?box|key_count|real.?money|cooldown_unlock|time.?gate|timer_unlock")
candidates = [
  # potential FALSE POSITIVES (legit game words)
  "lane_management", "engagement_ring", "arrangement.json", "segmentation", "BlacksmithShopZone",
  # potential FALSE NEGATIVES (paywall seams that slip)
  "lockbox", "lockbox_keys", "cash_store", "purchase_item", "iap_id", "paywall", "diamond_count",
  "unlock_with_keys", "premium_currency", "usd_price", "wallet", "monetize", "store_id",
]
print("word | intended_regex | wrapped_regex")
for w in candidates:
    print(f"{w:22s} | {bool(as_intended.search(w))} | {bool(as_wrapped.search(w))}")
