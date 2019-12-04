"""
Utility functions to pretty print the outputs
"""


def format_wf(workflow):
    """
    Takes a process nodes, and print to a dictionary the
    properties that I consider interesting to know
    : input: an AiiDA process class
    """
    interesting_process_attributes = [
        'process_label', 'process_class', 'process_state', 'version', 'exit_status', 'exit_message',
        'stepper_state_info'
    ]
    return dict(
        uuid=workflow.uuid,
        ctime=workflow.ctime,
        attributes={key: workflow.attributes.get(key) for key in interesting_process_attributes}
    )


def delete_key(dictionary, mykey, startswith=False):
    """
    Recursively remove keys of the dictionary that contains or start with a given string
    """

    list_keys = list(dictionary.keys())
    for key in list_keys:
        if isinstance(dictionary[key], dict):
            delete_key(dictionary[key], mykey, startswith)
        if (startswith and key.startswith(mykey) or mykey == key):
            del dictionary[key]


def delete_key_check_dict(dictionary, mykey, myvalue):
    """
    Check recursively if a mykey:myvalue pair is in a dictionary
    If it is, it and the value is not myvalue, remove each key of the dictionary
    """

    list_keys = list(dictionary.keys())
    for key in list_keys:
        if isinstance(dictionary[key], dict):
            if mykey in dictionary[key]:
                if myvalue != dictionary[key][mykey]:
                    del dictionary[key]
            else:
                delete_key_check_dict(dictionary[key], mykey, myvalue)
