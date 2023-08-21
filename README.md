<picture>
  <source media="(prefers-color-scheme: dark)" 
   srcset="https://raw.githubusercontent.com/bbye98/minim/main/assets/logo_dark.svg">
  <source media="(prefers-color-scheme: light)" 
   srcset="https://raw.githubusercontent.com/bbye98/minim/main/assets/logo_light.svg">
  <img alt="minim logo" 
   src="https://raw.githubusercontent.com/bbye98/minim/main/assets/logo_light.svg">
</picture>
<br></br>

# minim

Minim is a lightweight Python 3 library that can retrieve media information,
(semi-)automate music tagging, and more through the iTunes Store, Spotify,
Qobuz, and TIDAL APIs.

* **Documentation**: https://bbye98.github.io/minim/

## Installation and usage

If you use Conda to manage your Python packages, it is recommended that 
you use the conda-forge channel to install dependencies. To make 
conda-forge the default channel, use

    conda config --add channels conda-forge

### Virtual environment

It is recommended, but not necessary, that you create a virtual 
environment to prevent dependency conflicts.

#### pip: `venv` or `virtualenv`

If you use pip as your Python package manager, you can create a virtual 
environment using either the built-in `venv` or the (better) `virtualenv`
packages. With `venv`, run

    python -m venv <venv_path>

to initialize the new virtual environment, where `<venv_path>` is the 
path to the directory to be created, and one of the following commands 
to activate the environment, depending on your operating system (OS) and 
shell:

* POSIX: bash/zsh

      source <venv_path>/bin/activate

* POSIX/Windows: PowerShell

      <venv_path>\Scripts\Activate.ps1

* Windows: cmd.exe

      <venv_path>\Scripts\activate.bat

With `virtualenv`, you can create a virtual environment using

    virtualenv <venv_name>

where `<venv_name>` is the name of the new environment, and activate it 
using

* Linux or macOS:

      source <venv_name>/bin/activate

* Windows: 

      .\<venv_name>\Scripts\activate

#### Conda: `conda` or `mamba`

If you use Conda as your Python package manager, you can create and 
activate a virtual environment named `<venv_name>` using

    conda create --name <venv_name>
    conda activate <venv_name>

(For Mamba users, replace `conda` with `mamba`.)

### Option 1: Install from source

 1. Change to the directory where you want to store a copy of Minim 
    using

        cd <install_path>

    where `<install_path>` is the path to the desired directory. If you
    are already in the correct location, skip this step.

 2. Create a local copy of the Minim repository on your machine using

        git clone https://github.com/bbye98/minim.git

 3. Enter the root directory of Minim using

        cd minim

 4. Install Minim and its dependencies through pip using

        python -m pip install -e .

 5. To verify that Minim has been installed correctly, execute

        python -c "import minim"

### Option 2: Portable package

 1. Change to the directory where you want to store a copy of Minim 
    using

        cd <install_path>

    where `<install_path>` is the path to the desired directory. If you
    are already in the correct location, skip this step.

 2. Create a local copy of the Minim repository on your machine using

        git clone https://github.com/bbye98/minim.git

 3. Enter the root directory of Minim using

        cd minim

 4. Install the required dependencies using

        python -m pip install -r requirements_minimal.txt

    or

        conda install --file requirements_minimal.txt

    If you would like to install the optional dependencies as well,
    remove the `_minimal` suffix from the filenames above.

 5. Now, you can use Minim by first adding the path to the `src` 
    directory in your Python scripts. To verify that Minim has been 
    installed correctly, execute

        python -c "import sys; sys.path.insert(0, '<install_path>/minim/src'); import minim"

### Option 3: Install using pip

Coming soon (pending [PEP 541 request](https://github.com/pypi/support/issues/3068)).