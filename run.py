"""
Launcher for the TeXForm API. Sets TRANSFORMERS_NO_TF=1 before any other
imports so transformers uses only PyTorch and never loads TensorFlow.
"""
import os

os.environ["TRANSFORMERS_NO_TF"] = "1"

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )
