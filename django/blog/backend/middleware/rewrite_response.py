from django.utils.deprecation import MiddlewareMixin

class ResponseRewriteMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Check if the response is an HTML response
        r = { 'OpenTA-category-not-selected' : 'bg-green-200 hover:bg-green-400',\
            'OpenTA-category-selected' : 'bg-red-400',\
            'OpenTA-body' : 'bg-indigo-100 p-8 font-sans text-sm antialiased',\
            'OpenTA-comment-body' : 'py-2',\
            'OpenTA-comment-entry' : 'p-0',\
            'OpenTA-comment-list' : 'p-0' ,\
            'OpenTA-hide-button' :  'hover:bg-green-400 bg-green-200',\
            'OpenTA-leave-comment-form' : 'px-0',\
            'OpenTA-leave-comment-link' : 'bg-red-400',\
            'OpenTA-navigation-bar' : 'bg-blue-100', \
            'OpenTA-post-entry' : 'p-0',\
            'OpenTA-show-button' : 'hover:bg-red-400 bg-red-200',\
            'OpenTA-submit-button' : 'hover:bg-blue-400 btn btn-primary',\
            'OpenTA-toggle' : 'sm:italic',}
        if 'text/html' in response['Content-Type']:
            for pat in r.keys() :
                response.content = response.content.replace(
                    pat.encode()  , r[pat].encode()  
                )
            # Ensure the content length header is updated
            response['Content-Length'] = len(response.content)
        
        return response
