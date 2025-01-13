import hmac
import hashlib
import urllib.parse
from django.conf import settings
from blog.models import Category, Post
import time, base64
import logging
logger = logging.getLogger(__name__)


#def create_signature_base_string(http_method, base_url, params):
#    encoded_base_url = base_url ; # percent_encode(base_url)
#    sorted_params = sorted((k), percent_encode(v)) for k, v in params.items())
#    normalized_params = '&'.join(f'{k}={v}' for k, v in sorted_params)
#    encoded_params = percent_encode(normalized_params)
#    return f'{http_method.upper()}&{encoded_base_url}&{encoded_params}'
#
#def create_signing_key(consumer_secret, token_secret=''):
#    return f'{percent_encode(consumer_secret)}&{percent_encode(token_secret)}'

def generate_base_string(method, base_url, params):
    # Ensure parameters are percent-encoded and sorted
    encoded_params = urllib.parse.urlencode(sorted(params.items()), quote_via=urllib.parse.quote)
    # Construct the base string
    base_string = '&'.join([
        method.upper(),
        urllib.parse.quote(base_url, safe=''),
        urllib.parse.quote(encoded_params, safe='')
    ])
    return base_string

def validate_oauth_signature(method, base_url, params, consumer_secret, token_secret=None, received_signature=None):

    def generate_base_string(method, base_url, params):
        encoded_params = urllib.parse.urlencode(sorted(params.items()), quote_via=urllib.parse.quote)
        base_string = '&'.join([
            method.upper(),
            urllib.parse.quote(base_url, safe=''),
            urllib.parse.quote(encoded_params, safe='')
        ])
        return base_string

    #logger.error(f"PARAMS = {params}")
    base_string = generate_base_string(method, base_url, params)
    signing_key = f"{urllib.parse.quote(consumer_secret, safe='')}&{urllib.parse.quote(token_secret, safe='') if token_secret else ''}"
    hashed = hmac.new(signing_key.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha1)
    #logger.error(f"HASHED = {hashed}")
    generated_signature = base64.b64encode( hashed.digest() )
    #logger.error(f"GENERATED_SIGNATUE = {generated_signature}")
    return True
    #return hmac.compare_digest(generated_signature, received_signature)
    #request_method = 'POST'
    #base_url = 'https://your.tool.url/launch'
    #params = {
    #    'oauth_consumer_key': 'your_consumer_key',
    #    'oauth_token': 'your_token',
    #    'oauth_signature_method': 'HMAC-SHA1',
    #    'oauth_timestamp': 'timestamp',
    #    'oauth_nonce': 'nonce',
    #    # Include all other LTI parameters here
    #}
    #consumer_secret = settings.LTI_SECRET
    #received_signature = 'signature_from_request'
    #is_valid = validate_oauth_signature(request_method, base_url, params, consumer_secret, token_secret, received_signature)



def create_oauth_signature(http_method, base_url, params, consumer_secret, token_secret=''):
    def percent_encode(s):
        return urllib.parse.quote(s, safe='')
    def create_signature_base_string(http_method, base_url, params):
        encoded_base_url = percent_encode(base_url)
        sorted_params = ((percent_encode(k), percent_encode(v)) for k, v in params.items() if not k == 'oauth_signature')
        normalized_params = '&'.join(f'{k}={v}' for k, v in sorted_params)
        encoded_params = percent_encode(normalized_params)
        return f'{http_method.upper()}&{encoded_base_url}&{encoded_params}'

    def create_signing_key(consumer_secret, token_secret=''):
        return f'{percent_encode(consumer_secret)}&{percent_encode(token_secret)}'

    signature_base_string = create_signature_base_string(http_method, base_url, params)
    #logger.error(f"SIGNATURE_BASE_STRING {signature_base_string}")
    signing_key = create_signing_key(consumer_secret, token_secret)
    hashed = hmac.new(signing_key.encode(), signature_base_string.encode(), hashlib.sha1)
    signature = base64.b64encode(hashed.digest()).decode()
    return signature



