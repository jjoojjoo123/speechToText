from string_align import StringAlign, give_param

def to_final_result(API_results, weight, threshold, *, way = 'james', print_mode = False, **kwargs):
	S = StringAlign()
	S += API_results
	p = give_param(way)

	for k, n in kwargs.items():
		try:
			setattr(p, k, n)
		except:
			pass

	S.evaluate(p)
	#x = S.big_anchor_concat_james()
	x = S.big_anchor_concat_heuristic(p)
	x = x['word_set']
	alignment = S.str_big_anchor()
	final_result = S.final_result(weight, threshold)
	if print_mode:
		print(S)
		print(alignment)
		print("")
		print(list(final_result))
		return 0
	else:
		final_result_str = ' '.join(final_result)
		return alignment, final_result_str