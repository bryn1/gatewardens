# bank_list — the ONE list-fill loop over shared item_row rows (W16,
# MC 11274.1.28 / card 11384). The gear panel, blacksmith, tinkerer and
# the defense panel's relic picker each carried this same six-line build
# (clear box, instantiate Row_<uid>, bind the tables, show_item with the
# marked uid, wire picked, add_child); it now lives HERE once — the
# widget itself (scripts/item_row.gd) stays the one renderer, this file
# is only the fill loop shared by its four users (F2-12 reuse, the W9
# gate's "exactly ONE row renderer" reading, restated W16).
extends RefCounted

const ITEM_ROW := preload("res://scenes/item_row.tscn")


static func fill(box: Node, tables, rows: Array, marked_uid: int,
		on_picked: Callable) -> void:
	for child: Node in box.get_children():
		child.free()
	for row: Dictionary in rows:
		var item = ITEM_ROW.instantiate()
		item.name = "Row_%d" % int(row.get("uid", 0))
		item.bind(tables)
		item.show_item(row, int(row.get("uid", 0)) == marked_uid)
		item.picked.connect(on_picked)
		box.add_child(item)