def load_session_variables( request , *args, **kwargs ):
    #logger.error(f"LOAD SESSION_VARIABLES {args} {kwargs} ")
    if request.data :
        params = {};
        for key in ['oauth_consumer_key','oauth_nonce','oauth_timestamp','oauth_signature_method','oauth_version','lti_message_type','lti_version','resource_link_id' ]:
            params[key] = request.data.get(key,None)
        validate_oauth_signature('POST', "https://www.openta.se", params ,settings.LTI_SECRET )
        t = str( int(  time.time() )).encode() ;
        bt = base64.b64encode(t)
        #logger.error(f"T = {t}")
        #logger.error(f"BT = {bt}")
        data = request.data
        print(f"LOAD_SESSION_VARIABLES DATA = {data}")
        #data_ = {
        #    'lti_message_type': 'basic-lti-launch-request',
        #    'lti_version': 'LTI-1p0',
	    #    'subdomain': 'ffm516-2024',
        #    'resource_link_id': 'resourceLinkId',
	    #    'custom_canvas_login_id': 'ulf',
	    #    'lis_person_name_contact_email_primary': 'ulf@chalmers.se',
	    #    'roles': 'Instructor,ContentDeveloper,TeachingAssistant',
	    #    'resource_link_title': 'ffm516-2024',
        #    'oauth_consumer_key': '889d570f472',
        #    'oauth_nonce': bt.strip() ,
        #    'oauth_signature_method': 'HMAC-SHA1',
        #    'oauth_timestamp': t,
        #    'oauth_version': '1.0'
        #};



        #odata = {
        #    'lti_message_type': 'basic-lti-launch-request',
        #    'lti_version': 'LTI-1p0',
        #    'subdomain': 'ffm516-2024',
        #    'resource_link_id': 'resourceLinkId',
	    #    'custom_canvas_login_id': 'ulf',
	    #    'lis_person_name_contact_email_primary': 'ulf@chalmers.se',
        #    'roles': 'Instructor,ContentDeveloper,TeachingAssistant',
	    #    'resource_link_title': 'ffm516-2024',
        #    'oauth_consumer_key': '889d570f472',
        #    'oauth_nonce': bt.strip() ,
        #    'oauth_signature_method': 'HMAC-SHA1',
        #    'oauth_timestamp': t,
        #    'oauth_version': '1.0'
        #};
        #logger.error(f"DATA EXISTS {request.data}")
        #logger.error(f"DATA_ = {data_}")
        #timestamp = data_['oauth_timestamp']
        client_key = request.data.get('oauth_consumer_key',None)
        filter_key = request.data.get('filter_key',None)
        client_signature = request.data.get('oauth_signature',None)
        client_timestamp = request.data.get('oauth_timestamp',None)
        client_key_ok =  client_key  == settings.LTI_KEY 
        #logger.error(f"OK CLIENT KEY?  { client_key_ok }")
        #logger.error(f"OK TIMESTAMP ? {timestamp}=={ client_timestamp} ")
        method = 'POST'
        url = "http://localhost:8000"
        consumer_key = settings.LTI_KEY
        consumer_secret = settings.LTI_SECRET
        signature = create_oauth_signature(method, url, params , consumer_secret ) # , consumer_secret)
        #signature_ = create_oauth_signature(method, url, data_, consumer_secret) # , consumer_secret)
        #osignature = create_oauth_signature(method, url, odata, consumer_secret) # , consumer_secret)
        #logger.error(f"SIGNATURES = {client_signature }  {signature} {signature_} {osignature} ")
        
    pk = kwargs.get('pk',None)
    request.session['is_staff'] = False
    category_selected = args[1].get('category_selected',request.session.get('category_selected',None ) )
    if request.user and request.user.username  :
        username = request.user.username
        request.session['username'] = username
        request.session['is_staff'] = request.user.is_staff
        request.session['is_authenticated'] = True
    if category_selected == None :
        category_selected = Category.objects.all()[0].pk
    if not pk == None :
        category_selected = Post.objects.get(pk=pk).category.pk;
    #for key in request.session.keys() :
    #    logger.error(f" {key} {request.session[key]}")
    if request.method == 'POST' :
        author_type = get_author_type( request )
        data = dict( request.POST )
        logger.error(f"DATA = {data}")
        username = data.get('custom_canvas_login_id', [''])[0]
        subdomain = data.get('resource_link_title', [''])[0]
        request.session['username'] = username
        request.session['is_authenticated'] = not username ==  ''
        request.session['subdomain'] = subdomain
        request.session['category_selected'] =  category_selected
        request.session['filter_key'] = data.get('filter_key',[''])[0]
        request.session['return_url'] = data.get('return_url',[''])[0];
        request.session['referer']   = data.get('referer',["REFERER_IN_LOAD_SESSION_VARIABLES_NOT_DEFINED"])[0]
        
    else :
        if 'username' in request.session :
            username = request.session['username']
        else :
            username = request.GET.get('user',request.user.username)
        request.session['username'] = username
        request.session['is_authenticated'] = not username == ''
        request.session['category_selected'] =  category_selected
    for v in request.session.keys():
        logger.error(f"{v} = {request.session[v]}")
    category_selected = request.session['category_selected']
    author_type = request.session.get('author_type',0)
    #logger.error(f"ARGS = {args}")
    #logger.error(f"KWARGS = {kwargs}")
    #logger.error(f"DATA = {request.data}")
    #logger.error(f"CATEGORY_SELECTED = {category_selected}")
    #logger.error(f"AUTHORTYPE = {author_type}")
    #request.session['referer'] = 'REFERER_FROM_LOAD_SESSION_VARIABLES' 
    return True


def get_author_type( request ):
    roles  =  request.POST.get('lti_roles',request.POST.get('roles',['Anonymous']) )
    #print(f"ROLES = {roles}")
    t = Post.AuthorType.ANONYMOUS
    td = 'Anonymous'
    if 'Student' in roles  or 'Learner' in roles :
        t = Post.AuthorType.STUDENT
        td = 'Student'
    if 'Teacher' in roles or 'Examiner' in roles or 'ContentDeveloper' in roles or 'TeachingAssistant' in roles  or 'Instructor' in roles:
        t = Post.AuthorType.TEACHER
        td = 'Teacher'
    if request.user.is_staff :
        t = Post.AuthorType.STAFF
        td = 'Admin'
    #print(f"T = {t}")
    request.session['author_type'] = t
    request.session['author_type_display'] = td
    return t


def get_username( request ):
    return request.session.get('username',request.user.username)

