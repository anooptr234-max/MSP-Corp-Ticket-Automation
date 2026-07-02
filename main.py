import os
import sys
import uvicorn

# Dynamically add the current directory to Python's path to prevent folder import errors
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# PASTE YOUR REAL KEY INSIDE THE QUOTES BELOW ⬇️
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY_HERE"
if __name__ == "__main__":
    print("Starting the MSP Corp Ticket Automation Server...")
    # Start the FastAPI server on localhost port 8000
    uvicorn.run("api.app:app", host="127.0.0.1", port=8000, reload=False)
