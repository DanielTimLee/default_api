from flask import request

def validate_on_submit(form):
    if request.method == 'POST' and form.validate():
        return True

    return False
