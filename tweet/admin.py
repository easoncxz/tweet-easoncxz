from django.contrib import admin

from tweet.models import OneRequestToken, OneAccessToken

admin.site.register(OneRequestToken)
admin.site.register(OneAccessToken)
