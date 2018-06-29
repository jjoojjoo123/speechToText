import copy
import itertools
from collections import Counter

class Result():
	def __init__(self, API, str):
		self.API = API
		self.str = str

class Result_comb():
	def __init__(self, comb, result0, result1, max_score, best_sticks):
		self.comb = comb
		self.result0 = result0
		self.result1 = result1
		self.score = max_score
		self.sticks = best_sticks
		
def score_calculating(string0, string1, shift0 = 0, shift1 = 0):
	now_score = -2147483648
	max_score = -2147483648
	left_max_score = 0
	right_max_score = 0
	
	now_sticks = []
	best_sticks = []

	left_best_sticks = []
	right_best_sticks = []
	
	find_stick = False
	
	for i in range(0, len(string0)):
		for j in range(0, len(string1)):
			if string0[i] == string1[j]:
				find_stick = True
				left_max_score, left_best_sticks = score_calculating(string0[0:i], string1[0:j], shift0, shift1)
				right_max_score, right_best_sticks = score_calculating(string0[i + 1:len(string0)], string1[j + 1:len(string1)], shift0 + 1 + i, shift1 + 1 + j)
				now_sticks = left_best_sticks + [(shift0 + i, shift1 + j)] + right_best_sticks
				now_score = left_max_score + right_max_score + 2

		if now_score > max_score:
			max_score = now_score
			best_sticks = now_sticks
	
	if find_stick == False:
		max_score = -1 * (len(string0) + len(string1))

	return max_score, best_sticks

def word_counter(strings, word_to_count):
	count = 0
	for i in range(0, len(strings)):
		for word in strings[i]:
			if word == word_to_count:
				count +=1
	return count
	

