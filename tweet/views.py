#from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse

from rauth import OAuth1Service

from constants import service_name, consumer_key, consumer_secret, request_token_url, access_token_url, authorize_url, base_url

from tweet.models import OneRequestToken, OneAccessToken

def index(request):
    context = RequestContext(
        request,{'authorize_url': reverse('tweet:auth')})
    template = loader.get_template('tweet/index.html')
    return HttpResponse(template.render(context))

def auth(request):
    # work out an authorization url and point the user there
    twitter = _get_twitter()
    rt, rts = twitter.get_request_token() 
    OneRequestToken(
        request_token=rt,
        request_token_secret=rts).save()
    return HttpResponseRedirect(twitter.get_authorize_url(rt))

def callback(request):
    # get stuff twitter passed back via the user
    try:
        oauth_token = request.GET['oauth_token']
        oauth_verifier = request.GET['oauth_verifier']
    except KeyError:
        return HttpResponse("You need to give me the fucking oauth token and verifier.")

    # get previously saved stuff
    twitter = _get_twitter()
    t = OneRequestToken.objects.get(request_token=oauth_token)
    rt = t.request_token
    rts = t.request_token_secret
    t = None

    # ask twitter for the access token
    at, ats = twitter.get_access_token(
        rt,
        rts,
        method='POST',
        data={'oauth_verifier': oauth_verifier})
    OneAccessToken(
        access_token=at,
        access_token_secret=ats).save()
    return HttpResponseRedirect(reverse('tweet:home') + "?access_token=" + str(at))

def home(request):
    return HttpResponse("Your access token is:<br />" + request.GET['access_token'] + "<br />But we ain't got nothing for you.")

def _get_twitter():
    return OAuth1Service(
        name=service_name,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        request_token_url=request_token_url,
        access_token_url=access_token_url,
        authorize_url=authorize_url,
        base_url=base_url)
