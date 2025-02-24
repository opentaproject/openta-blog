from django.utils.deprecation import MiddlewareMixin

class ResponseRewriteMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Check if the response is an HTML response
        r = { 'OpenTA-category-not-selected' : 'inline-block border border-white rounded hover:border-gray-200 text-blue-500 hover:bg-gray-200 py-1 px-3',\
            'OpenTA-category-selected' : 'inline-block border border-blue-500 rounded py-1 px-3 bg-blue-500 text-white"',\
            'OpenTA-body' : 'bg-[#ffffff] p-4 font-sans text-sm antialiased',\
            'OpenTA-comment-body' : 'border border-gray-300 px-2 rounded-lg bg-red-400 shadow-md',\
            'OpenTA-post-list' : 'h-full border border-gray-300 rounded-lg bg-white shadow-md',\
            'OpenTA-comment-entry' : 'p-0',\
            'OpenTA-comment-list' : 'p-0 rounded-lg bg-white shadow-md ' ,\
            'OpenTA-hide-button' :  'hover:bg-blue-400 bg-blue-200',\
            'OpenTA-leave-comment-form' : 'px-0',\
            'OpenTA-leave-comment-link' : 'bg-blue-200',\
            'OpenTA-navigation-bar' : 'flex p-2 border-b bg-transparent bg-[#cccccc]', \
            'OpenTA-post-entry' : 'border bg-blue-400 border-gray-300 p-4 rounded-lg bg-green-200  shadow-md',\
            'OpenTA-post-body' : 'border  border-gray-300 p-4 rounded-lg bg-green-400  shadow-md',\
            'OpenTA-post-last-modified' : 'font-light text-xs',\
            'OpenTA-post-title' : 'italic bg-blue-400 ',\
            'OpenTA-show-button' : 'hover:bg-blue-400 bg-blue-200',\
            'OpenTA-submit-button' : 'hover:bg-blue-400 btn btn-primary',\
            'OpenTA-toggle' : 'sm:italic',}
    
        p = request.path
        try :
            q = response['Content-Type']
            if 'text/html' in response['Content-Type'] and not 'admin' in p :
                for pat in r.keys() :
                    response.content = response.content.replace(
                        pat.encode()  , r[pat].encode()  
                    )
                # Ensure the content length header is updated
                response['Content-Length'] = len(response.content)
        except :
            pass
        
        return response
