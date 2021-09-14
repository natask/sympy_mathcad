#!/bin/env python3
import sympy
from sympy import *
from sympy.physics.units import *

def parse_line(line, sym_list, eq_list, res_list, conv_list):
  if "`" in line:
    exec(line[:line.find("`")], globals())
  elif "?" in line:
    sym = sympy.var(line[:line.find("=")])
    res_list.append(sym)
    conv = (sym, None)
    if len(val := line[line.find("?") + 1:].strip()):
      conv = (sym, eval(val))
    conv_list.append(conv)
  else:
    #equation = line[:line.find("=", line.find("=") + 1)]
    equation = line
    sym_list += sympy.var(equation)
    str_eq = "sympy.Eq(" + equation.replace("=",",") + ")"
    eq = eval(str_eq)
    eq_list.append(eq)
  return (sym_list, eq_list,res_list, conv_list)

def print_res(res):
     ret = str(res) if 'sympy.core.numbers.Integer' in str(type(res)) else str(sympy.N(res,4))
     #ret += "" if "sympy.core.numbers" not in str(type(res)) else " or " + "{:e}".format(sympy.N(res,4))
     return  ret;

def parse_all(lines):
  sym_list = []
  eq_list = []
  res_list = []
  conv_list = []
  lines = lines.replace("^", "**")

  for line in lines.split("\n"):
    if line:
      sym_list, eq_list, res_list, conv_list = parse_line(line, sym_list,  eq_list, res_list, conv_list)
  sol = sympy.solve(eq_list, sym_list, dict=True) #want to use sym_list here
  print(sol)
  print(sympy.solve(eq_list, res_list, dict=True))
  for entry, conv in conv_list:
    dn = ""
    if len(sol) != 0:
      val = sol[0][entry]
      if conv:
           val = sympy.physics.units.convert_to(val,conv)
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
Enter any substring of "evaluate" to evaluate equations.
Enter any substring of "clear" to clear currently entered equations.
Enter any substring of "print" to see currently entered equations.
Enter any substring of "quit" to quit.
Press C-c or C-d to quit.
{"-"*30}END{"-"*30}""")
      lines = ""
      while True:
        line =  input()
        if not line.strip():
          pass
        elif line in "evaluate":
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
