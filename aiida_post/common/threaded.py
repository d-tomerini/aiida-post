"""
Module to handle concurrent execution in different threads
"""

from __future__ import absolute_import
from concurrent.futures.thread import ThreadPoolExecutor
from functools import wraps

_DEFAULT_POOL = ThreadPoolExecutor()


def threaded(func, executor=None):
    """
    Class to run a subroutine from a different thread, and return a
    future. I will mainly run short subroutine that would have run
    concurrently, but cannot because of flask
    """

    @wraps(func)
    def wrap(*args, **kwargs):
        return (executor or _DEFAULT_POOL).submit(func, *args, **kwargs)

    return wrap


@threaded
def submit_job(workflow, **inputs):
    """
    Simple wrapper to submit asyncronously a job to the scheduler
    : param wf: workchain to be submitted
    : output: the node object
    """
    from aiida.engine import submit

    node = submit(workflow, **inputs)
    return node


@threaded
def get_builder(workflow):
    """
    Building of namespaces triggers events that needs to be run asyncronously
    : input WF: AiiDA process type
    """
    builder = workflow.get_builder()

    return builder


@threaded
def submit_builder(builder):
    """
    Simple wrapper to submit asyncronously a job from its builder class
    : param wf: workchain to be submitted
    : output: the node object
    """
    from aiida.engine import submit

    node = submit(builder)
    return node
