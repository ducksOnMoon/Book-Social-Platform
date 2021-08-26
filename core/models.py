from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail

import random
import string
from django.utils import timezone
from PIL import Image

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, default='defaults/avatar.png')
    SOCIAL_MEDIA_CHOICES = (
        ('facebook', 'Facebook'), # TODO: Delete Facbook and LinkedIn 
        ('twitter', 'Twitter'),   # from social media choices
        ('linkedin', 'Linkedin'), # only Twitter Account.
    )
    social_media_username = models.CharField(max_length=255, blank=True, choices=SOCIAL_MEDIA_CHOICES)
    social_media_link = models.URLField(blank=True)

    followers = models.ManyToManyField(User, related_name='followers', blank=True)
    following = models.ManyToManyField(User, related_name='following', blank=True)

    # readed_books = models.ManyToManyField('Book', related_name='readed_books', blank=True) 

    def follow(self, user):
        if user not in self.following.all() and user.user != self.user:
            self.following.add(user.user)
            user.followers.add(self.user)
            return True
        return False
    
    def unfollow(self, user):
        if user.user in self.following.all() and user.user != self.user:
            self.following.remove(user.user)
            user.followers.remove(self.user)
            return True
        return False
    
    def save(self, *args, **kwargs):
        super(UserProfile, self).save(*args, **kwargs)
        # Resize the image to a square
        if self.avatar:
            img = Image.open(self.avatar)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)

    def __str__(self):
        return self.user.username


class ConfirmCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(
        max_length=255, 
        unique=True,
        default=''.join(random.choice(string.digits) for _ in range(6))
    )
    
    expires = models.DateTimeField(default=timezone.now() + timezone.timedelta(minutes=10))

    def __str__(self):
        return self.user.username

    def check_confirm_code(self, code):
        if self.code == code and self.expires > timezone.now():
            return True
        return False

    def send_confirm_code_to_email(self):
        send_mail(
            'Confirm Code', 
            'Your confirm code is ' + self.code, 
            settings.EMAIL_HOST_USER, 
            [self.user.email], 
            fail_silently=False
        )
