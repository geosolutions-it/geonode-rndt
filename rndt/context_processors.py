from ast import literal_eval


import ast, os

def rndt_tags(request):
    return {
        "DISABLE_LAYER_CONSTRAINTS": ast.literal_eval(os.getenv('DISABLE_LAYER_CONSTRAINTS', 'True'))
    }