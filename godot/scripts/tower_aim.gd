# tower_aim — the V-B turret-aim DRIVER (MC 12082, V16-PLAN-c2 §3 V-B):
# one pass per frame turns each placed shooter's "Turret" node (built by
# tower_forms.gd) toward the nearest live entity INSIDE that defense's
# OWN range door, else leaves it exactly as it stands (zero-write idle
# — an untouched turret keeps its last yaw, nothing ever recentres it).
#
# OBSERVER DISCIPLINE (the fx_director doctrine, MC 11552, reused — one
# mechanism family with selection_ring.gd): READS published state only
# — mission.defense_list records, obj.hp/pos/tier through the plain
# fields, obj.bonus_row() (the tier+relic range number, the same DATA
# door the sim itself fires with, I2: the number is read, never
# recomputed), and runner.nearest() (the ONE nearest loop living in
# enemy_runner — DA-verified equal to the sim's own _nearest selection,
# so the turret points exactly where the sim already deals damage; the
# tracer kit keeps painting the shot, THIS file only turns the head).
# WRITES: the Turret child node's rotation.y and NOTHING else — no sim
# field, no node creation, no signal wiring, no second targeting math.
#
# THE PUMP: mounted CODE-side as a mission-root child from
# mission_world.build_cores (the HERO_RIG code-mount idiom — mission.gd
# sits at its 400 ceiling, ZERO lines) and processes AFTER the root's
# step(), so it always observes the finished frame: the root-last
# observer rule of fx_director/selection_ring, met by the mount's place
# in the setup chain, not by the scene file. Under `-s` no frame
# dispatches _process (E5), so the probe drives aim_step() by hand in
# lockstep — the fx_step/ring_step idiom.
extends Node3D


func _process(_d: float) -> void:
	aim_step()


# One decision pass; every frame re-reads the CURRENT published picture
# (no held state — a sold or upgraded row is simply not walked).
func aim_step() -> void:
	var m = get_parent()
	if m == null or not ("defense_list" in m):
		return                       # not set up (E5: child, pre-setup)
	var runner = m.get_node_or_null(NodePath("EnemyRunner"))
	if runner == null:
		return                       # no runner mounted: aim-silent
	for rec: Dictionary in m.defense_list:
		var obj = rec["obj"]
		if float(obj.hp) <= 0.0:
			continue                 # dead rows hold no visual duty
		var node = obj.node
		if node == null or not is_instance_valid(node):
			continue
		var turret: Node3D = node.get_node_or_null(NodePath("Turret")) \
				as Node3D
		if turret == null:
			continue                 # blockade/trap: no aiming element
		var row: Dictionary = obj.bonus_row()
		var target: Dictionary = runner.nearest(obj.pos, float(row["range"]))
		if target.is_empty():
			continue                 # ZERO-WRITE IDLE (header)
		var to: Vector3 = (target["pos"] as Vector3) - obj.pos
		if to.x == 0.0 and to.z == 0.0:
			continue                 # same point: no facing to compute
		# The ONLY write in this file: local +Z of the Turret walks onto
		# the target (tower_forms faces every barrel down +Z).
		turret.rotation.y = atan2(to.x, to.z)
