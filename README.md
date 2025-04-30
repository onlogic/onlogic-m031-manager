# Use of a Python venv in Ubuntu 24.04 LTS 

Linux Ubuntu has enforced a stricter package management scheme in the new 24.04 LTS distribution to avoid interfering with global package dependencies used by the OS. While this is a more stable way to administer Python on a system, it is also more complex to program in user environments. To run the package OnLogicNuvotonManager in Ubuntu, it's best practice to use a venv.

* Creating a venv: 	$ python3 -m venv <path/to/venv> 
    * (One can get <path/to/venv> by navigating to desired directory in terminal and inputting pwd)
* Activating a venv: 	$ source <path/to/venv>/bin/activate
* Deactivating a venv: 	$ deactivate

- When the venv is activated, running any python scripts will use the venv's interpreter and packages. But, when running a script that needs root privileges (sudo python ...), the venv's Python won't be used, even if its activated. My solution has been to explicitly use the venv's interpreter when running a Python script. 

$ sudo <path/to/venv>/bin/python somescript.py
$ sudo /home/password/Desktop/titanium-dio-python-driver/bin/python3 dio_implementation.py

We have to use whole path because we need to sudo in, and we can't access IO without sudo privaleges 

# Set up required packages in venv
* pip install -e .
* Double Check With: