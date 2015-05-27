import os,sys,time
from subprocess import (PIPE, Popen)
import yaml
from flask import request


from flask import Flask
app = Flask(__name__)

def cmd(command):
  return Popen(command, stdout=PIPE, shell=True).stdout.read()

def runme(loc1,loc2):
    locdir = loc1
    locdir2 = loc2
    data = {}
    if os.path.isdir(locdir):
        if os.path.isdir(locdir2):
                for x in os.listdir(locdir):
                    path1 = os.path.join(locdir, x)
                    if os.path.isfile(path1) and path1.endswith(".yml"):
                        fs = open(path1, 'r')
                        yml = yaml.load(fs)
                        if ('lastAccountName' in yml):
                            key = yml['lastAccountName']

                            if (not key in data):
                                data[key] = { 'f1': path1, 'f2': None }
                            else:
                                data[key]['f1'] = path1

                for x in os.listdir(locdir2):
                    path1 = os.path.join(locdir2, x)
                    if os.path.isfile(path1) and path1.endswith(".yml"):
                        fs = open(path1, 'r')
                        yml = yaml.load(fs)
                        if ('lastAccountName' in yml):
                            key = yml['lastAccountName']

                            if (not key in data):
                                data[key] = { 'f1': None, 'f2': path1 }
                            else:
                                data[key]['f2'] = path1

                count = 0

                for y in data:

                    f1_file = data[y]['f1'] # old file
                    f2_file = data[y]['f2'] # new file
                    # compare both files, t ake the newer one
                    # ...
                    if f1_file and f2_file:
                        #cmd("rm -rf %s"%f2_file)
                        #cmd('mv "' + f2_file + '" "' + f1_file + '"')
                        count += 1

                return "Finished moving %i records"%count
        else:
            return "path 2 does not exist"

    else:
        return "path 1 does not exist"



@app.route('/bb&<path:loc1>&<path:loc2>&<apikey>', methods=['GET', 'POST'] )
def bb(loc1,loc2,apikey):
    if apikey == 'gprzZwWhC22qKEWWvISe6bFXHfA1NbT6':
        return runme(loc1,loc2)
    else:
        return "You are not welcome here!"

@app.route('/test')
def test():
    pass


if __name__ == '__main__':
    app.run(debug=True,host="127.0.0.1",port=1337)