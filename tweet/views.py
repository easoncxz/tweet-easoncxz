#from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse

from rauth import OAuth1Service

from constants import service_name, consumer_key, consumer_secret, request_token_url, access_token_url, authorize_url, base_url

from tweet.models import AuthInfo

def index(request):
    """Show log in page, or show home page."""
    if 'request_token' in request.COOKIES:
        # user already logged in: show home page
        request_token = request.COOKIES.get('request_token')
        info = AuthInfo.objects.get(request_token=request_token)
        access_token = info.access_token
        access_token_secret = info.access_token_secret
        import json
        twitter = _get_twitter()
        session = twitter.get_session((access_token, access_token_secret))
        r = session.get('account/verify_credentials.json')
        j = json.loads(r.content)
        return HttpResponse('<pre>Hello, ' + j['screen_name'] + '!</pre>')
    else:
        # user not logged in: show log in page
        context = RequestContext(
            request,{'authorize_url': reverse('tweet:auth')})
        template = loader.get_template('tweet/index.html')
        return HttpResponse(template.render(context))

def auth(request):
    """Ask Twitter for an authorization url and redirect the user there."""
    twitter = _get_twitter()
    request_token, request_token_secret = twitter.get_request_token() 
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

def _get_twitter():
    return OAuth1Service(
        name=service_name,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        request_token_url=request_token_url,
        access_token_url=access_token_url,
        authorize_url=authorize_url,
        base_url=base_url)
