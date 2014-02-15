#from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.shortcuts import render

from rauth import OAuth1Service

from constants import service_name, consumer_key, consumer_secret, request_token_url, access_token_url, authorize_url, base_url

from tweet.models import AuthInfo

def index(request):
    """Show log in page, or show home page."""
    if 'request_token' not in request.COOKIES:
        # user not logged in: show log in page
        return login(request)
    else:
        # user already logged in: show home page
        return home(request)

def login(request):
   context = RequestContext(request, None)
   template = loader.get_template('tweet/login.htmldj')
   return HttpResponse(template.render(context))

def home(request):
    # get stuff from storage
    request_token = request.COOKIES.get('request_token')
    info = AuthInfo.objects.get(request_token=request_token)
    access_token = info.access_token
    access_token_secret = info.access_token_secret

    # ask twitter for stuff
    #twitter = _get_twitter()
    #session = twitter.get_session((access_token, access_token_secret))
    #r = session.get('account/verify_credentials.json')
    #import json
    #j = json.loads(r.content)
    from twitter import Api
    from constants import consumer_key, consumer_secret
    api = Api(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token_key=access_token,
        access_token_secret=access_token_secret)
    user = api.VerifyCredentials()
    screen_name = user.GetScreenName()

    # respond to HTTP
    template = loader.get_template('tweet/home.htmldj')
    context = RequestContext(request,
        {
            'user': user,
            'profile_image_url': user.GetProfileImageUrl(),
            'screen_name': user.GetScreenName(),
            'name': user.GetName(),
        })
    return HttpResponse(template.render(context))

def auth(request):
    """Ask Twitter for an authorization url and redirect the user there."""
    twitter = _get_twitter()
    request_token, request_token_secret = twitter.get_request_token(
        # This is in rauth/requests API format for implementing:
        # http://oauth.net/core/1.0a/#auth_step1
        data={
            'oauth_callback': 'http://tweet-easoncxz.herokuapp.com/callback',
        }) 
    info = AuthInfo(
        request_token=request_token,
        request_token_secret=request_token_secret)
    info.save()
    return HttpResponseRedirect(twitter.get_authorize_url(request_token))

def callback(request):
    """Handles control when Twitter passes it back after the user has authorized us."""
    # get stuff twitter passed back via the user
    try:
        oauth_token = request.GET['oauth_token']
        oauth_verifier = request.GET['oauth_verifier']
    except KeyError:
        return HttpResponse("You need to give me the fucking oauth token and verifier.")

    # get previously saved stuff
    twitter = _get_twitter()
    info = AuthInfo.objects.get(request_token=oauth_token)
    request_token = info.request_token
    request_token_secret = info.request_token_secret

    # ask twitter for the access token
    info.access_token, info.access_token_secret = twitter.get_access_token(
        request_token,
        request_token_secret,
        method='POST',
        data={
            'oauth_verifier': oauth_verifier,
        })

    # save stuff
    info.save()

    # respond
    response = HttpResponseRedirect(reverse('tweet:index'))
    response.set_cookie('request_token', request_token)
    return response

def tweet(request):
    # extract info from request
    request_token = request.COOKIES.get('request_token')
    tweet_content = request.POST['tweet_content']

    # read info from storage
    info = AuthInfo.objects.get(request_token=request_token)
    access_token = info.access_token
    access_token_secret = info.access_token_secret

    # tell twitter we're posting an update
    from twitter import Api
    from constants import consumer_key, consumer_secret
    api = Api(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token_key=access_token,
        access_token_secret=access_token_secret)
    status = api.PostUpdate(tweet_content)
    return HttpResponseRedirect(reverse('tweet:success'))

def success(request):
    return render(request, 'tweet/success.htmldj', {})

static_twitter = OAuth1Service(
    name=service_name,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    request_token_url=request_token_url,
    access_token_url=access_token_url,
    authorize_url=authorize_url,
    base_url=base_url)

def _get_twitter():
    return static_twitter
