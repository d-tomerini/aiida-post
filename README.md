# AiiDA interface with an External program

## Communication app between an external program and AiiDA

Implementation of a REST API to implement external communication with AiiDA.
This program will act as a bridge to convey to AiiDA information through HTML communication

## Details

[AiiDA](http://www.aiida.net/) is a flexible and scalable informatics' infrastructure to manage, preserve,
and disseminate the simulations, data, and workflows of modern-day computational science.

Our interconnection app will provede very basic interaction with a AIiiDA from a server,
to deal with:
1. Requests for calculated data
2. Requests for stored data
3. Information on stored database nodes (calculations, previous requests)
4. Information on ongoing calculations

## Running the app

The app can be run through the ``verdi run`` executable, that loads some
of the necessary classes for the execution:

``
  verdi run app.py
``

In the future we will extend the functionality to have it run directly through a ``verdi`` command.


## Installation

The app can be downloaded from the gitlab directory.

## Acknowledgements

This work is supported by the [INTERSECT project](http://intersect-project.eu/),
Interoperable Material-to-Device simulation box for disruptive electronics

A H2020-NMBP-TO-IND-2018 funded project: GA n. 814487


