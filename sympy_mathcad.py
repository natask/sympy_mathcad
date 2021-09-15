#!/bin/env python3
import sympy
from sympy import *
from sympy.physics.units import *

def parse_line(line, sym_list, eq_list, res_list, conv_list):
  if "`" in line:
    exec(line[:line.find("`")], globals())
    try:
      print(eval(line[:line.find("`")]))
    except:
      pass
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

def print(*args, **kargs):
    new_args = []
    for arg in args:
      string = str(arg)
      string = string.replace("**", "^")
      new_args.append(string)
    __builtins__.print(*new_args, **kargs)


def parse_all(lines):
  sym_list = []
  eq_list = []
  res_list = []
  conv_list = []
  lines = lines.replace("^", "**")

  for line in lines.split("\n"):
    if line:
      sym_list, eq_list, res_list, conv_list = parse_line(line, sym_list,  eq_list, res_list, conv_list)
  try:
    sol = sympy.solve(eq_list, sym_list, dict=True) #want to use sym_list here
    sol2 = sympy.solve(eq_list, res_list, dict=True)
    print(sol)
    print(sol2)
  except:
    sol = sympy.dsolve(eq_list, dict=True)
    new_sol = []
    for soll in sol:
      new_sol.append({res_list[0] : soll.args[1] })
    sol = new_sol
    print(sol)

  for entry, conv in conv_list:
    dn = ""
    if len(sol) != 0:
      val = sol[0][entry] if entry in sol[0] else sol2[0][entry]
      if conv:
           val = sympy.physics.units.convert_to(val,conv)
      dn = print_res(val)
      for so in sol[1:]:
        dn += " or "
        dn += print_res(val)
    dn = dn if dn else "NONE";
    print(entry, " = ", dn)

def reset_repl():
  pass
 # import sys
 # __here__ = sys.modules[__name__]
 # try:
 #  delattr(__here__, '__package__')
 #  delattr(__here__, 'gram')
 # except:
 #   pass
 # from sympy_mathcad import parse_all, print, parse_line, print_res, reset_repl


if __name__ == "__main__":
    import sys
    from prompt_toolkit import prompt
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.key_binding import KeyBindings

    bindings = KeyBindings()

    @bindings.add('c-q')
    @bindings.add('c-c')
    @bindings.add('c-d')
    def _(event):
      event.app.exit()

    @bindings.add('c-j') #j for default eval
    def _(event):
      " Do something if 'a' has been pressed. "
      #event.app.layout.current_window.content.buffer.text += "\n" + "e\n"
      print()
      print("-"*30+"RES"+"-"*30)
      parse_all((event.current_buffer.text) + "`")
      print("-"*30+"END"+"-"*30)
      reset_repl()
      event.current_buffer.append_to_history()
      event.current_buffer.reset()

    @bindings.add('c-s') #s for show
    def _(event):
      " Do something if 'a' has been pressed. "
      #event.app.layout.current_window.content.buffer.text += "\n" + "e\n"
      global lines
      lines += event.current_buffer.text + "\n" if event.current_buffer.text else "";
      print()
      print("-"*30+"RES"+"-"*30)
      print(lines, end="")
      print("-"*30+"END"+"-"*30)
      event.current_buffer.append_to_history()
      event.current_buffer.reset()

    @bindings.add('c-f') #f for flush
    def _(event):
      " Do something if 'a' has been pressed. "
      #event.app.layout.current_window.content.buffer.text += "\n" + "e\n"
      #print("-"*30+"RES"+"-"*30)
      global lines
      event.current_buffer.append_to_history()
      event.current_buffer.reset()
      reset_repl()
      lines = ""
      print()
      print("-"*30+"END"+"-"*30)
      print("-"*30+"RES"+"-"*30)

    @bindings.add('escape','enter') #r for run/execute
    @bindings.add('c-r') #r for run/execute
    def _(event): # trancates evaluation at some part of parse_all if don't put new line before calling run.
      " Do something if 'a' has been pressed. "
      #event.app.layout.current_window.content.buffer.text += "\n" + "e\n"
      global lines
      add_str = event.current_buffer.text + "\n\n" if event.current_buffer.text else "";
      lines = lines + add_str;
      event.current_buffer.append_to_history()
      event.current_buffer.reset()
      print()
      print("-"*30+"RES"+"-"*30)
      parse_all(lines)
      print("-"*30+"END"+"-"*30)
      lines = ""

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
Press C-j to evaluate current line as a python statement.
Press C-c or C-q or C-d to quit.
{"-"*30}END{"-"*30}""")
      global lines
      lines = ""
      while True:
        line =  prompt(history=FileHistory('history.txt'), key_bindings=bindings)
        if line:
          if not line.strip():
            pass
          elif line in "evaluate":
            print("-"*30+"RES"+"-"*30)
            parse_all(lines)
            print("-"*30+"END"+"-"*30)
            reset_repl()
            lines = ""
          elif line in "clear":
            print("-"*30+"RES"+"-"*30)
            reset_repl()
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
        else:
          break
    elif len(sys.argv) == 2:
      with open(sys.argv[1]) as f:
        parse_all(f.read())
