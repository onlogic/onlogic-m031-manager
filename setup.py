'''
Setup file that configures the package.
'''
from setuptools import setup, find_packages

setup( 
    name='OnLogicM031Manager',
    # url='https://github.com/onlogic',
    author='OnLogic - Nick Hanna',
    author_email='firmwareengineeringteam@onlogic.com',
    packages=['OnLogicM031Manager'],
    package_dir={'OnLogicM031Manager': 'src'},
    install_requires=['pyserial>=3.4', 'fastcrc>=0.3.2', 'pytest>=7.0.0'],
    version='0.0.1',
    license='BSD-2.0',
    description='Tools for Helix 52x and Karbon 52x Peripherals',
    long_description=open('README.rst').read(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ]
)