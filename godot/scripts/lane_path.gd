# lane_path — waypoint walker (Modules row scripts/lane_path.gd, pinned
# signature verbatim; MC 11274.1.13 / card 11308). Shared by enemy_runner.
# The brief's advance(entity, dist) paraphrase is superseded by the pinned
# table (READ FIRST clause, precedent MC 11274.1.9/.10/.11/.12).
#
# F16 (binding): y comes from the map waypoints, NEVER rewritten here —
# C7 authors ground lanes at y 0 and air lanes at the flight height, the
# walker stays axis-agnostic and gravity is never applied on-lanes.
#
# Stateless by contract: the caller stores wp_index back. The next waypoint
# is re-derived from pos each call by the behind-the-plane test
# dot(wp - pos, wp - prev) > 0 (first waypoint the walker has not passed),
# so a step that lands exactly on, or overshoots past, a waypoint keeps
# walking forward — never backwards, never stuck.


# Walk `speed * dt` along the polyline. Returns {pos, wp_index, arrived};
# wp_index is the current target waypoint (the last index once arrived).
static func advance(pos: Vector3, wps: Array[Vector3], speed: float,
		dt: float) -> Dictionary:
	if wps.is_empty():
		return {"pos": pos, "wp_index": 0, "arrived": true}
	var i := 1
	while i < wps.size():
		var seg := wps[i] - wps[i - 1]
		if (wps[i] - pos).dot(seg) > 0.0:
			break
		i += 1
	if i >= wps.size():
		return {"pos": wps[wps.size() - 1], "wp_index": wps.size() - 1,
			"arrived": true}
	var remaining := speed * dt
	while remaining > 0.0 and i < wps.size():
		var step_vec := wps[i] - pos
		var dist := step_vec.length()
		if dist <= 0.0:
			i += 1
			continue
		if dist <= remaining:
			pos = wps[i]
			remaining -= dist
			i += 1
		else:
			pos += step_vec * (remaining / dist)
			remaining = 0.0
	var arrived := i >= wps.size()
	if arrived:
		i = wps.size() - 1
	return {"pos": pos, "wp_index": i, "arrived": arrived}
