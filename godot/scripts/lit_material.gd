extends RefCounted

# lit_material — the ONE builder of the lit-translucent ground material
# (v1.3 refactor W3, MC 11724, finding D-1): the shape G2 pinned and G4
# rode — unshaded so it reads lit on the dark arena, alpha-blended so the
# painted ground shows through. lane_bands.gd and range_ring.gd each
# hand-rolled this byte-shape inline (D-1); the fold keeps the MECHANISM
# HERE and every color with its caller — BAND_COLOR/RING_COLOR stay the
# callers' presentation constants. The web-raster law stands UNTOUCHED:
# geometry stays engine-managed PrimitiveMesh on the caller nodes (the
# G2 ArrayMesh lesson), this builder only ever produces the MATERIAL.
# Runtime-duplicate idiom kept: no .tres on disk to keep in sync.


static func make(color: Color) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = color
	return mat
