from django.utils.deprecation import MiddlewareMixin

class ResponseRewriteMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Check if the response is an HTML response
        r = { 'OpenTA-category-not-selected' : 'hoverbg-green-400',\
            'OpenTA-category-selected' : 'bg-red-400',\
            'OpenTA-body' : 'bg-bodycolor p-8',\
            'OpenTA-comment-body' : 'p-0',\
            'OpenTA-comment-entry' : 'p-0',\
            'OpenTA-comment-list' : 'px-0' ,\
            'OpenTA-hide-button' :  'bg-green-500',\
            'OpenTA-leave-comment-form' : 'px-0',\
            'OpenTA-leave-comment-link' : 'bg-red-400',\
            'OpenTA-navigation-bar' : 'bg-OpenTA_navigation',\
            'OpenTA-post-entry' : 'p-0',\
            'OpenTA-show-button' : 'bg-red-500',\
            'OpenTA-submit-button' : 'btn btn-primary',\
            'OpenTA-toggle' : 'sm:italic',}
        if 'text/html' in response['Content-Type']:
            for pat in r.keys() :
                response.content = response.content.replace(
                    pat.encode()  , r[pat].encode()  
                )
            # Ensure the content length header is updated
            response['Content-Length'] = len(response.content)
        
        return response
