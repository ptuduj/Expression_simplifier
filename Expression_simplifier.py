import sys
import string

operators = ["<=>", "=>", "||", "&&", "^"]
prefix_operator = ["~"]
precedence = {"<=>": 1, "=>": 2, "||": 3, "&&": 4, "^": 5}
associativity = {"<=>": "right", "=>": "right", "||": "left", "&&": "left", "^": "left",}
variables = []
var_num = 0


dec_bin_dict = {}               # {binary number: decimal number}   - values for which expression is true 
ones_count_dict = {}            # {binary number: how many "1" in binary}
flag_dict = {}                  # {binary number: if combined flag}
minterms = {}


def split(expr):	
	VARS = string.ascii_lowercase + string.ascii_uppercase + "0123456789"
	output = []
	tmp_operator = ""
	tmp_string = ""
	i = 0
		
	for char in expr:
		i += 1
		
		if char not in VARS and tmp_string != "":
			output.append(tmp_string)
			if tmp_string not in variables and tmp_string != "0" and tmp_string != "1":
				variables.append(tmp_string)
			tmp_string = ""	
			
		if char == " ":
			continue
			
		if char in "<=>|&~^":
			tmp_operator += char
			if tmp_operator in operators or tmp_operator in prefix_operator:
				output.append(tmp_operator)
				tmp_operator = ""
			else: continue	
					
		elif char in VARS:
			tmp_string += char
			if i == len(expr): 
				output.append(tmp_string)
				if tmp_string not in variables and tmp_string != "0" and tmp_string != "1":
					
					variables.append(tmp_string)
				
		elif char in "()":
			output.append(char)
			
		else:
			return False
	return output
			


def validate(expr):            # Check the syntactic correctness of expression 
		
	state = True
	par_count = 0
	
	for string in expr:
		if state == True:
			if string in variables:
				state = False
			elif string in "01":
				state = False

			elif string == "(":
				par_count += 1
			elif string in prefix_operator: pass
			else:
				return False
			
		else:
			if string in operators: 
				state = True
			elif string == ")": par_count -= 1
			else:
				return False
		
        if par_count < 0: 
			return False
	return par_count == 0 and not state 


#               conversion to RPN
def check_precedence(string, stack_top):
        if stack_top in prefix_operator:
            return True
        if stack_top in operators:
            if precedence[stack_top] > precedence[string]:
                return True
            if precedence[stack_top] == precedence[string] and associativity[stack_top] == "left":
                return True
            return False


def convert_to_RPN(expr): 
    stack = []
    output = []
        
    for string in expr:
        if string in variables or string in "01":
            output.append(string)
        elif string in prefix_operator:     # ~ has high precedence 
            stack.append(string)
        elif string == "(":
            stack.append(string)
        elif string == ")":
            while stack[-1] != "(":
                output.append(stack.pop())
            stack.pop()
        else:                                # string is infix operator
            while len(stack) > 0 and check_precedence(string, stack[-1]):
                output.append(stack.pop())
            stack.append(string)
            
    while len(stack) > 0:
        output.append(stack.pop())

    return output



#                      evaluate expressions         
def my_and(a, b):
	return bool(a and b)
        
def my_or(a, b):
	return bool(a or b)

def xor(a, b):
	return bool(a != b)
        
def negation(a):
	return not bool(a)

def implicaton(a,b):
	if a and not b:
		return False
	return True
		
        
def biconditional(a, b):
	return bool(a == b)  



def evaluate_expr(expr, bin_number):                # evaluate expression from RPN
	
	logic_functions = {
	"^": xor, 
	"=>": implicaton, 
	"<=>": biconditional, 
	"&&": my_and, 
	"||": my_or, 
	"~": negation
	}
	
	
	values = list(bin_number)     # bin numbers in array [1,0,0]
	dictionary = dict(zip(variables, values))
	stack = []
	
	for string in expr:
		if string in variables:
			stack.append(int(dictionary[string]))
		elif string in "01":
			stack.append(int(string))
		
		elif string in operators:             # infix operator
			a = stack.pop()
			b = stack.pop()
			funct = logic_functions[string](b, a)
			stack.append(funct)
			
		elif string in prefix_operator: # ~
			a = stack.pop()
			funct = logic_functions[string](a)
			stack.append(funct)
	return stack.pop()	



