from ast import Def, Formals, Param
from type import Type

printval = Def(
        'printval', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('val', 'single'))]),
        None, None)

printstr = Def(
        'printstr', 
        Type('proc', 'procedure'), 
        Formals([Param('v', Type('var', 'alias'))]),
        None, None)

functions = (
        printval,
        printstr
        )

