# bank_list — the ONE list-fill loop over shared item_row rows (W16,
# MC 11274.1.28 / card 11384). The gear panel, blacksmith, tinkerer and
# the defense panel's relic picker each carried this same six-line build
# (clear box, instantiate Row_<uid>, bind the tables, show_item with the
# marked uid, wire picked, add_child); it now lives HERE once — the
# widget itself (scripts/item_row.gd) stays the one renderer, this file
# is only the fill loop shared by its four users (F2-12 reuse, the W9
# gate's "exactly ONE row renderer" reading, restated W16). W17c made the
# clear step emit-safe (detach + queue_free — see fill(); E9: free() on a
# row that is mid-`picked` is an engine ERROR on the mouse path).
extends RefCounted

const ITEM_ROW := preload("res://scenes/item_row.tscn")


static func fill(box: Node, tables, rows: Array, marked_uid: int,
		on_picked: Callable) -> void:
	# W17c (MC 11274.1.30): detach NOW + queue_free. A MOUSE press on a
	# row reaches a panel's pick handler while `picked` is still emitting;
	# free() on the emitting Button is an engine ERROR ("Object is locked",
	# core/object/object.cpp:787 — VERIFIED this card, engine fact E9) and
	# silently leaves the old row half-cleared. queue_free unwinds after
	# the emit; remove_child keeps the repaint instant (no flicker).
	for child: Node in box.get_children():
		box.remove_child(child)
		child.queue_free()
	for row: Dictionary in rows:
		var item = ITEM_ROW.instantiate()
		item.name = "Row_%d" % int(row.get("uid", 0))
		item.bind(tables)
		item.show_item(row, int(row.get("uid", 0)) == marked_uid)
		item.picked.connect(on_picked)
		box.add_child(item)
