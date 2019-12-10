import subprocess
# Path to a Python interpreter that runs any Python script
# under the virtualenv /path/to/virtualenv/
python_bin = "./ytvk-venv/bin/python3"

# Path to the script that must run under the virtualenv
script_file = "./api.py"

p = subprocess.Popen("pwd", stdout=subprocess.PIPE)
result = p.communicate()[0]
print(result)
while True:
    try:
        output = open('logs.txt', 'w+')
        with subprocess.Popen([python_bin, script_file], stdout=output, stderr=subprocess.PIPE, universal_newlines=True) as app:
            data, err = app.communicate()
    except Exception as e:
        print(e)
        output.write("Blyat") 
