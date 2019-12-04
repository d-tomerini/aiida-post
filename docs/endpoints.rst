.. endpoints:

General Behavior
================

The API will generally return a list of available endpoints if the request refers to a non-supported URL, with a ``200`` code.

The API is to generally return a ``500`` error in case there was an error in the handling of the code (for example, on validation of one of the input to provide to a workflow, or a non-supported property), along with a json message containing only a ``message`` key with the error encountered in Python.

On successful request, the app returns a ``200`` status and a general list of properties:

- a ``data`` key containing the retrieved data
- a general summary of the request: the url, url_root, and query string, the relative path of the endpoint, the method used to access the page (GET, POST), and the ``ID`` of the node database accessed if relevant

Available intersect endpoints
=============================

The app runs at the the address ``HOSTNAME:PORT/PREFIX/ENDPOINT``, where ``HOST`` and ``PORT`` are property that can be set by the app options.

The prefix is the same of the aiida rest api, ``/api/v4/``; this can be changed in the configuration options if necessary.
All the new workflow related to the project have a prefix ``/api/v4/intersect`` in order to separate them from the existing AiiDA endpoints.

In the following therefore I'm going to assume a base URL as ``127.0.0.1:5000/api/v4``.

Every URL build upon this base URL, if it does not correspond to a used endpoint should redirect to a list of the accepted endpoints. This is a list of the AiiDA REST plus the ones we have defined.

For an explanation of the AiiDA endpoint you can check the
`AiiDA REST api page <https://aiida.readthedocs.io/projects/aiida-core/en/latest/restapi/>`_.
The additional ones are explained below.

Any of this endpoints can be accessed via a browser for ``GET`` method, but will need an extension to deal with a POST request.
In the proceeding I assume a request to be executed by a unix terminal call with the `httpie utility <https://httpie.org/>`_, i.e ::

    http 127.0.0.1:5000/api/v4/nodes/

accesses the ``127.0.0.1:5000/api/v4/nodes/`` with a ``GET`` request, while ::

    http 127.0.0.1:5000/api/v4/submit/ < filename

forward the content of the  ``filename`` file as a ``POST`` request.
Other resources, like ``curl`` or browser extensions can be used.


derived_data/structuredata
--------------------------

This endpoint is modelled on the idea to query for derived properties, that can be calculated with a function call, and not stored properties.

This is implemented in the AiiDA rest api as a way to display information on a single node; chemical_formula is such an example.

As a utility, I provide the ``intersect/derived_data/`` as a way to display derived data.

.. warning::
    This is a bad idea in principle; run a function on each database entry for very big database could be crippling slow.
    This is intended to be just a temporary solution to search a database for structures.

Without any query, the endpoint is equivalent to ::

    http://127.0.0.1:5000/api/v4/nodes?full_type="data.structure.StructureData.|"

i.e. to a node search with a query on ``StructureData`` objects.

The ``structuredata`` endpoint allows for query on ``chemical_formula`` to provide a filter on this non-stored property, and a ``chemical_formula_type`` to search for types of chemical formulas that are allowed in the verdi shell command ``node.get_formula()``.
This is executed as with the normal ``?`` query symbol at the endof the endpoint, eventually followed by others with the ``&`` symbol.
Additional keys for the database search can be used to further funnel the request. As it most simple::

    http://127.0.0.1:5000/api/v4/intersect/derived_data/structuredata?chemical_formula="O2Si"&chemical_formula_type="hill_compact"


properties
----------

The ``intersect/properties`` endpoint lists all the available property that can be request for a calculation, and returned as a list.

Example::

    http 127.0.0.1:5000/api/v4/properties

Expected response (http response 200)

.. code-block:: json

    {
        "data": {
            "band_gap.pw": "post.BandGap",
            "band_structure.pw": "quantumespresso.pw.band_structure",
            "relax.pw": "quantumespresso.pw.relax",
            "structure.cod": "post.CODImport"
        },
        "id": null,
        "method": "GET",
        "path": "/api/v4/intersect/properties",
        "query_string": "",
        "request_content": null,
        "resource_type": "Information about the properties available for calculation",
        "url": "http://127.0.0.1:5000/api/v4/intersect/properties",
        "url_root": "http://127.0.0.1:5000/"
    }

Each key of the ``data`` section represents a property that can be used as an input. Note that it is not necessary to have a map 1:1 between properties and workflows, as a workflow can be used for more than one.


