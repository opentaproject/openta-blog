from django.utils.deprecation import MiddlewareMixin

class ResponseRewriteMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        r = { 
            'OpenTA-category-not-selected' : 'OpenTA-text-size inline-block border border-white rounded hover:border-gray-200 hover:bg-gray-200 py-0 px-2',\
            'OpenTA-category-selected' : 'OpenTA-text-size  inline-block border border-blue-500 rounded py-0 px-2 bg-blue-500 text-white"',\
            'OpenTA-body' : 'bg-[#ffffff] p-4 font-sans antialiased',\
            'OpenTA-comment-body' : 'border-b border-gray-300 py-1 rounded-lg shadow-md',\
            'OpenTA-post-list' : 'h-full border border-gray-300 rounded-lg shadow-md OpenTA-text-size',\
            'OpenTA-comment-entry' : 'border-2 mt-2 p-2 border-gray-400 rounded-lg',\
            'OpenTA-comment-list' : 'p-0 rounded-lg  shadow-md OpenTA-background' ,\
            'OpenTA-hide-button' :  'hover:bg-blue-400',\
            'OpenTA-leave-comment-form' : 'px-0',\
            'OpenTA-leave-comment-link' : '',\
            'OpenTA-navigation-bar' : 'size flex p-2 border-b bg-transparent bg-[#cccccc]', \
            'OpenTA-post-selected-entry' : 'border border-gray-300 p-2 rounded-lg bg-yellow-100  shadow-md',\
            'OpenTA-post-rhs-entry' :      'bg-yellow-100 border border-gray-300 p-2 rounded-lg shadow-md',\
            'OpenTA-post-entry' :          'border border-gray-300 p-2 rounded-lg shadow-md',\
            'OpenTA-post-body' : '',\
            'OpenTA-post-last-modified' : 'font-light OpenTA-text-size ',\
            'OpenTA-post-title' : 'OpenTA-text-size font-semibold',\
            'OpenTA-show-button' : 'hover:bg-blue-400 bg-blue-200',\
            'OpenTA-submit-button' : 'hover:bg-blue-400 btn btn-primary',\
            'OpenTA-rhs-sidebyside' : 'w-3/4 align-top px-2',\
            'OpenTA-lhs-sidebyside' : 'OpenTA-background w-1/4 align-top px-2',\
            'OpenTA-table-sidebyside' : 'min-w-full border-collapse border border-blue-800',\
            'OpenTA-new-button' : 'p-1 text-white bg-blue-400 font-medium rounded me-2 ',\
            'OpenTA-toggle' : 'sm:italic',
            'OpenTA-text-size' : 'text-xs md:text-sm lg:text-base',\
            'OpenTA-background' : 'bg-white',\
             }
    
        p = request.path
        q = response['Content-Type']
        if 'text/html' in response['Content-Type'] and not 'admin' in p :
            for pat in r.keys() :
                response.content = response.content.replace(
                    pat.encode()  , r[pat].encode()  
                )
            # Ensure the content length header is updated
            response['Content-Length'] = len(response.content)
        
        return response
