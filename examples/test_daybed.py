"""Test daybed installation.

    $ git clone git@github.com:spiral-project/daybed.git
    $ cd daybed
    $ virtualenv .
    $ source bin/activate
    $ make serve
    bin/pserve development.ini --reload
    Using db "daybed"
    serving on http://0.0.0.0:8000
    $ python test_daybed.py

"""
from respire import client_from_url
from uuid import uuid4

todo='todo_%s' % uuid4()
print todo

def main():
    api = client_from_url("http://localhost:8000/spore")
    # Put the definition
    token = api.put_definition(
        model_name=todo, 
        data={
            "title": "todo",
            "description": "A list of my stuff to do", 
            "fields": [
                {
                    "name": "item", 
                    "type": "string",
                    "description": "The task todo."
                    }, 
                {
                    "name": "status", 
                    "type": "enum",
                    "choices": [
                        "todo", 
                        "done"
                        ], 
                    "description": "Status of the task."
                    }
                ]})
    # Post some data
    data_item = api.post_data(model_name=todo, data=dict(item='make it work', status='todo'))
    # Update some data
    api.put_data_item(model_name=todo, data_item_id=data_item['id'], 
                      data={'item': 'make it work', 'status': 'done'})
    print api.get_data(model_name=todo)
    # Delete definition and data
    api.delete_definition(model_name=todo, data={'token': token['token']})

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        try:
            import ipdb; ipdb.set_trace()
        except ImportError:
            import pdb; pdb.set_trace()
        raise
