from rest_framework.response import Response



def custom_response(data=None, errors=None, status=None, message=None):
    response_data = {}

    if data is not None:
        response_data["data"] = data
    if errors is not None:
        response_data["errors"] = errors
    if status is not None:
        response_data["status"] = status
    if message is not None:
        response_data["message"] = message

    return Response(response_data, status=status if status else 200)
