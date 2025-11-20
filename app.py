TypeError
TypeError: unsupported operand type(s) for -: 'decimal.Decimal' and 'float'

Traceback (most recent call last)
File "C:\Users\User\AppData\Local\Programs\Python\Python314\Lib\site-packages\flask\app.py", line 1536, in __call__
return self.wsgi_app(environ, start_response)
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\User\AppData\Local\Programs\Python\Python314\Lib\site-packages\flask\app.py", line 1514, in wsgi_app
response = self.handle_exception(e)
           ^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\User\AppData\Local\Programs\Python\Python314\Lib\site-packages\flask\app.py", line 1511, in wsgi_app
response = self.full_dispatch_request()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\User\AppData\Local\Programs\Python\Python314\Lib\site-packages\flask\app.py", line 919, in full_dispatch_request
rv = self.handle_user_exception(e)
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\User\AppData\Local\Programs\Python\Python314\Lib\site-packages\flask\app.py", line 917, in full_dispatch_request
rv = self.dispatch_request()
     ^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\User\AppData\Local\Programs\Python\Python314\Lib\site-packages\flask\app.py", line 902, in dispatch_request
return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "c:\Users\User\Desktop\sistema_inventario_motos\app.py", line 371, in decorated_function
return f(*args, **kwargs)
       ^^^^^^^^^^^^^^^^^^
File "c:\Users\User\Desktop\sistema_inventario_motos\app.py", line 781, in detalle_producto
return render_template("detalle_producto.html", producto=producto)
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\User\AppData\Local\Programs\Python\Python314\Lib\site-packages\flask\templating.py", line 150, in render_template
return _render(app, template, context)
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\User\AppData\Local\Programs\Python\Python314\Lib\site-packages\flask\templating.py", line 131, in _render
rv = template.render(context)
     ^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\User\AppData\Local\Programs\Python\Python314\Lib\site-packages\jinja2\environment.py", line 1295, in render
self.environment.handle_exception()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\User\AppData\Local\Programs\Python\Python314\Lib\site-packages\jinja2\environment.py", line 942, in handle_exception
raise rewrite_traceback_stack(source=source)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "c:\Users\User\Desktop\sistema_inventario_motos\templates\detalle_producto.html", line 1, in top-level template code
{% extends "base.html" %}
File "c:\Users\User\Desktop\sistema_inventario_motos\templates\base.html", line 1075, in top-level template code
{% block content %}{% endblock %}
File "c:\Users\User\Desktop\sistema_inventario_motos\templates\detalle_producto.html", line 77, in block 'content'
{% set ganancia_unitaria = (producto.precio_venta or 0) - precio_con_iva %}
TypeError: unsupported operand type(s) for -: 'decimal.Decimal' and 'float'
The debugger caught an exception in your WSGI application. You can now look at the traceback which led to the error.
To switch between the interactive traceback and the plaintext one, you can click on the "Traceback" headline. From the text traceback you can also create a paste of it. For code execution mouse-over the frame you want to debug and click on the console icon on the right side.

You can execute arbitrary Python code in the stack frames and there are some extra helpers available for introspection:

dump() shows all variables in the frame
dump(obj) dumps all that's known about the object
