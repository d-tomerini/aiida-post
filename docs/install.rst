.. _install:

************
Installation
************

Prerequisites
===============

The aiida_post extension requires an installation of AiiDA >= 1.0.0, and of its REST API.

To download it and install it, preferentially inside a virtual environment, follow the instruction you find in the AiiDA
documentation, at this `page <https://aiida-core.readthedocs.io/en/latest/install/installation.html>`_.

**Please set up a virtual environmente with Python 3!**
AiiDA will maintain compatibility with Python 2.7.x only until January 2020,
but aiida_post depends on asyncronous features available on Python > 3.4 only.

Quick installation from the github repository (useful for developers, if you want to keep up to date with the most recent
AiiDA iteration) can be done with the commands below: ::

     $ mkdir <your_directory>
     $ cd <your_directory>
     $ git clone https://github.com/aiidateam/aiida-core[atomic_tools,docs,advanced_plotting,rest]
     $ pip install

To simply install the most recent stable version of AiiDA from Python Package Index (PyPi) it is sufficient to just
type in a terminal inside the virtual environment:
``pip install aiida-core[atomic_tools,docs,advanced_plotting,rest]``.

The options in square bracket are a useful AiiDA extensions.
The full list of options of optional packages is available
`here <https://aiida.readthedocs.io/projects/aiida-core/en/latest/install/installation.html#aiida-python-package>`_.
The only *required* package is the REST extension, as this plugin is designed as an AiiDA REST api extension.

Python package
==============

The python package can be obtained from the
`Intersect gitlab repository <https://gitlab.cc-asp.fraunhofer.de/intersect/ext_to_aiida>`_.

The repository can be cloned locally: ::

    $ mkdir <your_directory>
    $ cd <your_directory>
    $ git clone https://gitlab.cc-asp.fraunhofer.de/intersect/ext_to_aiida
    (aiida) $ pip install -e aiida-post

The ``-e`` option simply signal the
`pip installer <https://pip.pypa.io/en/stable/reference/pip_install/#pip-install>`_
to install a package in *editable mode*,from a local path.


Updating the entry points
-------------------------

AiiDA (and its extensions) uses the ``reentry`` package to cache the entry points.
This provides access to the classes and workflows available to AiiDA.
After installing or updating a package is necessary to update the reentry cache by typing ::

    reentry scan


