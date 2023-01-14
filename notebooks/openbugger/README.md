# OpenBugger

https://github.com/furlat/OpenBugger/blob/main/README.md is a Python package
that allows you to inject syntax and logic errors into your code. This can be
useful for testing the robustness of your code or for creating test cases for
debugging exercises or for training an assistant to debug code.

The Python notebook openbugger_example.ipynb does the following:

1. Imports the necessary libraries to install OpenBugger in the notebookdirecory
   (os and subprocess).
2. Defines a function, install_openbugger, which clones the OpenBugger
   repository from GitHub and installs it using pip.
3. Calls the install_openbugger function to install OpenBugger.
4. Imports the SyntaxBug and LogicBug classes from the syntax_injector and
   logic_injector modules, respectively.
5. Creates an instance of the SyntaxBug class and assigns it to the syntax_bug
   variable.
6. Defines three scripts: a simple script, a medium script, and a hard script.
7. Calls the inject method on the simple script, passing in the string "easy" as
   the second argument and the integer 1 as the third argument. This will inject
   easy syntax errors into the script. The *item *item modified script, a list
   of the injected errors, and the number of errors injected are returned and
   assigned to variables.
8. Prints the original and modified versions of the simple script, as well as
   the list of injected errors and the number of errors injected. 10 Repeats
   steps 7 and 8 for the medium and hard scripts, but with the "medium" and
   "hard" injection methods and different numbers of errors to inject.

General Usage To use OpenBugger, import the SintaxBug or LogicBug classes from
the openbugger module and use them to inject a bug with a call to the inject().
The injector will return the modified script with the injected bug.

```
from syntax.syntax_injector import SyntaxInjector, SyntaxBug

syntax_bug = SyntaxBug()



# Simple script
simple_script = """
def greet(name):
    print("Hello, " + name)

greet("Bob")
"""

print(simple_script)
```

The simple script can be modified using the "easy" injection method because it
only contains simple syntax and does not have any nested code blocks. This means
that there are fewer characters (e.g. quotes, brackets, braces, parenthesis)
that could be the target of syntax errors, and the "easy" injection method,
which only injects errors that involve replacing or removing a single character,
is sufficient to modify the script.

```
# Inject easy syntax errors into the simple script

modified_simple_script, errors, counter = syntax_bug.inject(simple_script, "easy", 1)
print("Modified version Easy",errors,counter)
print(modified_simple_script)
```

Or for higher severity and logic error by directly transforming a Python class
into text

```
import inspect
import random
from logic.logic_injector import LogicBug


# Medium example script
def medium_script():
    # Choose a random integer and assign it to a variable
    num = random.randint(0, 10)

    # Use a loop to print all numbers from 0 to the chosen integer
    for i in range(num):
        print(i)

# create an instance of the LogicBug class
logic_bug = LogicBug()
# get the source code of the medium_script function as a string
medium_script_str = inspect.getsource(medium_script)
print("Medium",medium_script_str)
# inject a logic error into the medium_script function
modified_medium_script, error, counter = logic_bug.inject(medium_script_str,"medium",num_errors=3)
```