def advance_score_calculating(strings, sticks, shifts = [0, 0, 0, 0], shifts_diff = [0, 0, 0, 0], mode = "right"):
	strings_len = [len(s) for s in strings]
	
	now_score = -2147483648
	max_score = -2147483648
	left_max_score = 0
	right_max_score = 0

	now_sticks = []
	best_sticks = sticks
	left_best_sticks = []
	right_best_sticks = []
	find_stick = False
	
	if mode == "right":
		for i in range(0, 2):
			for j in range(0, len(sticks[i])):
				for k in range(0, len(sticks[i][j])):
					sticks[i][j][k][1] -= shifts_diff[sticks[i][j][k][0]]
	
	top_stick_index = 0
	for top_stick in sticks[0]:
		string2_index = 0
		for string2_word in strings[2]:
			if string2_word == strings[0][top_stick[0][1]]:
				find_stick = True
				
				is_stick = False
				left_strings = [strings[0][0:top_stick[0][1]], strings[1][0:top_stick[1][1]], strings[2][0:string2_index]]
				right_strings = [strings[0][top_stick[0][1] + 1:strings_len[0]],
											strings[1][top_stick[1][1] + 1:strings_len[1]],
											strings[2][string2_index + 1:strings_len[2]]]
				left_sticks = [sticks[0][0:top_stick_index]]
				right_sticks = [sticks[0][top_stick_index + 1:len(sticks[0])]]
				
				bottom_stick_index = 0
				for bottom_stick in sticks[1]:
					if bottom_stick[0][1] == string2_index:
						is_stick = True
						break
					bottom_stick_index += 1

				#the word is a stick
				if is_stick == True:
					left_strings.append(strings[3][0:sticks[1][bottom_stick_index][1][1]])
					right_strings.append(strings[3][sticks[1][bottom_stick_index][1][1] + 1:strings_len[3]])
					left_sticks.append(sticks[1][0:bottom_stick_index])
					right_sticks.append(sticks[1][bottom_stick_index + 1:len(sticks[1])])
					
					left_shifts = shifts
					right_shifts = [shifts[0] + 1 + top_stick[0][1], shifts[1] + 1 + top_stick[1][1], shifts[2] + 1 + string2_index, shifts[3] + 1 + sticks[1][bottom_stick_index][1][1]]
					left_shifts_diff = [0, 0, 0, 0]
					right_shifts_diff = []
					for i in range(0, 4):
						right_shifts_diff.append(right_shifts[i] - shifts[i])
					
					left_max_score, left_best_sticks = advance_score_calculating(left_strings, left_sticks, left_shifts, left_shifts_diff, "left")
					right_max_score, right_best_sticks = advance_score_calculating(right_strings, right_sticks, right_shifts, right_shifts_diff, "right")
					now_score = left_max_score + 4 + right_max_score
					if now_score > max_score:
						adjust_top_stick = [[l[0], l[1] + shifts[l[0]]] for l in top_stick]
						adjust_bottom_stick = [[l[0], l[1] + shifts[l[0]]] for l in sticks[1][bottom_stick_index]]
						
						max_score = now_score
						best_sticks = [left_best_sticks[0] + [adjust_top_stick + adjust_bottom_stick] + right_best_sticks[0], left_best_sticks[1] + right_best_sticks[1]]
				
				#the word is not a stick
				elif is_stick == False and strings_len[3] > 0:
					string3_to_count_index_start = 0
					string3_to_count_index_finish = strings_len[3] - 1
					bottom_stick_index_before = -1
					bottom_stick_index_after = -1
					for bottom_stick in sticks[1]:
						if bottom_stick[0][1] < string2_index:
							string3_to_count_index_start = bottom_stick[1][1] + 1
							bottom_stick_index_before += 1
						else:
							string3_to_count_index_finish = bottom_stick[1][1] - 1
							bottom_stick_index_after = bottom_stick_index_before + 1
							break
						
					string3_start_right_index = string3_to_count_index_finish + 1
					for string3_middle_index in range(string3_to_count_index_start, string3_to_count_index_finish + 1):
						if word_counter(left_strings, strings[3][string3_middle_index]) < word_counter(right_strings, strings[3][string3_middle_index]):
							string3_start_right_index = string3_middle_index
							break
					
					left_strings.append(strings[3][0:string3_start_right_index])
					right_strings.append(strings[3][string3_start_right_index:strings_len[3]])
					left_sticks.append(sticks[1][0:bottom_stick_index_before + 1])
					right_sticks.append(sticks[1][bottom_stick_index_after:len(sticks[1])])
					
					left_shifts = shifts
					right_shifts = [shifts[0] + 1 + top_stick[0][1], shifts[1] + 1 + top_stick[1][1], shifts[2] + 1 + string2_index, shifts[3] + 1 + string3_start_right_index-1]
					left_shifts_diff = [0, 0, 0, 0]
					right_shifts_diff = []
					for i in range(0, 4):
						right_shifts_diff.append(right_shifts[i] - shifts[i])
					
					left_max_score, left_best_sticks = advance_score_calculating(left_strings, left_sticks, left_shifts, left_shifts_diff, "left")
					right_max_score, right_best_sticks = advance_score_calculating(right_strings, right_sticks, right_shifts, right_shifts_diff, "right")
					
					now_score = left_max_score + 3 + right_max_score
					if now_score > max_score:
						adjust_top_stick = [[l[0], l[1] + shifts[l[0]]] for l in top_stick]
						
						max_score = now_score
						best_sticks = [left_best_sticks[0] + [adjust_top_stick + [[2,string2_index + shifts[2]]]] + right_best_sticks[0], left_best_sticks[1] + right_best_sticks[1]]

			string2_index += 1
		
		string3_index = 0
		for string3_word in strings[3]:
			if string3_word == strings[0][top_stick[0][1]]:
				find_stick = True
				is_stick = False
				left_strings = [strings[0][0:top_stick[0][1]], strings[1][0:top_stick[1][1]], strings[3][0:string3_index]]
				right_strings = [strings[0][top_stick[0][1] + 1:strings_len[0]],
											strings[1][top_stick[1][1] + 1:strings_len[1]],
											strings[3][string3_index + 1:strings_len[3]]]
				left_sticks = [sticks[0][0:top_stick_index]]
				right_sticks = [sticks[0][top_stick_index + 1:len(sticks[0])]]
				
				for bottom_stick in sticks[1]:
					if bottom_stick[1][1] == string3_index:
						is_stick = True
						break
				
				#the word is not a stick
				if is_stick == False and strings_len[2] > 0:
					
					string2_to_count_index_start = 0
					string2_to_count_index_finish = strings_len[2] - 1
					bottom_stick_index_before = -1
					bottom_stick_index_after = -1
					for bottom_stick in sticks[1]:
						if bottom_stick[1][1] < string3_index:
							string2_to_count_index_start = bottom_stick[0][1] + 1
							bottom_stick_index_before += 1
						else:
							string3_to_count_index_finish = bottom_stick[0][1] - 1
							bottom_stick_index_after = bottom_stick_index_before + 1
							break
						
					string2_start_right_index = string2_to_count_index_finish + 1
					for string2_middle_index in range(string2_to_count_index_start, string2_to_count_index_finish + 1):
						if word_counter(left_strings, strings[2][string2_middle_index]) < word_counter(right_strings, strings[2][string2_middle_index]):
							string2_start_right_index = string2_middle_index
							break
					
					left_strings.insert(2, strings[2][0:string2_start_right_index])
					right_strings.insert(2, strings[2][string2_start_right_index:strings_len[2]])
					left_sticks.insert(2, sticks[1][0:bottom_stick_index_before + 1])
					right_sticks.insert(2, sticks[1][bottom_stick_index_after:len(sticks[1])])
					
					left_shifts = shifts
					right_shifts = [shifts[0] + 1 + top_stick[0][1], shifts[1] + 1 + top_stick[1][1], shifts[2] + 1 + string2_start_right_index-1, shifts[3] + 1 + string3_index]
					left_shifts_diff = [0, 0, 0, 0]
					right_shifts_diff = []
					for i in range(0, 4):
						right_shifts_diff.append(right_shifts[i] - shifts[i])
					
					left_max_score, left_best_sticks = advance_score_calculating(left_strings, left_sticks, left_shifts, left_shifts_diff, "left")
					right_max_score, right_best_sticks = advance_score_calculating(right_strings, right_sticks, right_shifts, right_shifts_diff, "right")
					
					now_score = left_max_score + 3 + right_max_score
					if now_score > max_score:
						adjust_top_stick = [[l[0], l[1] + shifts[l[0]]] for l in top_stick]
						max_score = now_score
						best_sticks = [left_best_sticks[0] + [adjust_top_stick + [[3,string3_index + shifts[3]]]] + right_best_sticks[0], left_best_sticks[1] + right_best_sticks[1]]

			string3_index += 1
		
		top_stick_index += 1
	
	#base case
	if find_stick == False:
		bottom_stick_number = len(sticks[1])
		max_score = -1*(strings_len[0] + strings_len[1] + strings_len[2] + strings_len[3]) + bottom_stick_number * 2 * 2
	
	if mode == "right":
		for i in range(0,2):
			for j in range(0,len(sticks[i])):
				for k in range(0,len(sticks[i][j])):
					sticks[i][j][k][1] += shifts_diff[sticks[i][j][k][0]]

	return max_score, best_sticks
	
