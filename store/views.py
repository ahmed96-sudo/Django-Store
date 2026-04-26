import os
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .forms import ContactForm, LoginForm, RegisterForm, ReviewForm
from .models import Product, Categories, Profile, CartItem, Order, OrderItem, Review, Contact, Newsletter, Wishlist, Payment
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import F
from django.shortcuts import redirect, get_object_or_404


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
        return reverse('product_detail', kwargs={'pk': self.kwargs['pk']})

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

class LoginCustomView(FormView):
    template_name = 'store/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is None:
            form.add_error(None, 'Invalid username or password')
            messages.error(self.request, 'Invalid username or password. Please try again.')
            return self.form_invalid(form)
        
        login(self.request, user)
        messages.success(self.request, 'You have logged in successfully.')
        return super().form_valid(form)

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
        try:
            user = User.objects.create_user(username=username, email=email, password=password, first_name=firstname, last_name=lastname)
        except IntegrityError:
            form.error(None, 'An error occurred while creating your account. Please try again.')
            return self.form_invalid(form)
        Profile.objects.create(user=user)
        messages.success(self.request, 'Your account has been created successfully. You can now log in.')
        return super().form_valid(form)

class CartView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    permission_denied_message = "You must be logged in to view your cart."
    model = CartItem
    template_name = 'store/cart.html'
    context_object_name = 'cart_items'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to view your cart.')
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = self.get_queryset()
        context['total_price'] = sum(item.itemprice for item in cart_items)
        return context

class AddToCartView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')
    permission_denied_message = "You must be logged in to add items to your cart."
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to add items to your cart.')
            return redirect('login')
        if request.method != 'POST':
            messages.error(request, 'Invalid request method.')
            return redirect('product_list')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        product_id = self.request.POST.get('product_id')
        if not product_id:
            messages.error(request, 'Invalid product selection.')
            return redirect('product_list')
        product = get_object_or_404(Product, id=product_id)
        updated_stock = Product.objects.filter(id=product.id, stock__gt=0).update(stock=F('stock') - 1)
        if not updated_stock:
            messages.error(request, 'Sorry, this product is out of stock.')
            return redirect('product_list')
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product, defaults={'quantity': 1, 'itemprice': product.price})
        if not created:
            cart_item.quantity += 1
            cart_item.itemprice += product.price
            cart_item.save()
        
        messages.success(request, f'Added {product.name} to your cart.')
        return redirect('product_list')

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
