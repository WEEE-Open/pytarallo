from setuptools import setup

setup(
    name='pytarallo',
    packages=['pytarallo'],
    version='1.2',
    url='https://github.com/WEEE-Open/pytarallo',
    download_url='https://github.com/WEEE-Open/pytarallo/archive/1.0.tar.gz',
    license='MIT',
    author='Various people',
    author_email='',
    description='Python API for the T.A.R.A.L.L.O. Inventory System',
    keywords=['WEEEOpen', 'python-tarallo', 'T.A.R.A.L.L.O.', 'Inventory system'],
    install_requires=['requests'],
    extras_require={
        'dev': ['nose', 'python-dotenv']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
)
