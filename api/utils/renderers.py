from rest_framework.renderers import JSONRenderer


class LoginRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code

        # return an empty response if there is no data to render
        response = b'' if data is None else {"data": data}

        if not str(status_code).startswith('2'):
            response = {
                "errors": data,
            }
        return super(LoginRenderer, self).render(response, accepted_media_type, renderer_context)


"""
class CustomResponseRenderer(JSONRenderer):
    '''
    A custom Renderer to make all responses return a success key by default
    '''

    res = "data"
    is_paginated = False

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        if data is None:
            return b''
            
        if self.is_paginated:
            response = {"data": data}
        else:
            if self.res == "data":
                response = {
                    "data": {
                        **data,
                    },
                }
            else:
                response = {
                "data": {
                    self.res: data,
                },
            }
        if not str(status_code).startswith('2'):
            response = {
                "errors": data,
            }
        return super(CustomResponseRenderer, self).render(response, accepted_media_type, renderer_context)
"""
