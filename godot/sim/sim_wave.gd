class_name SimWave
extends RefCounted

# Wave/phase sequencing decisions (Modules row sim_wave). Inputs are C8
# wave files (the loaded "waves/waves_gatefall_<difficulty>" table) and
# single wave rows; nothing here mutates either. total_waves == 11 is
# pinned by test_waves (I4).


# The spawn rows of wave i: Array of {enemy_id,count,lane,delay} (C2/C8).
static func wave_comp(waves_file: Dictionary, i: int) -> Array:
	var waves: Array = waves_file.get("waves", [])
	var row: Dictionary = waves[i]
	return row.get("enemies", [])


# The sole boss per wave file is index 10 (I4); kind is the discriminator.
static func is_boss(wave_row: Dictionary) -> bool:
	return String(wave_row.get("kind", "")) == "boss"


# Build seconds of one wave row; `d` is the fallback default
# (balance.build_seconds_default) for a row that carries none.
static func build_seconds(wave_row: Dictionary, d: float) -> float:
	return float(wave_row.get("build_seconds", d))


static func total_waves(waves_file: Dictionary) -> int:
	var waves: Array = waves_file.get("waves", [])
	return waves.size()
