#from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse

from rauth import OAuth1Service

from constants import service_name, consumer_key, consumer_secret, request_token_url, access_token_url, authorize_url, base_url

from tweet.models import OneRequestToken, OneAccessToken

def index(request):
    access_token = ''
    if 'access_token' in request.COOKIES:
        access_token = request.COOKIES.get('access_token')
        return HttpResponseRedirect(reverse('tweet:home') + "?access_token=" + access_token)
    else:
        context = RequestContext(
            request,{'authorize_url': reverse('tweet:auth')})
        template = loader.get_template('tweet/index.html')
        return HttpResponse(template.render(context))

def auth(request):
    # work out an authorization url and point the user there
    twitter = _get_twitter()
    rt, rts = twitter.get_request_token() 
    if len(OneRequestToken.objects.filter(request_token=rt)) == 0:
        OneRequestToken(
            request_token=rt,
            request_token_secret=rts).save()
    else:
        t = OneRequestToken.objects.get(request_token=rt)
        t.request_token_secret = rts
        t.save()
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
        data={
            'oauth_verifier': oauth_verifier,
            'callback_url': 'http://tweet-easoncxz.herokuapp.com/callback',
        })
    if len(OneAccessToken.objects.filter(access_token=at)) == 0:
        OneAccessToken(
            access_token=at,
            access_token_secret=ats).save()
    else:
        t = OneAccessToken.objects.get(access_token=at)
        t.access_token_secret = ats
        t.save()
    response = HttpResponseRedirect(reverse('tweet:home') + "?access_token=" + at)
    response.set_cookie('access_token', at)
    return response

def home(request):
    if ('access_token' not in request.GET) or (request.GET['access_token'] not in [t.access_token for t in OneAccessToken.objects.filter(access_token=request.GET['access_token'])]):
        # Should remove that cookie now
        return HttpResponseRedirect(reverse('tweet:index'))
    else:
        at =  request.GET['access_token']
        t = OneAccessToken.objects.get(access_token=at)
        ats = t.access_token_secret
        twitter = _get_twitter()
        session = twitter.get_session((at, ats))
        r = session.get('account/verify_credentials.json')
        assert r.status_code == 200, 'twitter didn\'t give stuff back properly'
        from pprint import pformat
        import json
        j = json.loads(r.content)
        response_text = pformat(j)
        return HttpResponse('<pre>' + response_text + '</pre>')

def _get_twitter():
    return OAuth1Service(
        name=service_name,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        request_token_url=request_token_url,
        access_token_url=access_token_url,
        authorize_url=authorize_url,
        base_url=base_url)
