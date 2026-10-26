# phase_controller — build<->combat alternation (Modules row
# scripts/phase_controller.gd, MC 11274.1.13 / card 11308). State machine
# ONLY: every number arrives from economy/balance/xp (I2) and the wave
# rows via SimWave. I4 (binding): the wave-completion green award, the
# blue refill and the downed-hero revival all happen HERE, the one
# grep-able site, and nowhere else.
#
# Flow (brief row + C8): intermission = the build phase. Build for wave i
# lasts SimWave.build_seconds(waves[i], balance.build_seconds_default);
# at combat start the ONE blue refill fires when
# economy.blue.refill_on_phase_start (C4: one path). Wave clear (nothing
# left to spawn + nothing alive on the lanes — declared reading: the
# pinned "all spawned dead" cannot be the sole exit in W6 because no
# damage source ships before W7, and a breaching entity is consumed the
# same way a kill consumes one) awards economy green per_wave + xp
# wave_xp, then alternates. The sole boss is wave index total-1 (I4);
# boss_died() on that wave sets the mission's win-pending flag — the
# outcome itself is decided ONLY in mission bookkeeping step (5), where
# F2-9's win-first/lose-overwrites precedence lives.

extends Node

const SIM_WAVE := preload("res://sim/sim_wave.gd")
const SIM_ECONOMY := preload("res://sim/sim_economy.gd")

signal phase_changed(kind)
signal wave_done(index)

var mission = null              # mission root node (duck-typed host)
var waves_file: Dictionary = {}
var economy: Dictionary = {}
var balance: Dictionary = {}
var xp_table: Dictionary = {}
var total := 0
var wave := 0                   # current/next wave index (0-based, C5)
var build_timer := 0.0


func setup(m) -> void:
	mission = m
	waves_file = m.waves_file
	economy = m.economy
	balance = m.balance
	xp_table = m.xp_table
	total = SIM_WAVE.total_waves(waves_file)
	_enter_build(0)


func step(delta: float) -> void:
	if mission.outcome != null:
		return
	if bool(mission.in_combat):
		if mission.spawn_queue.is_empty() and mission.alive == 0:
			_finish_wave()
		return
	build_timer -= delta
	if build_timer <= 0.0:
		_enter_combat()


func _wave_row(i: int) -> Dictionary:
	var waves: Array = waves_file.get("waves", [])
	return waves[i]


func _enter_build(i: int) -> void:
	wave = i
	mission.wave = i
	mission.phase_kind = "build"
	mission.in_combat = false
	build_timer = SIM_WAVE.build_seconds(
			_wave_row(i), float(balance.get("build_seconds_default", 0.0)))
	mission.revive_downed()      # C4: full-HP revival, build start only
	phase_changed.emit("build")


func _enter_combat() -> void:
	mission.phase_kind = "combat"
	mission.in_combat = true
	if bool(economy.get("blue", {}).get("refill_on_phase_start", false)):
		mission.blue = float(mission.blue_max)   # the ONE refill (I4)
	phase_changed.emit("combat")
	mission.start_wave(wave)


func _finish_wave() -> void:
	wave_done.emit(wave)
	# I4 single site: per-wave green + per-wave hero xp, data numbers only
	var green_block: Dictionary = economy.get("green", {})
	mission.green = SIM_ECONOMY.add_green(
			int(mission.green), int(green_block.get("per_wave", 0)),
			int(green_block.get("cap", 0)))
	mission.xp_earned += int(xp_table.get("wave_xp", 0))
	if SIM_WAVE.is_boss(_wave_row(wave)):
		mission.win_pending = true
		return
	_enter_build(wave + 1)


# Wave 10's first group IS the sole boss (declared reading); the
# funnel routes its death here. Win-pending is only the FLAG — outcome
# stays a step-(5) decision so F2-9's same-tick lose precedence holds.
func boss_died() -> void:
	if wave == total - 1:
		mission.win_pending = true
