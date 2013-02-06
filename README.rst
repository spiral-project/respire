Respire: Yet Another SPORE client
=================================

**Respire** is a python client which consumes a SPORE description file and
expose a python API for it.

Here is how to use it, out of the box, with a working SPORE defined website.

(These examples works with the `Daybed
<http://github.com/spiral-project/daybed>`_ project, but it woks the same with
any other SPORE enabled service.)::

    from respire import client_from_url

    cl = client_from_url('http://localhost:8000/spore')
    cl.post_data(model_name='todo', data=dict(item='make it work', status='todo'))
    cl.get_data(model_name='todo')

If you need to add headers to all the queries or handle cookies, you can pass a
``requests.Session`` instance::

    from request import client_from_url
    import requests

    session = requests.Session()
    session.headers['X-Some-App-Key'] = 'myapplicationkey'
    
    cl = client_from_url('http://localhost:8000/spore', session=session)
    cl.post_data(model_name='todo', data=dict(item='make it work', status='todo'))
    cl.get_data(model_name='todo')

How to install it?
------------------

Currently, Respire is not packaged for pypi, so you need to get it from git::

    $ git clone http://github.com/spiral-project/respire.git
    (respire)$ make install
    (respire)$ make tests
