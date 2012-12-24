def remap_keys_with_dict(original, keys_remap, keep_unmapped_keys=False):
	remapped = {
		new_key: original[old_key]
		for old_key, new_key in keys_remap.iteritems()
		if old_key in original
	}

	if keep_unmapped_keys:
		for key, value in original.iteritems():
			if key not in keys_remap:
				remapped[key] = value

	return remapped
