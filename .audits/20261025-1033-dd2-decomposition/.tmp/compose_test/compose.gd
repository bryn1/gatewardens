class_name GWCompose extends RefCounted
static func build_graph() -> Dictionary:
	var s := GWState.new()
	var st := GWStore.new()
	s.mutated.connect(func(): st.write(s.to_save()))
	return {"state": s, "save": st}
