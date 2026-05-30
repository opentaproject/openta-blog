import hmac
import html
import hashlib
import urllib.parse
import json
from django.conf import settings
from blog.models import Category, Post, Subdomain
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

def percent_encode(value):
    return urllib.parse.quote(str(value), safe='~-._')


def generate_base_string(method, base_url, params):
    encoded_pairs = [
        (percent_encode(key), percent_encode(value))
        for key, value in params.items()
        if key != "oauth_signature" and value is not None
    ]
    normalized_params = "&".join(
        f"{key}={value}" for key, value in sorted(encoded_pairs)
    )
    return "&".join([
        method.upper(),
        percent_encode(base_url),
        percent_encode(normalized_params),
    ])

def validate_oauth_signature(method, base_url, params, consumer_secret, token_secret=None, received_signature=None):
    received_signature = received_signature or params.get("oauth_signature")
    if not received_signature:
        return False
    base_string = generate_base_string(method, base_url, params)
    signing_key = f"{percent_encode(consumer_secret)}&{percent_encode(token_secret or '')}"
    hashed = hmac.new(signing_key.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha1)
    generated_signature = base64.b64encode(hashed.digest()).decode("utf-8")
    return hmac.compare_digest(generated_signature, received_signature)



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
    signing_key = create_signing_key(consumer_secret, token_secret)
    hashed = hmac.new(signing_key.encode(), signature_base_string.encode(), hashlib.sha1)
    signature = base64.b64encode(hashed.digest()).decode()
    return signature



def load_session_variables( request , *args, **kwargs ):
    def reject_lti(reason, detail, **context):
        request.lti_validation_error = {
            "reason": reason,
            "detail": detail,
            "context": context,
        }
        logger.warning("Rejected LTI launch: %s", reason)
        return False

    if request.data :
        params = request.data.dict() if hasattr(request.data, "dict") else dict(request.data)
        client_key = params.get('oauth_consumer_key',None)
        if not settings.DISABLE_LTI_VALIDATION:
            if client_key != settings.LTI_KEY:
                return reject_lti(
                    "Invalid consumer key",
                    "Canvas sent an oauth_consumer_key that does not match LTI_KEY.",
                    received_consumer_key=client_key or "",
                )
            base_url = request.build_absolute_uri(request.path)
            if not validate_oauth_signature('POST', base_url, params, settings.LTI_SECRET):
                return reject_lti(
                    "Invalid OAuth signature",
                    "The OAuth signature did not validate with LTI_SECRET.",
                    signature_base_url=base_url,
                    has_oauth_signature=bool(params.get("oauth_signature")),
                )
        t = str( int(  time.time() )).encode() ;
        bt = base64.b64encode(t)
        #logger.error(f"T = {t}")
        #logger.error(f"BT = {bt}")
        data = request.data
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
        filter_key = request.data.get('filter_key',None)
        client_signature = request.data.get('oauth_signature',None)
        client_timestamp = request.data.get('oauth_timestamp',None)
        client_key_ok = True
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
        #category_selected = Category.objects.all()[0].pk
        cat , _  =  Category.objects.get_or_create(name='Unread')
        category_selected = cat.pk
    if not pk == None :
        category_selected = Post.objects.get(pk=pk).category.pk;
    if request.method == 'POST' :
        author_type = get_author_type( request )
        course_pk = data.get('course_pk',None)
        data = dict( request.POST )
        server = data.get('server',['NONE'] )[0]
        request.session['server'] = server
        username = data.get('custom_canvas_login_id', [''])[0]
        subdomain = data.get('resource_link_title', [''])[0]
        request.session['username'] = username
        request.session['is_authenticated'] = not username ==  ''
        request.session['subdomain'] = subdomain
        if not subdomain == ''  :
            subdomain_ , _ = Subdomain.objects.get_or_create(
                name=subdomain,
                defaults={"hidden": True},
            )
            category_selected , new  = Category.objects.get_or_create(name=subdomain,subdomain=subdomain_)
            if new :
                category_selected.restricted = True
                category_selected.save();
            category_selected = category_selected.pk
        request.session['category_selected'] =  category_selected
        fkey =  html.unescape(  data.get('filter_key',[''])[0]   )
        request.session['course_pk'] = course_pk
        request.session['filter_key'] = fkey
        request.session['filter_key_selected'] = data.get('filter_key',[''])[0]
        request.session['referer']   = data.get('referer',[request.META.get('HTTP_REFERER')])
        if 'launch_presentation_return_url' in request.POST :
            launch_presentation_return_url = request.POST.get('launch_presentation_return_url')
            return_url = '/'.join( launch_presentation_return_url.split('/')[0:5] ) + '/'
            request.session['return_url'] = return_url
            request.session['referer'] = return_url
        else :
            request.session['return_url'] = data.get('return_url',[''])[0];
            request.session['referer']   = data.get('referer',[''])[0]
        request.session['filter_title'] = data.get('filter_title',[''])[0]
        uri = str(  request.build_absolute_uri()  )
        if 'home' in uri :
            request.session['filter_key']  = ''
        #    request.session['category_selected'] = None


        
    else :
        if 'username' in request.session :
            username = request.session['username']
        else :
            username = request.GET.get('user',request.user.username)
        request.session['username'] = username
        request.session['is_authenticated'] = not username == ''
        request.session['category_selected'] =  category_selected
    #for v in request.session.keys():
    #    logger.error(f"{v} = {request.session[v]}")
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
    if 'author_type' in request.session :
        return request.session['author_type']
    roles  =  request.POST.get('roles', request.POST.get('lti_roles', 'Anonymous') )
    t = Post.AuthorType.ANONYMOUS
    td = 'Anonymous'
    if 'Student' in roles  or 'Learner' in roles :
        t = Post.AuthorType.STUDENT
        td = 'Student'
    if 'Teacher' in roles or 'Examiner' in roles or 'ContentDeveloper' in roles or 'TeachingAssistant' in roles  or 'Instructor' in roles or 'Admin' in roles  or 'Author' in roles :
        t = Post.AuthorType.TEACHER
        td = 'Teacher'
    if request.user.is_staff :
        t = Post.AuthorType.STAFF
        td = 'Admin'
    request.session['author_type'] = t
    request.session['author_type_display'] = td
    return t


def get_username( request ):
    return request.session.get('username',request.user.username)
