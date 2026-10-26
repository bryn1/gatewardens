# mission_relics — the C11 relic-pool crossing of the mission root (W16
# split of mission.gd, MC 11274.1.28 / card 11384; crossing authored
# W14, MC 11274.1.25 / card 11341). Pure move — bodies byte-identical.
# C11 (R2 relics-for-towers): build phase ONLY, one relic per defense,
# one defense per relic (pool uids unique). The bank is NOT consumed —
# relic_pool is the mission-local copy setup() made; the bonus
# application lives on defense_obj (the row), the stat math in
# SimInventory.relic_bonuses (the ONE relic static, never
# reimplemented). mission.gd keeps the public assign_relic/unassign_relic
# crossing (defense_panel + the hub probe call THOSE), so the pinned
# crossing site and its refusals are unchanged.
extends RefCounted


static func assign(m, defense_uid: int, relic_uid: int) -> Dictionary:
	if String(m.phase_kind) != "build":
		return {"ok": false, "why": "phase"}
	var obj = defense_by_uid(m, defense_uid)
	if obj == null:
		return {"ok": false, "why": "uid"}
	var relic := pool_row(m, relic_uid)
	if relic.is_empty():
		return {"ok": false, "why": "relic"}
	if int(obj.relic_uid) != 0 or relic_owner(m, relic_uid) != 0:
		return {"ok": false, "why": "taken"}
	obj.assign_relic(relic)
	m.relics_assigned = live_count(m)
	return {"ok": true, "uid": defense_uid, "relic": relic_uid}


static func unassign(m, defense_uid: int) -> Dictionary:
	if String(m.phase_kind) != "build":
		return {"ok": false, "why": "phase"}
	var obj = defense_by_uid(m, defense_uid)
	if obj == null:
		return {"ok": false, "why": "uid"}
	if int(obj.relic_uid) == 0:
		return {"ok": false, "why": "none"}
	# Pool semantics (C11): the row never left relic_pool, so the return
	# IS the clear — the defense drops its bonus leg, the pool is intact.
	var relic_uid := int(obj.relic_uid)
	obj.clear_relic()
	m.relics_assigned = live_count(m)
	return {"ok": true, "uid": defense_uid, "relic": relic_uid}


static func defense_by_uid(m, uid: int):
	for rec: Dictionary in m.defense_list:
		if int(rec["uid"]) == uid:
			return rec["obj"]
	return null


static func pool_row(m, uid: int) -> Dictionary:
	for row: Dictionary in m.relic_pool:
		if int(row.get("uid", 0)) == uid:
			return row
	return {}


static func relic_owner(m, relic_uid: int) -> int:
	for rec: Dictionary in m.defense_list:
		if int((rec["obj"] as RefCounted).relic_uid) == relic_uid:
			return int(rec["uid"])
	return 0


# The C5 relics_assigned mirror, ONE site: count of live assignments —
# sell-safe (a sold defense's relic returns to the pool unassigned,
# F2-7's ±1 reads after the crossing's own call).
static func live_count(m) -> int:
	var n := 0
	for rec: Dictionary in m.defense_list:
		if int((rec["obj"] as RefCounted).relic_uid) != 0:
			n += 1
	return n
