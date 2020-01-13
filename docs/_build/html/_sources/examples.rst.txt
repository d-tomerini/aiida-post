.. examples:

Examples
========

Here I will try to detail the possible uses of the app, by using the *json* examples provided in the examples folder.

Prerequisites
-------------

Again, beware! The examples required at the very minimum that you have:

- A working installation of AiiDA, with the REST api working.
- AiiDA **must**  be active. All the basic calls to the database requires *postgresql* to be active; each workflow submission requires RabbitMQ to be active **and** the daemon to be running, to broadcast the information
- The app should be running. In the examples I'm going to assume no change to the basic setup, meaning that the app listen to requests at ``127.0.0.1:5000/api/v4/``
- Examples using Quantum ESPRESSO requires the installation of the `aiida-quantumespresso` plugin, and at least of a *pw.x* executable configured.
- Examples with the `aiida-defect` workflows requires the installation of the aiida-defect plugin by Conrad Johnston. This plugin requires the aiida-quantumespresso, and installed ``ph.x`` and ``pp.x`` from Quantum ESPRESSO.
- Of course, in general when you add a workflow, you need to have installed the plugin and a code! The additional hurdle for this is to add a dictionary of property-workflow mapping in the mapping file in the config directory, if *properties* endpoints are used.

I'm going to assume that the files are in the ``examples/`` folder. Adapt the calls to your actual directory!

Structures in the AiiDA database
---------------------------------

Let's say I want to run a calculation on SiO\ :sub:`2`.
The first thing I might want to check is whether or nor such a structure node is available in my AiiDA database.
To look for it, I can query the database as  ::

    http://127.0.0.1:5000/api/v4/intersect/derived_data/structuredata?chemical_formula="O2Si"&chemical_formula_type="hill_compact"

Where the ``chemical formula`` is the string that we want to use as a comparison to the calculated value from the database, and the ``chemical_formula_type`` provides the grammar of how this formula is written.

The ``hill`` formula counts all the atoms in the unit cell, and order the types alphabetically except for Oxygen; so, it differentiate between SiO\ :sub:`2`  and Si\ :sub:`10` O\ :sub:`20`.
If we choose ``hill_compact`` we can consider formulas at the minimal terms between the atomic ratios.
For now it is not possible to execute complex queries as *I want* SiO\ :sub:`n`, *with n > 3*; this will be supported when the ``optimade`` specification are available.

The database query will return a list of the nodes that satisfy the request. Due to the simple implementation, for now the ``page`` or ``limit`` specifications are ignored:

.. code-block:: JSON

        {
        "data": {
            "nodes": [
                {
                    "ctime": "Fri, 22 Nov 2019 15:39:02 GMT",
                    "full_type": "data.structure.StructureData.|",
                    "id": 4023,
                    "label": "",
                    "mtime": "Fri, 22 Nov 2019 15:39:02 GMT",
                    "node_type": "data.structure.StructureData.",
                    "process_type": null,
                    "user_id": 1,
                    "uuid": "b2b7ec7e-0155-4a5e-b820-45a8ac8ffb0d"
                },
                {
                    "ctime": "Fri, 22 Nov 2019 15:39:02 GMT",
                    "full_type": "data.structure.StructureData.|",
                    "id": 4024,
                    "label": "",
                    "mtime": "Fri, 22 Nov 2019 15:39:02 GMT",
                    "node_type": "data.structure.StructureData.",
                    "process_type": null,
                    "user_id": 1,
                    "uuid": "066cce6e-9678-4ca3-beb3-576850a5f349"
                },
                {
                    "ctime": "Mon, 02 Dec 2019 10:57:31 GMT",
                    "full_type": "data.structure.StructureData.|",
                    "id": 6048,
                    "label": "",
                    "mtime": "Mon, 02 Dec 2019 10:57:31 GMT",
                    "node_type": "data.structure.StructureData.",
                    "process_type": null,
                    "user_id": 1,
                    "uuid": "15753414-601b-4fb1-b29a-245a8011a394"
                }
            ]
        },
        "id": null,
        "method": "GET",
        "path": "/api/v4/intersect/derived_data/structuredata",
        "query_string": "chemical_formula=HfO2&chemical_formula_type=hill_compact",
        "resource_type": "structuredata search",
        "url": "http://127.0.0.1:5000/api/v4/intersect/derived_data/structuredata?chemical_formula=HfO2&    chemical_formula_type=hill_compact",
        "url_root": "http://127.0.0.1:5000/"
    }


