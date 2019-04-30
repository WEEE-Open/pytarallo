# pytarallo
Python API for the T.A.R.A.L.L.O. Inventory System

## Development instructions

### 1. Setting up the environment

Create a python3 virtual environment  
`python3 -m venv venv`  
or using virtualenv  
`virtualenv -p python3 venv`

### 2. Add some environment variables

Add these lines on the `venv/bin/activate`

```Bash
export TARALLO_URL=value
export TARALLO_USER=value
export TARALLO_PASS=value
```

Activate the virtualenv
`source venv/bin/activate`

### 3. Dependecies

Install depencies for developement
`pip install -e ".[dev]"`
or for production only
`pip install -e .`

### 4. Run tests

To run tests type  
`nosetests -v`  

## pytarallo on Pypi
You may also get pytarallo through Pypi by using the command `pip install pytarallo`

