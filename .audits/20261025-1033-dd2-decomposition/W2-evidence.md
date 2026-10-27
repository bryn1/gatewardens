=== W2 close evidence (MC 11274.1.8 / card 11298) ===
commit: 795f61fb6d3285a6b10aae410596db6ad7b7084a
author: code (11298) <code@agent-town.local>
 15 files changed, 1404 insertions(+)

--- pytest tests/ -q (exit 0) ---
...................................................................      [100%]
67 passed in 0.58s
--- tools/check_hygiene.py (exit 0) ---
check_hygiene: 0 hit(s)
--- planted-bad red runs (guards proven red-capable) ---
1 hp.hard<hp.normal        -> FAILED test_enemy_rows_and_hard_scaling
2 boss removed from idx 10 -> FAILED test_waves_c8_contract[normal]
3 planted 'item_price_default' field -> FAILED test_no_banned_i1_field_names_in_data[balance.json]
all restored; full suite green after (above)
VERIFY_EXIT=0