def sticks_position_change(sticks):
	for top_or_bottom_stick in sticks:
		for eachStick in top_or_bottom_stick:
			for word in eachStick:
				if word[0] == 0 or word[0] == 1:
					word[0] += 2
				else:
					word[0] -= 2
	return sticks

# def word_selection(strings):
# 	result = []
# 	words_to_select = []
# 	for string in strings:
# 		words_to_select.append(' '.join(string))
# 	word_counts = Counter(words_to_select)
# 	if word_counts.most_common(1)[0][1] == 1:
# 		result.append(words_to_select[google_index])
# 	else:
# 		word_counts.most_common(1)[0][0]
# 	return result
	
# def all_in_one(strings, ordered_sticks, google_index, shifts = [0, 0, 0, 0]):
# 	strings_to_select = []
# 	strings_to_pass = []
# 	now_result = []
# 	for stick in ordered_sticks:
# 		for word in stick:
# 			word[1] -= shifts[word[0]]
	
# 	if len(ordered_sticks) == 0:
# 		now_result.insert(0, word_selection(strings))
# 		return now_result
		
# 	if len(ordered_sticks[0]) == 4:
# 		for i in range(0, 4):
# 			if ordered_sticks[0][i][1] == 0:
# 				strings_to_select.append([])
# 				strings_to_pass.append(strings[i][1:len(strings[i])])
# 			else:
# 				strings_to_select.append(strings[i][0:ordered_sticks[0][i][1]])
# 				strings_to_pass.append(strings[i][ordered_sticks[0][i][1]+1:len(strings[i])])
# 			shifts[i] = ordered_sticks[0][i][1]
		
		
# 	if len(ordered_sticks[0]) == 3:
# 		average_index = round((ordered_sticks[0][0][1] + ordered_sticks[0][1][1] + ordered_sticks[0][2][1])/3)
# 		show_index = []
# 		for i in range(0, 3):
# 			show_index.append(ordered_sticks[0][i][0])
# 			if ordered_sticks[0][i][1] == 0:
# 				strings_to_select.append([])
# 			else:
# 				strings_to_select.append(strings[i][0:ordered_sticks[0][i][1]])
# 			shifts[i] = ordered_sticks[0][i][1]
# 		the_rest_index_set = set([0,1,2,3]) - set(show_index)
# 		the_rest_index = [i for i in the_rest_index_set][0]
# 		strings_to_select.insert(the_rest_index, strings[0:average_index])
# 		shifts.insert(the_rest_index, average_index)
	
