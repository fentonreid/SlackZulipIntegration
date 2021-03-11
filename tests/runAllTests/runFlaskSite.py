import os
# these tests run the test_flask.py file
os.chdir("../flaskSite")
os.system("pytest test_flask.py -s -v --tb=native")