If no structure satisfy the request, there will be an empty list as ``nodes`` entry.


Searching for a crystal structure
---------------------------------

I've written an extremely basic workflow to search for structures in the COD database.
This is simply a wrapper around a 2-line command in AiiDA, but it is useful to have in some form.
A structure query can be performed as ::

    http 127.0.0.1:5000/api/v4/submit < examples/search_HfO2_strict.json

If you inspect the ``search_HfO2_strict.json`` you see that the file contains a misspelled keyword, as ``schemical``, and a totally new one, ``somedata``, that are filtered out by the workflow.
There is an input,  ``"strictcheck": true,`` that does *NOT* allow for bad keywords, or even no keywords.

No keywords means that **the whole COD database** will be downloaded! So this acts as a sanity check.

A possible output of this command is:

.. code-block:: JSON

    {
    "data": {
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
            "ctime": "Fri, 29 Nov 2019 17:17:29 GMT",
            "uuid": "03d55d92-8589-4587-b2b0-2108f18f2856"
        }
    },
    "id": null,
    "method": "POST",
    "path": "/api/v4/intersect/submit",
    "query_string": "",
    "request_content": {
        "data": {
            "calculation": "structure.cod",
            "input": {
                "codquery": {
                    "formula": "Hf O2",
                    "schemical_name": "wurtzite",
                    "some_data": 32
                },
                "strictcheck": true
            }
        },
        "node": "b3e4652d-5c04-40ee-9625-833ef2b49c6b"
    },
    "resource_type": "submission of workflows",
    "url": "http://127.0.0.1:5000/api/v4/intersect/submit",
    "url_root": "http://127.0.0.1:5000/"

In this response you should focus on the ``workflow{uuid}`` identifier, that is required for further inquiries about the calculation.


Checking the status of the search
---------------------------------

Now that we know the `uuid`, that is the value ``03d55d92-8589-4587-b2b0-2108f18f2856`` above, we can
check the status of the calculation: ::

    http 127.0.0.1:5000/api/v4/intersect/status/03d55d92-8589-4587-b2b0-2108f18f2856

That should give a negative response (your uuid should of course differ from mine!), since we
defined non-existing keywords. The http response will look like:

.. code-block:: JSON

    {
        "data": {
            "logs": [
                {
                    "dbnode_id": 5996,
                    "levelname": "REPORT",
                    "loggername": "aiida.orm.nodes.process.workflow.workchain.WorkChainNode",
                    "message": "[5996|CODImportWorkChain|check_keywords]: The query contains invalid keys: {'some_data': 32, 'schemical_name': 'wurtzite'}",
                    "time": "Fri, 29 Nov 2019 17:17:29 GMT"
                }
            ],
            "workflow": {
                "attributes": {
                    "exit_message": "The query contains invalid keywords",
                    "exit_status": 201,
                    "process_class": null,
                    "process_label": "CODImportWorkChain",
                    "process_state": "finished",
                    "stepper_state_info": "1:if_(should_check_query)",
                    "version": {
                        "core": "1.0.0",
                        "plugin": "0.1a1"
                    }
                },
                "ctime": "Fri, 29 Nov 2019 17:17:29 GMT",
                "uuid": "03d55d92-8589-4587-b2b0-2108f18f2856"
            }
        },
        "id": "03d55d92-8589-4587-b2b0-2108f18f2856",
        "method": "GET",
        "path": "/api/v4/intersect/status/03d55d92-8589-4587-b2b0-2108f18f2856/",
        "query_string": "",
        "resource_type": "workflow status",
        "url": "http://127.0.0.1:5000/api/v4/intersect/status/03d55d92-8589-4587-b2b0-2108f18f2856/",
        "url_root": "http://127.0.0.1:5000/"
    }