# 	del ordered_sticks[0]
# 	now_result = all_in_one(strings_to_pass, ordered_sticks, google_index, shifts)
# 	now_result.insert(0, word_selection(strings_to_select))
	
# 	for stick in ordered_sticks:
# 		for word in stick:
# 			word[1] += shifts[word[0]]
	
	
# 	return now_result
	
if __name__ == '__main__':
	results = []
	while True:
		#print("API name:")
		#API_name = input()
		#if API_name == "end" or API_name == "END":
		#	break
		print("Recognition result:")
		str = input().lower().split()
		if str == ["end"]:
			break
		result = Result("none", str)
		results.append(result)
	
	result_number = len(results)
	result_combs = []
	
	for comb in itertools.combinations(range(0,result_number), 2):
		string0 = results[comb[0]].str
		string1 = results[comb[1]].str
		max_score, best_sticks = score_calculating(string0, string1)
		result_combs.append(Result_comb(comb, results[comb[0]], results[comb[1]], max_score, best_sticks))
	
	if result_number == 4:
		result_comb0 = type('Result_comb()', (), {})()
		result_comb1= type('Result_comb()', (), {})()
		best_comb = (result_comb0, result_comb1)
		max_comb_socre = -2147483648
		all_combs = [[(0,1),(2,3)], [(0,2),(1,3)], [(0,3),(1,2)]]
		
		for comb in all_combs:
			for result_comb in result_combs:
				if result_comb.comb == comb[0]:
					result_comb0 = result_comb
				elif result_comb.comb == comb[1]:
					result_comb1 = result_comb
			if result_comb0.score + result_comb1.score > max_comb_socre:
				max_comb_socre = result_comb0.score + result_comb1.score
				best_comb = (result_comb0, result_comb1)
		
		strings = [best_comb[0].result0.str, best_comb[0].result1.str, best_comb[1].result0.str, best_comb[1].result1.str]
		sticks = [[], []]
		for stick in best_comb[0].sticks:
			sticks[0].append([[0, stick[0]], [1, stick[1]]])
		for stick in best_comb[1].sticks:
			sticks[1].append([[2, stick[0]], [3, stick[1]]])
		
		print("===============================")
		print(best_comb[0].result0.str)
		print(best_comb[0].result1.str)
		print("-----------------------------")
		print(best_comb[1].result0.str)
		print(best_comb[1].result1.str)
		print("===============================")
		
		max_score_top_to_bottom, best_sticks_top_to_bottom = advance_score_calculating(strings, sticks)

		after_change_sticks = sticks_position_change(copy.deepcopy(sticks))
		max_score_bottom_to_top, best_sticks_bottom_to_top = advance_score_calculating([strings[2], strings[3], strings[0], strings[1]], [after_change_sticks[1], after_change_sticks[0]])
		best_sticks_bottom_to_top = sticks_position_change(best_sticks_bottom_to_top)
		for top_or_bottom_stick in best_sticks_bottom_to_top:
			for eachStick in top_or_bottom_stick:
				eachStick.sort(key=lambda x :x[0])
		
		best_sticks = [best_sticks_top_to_bottom[0] , best_sticks_bottom_to_top[0]]

		for i in range(0, len(best_sticks[0])):
			for j in range(0, len(best_sticks[1])):
				if all(elem in best_sticks[1][j] for elem in best_sticks[0][i]):
					best_sticks[0][i] = []
				elif all(elem in best_sticks[0][i] for elem in best_sticks[1][j]):
					best_sticks[1][j] = []
				elif any(elem in best_sticks[0][i] for elem in best_sticks[1][j]):
					if len(best_sticks[0][i]) >= len(best_sticks[1][j]):
						best_sticks[1][j] = []
					else:
						best_sticks[0][i] = []
		best_sticks[0] = list(filter(lambda a: a != [], best_sticks[0]))
		best_sticks[1] = list(filter(lambda a: a != [], best_sticks[1]))

		best_sticks = best_sticks[0] + best_sticks[1]
		
		crosses = {}
		for i in range(0,len(best_sticks)):
			crosses[i] = []
		for i in range(0, len(best_sticks) - 1):
			for j in range(i+1, len(best_sticks)):
				if len(best_sticks[i]) >= 3 and len(best_sticks[j]) >= 3:
					order = []
					find_cross = False
					for i_word in best_sticks[i]:
						for j_word in best_sticks[j]:
							if i_word[0] ==  j_word[0]:
								if len(order) == 0:
									if i_word[1] > j_word[1]:
										order = [j, i]
									else:
										order = [i, j]
								else:
									if i_word[1] > j_word[1] and order[0] == i:
										crosses[i].append(j)
										crosses[j].append(i)
										find_cross = True
										break
									elif i_word[1] < j_word[1] and order[0] == j:
										crosses[i].append(j)
										crosses[j].append(i)
										find_cross = True
										break
						if find_cross == True:
							break
		
		# solve cross sticks
		no_cross_sticks = []
		while any(len(crosses[x]) > 0 for x in crosses):
			max_len = 0
			index_to_delete = -1
			for i in range(0, len(crosses)):
				if len(crosses[i]) > max_len:
					index_to_delete = i
					max_len = len(crosses[i])
			
			if len(best_sticks[index_to_delete]) == 4:
				no_cross_sticks.append([best_sticks[index_to_delete][0], best_sticks[index_to_delete][1]])
				no_cross_sticks.append([best_sticks[index_to_delete][2], best_sticks[index_to_delete][3]])
				best_sticks[index_to_delete] = []
			
			elif best_sticks[index_to_delete][0][0] == 0 and best_sticks[index_to_delete][1][0] == 1:
				no_cross_sticks.append([best_sticks[index_to_delete][0], best_sticks[index_to_delete][1]])
				best_sticks[index_to_delete] = []
			
			elif best_sticks[index_to_delete][1][0] == 2 and best_sticks[index_to_delete][2][0] == 3:
				no_cross_sticks.append([best_sticks[index_to_delete][1], best_sticks[index_to_delete][2]])
				best_sticks[index_to_delete] = []
			
			crosses[index_to_delete] = []
			for i in range(0, len(crosses)):
				if index_to_delete in crosses[i]:
					crosses[i].remove(index_to_delete)
			
		best_sticks = list(filter(lambda a: a != [], best_sticks))
		no_cross_sticks += best_sticks
		
		
		#sort those no_cross_sticks
		temp_sticks_order_in_string = {0:[], 1:[], 2:[], 3:[]}
		for stick_index in range(0, len(no_cross_sticks)):
			for word in no_cross_sticks[stick_index]:
				if len(temp_sticks_order_in_string[word[0]]) == 0:
					temp_sticks_order_in_string[word[0]].append((stick_index, word[1]))
				else:
					index_to_insert = 0
					for i in range(0, len(temp_sticks_order_in_string[word[0]])):
						if word[1] > temp_sticks_order_in_string[word[0]][i][1]:
							index_to_insert = i+1

					temp_sticks_order_in_string[word[0]].insert(index_to_insert, (stick_index, word[1]))
		
		sticks_order_in_string = {0:[], 1:[], 2:[], 3:[]}
		for string_index in temp_sticks_order_in_string:
			for tuple in temp_sticks_order_in_string[string_index]:
				sticks_order_in_string[string_index].append(tuple[0])
		
				
		stick_order = sticks_order_in_string[0]
		for string_index in range(1, 4):
			for i in range(0, len(sticks_order_in_string[string_index])):
				if sticks_order_in_string[string_index][i] not in stick_order:
					inserted = False
					for j in range(i-1, -1, -1):
						if sticks_order_in_string[string_index][j] in stick_order:
							stick_order.insert(stick_order.index(sticks_order_in_string[string_index][j])+1, sticks_order_in_string[string_index][i])
							inserted = True
							break
					if inserted == False:
						for j in range(i+1, len(sticks_order_in_string[string_index])):
							if sticks_order_in_string[string_index][j] in stick_order:
								stick_order.insert(stick_order.index(sticks_order_in_string[string_index][j]), sticks_order_in_string[string_index][i])
								inserted = True
								break
					if inserted == False:
						stick_order.insert(0, sticks_order_in_string[string_index][i])
		
		ordered_sticks = []
		for i in stick_order:
			ordered_sticks.append(no_cross_sticks[i])
		for stick in ordered_sticks:
			print(stick)
		
		google_index = 0
		google_str = ""
		if result_comb0.result0.API == "google":
			google_str = result_comb0.result0.string0
		elif result_comb0.result1.API == "google":
			google_str = result_comb0.result0.string0
		elif result_comb1.result0.API == "google":
			google_str = result_comb0.result0.string0
		elif result_comb1.result1.API == "google":
			google_str = result_comb0.result0.string0
		
		if google_str != "":
			google_index = strings.index(google_str)
		