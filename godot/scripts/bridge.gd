class_name GWBridge
extends RefCounted

# Keyboard relay (Modules row scripts/bridge.gd, MC 11274.1.11): the VS
# bridge.gd mechanism EXTENDED — adds Digit4, KeyE, KeyN, F1-F3 and the
# mouse-button codes — with NO Node/_input here (R3/C1: main.gd forwards
# desktop _input and web JS callbacks into on_key). RefCounted like the
# other core objects, so GWCompose.build_graph can construct it under -s.
#
# Reading recorded on the card trail: the W4 brief described a Node with
# a _process pump and a JS snapshot push; the PINNED Modules row wins
# (stop-condition precedent MC 11274.1.9/.10) — the snapshot push is the
# main.gd row's own `_js_eval("window.__gwSnapshot="+…)` mechanism (W5),
# never the bridge's, and input arrives by forwarding, not by polling.

const MOVE_KEYS := ["KeyW", "KeyA", "KeyS", "KeyD",
	"ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"]

# Discrete codes appended to the presses queue (hot-swap F1-F3, Digit4
# and KeyE/KeyN are the W4 additions over the VS set).
const DISCRETE_KEYS := ["Escape", "KeyM", "Digit1", "Digit2", "Digit3",
	"Digit4", "KeyE", "KeyN", "F1", "F2", "F3", "Enter", "NumpadEnter",
	"MouseLeft", "MouseMiddle", "MouseRight"]

# Physical keys -> the DOM-style codes the queues are keyed on (desktop
# only; mirrors the e.code values the web relay forwards). main.gd's
# _input forwarder (W5) reads this table; mouse buttons map via
# MOUSE_CODES from InputEventMouseButton.button_index.
const NATIVE_CODES := {
	KEY_W: "KeyW", KEY_A: "KeyA", KEY_S: "KeyS", KEY_D: "KeyD",
	KEY_UP: "ArrowUp", KEY_DOWN: "ArrowDown", KEY_LEFT: "ArrowLeft",
	KEY_RIGHT: "ArrowRight", KEY_ESCAPE: "Escape", KEY_M: "KeyM",
	KEY_1: "Digit1", KEY_2: "Digit2", KEY_3: "Digit3", KEY_4: "Digit4",
	KEY_E: "KeyE", KEY_N: "KeyN",
	KEY_F1: "F1", KEY_F2: "F2", KEY_F3: "F3",
	KEY_ENTER: "Enter", KEY_KP_ENTER: "NumpadEnter",
}

const MOUSE_CODES := {
	MOUSE_BUTTON_LEFT: "MouseLeft", MOUSE_BUTTON_RIGHT: "MouseRight",
	MOUSE_BUTTON_MIDDLE: "MouseMiddle",
}

var held: Dictionary = {} # code -> true while the key/button is down
var presses: Array = []   # discrete codes, drained once per frame by main


# The ONE feed point (web JS relay + the desktop _input forwarder both
# call this; unknown codes are dropped exactly like the VS relay dropped
# unmatched e.code values).
func on_key(code: String, down: bool) -> void:
	if down:
		held[code] = true
		if code in DISCRETE_KEYS:
			presses.append(code)
	else:
		held.erase(code)


# Desktop forwarder helper: DOM-style code for a physical keycode, ""
# when unmapped (the caller then drops the event).
func native_code(physical_keycode: int) -> String:
	return String(NATIVE_CODES.get(physical_keycode, ""))


func mouse_code(button_index: int) -> String:
	return String(MOUSE_CODES.get(button_index, ""))


# Normalised 8-direction move vector, or ZERO when idle.
func move_vector() -> Vector2:
	var x := 0.0
	var y := 0.0
	if held.has("KeyA") or held.has("ArrowLeft"):
		x -= 1.0
	if held.has("KeyD") or held.has("ArrowRight"):
		x += 1.0
	if held.has("KeyW") or held.has("ArrowUp"):
		y -= 1.0
	if held.has("KeyS") or held.has("ArrowDown"):
		y += 1.0
	if x == 0.0 and y == 0.0:
		return Vector2.ZERO
	return Vector2(x, y).normalized()


func drain_presses() -> Array:
	var out := presses
	presses = []
	return out
