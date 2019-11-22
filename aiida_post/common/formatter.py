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
