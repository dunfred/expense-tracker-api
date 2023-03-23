from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Update the structure of the response data.
    if response is not None:
        customized_response = {}
        customized_response['validations'] = {}
        for key, value in response.data.items():

            if key ==  'detail':
                if type(value) is list: # check if key is detail and value is list
                    customized_response['detail'] = ','.join(value)
                else:
                    # try: # check if this is a TokenError
                    #     if value.code == 'token_not_valid':
                    #         response.data = {
                    #             'detail': 'Invalid refresh token'
                    #         }
                    #         response.status_code = 400
                    #         return response # return here to avoid the rest of the token error code
                    #     else:
                    #         customized_response['detail'] = value
                    # except Exception:
                    #     customized_response['detail']= value
                    customized_response['detail']= value
            else:
                if type(value) is dict: # if key is not detail and value is dict
                    for k,v in value.items():
                        customized_response['validations'][key][k] = v
                elif type(value) is list: # if key is not detail and value is list
                    for inner_val in value:
                        customized_response['validations'][key] = {}
                        if type(inner_val) is dict: # if key is not detail and value is list and inner value is dict
                            for k,v in inner_val.items():
                                customized_response['validations'][key][k] = v
                        else: # if key is not detail and value is list and inner value is not dict
                            try:
                                error_list = eval(list(value)[0]) # using eval to prevent string being converted to list
                                customized_response['validations'][key] = " ".join(error_list)
                            except Exception: # if key is not detail and value is list and inner value is not dict and not list
                                error = ''.join(value) #join on empty string to remove the list brackets
                                customized_response['validations'][key]= error
                else: # if key is not detail and value is not dict and not list
                    error = ''.join(value) #join on empty string to remove the list brackets
                    customized_response['validations'][key]= error

        response.data = customized_response
    return response