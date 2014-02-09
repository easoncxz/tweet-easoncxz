from django.db import models

class OneRequestToken(models.Model):
    request_token = models.CharField(max_length=200)
    request_token_secret = models.CharField(max_length=200)

class OneAccessToken(models.Model):
    access_token = models.CharField(max_length=200)
    access_token_secret = models.CharField(max_length=200)
