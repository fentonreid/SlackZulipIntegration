import os
# create the jasmine server instance, automatically detects and runs the spec.js test
os.chdir("../javascript")
os.system("jasmine server -p 5000")