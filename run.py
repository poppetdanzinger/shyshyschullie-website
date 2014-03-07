#!venv/bin/python3
import sys, os

realpath=os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(realpath,"venv"))
sys.path.append(os.path.join(realpath,"venv/lib/python3.3/site-packages"))

from app import app

if __name__=="__main__":
    app.run(debug = True)
