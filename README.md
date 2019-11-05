# pytarallo
Python API for the T.A.R.A.L.L.O. Inventory System

## Development instructions

### 1. Setting up the environment

Create a python3 virtual environment  

```shell script
python3 -m venv venv
```  

or using virtualenv

```shell script
`virtualenv -p python3 venv`
```  

### 2. Add some environment variables

Create a file named `.env` (a dot followed by the word "env") with this content:

```shell script
export TARALLO_URL=http://127.0.0.1:8080
export TARALLO_TOKEN=4qzgVAOo_U15EodQ6kukgQ==:6eAT52MyNMkqPVi9sCHeoIphNrdI0yWI2tngJxQLLI8=
```

The token is just an example, you need to generate one in T.A.R.A.L.L.O. obviously.

Or, as an alternative, you can add these lines at the end of `venv/bin/activate`. Or you can add them to PyCharm (or whatever other IDE you're using) configuration for the test script launcher.

Activate the virtualenv

```shell script
source venv/bin/activate
```

### 3. Dependecies

Install depencies for developement

```shell script
pip install -e ".[dev]"
```

or for production only

```shell script
pip install -e .
```

### 4. Run tests

To run tests type  

```shell script
nosetests -v
```  

## pytarallo on PyPI
You may also get pytarallo through PyPI by using the command `pip install pytarallo`

## For devs, to publish this repo to PyPI

Clone the repo locally:  
`git clone https://github.com/WEEE-Open/pytarallo`  
`cd pytarallo`  
Update the setup.py so that it contains the correct version and other info (including dependencies):  
`vim setup.py`  
Make a venv and activate it:  
`python3.7 -m venv venv`  
`source venv/bin/activate`  
Install required packages for publishing on PyPI:  
`pip install setuptools wheel twine`  
Make a directory and copy all the meaningful content from the pytarallo dir:  
`mkdir pytarallo`  
`cp LICENSE README.md __init__.py setup.py tarallo.py test.py pytarallo`  
Make the .tar.gz package:  
`python setup.py sdist bdist_wheel`  
Upload the output packages to PyPI:  
`twine upload dist/*`  

This last step requires:
- you having an account on pypi.org
- your account being owner or maintainer of the pytarallo package
- you entering your username and password when prompted by twine
