import time
import functools
from functools import wraps
from typing import Callable, Any, Union, Dict

from django.http import HttpRequest
from rest_framework.exceptions import NotFound as Http404
from rest_framework import status
from django.http import JsonResponse





class Color:
    WHITE = '\033[97m'
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def Profiler(process_name: str):
  """
  Decorator factory to profile a function, logging its start and end time
  
  :params process_name (str): The name of the process to profile.
  :rettype: function
  """
  def decorator(func: Callable):
    
    @wraps(func)
    def wrapper(*args, **kwargs):
      print(f"{Color.HEADER}──────────────────────── {process_name} [START] ────────────────────────{Color.ENDC}")
      
      start_time = time.time()
      try: 
        result = func(*args, **kwargs)
      except Exception as e:
        print(f"An error occurred: {e}")
        raise e
      finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{Color.HEADER}──────────────────────── {process_name} [END] ──────────────────────────{Color.ENDC}")
        print(f"{Color.HEADER}Elapsed time: {elapsed_time:.2f} seconds{Color.ENDC}")
        
      return result
    return wrapper
  
  return decorator

def HandleExceptions(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Http404 as e:
            return ErrorResponse(str(e), status=404)
        except ValueError as e:
            return ErrorResponse(str(e), status=404)
        except Exception as e:
            return ErrorResponse(str(e), status=500)
    return wrapper

def Logger(func: Callable, _name: str = None, _class: str = None) -> Callable:
    """ 
    Decorator to log the function name and arguments.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        name = f"{_class} - {func.__name__}" if _class else func.__name__
        print(f"-------------- [Start] {name} -----------------")
        if args and isinstance(args[0], HttpRequest):
            print(f"Arguments: {args[0]}")
        result = func(*args, **kwargs)
        print(f"-------------- [End] {name} -------------------")
        return result
    return wrapper

def Controller(func: Callable) -> Callable:
    """ 
    Decorator to handle exceptions in the controller methods.
    """
    return HandleExceptions(Logger(Profiler(func), _name=__name__, _class=func.__class__))


def ErrorResponse(error: Union[str, Dict[str, Union[Any]]], status: int = status.HTTP_400_BAD_REQUEST):
    """
    Returns a JSON response with the error message(s).

    :param error: The error message(s) to be returned. 
    :param status: The status code of the response. Default is 400.
    :return: A JSON response with the error message(s).

    >>> ErrorResponse("Invalid request. The maximum content length is 4000.")
    {"error": "Invalid request. The maximum content length is 4000."}

    >>> ErrorResponse({"msg": "Invalid request. The maximum content length is 4000."})
    {"error": {"msg": "Invalid request. The maximum content length is 4000."}}
    """

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

