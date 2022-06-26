import json


class ComplexEncoder(json.JSONEncoder):
    """
    Define a JSON encoder which overrides the default implementation.
    This definition checks for the presence of a JSON_object function so that nested objects can be written to JSON.
    """

    def default(self, obj):
        if hasattr(obj, "JSON_object"):
            return obj.JSON_object()
        else:
            return json.JSONEncoder.default(self, obj)
