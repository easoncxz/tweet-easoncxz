from django.db import models

class AuthInfo(models.Model):
    request_token = models.CharField(max_length=200)
    request_token_secret = models.CharField(max_length=200)
    access_token = models.CharField(max_length=200)
    access_token_secret = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.request_token)
