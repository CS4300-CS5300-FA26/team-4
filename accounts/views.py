from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from .forms import CustomRegistrationForm
from movies.models import WatchlistItem


class RegisterView(CreateView):
    form_class = CustomRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        self.object = form.save()
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