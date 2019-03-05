import sys

activate_this = '/var/www/flask/myenv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0,'/var/www/flask')
from li import app as application
