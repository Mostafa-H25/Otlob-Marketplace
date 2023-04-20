from django.views import generic
from django.views.generic.edit import FormMixin

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from django.utils.text import slugify
from django.urls import reverse_lazy

from core.models import Item
from .models import Profile, Address, Conversation, Message
from . import forms


class ConversationView(LoginRequiredMixin, FormMixin, generic.DetailView):
    model = Conversation
    form_class = forms.ConversationForm
    template_name = "user/conversation.html"

    def get_context_data(self, **kwargs):
        context = super(ConversationView, self).get_context_data(**kwargs)
        context['form'] = forms.ConversationForm()
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            msg = Message.objects.create(
                conversation=self.object, content=form.cleaned_data['content'], created_by=self.request.user)
            msg.save()
            return redirect('auth:conversation', pk=self.object.uuid)


@login_required()
def create_conversation(request, slug):
    receiver = Profile.objects.get(slug=slug)
    receiver = receiver.user
    sender = User.objects.get(id=request.user.id)

    if Conversation.objects.filter(members=sender).filter(members=receiver).exists():

        conversation = Conversation.objects.filter(
            members=sender).filter(members=receiver).first()

    else:
        conversation = Conversation.objects.create()
        conversation.members.add(receiver)
        conversation.members.add(sender)
        conversation.save()
        conversation = Conversation.objects.filter(
            members=sender).filter(members=receiver).first()

    return redirect('auth:conversation', pk=conversation.uuid)


class InboxView(LoginRequiredMixin, generic.ListView):
    model = Conversation
    template_name = 'user/inbox.html'

    def get_queryset(self):
        queryset = super(InboxView, self).get_queryset()
        queryset = Conversation.objects.filter(members=self.request.user)
        return queryset


class UserProfileView(LoginRequiredMixin, generic.DetailView):
    model = Profile
    template_name = 'user/profile_info.html'

    def get_context_data(self, **kwargs):
        slug = self.kwargs['slug']
        profile = Profile.objects.get(slug=slug)
        user = profile.user
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context['address'] = Address.objects.filter(
            user=user, address_type='B').first()
        context['items'] = Item.objects.filter(
            seller=user)
        return context


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = User
    template_name = "user/user_confirm_delete.html"
    success_url = reverse_lazy('core:home')

    def test_func(self):
        self.object = self.get_object()
        if self.request.user == self.object:
            return True
        return False


@login_required()
def profile_update(request, slug):
    profile_ins = get_object_or_404(Profile, slug=slug)
    address_ins = Address.objects.filter(
        user=request.user, address_type='B').first()
    if request.method == 'POST':
        profile = forms.ProfileForm(
            request.POST, request.FILES, instance=profile_ins)
        address = forms.AddressForm(request.POST, instance=address_ins)

        if profile.is_valid() and address.is_valid():
            profile.save()

            address = Address(
                user=request.user,
                apartment=address.cleaned_data['apartment'],
                building=address.cleaned_data['building'],
                street=address.cleaned_data['street'],
                district=address.cleaned_data['district'],
                city=address.cleaned_data['city'],
                country=address.cleaned_data['country'],
                zip=address.cleaned_data['zip']
            )
            address.save()
            return redirect('auth:profile', slug)
    else:
        profile = forms.ProfileForm(instance=(profile_ins))
        address = forms.AddressForm(instance=(address_ins))

    return render(request, 'user/profile.html', {'profile': profile, 'address': address})


class UpdatedLoginView(LoginView):
    template_name = 'user/login.html'
    form_class = forms.LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data['remember_me']
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super(UpdatedLoginView, self).form_valid(form)


def register(request):
    if request.method == 'POST':
        register = forms.RegisterForm(request.POST)
        profile = forms.ProfileForm(
            request.POST, request.FILES)
        address = forms.AddressForm(request.POST)

        if register.is_valid() and address.is_valid() and profile.is_valid():
            register.save()

            user = User.objects.get(username=register.cleaned_data['username'])

            profile_ins = Profile(
                user=user,
                phone_number=profile.cleaned_data['phone_number'],
                birthday=profile.cleaned_data['birthday'],
                image=profile.cleaned_data['image'],
            )
            profile_ins.save()

            address_ins = Address(
                user=user,
                apartment=address.cleaned_data['apartment'],
                building=address.cleaned_data['building'],
                street=address.cleaned_data['street'],
                district=address.cleaned_data['district'],
                city=address.cleaned_data['city'],
                country=address.cleaned_data['country'],
                zip=address.cleaned_data['zip']
            )
            address_ins.save()

            messages.success(
                request, f'Your account has been created! You are now able to login.')
            return redirect('auth:login')
    else:
        register = forms.RegisterForm()
        profile = forms.ProfileForm()
        address = forms.AddressForm()
    return render(request, 'user/register.html', {'register': register, 'profile': profile, 'address': address})
