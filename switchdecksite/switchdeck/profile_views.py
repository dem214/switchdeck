from django.shortcuts import render, redirect
from django.views.generic import DetailView, ListView, CreateView, FormView, \
UpdateView
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site

from .forms import SignUpForm
from .models import Profile
from .token_generator import account_activation_token

class UserProfileView(DetailView):
    """Class view represents profile page"""
    model = get_user_model()
    #search in db by 'username' field and from 'username' kwarg
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'registration/profile.html'
    context_object_name = 'userprof'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        same_user = (self.object == self.request.user)
        context['keep_list'] = self.object.profile.keep_list(
            with_inactive=same_user)
        context['wish_list'] = self.object.profile.wish_list(
            with_inactive=same_user)
        context['sell_list'] = self.object.profile.sell_list(
            with_inactive=same_user)
        context['buy_list'] = self.object.profile.buy_list(
            with_inactive=same_user)
        return context


@login_required
def profile_redirect(request):
    """Must to redirect on session user profile page. Rarely use"""
    return redirect(request.user.profile)


class SignUpView(FormView):
    template_name = 'registration/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('need_confirmation')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        profile = Profile.objects.create(user=user)
        profile.save()

        send_mail(
            subject="SwitchDeck: Account Verification",
            message = render_to_string(
                'registration/email_confirm_email.html',
                {
                    'user': user,
                    'domain': get_current_site(self.request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user)
                }
            ),
            from_email="verify@switchdeck.net",
            recipient_list = [form.cleaned_data['email'],]
        )

        token = account_activation_token.make_token(user)

        return super().form_valid(form)


def activate(request, uid, token):
    try:
        uid = force_text(urlsafe_base64_decode(uid))
        user = get_user_model().objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'registration/confirmation_ok.html')
    else:
        return render(request, 'registration/confirmation_error.html')

class UsersListView(ListView):
    model = Profile
    template_name = 'registration/profile_list.html'

class UpdateProfileView(UpdateView):
    model = Profile
    slug_field = 'user__username'
    slug_url_kwarg = 'username'
    fields = ['place']
    template_name = 'registration/user_form.html'
