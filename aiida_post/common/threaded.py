
from threading import Thread

def threaded(f, daemon=False):
    import queue

    def wrapped_f(q, *args, **kwargs):
        '''this function calls the decorated function and puts the
        result in a queue'''
        ret = f(*args, **kwargs)
        q.put(ret)

    def wrap(*args, **kwargs):
        '''this is the function returned from the decorator. It fires off
        wrapped_f in a new thread and returns the thread object with
        the result queue attached'''

        q = queue.Queue()

        t = Thread(target=wrapped_f, args=(q,)+args, kwargs=kwargs)
        t.daemon = daemon
        t.start()
        t.result_queue = q
        return t

    return wrap

@threaded
def submit_job(wf, *args,**kwargs):
    """
    submit asyncronously a job to the scheduler
    returns the uuid of the node responding to the request
    """
    from aiida.engine import submit, run
    print ('mu',args)
    #for k, v in kwargs.items():
    #    kwargs.update(k,load_node(v))
    node = submit(wf,*args,**kwargs)
    return node

@threaded
def run_calculation(wf, *args,**kwargs):
    """
    submit asyncronously a job to the scheduler
    returns the uuid of the node responding to the request
    """
    from aiida.engine import submit, run
    from aiida.orm import load_node
    #aargs = [load_node(x)  for x in args]
    node = wf(*args,**kwargs)
    return node

