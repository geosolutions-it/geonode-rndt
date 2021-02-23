import ast
import os

from rndt.layers.forms import LayerRNDTForm


def rndt_tags(request):
    return {
        "DISABLE_LAYER_CONSTRAINTS": ast.literal_eval(
            os.getenv("DISABLE_LAYER_CONSTRAINTS", "True")
        ),
        "LayerRNDTForm": LayerRNDTForm,
    }
