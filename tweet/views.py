from django.shortcuts import render

from rauth import OAuth1Service

import constants

def index(request):
    return render(request, 'tweet/index.html', {'authorize_url': 'http://google.com'})