def to_bin(val, count):   
	bin_num = str(bin(val)[2:]).zfill(count)
	return bin_num



def count_ones(bin_num):
	counter = 0
	for i in bin_num:
		if i == "1":
			counter += 1
	return counter


def find_minterms():
	any_changes = False
	global dec_bin_dict, ones_count_dict, flag_dict 
	global minterms
	minterms = {}
	
	i = 0
	for num, ones_count in ones_count_dict.items():                      # combine binary numbers which differ in one position 
		for num2, ones_count2 in ones_count_dict.items():
			
			if (ones_count+1) == ones_count2:
				out = combine_minterms(num, num2)
				if out:
					flag_dict[num] = True
					flag_dict[num2] = True				
					set1 = {}
					set1 = dec_bin_dict[num].union(dec_bin_dict[num2])				
					minterms.update({out: set1})
					any_changes = True 					
		i += 1
	return any_changes


def combine_minterms(bin_num, bin_num2):           # firstly check
	different_int_counter = 0
	position = -1
	
	for i in range(len(bin_num)):                 # check
		if bin_num[i] != bin_num2[i]:
			different_int_counter +=1
			position = i
		if different_int_counter == 2:
			return False                         # can't combine minterms 
	
	output = ""
	for i in range(len(bin_num)):               # combine two binary numbers which differ in one position 
		if i != position:
			output += bin_num[i]
		else:
			output += '-'
	return output


def simplify(expr):	
	
	global var_num 
	var_num = len(variables)
	
	global dec_bin_dict, ones_count_dict, flag_dict, minterms         
	
	# find numbers for which expression evaluates to true  
	for i in range(2**var_num):
		bin_num = to_bin(i, var_num)
		if evaluate_expr(expr, bin_num):
			dec_bin_dict.update({bin_num: {i}})
			ones_count_dict.update({bin_num: count_ones(bin_num)})
			flag_dict.update({bin_num: False})
			
#                    	 Quine-McCluskey algorithm	
	
	essential_minterms = []
	state = find_minterms()     # flag 
	
	while state:	
		for x,y in flag_dict.items():
			if y == False:
				essential_minterms.append(x)
		flag_dict = {}
		ones_count_dict = {}
		dec_bin_dict = {}
		for key, val in minterms.items():              #update dictinaries	
			flag_dict.update({key: False})
			dec_bin_dict.update({key: val})
			ones_count_dict.update({key: count_ones(key)})
		
		state = find_minterms()
		
	for x in ones_count_dict:                    #  update essential_minterms
		essential_minterms.append(x)
	
	# print("essential_minterms: ", essential_minterms)
	
	# find simplifed expression  
	if essential_minterms == []:
		return "Always false!"
	
	if (len(variables) == 0 and essential_minterms == ['0']) or essential_minterms == ['-']:
		return "Always true!"
	
	simplified_expression = []

	for minterm in essential_minterms:	
		bin_list = list(minterm)
		component = []
		
		for var, val in zip(variables, bin_list):
			if val == "0":
				component.append("~" + var)	
			elif val == "1":
				component.append(var)
		simplified_expression.append(" && ".join(component))
	
	simplified_expression = " || ".join(simplified_expression)
	
	return simplified_expression
	

	
def main():
		  
	if len(sys.argv) < 2:
		print("Not enough argumnets! Give an expression to simplify.")
		return
	
	elif len(sys.argv) == 2:
		expr = split(sys.argv[1])
		
		if_valid = validate(expr)
		if if_valid:
			RPN_expr = convert_to_RPN(expr)
			#print("RPN expression: ",RPN_expr)
			print("Simplified expression: ")
			print(simplify(RPN_expr))
	
		
		
if __name__ == "__main__":
    main()
