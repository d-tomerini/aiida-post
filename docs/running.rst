.. _running:

***************
Running the app
***************

.. warning::
    AiiDA must be active! This implies that **at the very least** PostGres is running, so that the
    database is accessible; to run a calculation, the RabbitMQ service should be active and the daemon running.

    Check that the command ``verdi status`` returns everything working as expected:

    .. code-block:: console

        ✓ profile:     On profile tomerini
        ✓ repository:  /home/dtomerini/.virtualenvs/aiida/.aiida/repository/tomerini
        ✓ postgres:    Connected as aiida_qs_dtomerini_13d3f27e28d94d9d0f2372d27f0cc2b0@localhost:5432
        ✓ rabbitmq:    Connected to amqp://127.0.0.1?heartbeat=600
        ✓ daemon:      Daemon is running as PID 31452 since 2019-11-28 10:50:34


The main executable is the file app.py, a click executable that launch an extension of the AiiDA REST api.
The executable can be either run as ``verdi run app.py`` or by copying the wrapper
`aiida_intersect_interface` file is a wrapper to the bin folder and given adequate permission to be executed: ::

    chmod 775 aiida_intersect_interface

The click command has option, that are accessible by typing ``aiida_intersect_interface --help``. These are the equivalent options to the AiiDA rest api:

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







