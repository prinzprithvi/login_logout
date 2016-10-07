__author__ = 'prathvi'
from bson import ObjectId
from bson.dbref import DBRef
import  mongoengine
import datetime

def encode_model(obj, recursive=False):
    if obj is None:
        return obj
    if isinstance(obj, (mongoengine.Document, mongoengine.EmbeddedDocument)):
        out = dict(obj._data)
        for k,v in out.items():
            if isinstance(v, ObjectId):
                if k is None:
                    out['_id'] = str(v)
                    del(out[k])
                else:
                    # Unlikely that we'll hit this since ObjectId is always NULL key
                    out[k] = str(v)
            else:
                out[k] = encode_model(v)
    elif isinstance(obj, mongoengine.queryset.QuerySet):
        out = encode_model(list(obj))
    elif isinstance(obj, (list)):
        out = [encode_model(item) for item in obj]
    elif isinstance(obj, (dict)):
        out = dict([(k,encode_model(v)) for (k,v) in obj.items()])
    elif isinstance(obj, datetime.datetime):
        out = obj.strftime("%Y-%m-%d-%H:%M:%S")
    elif isinstance(obj, ObjectId):
        out = str(obj)
    elif isinstance(obj, DBRef):
        out = str(obj)
    elif isinstance(obj, (str, unicode)):
        out = obj
    elif isinstance(obj, float):
        out = obj
    elif isinstance(obj, int):
        out = obj
    else:
        raise TypeError, "Could not JSON-encode type '%s': %s" % (type(obj), str(obj))
    return out
