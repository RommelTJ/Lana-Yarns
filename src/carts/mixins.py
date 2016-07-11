import ast
import base64


class TokenMixin(object):

    def create_token(self, data_dict):
        if type(data_dict) == type(dict()):
            token = base64.b64encode(str(data_dict))
            return token
        else:
            raise ValueError("Creating a token must use a python dictionary.")

    def parse_token(self, token):
        token_decoded = base64.b64decode(token)
        token_dict = ast.literal_eval(token_decoded)
        return token_dict