The ``logs`` are simple messages from the workflow, to document the status of the calculation, or some problem.
In this case we just have one message. In general it will be a list of more (or no) messages. In this case the warning is about the non-existing keywords.

The logs also provide a simple way to keep track of the status of a calculation that is running correctly.

The relevant info about the workflow are in the ``workflow`` dictionary, and here we see that the ``exit_status`` is non zero, signalling some problem was encountered. The ``exit_message`` provides the error encountered, if defined in the workflow by their authors.

Generally, there might also be a (long) python error stack if the exit was not graceful.

We also see that the process is ``process_state`` finished. Other options are ``submitted`` (we are waiting for it to run through a scheduler) or ``running`` (some calculation is going on, at same stage of the workflow).


Submitting a search with no strict checks
-----------------------------------------

If we submit another example where the strict check has been disabled, the search effectively goes through the accepted ``formula`` keyword and ignore all the rest: ::

    http 127.0.0.1:5000/api/v4/intersect/submit <  examples/search_HfO2.json

Returns

.. code-block:: JSON

    {
       "data": {
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
               "ctime": "Fri, 29 Nov 2019 17:32:58 GMT",
               "uuid": "1e6d99e4-1966-45c7-b481-55513d3ed827"
           }
       },
       "id": null,
       "method": "POST",
       "path": "/api/v4/intersect/submit",
       "query_string": "",
       "request_content": {
           "data": {
               "calculation": "structure.cod",
               "input": {
                   "codquery": {
                       "formula": "Hf O2",
                       "schemical_name": "wurtzite",
                       "some_data": 32
                   },
                   "strictcheck": false
               }
           },
           "node": "f0edad7a-09b2-404e-a270-f4b696d21fcc"
       },
       "resource_type": "submission of workflows",
       "url": "http://127.0.0.1:5000/api/v4/intersect/submit",
       "url_root": "http://127.0.0.1:5000/"
    }

And upon checking on the node ``1e6d99e4-1966-45c7-b481-55513d3ed827``: ::

    http 127.0.0.1:5000/api/v4/intersect/status/1e6d99e4-1966-45c7-b481-55513d3ed827

yields:

.. code-block:: JSON

    {
        "data": {
            "logs": [
                {
                    "dbnode_id": 6003,
                    "levelname": "REPORT",
                    "loggername": "aiida.orm.nodes.process.workflow.workchain.WorkChainNode",
                    "message": "[6003|CODImportWorkChain|find_structures_and_return]: 6 structures satisfies the query",
                    "time": "Fri, 29 Nov 2019 17:33:02 GMT"
                }
            ],
            "workflow": {
                "attributes": {
                    "exit_message": null,
                    "exit_status": 0,
                    "process_class": null,
                    "process_label": "CODImportWorkChain",
                    "process_state": "finished",
                    "stepper_state_info": "2:find_structures_and_return",
                    "version": {
                        "core": "1.0.0",
                        "plugin": "0.1a1"
                    }
                },
                "ctime": "Fri, 29 Nov 2019 17:32:58 GMT",
                "uuid": "1e6d99e4-1966-45c7-b481-55513d3ed827"
            }
        },
        "id": "1e6d99e4-1966-45c7-b481-55513d3ed827",
        "method": "GET",
        "path": "/api/v4/intersect/status/1e6d99e4-1966-45c7-b481-55513d3ed827",
        "query_string": "",
        "resource_type": "workflow status",
        "url": "http://127.0.0.1:5000/api/v4/intersect/status/1e6d99e4-1966-45c7-b481-55513d3ed827",
        "url_root": "http://127.0.0.1:5000/"
    }

Now we have a different log, with the succesful end of workflow (6 structures retrieved), ``exit_status`` is  equal zero, e no ``exit_message`` signal a correct execution of the workflow.

