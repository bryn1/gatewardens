extends SceneTree
func _init():
	var g := GWCompose.build_graph()
	var s = g["state"]
	var st = g["save"]
	s.add_gold(5)
	s.add_gold(3)
	print("ACK=", st.write_seq, " GOLD=", s.gold, " LASTSAVED=", st.last)
	quit()
