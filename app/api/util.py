from flask import request


def check_content_type():
    if 'application/json' in request.content_type:
        return request.get_json()

    elif 'application/x-www-form-urlencoded' in request.content_type:
        return request.form
