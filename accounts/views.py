from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from .forms import CustomRegistrationForm
from movies.models import WatchlistItem
from django.db import IntegrityError, transaction


class RegisterView(CreateView):
    form_class = CustomRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save()
        except IntegrityError as exc: # store error in exc
            cause = getattr(exc, '__cause__', None)
            diag = getattr(cause, 'diag', None)
            constraint_name = getattr(diag, 'constraint_name', None)

            # check if the cause for the error was a duplicate email
            is_duplicate_email = (
                constraint_name == 'unique_auth_user_email_ci'
                or 'unique_auth_user_email_ci' in str(exc)
            )

            if not is_duplicate_email:
                raise # raise the actual error

            form.add_error(
                'email',
                "An account with this email already exists."
            )
            return self.form_invalid(form)

        authenticated_user = authenticate(
            request=self.request,
            username=self.object.username,
            password=form.cleaned_data['password1'],
        )

        if authenticated_user is not None:
            login(self.request, authenticated_user)

        return HttpResponseRedirect(self.get_success_url())


class HomeView(TemplateView):
    template_name = 'accounts/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['watchlist_items'] = (
                WatchlistItem.objects
                .filter(user=self.request.user)
                .select_related('movie')
                .order_by('-added_at')
            )
        else:
            context['watchlist_items'] = WatchlistItem.objects.none()

        return context