#!/bin/env python3
import sympy
from sympy import *
from sympy.physics.units import *

def parse_line(line, sym_list, eq_list, res_list, conv_dict):
  if " in " in line:
    pre = line[:line.find("=") + 1].strip()
    post = line[line.find("=") + 1 :line.find("in")].strip()
    arg = line[line.find("in") + len("in"):].strip()
    equation =  pre + " sympy.physics.units.convert_to(" + post + ", " + arg + ")"
    print(equation)
    sym_list += sympy.var(equation)
    str_eq = "sympy.Eq(" + equation.replace("=",",") + ")"
    eq = eval(str_eq)
    eq_list.append(eq)
  elif "?" in line:
    sym = sympy.var(line[:line.find("=")])
    res_list.append(sym)
    if len(val := line[line.find("?") + 1:].strip()):
      conv_dict[sym] = eval(val)
  else:
    #equation = line[:line.find("=", line.find("=") + 1)]
    equation = line
    sym_list += sympy.var(equation)
    str_eq = "sympy.Eq(" + equation.replace("=",",") + ")"
    eq = eval(str_eq)
    eq_list.append(eq)
  return (sym_list, eq_list,res_list, conv_dict)

def print_res(res):
     ret = str(res) if 'sympy.core.numbers.Integer' in str(type(res)) else str(sympy.N(res,4))
     #ret += "" if "sympy.core.numbers" not in str(type(res)) else " or " + "{:e}".format(sympy.N(res,4))
     return  ret;

def parse_all(lines):
  sym_list = []
  eq_list = []
  res_list = []
  conv_dict = {}
  lines = lines.replace("^", "**")

  for line in lines.split("\n"):
    if line:
      sym_list, eq_list, res_list, conv_dict = parse_line(line, sym_list,  eq_list, res_list, conv_dict)
  sol = sympy.solve(eq_list, sym_list, dict=True) #want to use sym_list here
  print(sol)
  print(sympy.solve(eq_list, res_list, dict=True))
  for entry in res_list:
    dn = ""
    if len(sol) != 0:
      val = sol[0][entry]
      if entry in conv_dict:
           val = sympy.physics.units.convert_to(val,conv_dict[entry])
      dn = print_res(val)
      for so in sol[1:]:
        dn += " or "
        dn += print_res(val)
    dn = dn if dn else "NONE";
    print(entry, " = ", dn)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
      print(
f"""Welcome to repl.
Enter equations in mathcad like format.
Make sure terms are seperated by space in front and back of the term. 1 * x + y instead of 1*x+y.
Make sure built-in terms like 'pi', and units like 'newton', DON'T have space in front of the term. like 1*pi intead of 1* pi.
Enter any substring of "evaluate" or empty line to evaluate equations.
Enter any substring of "clear" to clear currently entered equations.
Enter any substring of "print" to see currently entered equations.
Enter any substring of "quit" to quit.
Press C-c or C-d to quit.
{"-"*30}END{"-"*30}""")
      lines = ""
      while True:
        line =  input()
        if line in "evaluate":
          print("-"*30+"RES"+"-"*30)
          parse_all(lines)
          print("-"*30+"END"+"-"*30)
          lines = ""
        elif line in "clear":
          print("-"*30+"RES"+"-"*30)
          lines = ""
          print("-"*30+"END"+"-"*30)
        elif line in "print":
          print("-"*30+"RES"+"-"*30)
          print(lines, end="")
          print("-"*30+"END"+"-"*30)
        elif line in "quit":
          break
        else:
          lines += line + "\n"
    elif len(sys.argv) == 2:
      with open(sys.argv[1]) as f:
        parse_all(f.read())
