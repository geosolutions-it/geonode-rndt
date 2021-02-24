import ast
import os
from ast import literal_eval


def rndt_tags(request):
    return {
        "DISABLE_LAYER_CONSTRAINTS": ast.literal_eval(os.getenv('DISABLE_LAYER_CONSTRAINTS', 'True'))
    }
