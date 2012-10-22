import json

from cornice import Service
from cornice.ext.spore import generate_spore_description
from cornice.service import get_services
from pyramid.exceptions import NotFound
from pyramid.response import Response

TODOS = {}
HEADERS = {'Content-Type': 'application/json'}
VERSION = '0.1'

todo = Service(name='todo',
               path='/todo',
               description='Manage a todo')

task = Service(name='task',
               path='/todo/{key}',
               description='Manage a task')


spore = Service(name="spore",
                path='/spore',
                description="Spore endpoint")


@todo.get()
def get(request):
    """Retrieves all task."""
    return TODOS


@todo.post()
def post(request):
    """Saves a new task."""
    try:
        data = json.loads(request.body)
        key = data.keys()[0]
        value = data[key]
    except (SyntaxError, ValueError, IndexError, KeyError) as e:
        response = Response(status=400, body=json.dumps({"error": e.message}),
                            headers=HEADERS)
    else:
        TODOS[key] = value
        created = '%s/todo/%s' % (request.application_url, key)
        response = Response(status="201 Created",
                            body=json.dumps({'key': key}),
                            headers=HEADERS)

    return response


@task.get()
def get(request):
    """Retrieves."""
    key = request.matchdict['key']

    if key not in TODOS:
        raise NotFound("Unknown key '%s'." % (key))

    return {key: TODOS[key]}


@task.put()
def put(request):
    """Update a data item.

    Checks that the data is a valid data item.

    """
    key = request.matchdict['key']
    try:
        data = json.loads(request.body)
        value = data[key]
    except (SyntaxError, ValueError, KeyError) as e:
        response = Response(status=400, body=json.dumps({"error": e.message}),
                            headers=HEADERS)
    else:
        TODOS[key] = value
        response = {'key': key}

    return response


@task.delete()
def delete(request):
    """Delete the data item.

    Checks that the data is a valid data item.

    """
    key = request.matchdict['key']

    if key not in TODOS:
        raise NotFound("Unknown key '%s'." % (key))

    del TODOS[key]


@spore.get()
def get_spore(request):
    return generate_spore_description(get_services(), 'daybed',
              request.application_url, VERSION)
