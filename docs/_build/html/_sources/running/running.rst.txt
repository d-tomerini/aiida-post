.. _running:

***************
Running the app
***************

The main executable is the file app.py, a click executable that launch an extension of the AiiDA REST api.
The executable can be either run as ``verdi run app.py`` or by copying the wrapper
`aiida_ginestra_interface` file is a wrapper to the bin folder and given adequate permission to be executed: ::

    chmod 775 aiida_ginestra_interface

The click command has option, that are accessible by typing ``aiida_ginestra_interface --help``. These are the equivalent options to the AiiDA rest api:

- *Hostname*: Where the app is executed
- *Port*: port number
- *config-dir*: the file that contains the AiiDA rest configuration, and the expected
  association between property and endpoint. Also used (for now) to contain all the configurations for the rest app extension
- *wsgi-profile*: flag to use WSGI profiler
- *hookup*: whether or not to hookup the app
- *debug*: debug option

Configuration options
=====================

The ``common/config.py`` contains useful information about the supported properties and their
relation with the workflows that need to be executed to obtain them.
This information is obtained from the variable ``PROPERTY_MAPPING``, that is a dictionary
of property with their own entry point string, directly connected to the workflow class that needs to be loaded.

Each time we want to support a new property we need to modify this dictionary to include it.

**TODO**: introduce a similar dictionary to map the property position, so that we know where to search in the outputs







