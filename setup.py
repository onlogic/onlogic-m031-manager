'''
Setup file that configures the package.
'''
from setuptools import setup, find_packages

setup( 
    name='OnLogicNuvotonManager',
    # url='https://github.com/onlogic',
    author='OnLogic',
    author_email='firmwareengineeringteam@onlogic.com',
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    install_requires=['pyserial>=3.4', 'colorama>=0.4.5', 'fastcrc==0.3.2'],
    version='0.0.1',
    license='BSD-2.0',
    description='Tools for Helix 52x and Karbon 5XX interfaces',
    # long_description=open('README.rst').read(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ]
)
