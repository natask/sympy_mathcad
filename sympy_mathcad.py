#!/bin/env python3
import sympy
import ast
from sympy import *
from sympy.physics.units import *

DEFINED_EXPRESSIONS = []
def define_vars(var_string):
  root_node = ast.parse(var_string.replace("=","+")); #equal sign messes up parser
  node_names = [node.id for node in ast.walk(root_node) if type(node) == ast.Name]
  old_syms = [sym for (name,sym) in globals().items() if type(sym) == sympy.core.symbol.Symbol]; #TODO: I would want to store all syms and flush them when session ends so I can redefine them in the next session
  new_syms = [sympy.var(name) for name in node_names if not name in globals()];
  replace_names = [name for name in DEFINED_EXPRESSIONS if name in node_names];
  [DEFINED_EXPRESSIONS.remove(name) for name in replace_names];
  replace_syms = [sympy.var(name) for name in replace_names];
  return new_syms + old_syms + replace_syms

def define_expressions(var_string):
  global DEFINED_EXPRESSIONS;
  root_node = ast.parse(var_string[:var_string.find("=")]); #removes ";" at the end if "=" not found and still parses correctly
  node_names = [node.id for node in ast.walk(root_node) if type(node) == ast.Name]
  expressions = [name for name in node_names if not name in globals()];
  DEFINED_EXPRESSIONS += expressions

def parse_line(line, sym_list, eq_list, res_list, conv_list, guess_list, inequality):
  if ";" in line: # eval line in python mode
    define_expressions(line)
    sym_list += define_vars(line)
    exec(line, globals())
    try:
      res = (eval(line[:line.find(";")]))
      if a != None:
        print(res)
    except:
      pass
  elif "?" in line: # find this variable
    sym = sympy.var(line[:line.find("=")])
    res_list.append(sym)
    if line.find("~") != -1:
      guess_list.append(float(line[line.find("~") + 1:]))
    conv = (sym, None)
    if len(val := line[line.find("?") + 1:].strip()):
       conv = (sym, eval(val))
    conv_list.append(conv)
  else:
    #equation = line[:line.find("=", line.find("=") + 1)]
    equation = line
    sym_list += define_vars(equation)
    if (">" in equation or "<" in equation): # inequalities don't seem to work for solving multiple equations
      str_eq = equation
      inequality = True
      eq = eval(str_eq)
      eq_list.append(eq)
    elif "=" in equation and not (">" in equation or "<" in equation): # inequalities don't seem to work for solving multiple equations
       str_eq = "sympy.Eq(" + equation.replace("=",",") + ")"
       eq = eval(str_eq)
       eq_list.append(eq)
    else: # must be a single line
      exec(line, globals())
      try:
        print(eval(line))
      except:
        pass
  return (sym_list, eq_list,res_list, conv_list, guess_list, inequality)

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
  guess_list = []
  inequality = False
  lines = lines.replace("^", "**")

  for line in lines.split("\n"):
    if line:
      sym_list, eq_list, res_list, conv_list, guess_list,inequality = parse_line(line, sym_list, eq_list, res_list, conv_list, guess_list, inequality)
  try:
    if guess_list:
      raise
    sol = sympy.solve(eq_list, sym_list, dict=True) #want to use sym_list here
    sol2 = sympy.solve(eq_list, res_list, dict=True)
    print(sol)
    print(sol2)
  except:
    try: #numerical solve
      print("--trying numerical solve--")
      #print(eq_list)
      #print(res_list)
      #print(guess_list)
      sol2 = sympy.nsolve(eq_list, res_list, guess_list, dict=True)
      sol = sol2
      #print(eq_list)
      print(sol2)
    except Exception as e: #diff eq
      print(e)
      print("--trying diff eq solve--")
      sol = sympy.dsolve(eq_list, dict=True)
      new_sol = []
      for soll in sol:
        new_sol.append({res_list[0] : soll.args[1] })
        sol = new_sol
        print(sol)

  print(conv_list)
  for entry, conv in conv_list:
    dn = ""
    if inequality:
      dn = str(sol)
    elif len(sol) != 0:
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
    import os
    HISTORY_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "history.txt")

    bindings = KeyBindings()

    @bindings.add('c-q')
    def _(event):
      event.app.exit()

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

    @bindings.add('c-r') #r for run/execute
    @bindings.add('escape','enter') #r for run/execute
    def _(event): # trancates evaluation at some part of parse_all if don't put new line before calling run.
      " Do something if 'a' has been pressed. "
      #event.app.layout.current_window.content.buffer.text += "\n" + "e\n"
      global lines
      add_str = event.current_buffer.text if event.current_buffer.text else "";
      lines = lines + add_str;
      #event.current_buffer.validate_and_handle()
      event.current_buffer.text = lines[:-1];
      event.current_buffer.append_to_history()
      event.current_buffer.reset()
      print("-"*30+"RES"+"-"*30)
      parse_all(lines)
      print("-"*30+"END"+"-"*30)
      lines = ""

    @bindings.add('enter') #r for run/execute
    def _(event):
      #event.current_buffer.text += "\n"
      #event.current_buffer.cursor_position = len(event.current_buffer.text)
      valid = event.current_buffer.validate(set_cursor = True)
      if valid:
        if event.current_buffer.accept_handler:
           keep_text =  event.current_buffer.accept_handler(event.current_buffer)
        else:
           keep_text = False
      else:
        print(event.current_buffer.text)
        print(event.current_buffer.document)
        # if not keep_text:
        #   event.current_buffer.reset()

    if len(sys.argv) == 1:
      print(
f"""Welcome to repl.
Press Enter to enter equations in mathcad like format. can be used to enter multi line equations. This is useful for keeping history intact.
Press Alt-Enter or C-r to evaluate equations. Needs to be preceded by an Enter.
Press C-f to flush or clear currently entered equations.
Press C-s to show or print currently entered equations.
Press C-c or C-q or C-d to quit.

text based:
Enter any substring of "evaluate" to evaluate equations.
Enter any substring of "clear" to clear currently entered equations.
Enter any substring of "print" to see currently entered equations.
Enter any substring of "quit" to quit.
{"-"*30}END{"-"*30}""")
      global lines
      lines = ""
      while True:
        line =  prompt(history=FileHistory(HISTORY_FILE), key_bindings=bindings)
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
    elif len(sys.argv) > 1:
      if sys.argv[1] == "term":
        with open('/dev/stdin') as f:
          parse_all(f.read()) # -> "values"
      else:
        with open(sys.argv[1]) as f:
          parse_all(f.read())
