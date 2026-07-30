import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from webapp.app import app

if __name__ == "__main__":
    app.run()
