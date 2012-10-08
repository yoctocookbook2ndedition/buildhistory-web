from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class WarningItem(models.Model):
    STATUS_CHOICES = (
        ('N', 'New'),
        ('I', 'Ignored'),
        ('A', 'Action Required'),
        ('R', 'Resolved'),
    )
    created_date = models.DateTimeField('Created')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N')
    status_date = models.DateTimeField('Status Changed', default=datetime.now, editable=False)
    status_user = models.CharField('Status Changed By', max_length=50, blank=True)
    package = models.CharField(max_length=200)
    summary = models.CharField(max_length=200)
    description = models.TextField()
    vcs_rev = models.CharField(max_length=80)
    vcs_link = models.URLField(blank=True)

    def change_status(self, newstatus, username):
        self.status = newstatus
        self.status_date = datetime.now()
        self.status_user = username

    def __unicode__(self):
        return self.summary

class Comment(models.Model):
    warningitem = models.ForeignKey(WarningItem)
    comment = models.TextField()
    date = models.DateTimeField()
    author = models.CharField(max_length=50)

    def __unicode__(self):
        return self.comment

    def author_full_name(self):
        usrs = User.objects.filter(username__exact=self.author)
        if usrs:
            fullname = usrs[0].get_full_name()
            if fullname:
                return fullname
        return self.author