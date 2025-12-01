import flask, inspect, sys
print("flask module:", getattr(flask, '__file__', None))
print("flask version:", getattr(flask, '__version__', None))
print("is Flask available on flask.Flask:", hasattr(flask, 'Flask'))
print("has before_first_request on class:", hasattr(flask.Flask, 'before_first_request'))
print("type(app) check (if app defined):")
# attempt to import app only if safe
try:
    import app as myapp
    print("imported app.py from:", myapp.__file__)
    print("type(myapp.app):", type(getattr(myapp, 'app', None)))
except Exception as e:
    print("could not import local app.py:", e)
