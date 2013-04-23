[Getb2g](https://github.com/ahal/getb2g)
is a python package intended to make setting up a working B2G environment as easy as possible. It can download various configurations
(e.g emulator, unagi, panda, etc.) as well as extraneaous resources such as tests and symbols. It is an alternative to building B2G
from scratch which can sometimes be a large barrier to entry for those not familiar with B2G development.

# Installation

Install setuptools if you don't have it already:

    curl -O http://python-distribute.org/distribute_setup.py
    python distribute_setup.py

Install pip if you don't have it already:

    easy_install pip

Install getb2g:

    pip install getb2g

Note on python packages: getb2g has several dependent packages that will also be installed alongside it. Doing the above will install 
all those packages in your global package index. This makes it easy to get into situations where you have several libraries that depend 
on different versions of the same package. It is easy to get into python version hell. To avoid hell, I'd recommend using a virtual 
environment. See [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://bitbucket.org/dhellmann/virtualenvwrapper) 
(an optional tool to help manage virtual environments) for more details.

# Usage

getb2g is used from the command line.

The most basic usage is:

    getb2g

You will be prompted for a device to configure. An educated guess will be made for extraneous resources depending on the choice you
select. Run:

    getb2g --help

to see more options. All of these options are optional and are mostly just a convenience to circumvent the interactive prompt.
Here are some examples of other command lines you can use:

    # sets up an emulator build
    getb2g --prepare-emulator

    # sets up a panda build and only a panda build (no tests, symbols, etc)
    getb2g --prepare-panda --only

    # sets up a unagi build based off the mozilla-b2g18 branch
    getb2g --prepare-unagi --metadata branch=mozilla-b2g18

    # set up a b2g gecko build from a specific build directory on ftp.mozilla.org
    getb2g --prepare-gecko --metadata build_dir='https://ftp.mozilla.org/pub/mozilla.org/b2g/tinderbox-builds/mozilla-central-ics_armv7a_gecko/1366715435/'

    # provide a user name and password and never get prompted
    getb2g --prepare-emulator --no-prompt --metadata user=<username> --metadata password=<password>

# Authentication

Many of the resources require authentication because their packages contain proprietary software. If you are attempting to download one such resource, you
will be prompted to enter the proper credentials. If you do not know the credentials, I apologize.

Once you have successfully entered credentials, they will be stored so you won't have to enter them again in the future. If you want to disable this
behaviour permanently, just run:

    getb2g no-store

To re-enable:

    getb2g store

