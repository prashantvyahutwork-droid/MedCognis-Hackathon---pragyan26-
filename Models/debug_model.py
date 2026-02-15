import traceback
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from triage_logic import TriageEngine
    print("CWD:", os.getcwd())
    print("Files:", os.listdir('.'))
    engine = TriageEngine()
    print("Success: Model loaded!")
except Exception as e:
    print(f"Error type: {type(e)}")
    print(f"Error message: {e}")
    traceback.print_exc()
