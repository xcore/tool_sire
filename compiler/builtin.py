from ast import Def, Formals, Param
from type import Type

printchar = Def(
        'printchar', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('val', 'single'))]),
        None, None)

printcharln = Def(
        'printcharln', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('val', 'single'))]),
        None, None)

printval = Def(
        'printval', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('val', 'single'))]),
        None, None)

printvalln = Def(
        'printvalln',
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('val', 'single'))]),
        None, None)

printstr = Def(
        'printstr', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('var', 'alias'))]),
        None, None)

printstrln = Def(
        'printstrln', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('var', 'alias'))]),
        None, None)

exit = Def(
        'exit', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('val', 'single'))]),
        None, None)

functions = (
	printchar,
	printcharln,
    printval,
	printvalln,
    printstr,
	printstrln,
    exit,
)

