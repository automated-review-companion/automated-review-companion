import functools
from django.http import JsonResponse
from rest_framework import status
from django.http import Http404


def HandleExceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Http404 as e:            
            return ErrorResponse(str(e), status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return ErrorResponse(str(e), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return ErrorResponse(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper


def Controller(func):
    return HandleExceptions(func)


def ErrorResponse(error, status):

    def parse_error(error):
        """
        Rules to parse the error message
        """
        error_message = error.replace('\"', "'")
        return error_message

    if not isinstance(error, dict):
        return JsonResponse({"error": error}, status=status)

    errors = {"error": {}}
    for key, value in error.items():
        if isinstance(value, str):
            error_message = parse_error(value)
        elif isinstance(value, list):
            error_message = [parse_error(item) for item in value]
        else:
            error_message = value

        errors["error"][key] = error_message

    return JsonResponse(errors, status=status)