Note that it is possible to submit requests that, as in the corresponding COD search in *verdi*, allows for queries asking for multiple values. For example,

"chemical_name":["caffeine", "adenine"]

will look in the COD database for structure that have *either* chemical name. The example is in the *search_multiple.json* file.


Asking information about the available properties to calculate
--------------------------------------------------------------

A simple request can be submitted to know all the supported properties ::

    http 127.0.0.1:5000/api/v4/intersect/properties/

That will return all the keywords that can be used as a property to calculate.
This property are connected to a workflow to call.
A possible answer is

.. code-block:: JSON

    {
        "data": {
            "band_gap.pw": "post.BandGap",
            "`band_structure`.pw": "quantumespresso.pw.band_structure",
            "formationenergy.qe": "defects.formation_energy.qe",
            "relax.pw": "quantumespresso.pw.relax",
            "structure.cod": "post.CODImport"
        },
        "id": null,
        "method": "GET",
        "path": "/api/v4/intersect/properties/",
        "query_string": "",
        "request_content": null,
        "resource_type": "Information about the properties available for calculation",
        "url": "http://127.0.0.1:5000/api/v4/intersect/properties/",
        "url_root": "http://127.0.0.1:5000/"
    }

The keys of data (e.g. ``band_structure``) can be used as value in the ``calculation`` entry in the submit json file.
The other required field is ``input``, that is a dictionary of the inputs of the related workflow.



Asking information about the inputs of workflow
------------------------------------------------

The inputs to submit a workflow is a dictionary, whose fields we do not always know.
To have information about this, there is a `` verdi plugin list aiida.workflows <entry> `` shell command that can be used to have basic information.
The equivalent endpoint for us is ::

    http 127.0.0.1:5000/api/v4/intersect/properties/<entry>/inputs

That provides a list of all the supported inputs of a workflow, their type, a help when available, and whether it is a required inputs or not.

