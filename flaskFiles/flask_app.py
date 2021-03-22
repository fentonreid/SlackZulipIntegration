import os
import sys

sys.path.append("\\".join(os.getcwd().split("\\")[:-1]))

from flaskFiles import app

if __name__ == '__main__':
    try:
        app.run(port=sys.argv[1])
    except:
        app.run()