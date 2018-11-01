# python-tarallo
Python API for the T.A.R.A.L.L.O. Inventory System

## Development instructions
### 1. Setting up the environment
Create a python3 virtual environment  
`python3 -m venv venv`  
or using virtualenv  
`virtualenv -p python3 venv`  
### 2. Add some environment variables
Add these lines on the `venv/bin/activate`  
`export TARALLO_URL=value`  
`export TARALLO_USER=value`  
`export TARALLO_PASS=value` 
### 3. Installing the test suite
Activate the virtualenv  
`source venv/bin/activate`  
Install the `nose` test suite  
`pip install nose`  
### 4. Run tests
To run tests type  
`nosetests`  

