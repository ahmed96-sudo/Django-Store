import os
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .forms import ContactForm, LoginForm, RegisterForm, ReviewForm
from .models import Product, Categories, Profile, CartItem, Order, OrderItem, Review, Contact, Newsletter, Wishlist, Payment
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib import messages

from store import forms

# Create your views here.

class HomeView(TemplateView, FormView):
    template_name = 'store/home.html'
    form_class = ContactForm
    success_url = reverse_lazy('home')

    # Handle form validation errors
    def form_invalid(self, form):
        messages.error(self.request, 'There was an error submitting your message. Please try again.')
        return super().form_invalid(form)

    # Send email on successful form submission
    def form_valid(self, form):
        form.save()
        from_who = form.cleaned_data['email']
        mail_subject = f"New Contact Message from {form.cleaned_data['name']}"
        message = f"Name: {form.cleaned_data['name']}\nEmail: {from_who}\nMessage:\n{form.cleaned_data['message']}"
        send_mail(mail_subject, message, from_who, [os.getenv('CONTACT_EMAIL')])
        messages.success(self.request, 'Your message has been sent successfully.')
        return super().form_valid(form)

    # Show latest 8 products on home page
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.order_by('created_at')[:8]  # Show only the latest 8 products on the home page
        return context

class ContactView(FormView):
    model = Contact
    template_name = 'store/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('thanks')
    
    # Handle form validation errors
    def form_invalid(self, form):
        messages.error(self.request, 'There was an error submitting your message. Please try again.')
        return super().form_invalid(form)

    # Send email on successful form submission
    def form_valid(self, form):
        form.save()
        from_who = form.cleaned_data['email']
        mail_subject = f"New Contact Message from {form.cleaned_data['name']}"
        message = f"Name: {form.cleaned_data['name']}\nEmail: {from_who}\nMessage:\n{form.cleaned_data['message']}"
        send_mail(mail_subject, message, from_who, [os.getenv('CONTACT_EMAIL')])
        return super().form_valid(form)

class ThanksView(TemplateView):
    template_name = 'store/thanks.html'

class ProductDetailView(DetailView, CreateView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'data'
    form_class = ReviewForm

    def get_success_url(self, **kwargs):
        return reverse_lazy('product_detail', kwargs={'pk': self.kwargs['pk']})

    # Increase product views count
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views += 1
        obj.save()
        return obj

    # Handle form validation errors
    def form_invalid(self, form):
        messages.error(self.request, 'There was an error submitting your review. Please try again.')
        return super().form_invalid(form)

    # Handle review submission
    def form_valid(self, form):
        review = form.save(commit=False)
        review.product = self.get_object()
        review.user = self.request.user
        review.save()
        messages.success(self.request, 'Your review has been submitted successfully.')
        return super().form_valid(form)

    # Add reviews to context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(product=self.object)
        return context

class ProductListView(ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    paginate_by = 2  # Show 2 products per page
    queryset = Product.objects.all().order_by('created_at')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categories.objects.all()
        return context

class LoginCustomView(LoginView):
    template_name = 'store/login.html'
    authentication_form = LoginForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if User.objects.filter(username=username).exists() and authenticate(username=username, password=password) is None:
            form.add_error(None, 'Invalid username or password')
            messages.error(self.request, 'Invalid username or password. Please try again.')
            return self.form_invalid(form)
        elif user is not None:
            login(self.request, user)
            messages.success(self.request, 'You have logged in successfully.')
            return super().form_valid(form)
        else:
            form.add_error(None, 'Invalid username or password')
            messages.error(self.request, 'Invalid username or password. Please try again.')
            return self.form_invalid(form)

class LogoutCustomView(LogoutView):
    template_name = None
    next_page = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)

class RegisterView(FormView):
    template_name = 'store/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        firstname = form.cleaned_data.get('first_name')
        lastname = form.cleaned_data.get('last_name')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            form.add_error(None, 'Username or email already exists')
            messages.error(self.request, 'Username or email already exists. Please choose a different username or email.')
            return self.form_invalid(form)
        
        user = User.objects.create_user(username=username, email=email, password=password, first_name=firstname, last_name=lastname)
        Profile.objects.create(user=user)
        messages.success(self.request, 'Your account has been created successfully. You can now log in.')
        return super().form_valid(form)

# class MailErrorView(TemplateView):
#     template_name = 'store/mailerror.html'

# @login_required
# def cart(request):
#     cart_items = CartItem.objects.filter(user=request.user)
#     total_price = sum(item.product.price * item.quantity for item in cart_items)
#     return render(request, 'store/cart.html', {'cart_items': cart_items, 'total_price': total_price})

# @login_required
# def checkout(request):
#     cart_items = CartItem.objects.filter(user=request.user)
#     total_price = sum(item.product.price * item.quantity for item in cart_items)
#     return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total_price': total_price})

# @login_required
# def order_confirmation(request):
#     cart_items = CartItem.objects.filter(user=request.user)
#     total_price = sum(item.product.price * item.quantity for item in cart_items)
#     return render(request, 'store/order_confirmation.html', {'cart_items': cart_items, 'total_price': total_price})

# class ProfileView(TemplateView):
#     template_name = 'store/profile.html'
#     context_object_name = 'profile'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['profile'] = Profile.objects.get(user=self.request.user)
#         return context
