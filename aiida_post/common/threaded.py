from concurrent.futures.thread import ThreadPoolExecutor
from functools import wraps

_DEFAULT_POOL = ThreadPoolExecutor()


def threaded(f, executor=None):
    @wraps(f)
    def wrap(*args, **kwargs):
        return (executor or _DEFAULT_POOL).submit(f, *args, **kwargs)

    return wrap

@threaded
def submit_job(wf, *args,**kwargs):
    """
    Simple wrapper to submit asyncronously a job to the scheduler
    : param wf: workchain to be submitted
    : output: the node object
    """
    from aiida.engine import submit

    node = submit(wf, *args, **kwargs)
    return node

@threaded
def run_calculation(wf, *args,**kwargs):
    """
    submit asyncronously a job to the scheduler
    returns the uuid of the node responding to the request
    """
    #aargs = [load_node(x)  for x in args]
    node = wf(*args,**kwargs)
    return node

