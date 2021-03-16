"""All views related to profile user's action such as login logout etc."""
from django.shortcuts import render, redirect
from django.views.generic import DetailView, ListView, FormView, UpdateView
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from .forms import SignUpForm, UpdateProfileForm
from .models import Profile
from .token_generator import account_activation_token


class UserProfileView(DetailView):
    """
    Show details of profile page.

    **Arguments**

    ``username: str``
        Username of profile.

    **Context**

    ``userprof``
        Related :model:`switchdeck.Profile` instances.
    ``keep_list``
        List of profile's :model:`switchdeck/Lot` instances marked as
        ``keep`` and ``sell``.
    ``wish_list``
        List of profile's :model:`switchdeck/Lot` instances marked as
        ``wish`` and ``buy``.
    ``sell_list``
        List of profile's :model:`switchdeck/Lot` instances marked as
        ``sell``.
    ``buy_list``
        List of profile's :model:`switchdeck/Lot` instances marked as
        ``buy``.

    **Template**

    :template:`account/profile_detail.html`
    """

    model = get_user_model()
    # search in db by 'username' field and from 'username' kwarg
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'users/profile_detail.html'

    def get_context_data(self, **kwargs):
        """Insert additional information into context."""
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
    """Must to redirect on session user profile page. Rarely use."""
    return redirect(request.user.profile)


class SignUpView(FormView):
    """
    View there anonymous user can sign up (registrate).

    **Context**

    ``from``
        Form using for registration.

    **Template**

    :template:`account/signup.html`
    """

    template_name = 'account/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('account:need_confirmation')

    def form_valid(self, form):
        """Save user profile in case of valid form."""
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        profile = Profile.objects.create(user=user)
        profile.save()

        send_mail(
            subject="SwitchDeck: Account Verification",
            message=render_to_string(
                'account/email_confirm_email.html', {
                    'user': user,
                    'domain': get_current_site(self.request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user)}),
            from_email="verify@switchdeck.net",
            recipient_list=[form.cleaned_data['email']]
        )
        return super().form_valid(form)


def activate(request, uid, token):
    """Profile activation view."""
    try:
        uid = force_text(urlsafe_base64_decode(uid))
        user = get_user_model().objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError,
           get_user_model().DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'account/confirmation_ok.html')
    else:
        return render(request, 'account/confirmation_error.html')


class ProfileListView(ListView):
    """
    Show the list of all available Profiles.

    **Context**

    ``objects``
        List of all available :model:`switchdeck.Profile` instances.

    **Template**

    :template:`account/profile_list.html`
    """

    model = Profile


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    """
    Update the info about Porfile and related User.

    **Context**

    ``object``
        Related :model:`switchdeck.Profile` instance.
    ``form``
        Form to update.

    **Template**
    :template:`account/user_form.html`
    """

    model = Profile
    form_class = UpdateProfileForm
    template_name = 'account/user_form.html'

    def get_object(self):
        """Return requested user's `Profile` object."""
        return self.request.user.profile

    def get_initial(self):
        """Prepare form, fill it with needed information."""
        initial = super().get_initial()
        initial['first_name'] = self.object.user.first_name
        initial['last_name'] = self.object.user.last_name
        return initial

    def form_valid(self, form):
        """Save user's `Profile` info in case of valid form."""
        userprof = self.object.user
        userprof.first_name = form.cleaned_data['first_name']
        userprof.last_name = form.cleaned_data['last_name']
        userprof.save()
        return super().form_valid(form)