.. code-block:: JSON

    {
        "data": {
            "description": "Extension to the PwBandStructureWorkChain to compute a band gap for a given structure\n    using Quantum    ESPRESSO pw.x",
            "inputs": {
                "code": {
                    "name": "code",
                    "non_db": "False",
                    "required": "True",
                    "valid_type": "<class 'aiida.orm.nodes.data.code.Code'>"
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
                "structure": {
                    "name": "structure",
                    "non_db": "False",
                    "required": "True",
                    "valid_type": "<class 'aiida.orm.nodes.data.structure.StructureData'>"
                }
            },
            "workflow": "PwBandGapWorkChain"
        },
        "id": null,
        "method": "GET",
        "path": "/api/v4/intersect/properties/band_gap.pw/inputs",
        "query_string": "",
        "request_content": null,
        "resource_type": "Information about the workflow inputs",
        "url": "http://127.0.0.1:5000/api/v4/intersect/properties/band_gap.pw/inputs",
        "url_root": "http://127.0.0.1:5000/"
    }


The request can be further filtered to obtain just a subset of the inputs with respect to the key of each input.
For example we can filter just the required inputs: ::

    http 127.0.0.1:5000/api/v4/intersect/properties/band_gap.pw/inputs?required=True

That returns

.. code-block:: JSON

    {
        "data": {
            "description": "Extension to the PwBandStructureWorkChain to compute a band gap for a given structure\n    using Quantum    ESPRESSO pw.x",
            "inputs": {
                "code": {
                    "name": "code",
                    "non_db": "False",
                    "required": "True",
                    "valid_type": "<class 'aiida.orm.nodes.data.code.Code'>"
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
                "structure": {
                    "name": "structure",
                    "non_db": "False",
                    "required": "True",
                    "valid_type": "<class 'aiida.orm.nodes.data.structure.StructureData'>"
                }
            },
            "workflow": "PwBandGapWorkChain"
        },
        "id": null,
        "method": "GET",
        "path": "/api/v4/intersect/properties/band_gap.pw/inputs",
        "query_string": "required=True",
        "request_content": null,
        "resource_type": "Information about the workflow inputs",
        "url": "http://127.0.0.1:5000/api/v4/intersect/properties/band_gap.pw/inputs?required=True",
        "url_root": "http://127.0.0.1:5000/"
    }


Multiple filters can be set at the same time, and if a field does not contain the keyword it is ignored.


Checking the outputs of a workflow
----------------------------------

We can now use one of the standard endpoints of the AiiDA rest api to have a list of the outputs of a process: ::

    http 127.0.0.1:5000/api/v4/nodes/1e6d99e4-1966-45c7-b481-55513d3ed827/links/outgoing

That returns a response that looks like:

.. code-block:: JSON

    {
        "data": {
            "outgoing": [
                {
                    "ctime": "Fri, 29 Nov 2019 17:32:59 GMT",
                    "full_type": "process.calculation.calcfunction.CalcFunctionNode.|aiida_post.calculations.COD.cod_check",
                    "id": 6004,
                    "label": "cod_check",
                    "link_label": "CALL",
                    "link_type": "call_calc",
                    "mtime": "Fri, 29 Nov 2019 17:32:59 GMT",
                    "node_type": "process.calculation.calcfunction.CalcFunctionNode.",
                    "process_type": "aiida_post.calculations.COD.cod_check",
                    "user_id": 1,
                    "uuid": "f732e9c3-99ff-4cd1-87f2-876848a0f7c7"
                },
                {
                    "ctime": "Fri, 29 Nov 2019 17:32:59 GMT",
                    "full_type": "process.calculation.calcfunction.CalcFunctionNode.|aiida_post.calculations.COD.cod_find_and_store",
                    "id": 6006,
                    "label": "cod_find_and_store",
                    "link_label": "CALL",
                    "link_type": "call_calc",
                    "mtime": "Fri, 29 Nov 2019 17:33:02 GMT",
                    "node_type": "process.calculation.calcfunction.CalcFunctionNode.",
                    "process_type": "aiida_post.calculations.COD.cod_find_and_store",
                    "user_id": 1,
                    "uuid": "19ba2bdb-c631-4c80-90de-d0904af82f27"
                },
                {
                    "ctime": "Fri, 29 Nov 2019 17:33:02 GMT",
                    "full_type": "data.list.List.|",
                    "id": 6013,
                    "label": "",
                    "link_label": "output",
                    "link_type": "return",
                    "mtime": "Fri, 29 Nov 2019 17:33:02 GMT",
                    "node_type": "data.list.List.",
                    "process_type": null,
                    "user_id": 1,
                    "uuid": "36b1abcd-d28c-4362-8147-08e279e4ca5d"
                }
            ]
        },
        "id": "1e6d99e4-1966-45c7-b481-55513d3ed827",
        "method": "GET",
        "path": "/api/v4/nodes/1e6d99e4-1966-45c7-b481-55513d3ed827/links/outgoing",
        "query_string": "",
        "resource_type": "nodes",
        "url": "http://127.0.0.1:5000/api/v4/nodes/1e6d99e4-1966-45c7-b481-55513d3ed827/links/outgoing",
        "url_root": "http://127.0.0.1:5000/"
    }


This does not simply represent the output of a workflow, but all the outgoing links of a Node, that in this case happens to be a process.

We can see what it is by the ``link_type`` key, that labels called calculations/workflows, i.e. the first two nodes, and a ``return`` link called ``output``. Each of the calculations can be inspected in a similar way, to check their outputs and calls.

In this case we have only one output, that is a ``List``, and we have its ``id`` and ``uuid``, that uniquely identify the object in the databases. ``id`` are shorter identifiers, but are not unique when copied in other databases.)

There is a similar endpoint for inputs, instead that for outputs: ::

    http 127.0.0.1:5000/api/v4/nodes/1e6d99e4-1966-45c7-b481-55513d3ed827/links/incoming

That returns the inputs of a workflow (or for a node, all the nodes that points to it):

.. code-block:: JSON

    {
        "data": {
            "incoming": [
                {
                    "ctime": "Fri, 29 Nov 2019 17:32:58 GMT",
                    "full_type": "data.dict.Dict.|",
                    "id": 6001,
                    "label": "",
                    "link_label": "codquery",
                    "link_type": "input_work",
                    "mtime": "Fri, 29 Nov 2019 17:32:59 GMT",
                    "node_type": "data.dict.Dict.",
                    "process_type": null,
                    "user_id": 1,
                    "uuid": "1a6cfe33-4275-4320-8f35-da2cacd9d43a"
                },
                {
                    "ctime": "Fri, 29 Nov 2019 17:32:58 GMT",
                    "full_type": "data.bool.Bool.|",
                    "id": 6002,
                    "label": "",
                    "link_label": "strictcheck",
                    "link_type": "input_work",
                    "mtime": "Fri, 29 Nov 2019 17:32:59 GMT",
                    "node_type": "data.bool.Bool.",
                    "process_type": null,
                    "user_id": 1,
                    "uuid": "5751b30f-ab5f-4dc7-a9c8-0e864d6f9d5f"
                }
            ]
        },
        "id": "1e6d99e4-1966-45c7-b481-55513d3ed827",
        "method": "GET",
        "path": "/api/v4/nodes/1e6d99e4-1966-45c7-b481-55513d3ed827/links/incoming",
        "query_string": "",
        "resource_type": "nodes",
        "url": "http://127.0.0.1:5000/api/v4/nodes/1e6d99e4-1966-45c7-b481-55513d3ed827/links/incoming",
        "url_root": "http://127.0.0.1:5000/"
    }

That returns what we know about the process: that it has two inputs, of the given class and name, but also returns how they are stored in the database.

Coming back to the results, we can pirnt the content by querying for the attributes of a node: ::

    http 127.0.0.1:5000/api/v4/nodes/36b1abcd-d28c-4362-8147-08e279e4ca5d/contents/attributes

That returns

.. code-block:: JSON

    {
        "data": {
            "attributes": {
                "list": [
                    "ffdf766d-6130-47da-b62f-e2a8ef063fa8",
                    "47090f18-3c80-4482-b4ea-89e4bd1a6ad3",
                    "c3d4b113-8faa-4caa-8141-2d76f149c843",
                    "db526bd5-96d7-4747-abde-9c602a67cc24",
                    "3633634c-2543-4915-83d7-1b7cf1d89df5",
                    "aa03b830-9c90-4240-87b3-3da58614676e"
                ]
            }
        },
        "id": "36b1abcd-d28c-4362-8147-08e279e4ca5d",
        "method": "GET",
        "path": "/api/v4/nodes/36b1abcd-d28c-4362-8147-08e279e4ca5d/contents/attributes",
        "query_string": "",
        "resource_type": "nodes",
        "url": "http://127.0.0.1:5000/api/v4/nodes/36b1abcd-d28c-4362-8147-08e279e4ca5d/contents/attributes",
        "url_root": "http://127.0.0.1:5000/"
    }

And returns a list of the ``uuid`` of the structure data that we retrieved from the COD.


Looking for a specific property from a workflow
-------------------------------------------------

The idea of this app is to automatically calculate materials properties based on their names.

The *existing/properties/<prop>/<node>* endpoint check if the node *<node>* is an output of a workflow that result in the value relative to the property *<prop>*. It will list all of the calculated properties (i.e. duplicates, but also calculaction that might have different parameters while being generated by the same input *<node>*). A list of the workflows executed with this node and the corresponding workflow type will be returned, in order to know whether there are excepted or running workflows; this information is useful to know if there is another calculation on the way, or to double check what was the reason of the failures in the excepted one (to correct the inputs in advance rather than spending valuable computational time).

Listing all the workflows of a particular type
----------------------------------------------

A specific list of all the workflows launched in the database, there is the endpoint

http 127.0.0.1:5000/api/v4/intersect/properties/<prop>/list

THis will provide a list of all the executed workflows that can generate the property requested. This is very general: it will return all the workflows that could generate a bnd gap in quantum espresso, regardless of the calculation status, or the structure input.