properties/<string>/inputs
^^^^^^^^^^^^^^^^^^^^^^^^^^

By providing an identifier, it is possible to require a list of the inputs to run a workflow; this will be a list of all the possible keys that is possible to require as a dictionary.
Each of the entry of this dictionary schema can be arbitrarily nested, to allow, for example, to provide inputs to sub-workflows called by the main workflow.

Each of the keywords will return whether it is required (workflow will fail if not provided), valid types, and whether if it is going to be stored in the database.
Additionally, a ``help`` string, if the workflow has it, to better specify the use of this key.
The ``dynamic`` attribute is returned as ``true`` in case a value can be a list of valid types (for example, the number of pseudopotential files to be provided to a calculation may vary, and their precise number cannot be known in advance).

Example:

.. code-block:: json

    {
        "data": {
            "description": "Workfunction to query the COD database\n    Check for data according to a dictionary query, Import nodes,   Clean them, Import them as needed",
            "inputs": {
                "codquery": {
                    "help": "A list of option to the query to the COD database",
                    "name": "codquery",
                    "non_db": "False",
                    "required": "True",
                    "valid_type": "<class 'aiida.orm.nodes.data.dict.Dict'>"
                },
                "metadata": {
                    "call_link_label": {
                        "default": "CALL",
                        "help": "The label to use for the `CALL` link if the process is called by another process.",
                        "name": "call_link_label",
                        "non_db": "True",
                        "required": "False",
                        "valid_type": "(<class 'str'>,)"
                    },
                    "description": {
                        "help": "Description to set on the process node.",
                        "name": "description",
                        "non_db": "True",
                        "required": "False",
                        "valid_type": "(<class 'str'>,)"
                    },
                    "label": {
                        "help": "Label to set on the process node.",
                        "name": "label",
                        "non_db": "True",
                        "required": "False",
                        "valid_type": "(<class 'str'>,)"
                    },
                    "store_provenance": {
                        "default": "True",
                        "help": "If set to `False` provenance will not be stored in the database.",
                        "name": "store_provenance",
                        "non_db": "True",
                        "required": "False",
                        "valid_type": "<class 'bool'>"
                    }
                },
                "strictcheck": {
                    "default": "uuid: f6028da2-0ef6-4e8b-a506-42086e92fdd8 (unstored) value: False",
                    "help": "Whether we should strictly check COD_query keywords",
                    "name": "strictcheck",
                    "non_db": "False",
                    "required": "False",
                    "valid_type": "<class 'aiida.orm.nodes.data.bool.Bool'>"
                }
            },
            "workflow": "CODImportWorkChain"
        },
        "id": null,
        "method": "GET",
        "path": "/api/v4/intersect/workflows/post.CODImport/inputs",
        "query_string": "",
        "resource_type": "Information about the workflow inputs",
        "url": "http://127.0.0.1:5000/api/v4/intersect/workflows/post.CODImport/inputs",
        "url_root": "http://127.0.0.1:5000/"
    }



properties/<string>/outputs
^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this case, the information provided is only the output node, and eventually its attribute/s,  that contain the information required by the ``property`` workflow.
This can be a list of nodes/property, in general.

In this way, we can provide a more granular information about the value of interest, among all the outputs.

.. warning::
    **THIS IS NOT YET IMPLEMENTED! THE REQUEST RETURNS ALL THE OUTPUTS**


properties/<string>/outline
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The information returned is the steps performed in the workflow.
Note that this provides information about the status of the workflow, but not about the missing expected time!
Different steps can in principle take vastly different time to run, and can be wrapped into ``while`` loops at deeper levels.


workflows
---------

The ``intersect/workflows`` endpoint lists  works in a similar way as ``properties``, but returns information about the workflow entrypoint, rather than the property to be calculated.
In this way, it is possible to run ad inspect a calculation even if the property mapping is not specified.

The possibilities for a query are:

- **intersect/workflows** returns the list of all the aiida workflows that are accessible
- **intersect/workflows/<entrypoint>/inputs** returns all the port inputs accessible, with information about whether they are required, stored in the database, and their expected type.
- **intersect/workflows/<entrypoint>/outputs** returns all the output of a successful calculation.
- **intersect/workflows/<entrypoint>/outline** returns the steps that are going to be executed by the workflow.





submit
------

This is the endpoint related to the submission of a workflow.

