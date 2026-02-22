"""
Launcher for the TeXForm API. Blocks TensorFlow before any other imports
so transformers uses only PyTorch and never triggers the ml_dtypes error.
"""
import os
import sys

os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["USE_TORCH"] = "1"

# Prevent transformers from importing TensorFlow even when it's installed.
# Newer transformers (4.50+) can still import TF in image_transforms.py;
# blocking the module entirely avoids the ml_dtypes "handle" crash.
# The stub needs a proper __spec__ so torch._dynamo.trace_rules doesn't fail.
if "tensorflow" not in sys.modules:
    import importlib.machinery
    _fake_tf = type(sys)("tensorflow")
    _fake_tf.__version__ = "0.0.0"
    _fake_tf.__spec__ = importlib.machinery.ModuleSpec("tensorflow", None)
    sys.modules["tensorflow"] = _fake_tf

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )
