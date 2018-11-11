from setuptools import setup

setup(
    name='python-tarallo',
    version='0',
    url='https://github.com/WEEE-Open/python-tarallo',
    license='MIT',
    author='Various people',
    author_email='',
    description='Python API for the T.A.R.A.L.L.O. Inventory System',
    install_requires=['requests'],
    extras_require={
        'dev': ['nose']
    }
)
