from langchain.tools import tool
import restrictedpython 
from restrictedpython import compile_restricted, safe_globals, limited_builtins
import os 
import signal
import pandas as pd
import plotly.express as px

timeout = int (os.getenv("SAFE_PYTHON_TIMEOUT", "5"))
safe_globals['pd'] = pd
safe_globals['px'] = px 
safe_globals['print'] = print
safe_globals['_getitem_'] = limited_builtins['getitem']
safe_globals['_getattr_'] = limited_builtins['getattr']

del safe_globals['__import__']
del safe_globals['open']
del safe_globals['eval']
del safe_globals['exec']

def timeout_handler(signum, frame):
    raise TimeoutError("Code execution exceeded the time limit.")   
@tool
def safe_python_executor(code: str) -> str:
    try:
        byte_code = compile_restricted(code, '<string>', 'exec')
        locals_dict= {}
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm (timeout)
        exec(byte_code, safe_globals, locals_dict)
        signal.alarm(0)
        return "Code executed successfully."
    except TimeoutError as te:
        return f"TimeoutError: {str(te)}"
    except restrictedpython.RestrictedPythonError as rpe:
        return restrictedpython
    

    