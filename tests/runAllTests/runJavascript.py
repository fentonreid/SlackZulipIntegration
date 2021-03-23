import os
import sys

# create the jasmine server instance, automatically detects and runs the spec.js test
os.chdir("../javascript")
try:
    os.system(f"jasmine server -p {sys.argv[1]}")
except:
    os.system("jasmine server -p 5000")
