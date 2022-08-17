from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse

from .models_utils import find_likes_received_count

# Profile Model

class ProfileManager(models.Manager):
    def get_all_profiles(self, user):
        # All profiles except request's user
        profiles = Profile.objects.all().exclude(user=user)
        return profiles

    def get_my_friends_profiles(self, user):
        users = Profile.objects.get(user=user).friends.all()
        result = [Profile.objects.get(user=friend) for friend in users]
        return result

class Profile(models.Model):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default='No Bio..', max_length=300)
    email = models.EmailField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(default='avatar.png', upload_to='avatars/')
    friends = models.ManyToManyField(User, blank=True, related_name='friends')
    following = models.ManyToManyField(User, blank=True, related_name='following')
    slug = models.SlugField(unique=True, blank=True)
    
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ProfileManager()

    def __str__(self):
        return f"{self.user.username}"

    def get_absolute_url(self):
        return reverse("profiles:profile-detail-view", kwargs={"slug": self.slug})

    # Methods for profile details #

    def get_all_authors_posts(self):
        return self.posts.all()    

    def get_posts_count(self):
        return self.posts.all().count()

    def get_likes_given_count(self):
        # Like model is connected to Profile model via a foreign key,
        # likes given are stored in that Profile model
        likes = self.like_set.all()

        total_liked = likes.count()
        
        return total_liked

    def get_likes_received_count(self):
        posts = self.posts.all()

        total_liked = find_likes_received_count(posts)
        
        return total_liked
        
    ###############################

    def save(self, *args, **kwargs):
        self.slug = str(self.user)
        super().save(*args, **kwargs)

# Relationship Model

class RelationshipManager(models.Manager):
    def invitations_received(self, receiver):
        qs = Relationship.objects.filter(receiver=receiver, status='sent')
        return qs

    def invitations_sent(self, sender):
        qs = Relationship.objects.filter(sender=sender, status='sent')
        return qs

STATUS_CHOICES = (
    ('sent', 'sent'),
    ('accepted', 'accepted')
)

class Relationship(models.Model):
    """
    This model is used to send/receive friend requests
    """
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = RelationshipManager()

    def __str__(self):
        return f"{self.sender} - {self.receiver} - {self.status}"

# Message Model

class Message(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='message_sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='message_receiver')
    content = models.TextField(max_length=200)
    
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if len(str(self.content)) > 50:
            return f"{self.sender} - {str(self.content)[:50].strip()}.."
        return f"{self.sender} - {str(self.content)}"
        