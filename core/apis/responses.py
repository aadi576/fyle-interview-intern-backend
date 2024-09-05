from flask import Response, jsonify, make_response

class APIResponse(Response):
    @classmethod
    def respond(cls, data, status_code=200, message=None):
        # Create a response dictionary with a message if provided
        response_dict = {'data': data}
        if message:
            response_dict['message'] = message
        
        # Create and return a Flask response object
        return make_response(jsonify(response_dict), status_code)
