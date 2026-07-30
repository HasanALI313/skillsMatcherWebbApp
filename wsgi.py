import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "webapp"))

from app import app

if __name__ == "__main__":
    app.run()