Since it requires an input to work, it is necessary to use a ``POST`` request to provide this information to AiiDA.

A json file for now is just a dictionary with two entries:
- *calculation*: the mapped keyword to identify the workflow to run through its property name;
- *input*: the dictionary input for the workflow

There are two possibilities: if nothing, or ``intersect/submit/property`` endpoint is selected, the expected value of the *calculation* key is the value of the property to be calculated, that will be converted to the corresponding workflow.

If the ``intersect/submit/workflow`` is used, the *calculation* line is the entrypoint relative to a workflow to calculate.
In this way, any workflow can be submitted, and we are not limited by the mapping of the properties.

The ``input`` key of the request is a dictionary with the input names of the workflow.

Since we cannot pass some of them, specifically a ``Node`` class, the plugin will try to interpret the value passed and convert it.
This is to avoid having to specify for each key entry what kind of classes it is expected to be and to make it more easy to read: if an input expect a ``code`` instance, we can pass a ``pk``, ``uuid`` that will be loaded from the database;  if a node is of ``Float`` type it will convert the float provided to the equivalent database type, and so on.

If we want to force the code to choose a ``Node`` instead of a value, we need to pass a dictionary where the key is
called ``LOADNODE``; the input will be generated by passing the content of the node ID provided.

For a code, additionally, we can specify ``CODELABEL`` and provide the label string that identify the code.
Note that label might not be univoque: an exception will be raised if there is ambiguity.

For example, imagine the following case:

.. code-block:: json

    {
        "calculation": "property.siesta",
        "input": {
            "structure": 2547,
            "code": 667,
            "string_entry": "my string value"
        }
    }

The ``string_entry`` value will be converted to ``Str(str="my string value")`` (the AiiDA database string node), while

.. code-block:: json

    {
        "calculation": "property.siesta",
        "input": {
            "structure": 2547,
            "code": 667,
            "string_entry": {
                "LOADNODE": 3546
            }
        }
    }

will load the content of the node ``3546`` and use if as input, and the following will select the node by its label:

.. code-block:: json

    {
        "calculation": "property.siesta",
        "input": {
            "structure": 2547,
            "code": 667,
            "string_entry": {
                "CODELABEL": "siesta@localhost"
            }
        }
    }

The result of this call to the endpoint ::

    http 127.0.0.1:5000/api/v4/intersect/submit < examples/search_hfo2.json

where the ``search_hfo2.json`` file is taken from the examples folder, should return the following response (html code 200)

.. code-block:: json

    {
        "data": {
            "error": "",
            "error_info": "",
            "workflow": {
                "attributes": {
                    "exit_message": null,
                    "exit_status": null,
                    "process_class": null,
                    "process_label": "CODImportWorkChain",
                    "process_state": "created",
                    "stepper_state_info": null,
                    "version": {
                        "core": "1.0.0",
                        "plugin": "0.1a1"
                    }
                },
                "ctime": "Tue, 26 Nov 2019 14:58:48 GMT",
                "uuid": "bf80763c-aea3-48e5-a5e9-c1649caf9fca"
            }
        },
        "id": null,
        "method": "POST",
        "path": "/api/v4/intersect/submit/",
        "query_string": "",
        "request_content": {
            "data":{
              "calculation": "structure.cod",
              "input": {
                "codquery": {
                    "formula": "Hf O2",
                    "schemical_name": "wurtzite",
                    "some_data": 32
                },
                "metadata": {
                    "label": "somelabel"
                },
                "strictcheck": false
              },
            "node": "6c13fa84-aea4-44d8-a202-93d8b0e34f24"

        },
        "resource_type": "submission of workflows",
        "url": "http://127.0.0.1:5000/api/v4/intersect/submit/",
        "url_root": "http://127.0.0.1:5000/"
    }

where the ``data`` key contains the ``uuid`` entry that identify the workflow ``uuid`` that can be queried to the database, and other attributes of the created process.

The process has at this point just been created: unless extremely quick its attributes will not be populated; the ``exit_message`` and ``exit_code`` would provide a clue that something failed, while the other attributes provides hints regarding the python class and the version of AiiDA/plugin used for such calculation.

The response also include a copy of the provided json file under the ``request_content`` key, and its node ``uuid`` in case this information is needed for future queries.

In case of failure during the creation of the workflow the response will simply be be an error message with some more indication of the problem, but no ``data`` key or other attributes.