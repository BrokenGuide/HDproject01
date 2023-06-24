from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect

from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from ACCOUNTS.models import User

# Modified this import here
from django.contrib.auth import get_user_model

from . import models
from GROUPS_SM.models import Group, GroupMember

class CreateGroup(LoginRequiredMixin, generic.CreateView):
    fields = ('name', 'description') 
    model = Group

class SingleGroup(generic.DetailView):
    model = Group
    template_name = 'groups_sm/group_details.html'

class ListGroups(generic.ListView):
    model = Group

class JoinGroup(LoginRequiredMixin, generic.RedirectView):
    
    def get_redirect_url(self, *args, **kwargs):
        return reverse("groups:single", kwargs={"slug": self.kwargs.get("slug")})

    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group, slug=self.kwargs.get("slug"))
        
        try:
            # Added a way to generate the User instance
            User = get_user_model()
            GroupMember.objects.create(user=self.request.user.user, group=group)

        except IntegrityError:
            messages.warning(self.request, "Warning, already a member of {}".format(group.name))
        else:
            messages.success(self.request, "You are now a member of the {} group.".format(group.name))

        template_name = 'groups_sm/group_details.html'
        return super().get(request, *args, **kwargs)

class LeaveGroup(LoginRequiredMixin, generic.RedirectView):
    
    def get_redirect_url(self, *args, **kwargs):
        return reverse('groups:single', kwargs={'slug': self.kwargs.get('slug')})
    
    def get(self, request, *args, **kwargs):
        try:
            membership = models.GroupMember.objects.filter(
                user=self.request.user,
                group__slug=self.kwargs.get('slug')
            ).get()
        except models.GroupMember.DoesNotExist:
            messages.warning(self.request, 'Sorry you are not in this group')
        else:
            membership.delete()
            messages.success(self.request, 'You have left the group')
        return super().get(request, *args, **kwargs)
