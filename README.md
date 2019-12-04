# AiiDA interface with an External program

## Communication app between an external program and AiiDA

Implementation of a REST API to implement external communication with AiiDA.
This program will act as a bridge to convey to AiiDA information through HTML communication

## Details

[AiiDA](http://www.aiida.net/) is a flexible and scalable informatics' infrastructure to manage, preserve,
and disseminate the simulations, data, and workflows of modern-day computational science.

Our interconnection app will provede very basic extension to the existing REST API of AiiDA, to deal specifically with:
1. Submission of workflow
2. Retrieval of specific workflow nodes
3. Structural search
4. Information on ongoing calculations

## Running the app

The app can be run through the ``verdi run`` executable, that loads some of the necessary classes for the execution:

``
  verdi run app.py
``
## TODO

In the future we will extend the functionality to have it run directly through a ``verdi`` command , or its own executable.

## Installation

The app can be downloaded from the gitlab directory at this address:
https://gitlab.cc-asp.fraunhofer.de/intersect/ext_to_aiida/tree/develop

## Documentation

Documentation is available in the docs/\_build/html/index.html directory.
To build them, you need to have sphinx installed and type make html in the docs folder.

## Acknowledgements

This work is supported by the [INTERSECT project](http://intersect-project.eu/),
Interoperable Material-to-Device simulation box for disruptive electronics

A H2020-NMBP-TO-IND-2018 funded project: GA n. 814487


