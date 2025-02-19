 Creation of venv
  #install python version you wish to run in venv:
```  
brew install python@3.11
rehash
```
#create venv, choose the folder. In my case ~/espp.
#could be e.g. ~/python-projects/espp/venv
#venv name is espp - it is the name of the folder
```
  mkdir ./venv
  python3.11 -m venv ./venv --clear --prompt='espp@3.11'
```
#activate the venv
```
source venv/bin/activate
```
#Install modules
```
  pip install -U pip requests pandas xlsxwriter
```
#Run the sript
```
  python3 main-json.py inout_data.json output.xlsx
``` 
