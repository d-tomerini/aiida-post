This directory contains the required codes to run a workflow.
If a code is not given as an input, and we want to use what is available in the database,
we need to be able to provide the right code type.
Unfortunately, in many workflow the type of code is not issued: so we cannot be sure about
what type needs to be provided.
In order to be general, we can provide a schema that list of all the code used in a workflow that
is needed.

This adds additional complexity (an additional file for every workflow we need to use), but it
is unfortunately necessary, as a workflow might include different codes in its execution (for example,
a pw and a ph code) and we cannot inherit it in a simple way from the workchain entry point.

Files in this directory are simple dictionaries that contains the code in a nested way.