from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth import login
from .forms import CustomRegistrationForm

class RegisterView(CreateView):
    form_class = CustomRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Save the user and log them in immediately upon successful registration
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class HomeView(TemplateView):
    template_name = 'accounts/home.html'