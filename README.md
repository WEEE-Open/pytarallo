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
virtualenv -p python3 venv
```  

### 2. Add some environment variables

Create a file named `.env` (a dot followed by the word "env") with this content:

```shell script
export TARALLO_URL=http://127.0.0.1:8080
export TARALLO_TOKEN=yoLeCHmEhNNseN0BlG0s3A:ksfPYziGg7ebj0goT0Zc7pbmQEIYvZpRTIkwuscAM_k
```

Or, as an alternative, you can add these lines to PyCharm (or whatever other IDE you're using) configuration for the test script launcher, they are just environment variables.

The token is the default one for the dev enviroment (see [T.A.R.A.L.L.O. developement](https://github.com/WEEE-Open/tarallo#developement), but you can generate different ones from T.A.R.A.L.L.O. obviously.

Then activate the virtualenv:

```shell script
source venv/bin/activate
```

### 3. Dependecies

Install dependencies for developement

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

## For devs, to publish this repo on PyPI

### Automatic method

1. Click [here](https://github.com/WEEE-Open/pytarallo/releases/new) (or on the right of this page, on "Releases", then "Draft a new release").  
2. Enter the version tag with format "vX.Y.Z" without double quotes.  
3. Optionally enter a release title and a release description.
4. You can follow the build and release process in the Actions tab at the top.

⚠️ Wait for the automatic tests that run after pushing a new commit to complete succesfully before releasing a broken library on PyPI.

### Manual method - DEPRECATED

1. Clone the repo locally
    ```
    git clone https://github.com/WEEE-Open/pytarallo && cd pytarallo
    ```
2. Update the setup.py so that it contains the correct version and other info (including dependencies).  
   You should update at least `version` and `download_url`.
    ```
    vim setup.py
    ```
3. Enter in the virtual environment
    ```
    source venv/bin/activate
    ```
4. Install required packages for publishing on PyPI
    ```
    pip install setuptools wheel twine
    ```
5. Build the .tar.gz package
    ```
    python setup.py sdist bdist_wheel
    ```
6. Upload the output packages to PyPI:  
    ```
    twine upload dist/*
    ```

    This last step requires:
    - you having an account on pypi.org
    - your account being owner or maintainer of the pytarallo package
    - you entering your username and password when prompted by twine

Remember to  
7. `rm -rf dist/` before uploading a new release
