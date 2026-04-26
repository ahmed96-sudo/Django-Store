from django.db.models import Model, Index, EmailField, CharField, DecimalField, ForeignKey, DateTimeField, IntegerField, OneToOneField, TextField, CASCADE, PositiveIntegerField
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Product(Model):
    name = CharField(max_length=255)
    description = TextField()
    price = DecimalField(max_digits=10, decimal_places=2)
    category = ForeignKey('Categories', on_delete=CASCADE, related_name='products')
    stock = PositiveIntegerField()
    views = PositiveIntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Categories(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name

class Profile(Model):
    user = OneToOneField(User, on_delete=CASCADE)
    address1 = CharField(max_length=255, blank=True)
    address2 = CharField(max_length=255, blank=True)
    city = CharField(max_length=255, blank=True)
    state = CharField(max_length=255, blank=True)
    zip_code = CharField(max_length=20, blank=True)
    country = CharField(max_length=255, blank=True)

    def __str__(self):
        return (f"Profile for {self.user.first_name} {self.user.last_name}")

class CartItem(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    product = ForeignKey(Product, on_delete=CASCADE)
    quantity = PositiveIntegerField(default=1)
    itemprice = DecimalField(max_digits=10, decimal_places=2, default=0)
    # expiry_date = DateTimeField(default=timezone.now() + timezone.timedelta(hours=1))
    
    class Meta:
        indexes = [
            Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.quantity} of {self.product.name} for {self.user.first_name} {self.user.last_name}"

class Order(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order for {self.user.first_name} {self.user.last_name} at {self.created_at}"

class OrderItem(Model):
    order = ForeignKey(Order, on_delete=CASCADE)
    product = ForeignKey(Product, on_delete=CASCADE)
    quantity = PositiveIntegerField(default=1)
    price = DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} for order {self.order.id}"

class Review(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    product = ForeignKey(Product, on_delete=CASCADE)
    rating = PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = TextField()
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.first_name} {self.user.last_name} for {self.product.name}"

class Contact(Model):
    name = CharField(max_length=255)
    email = EmailField(max_length=255)
    message = TextField()
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact from {self.name} at {self.created_at}"

class Newsletter(Model):
    email = EmailField(max_length=255, unique=True)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Newsletter subscription from {self.email} at {self.created_at}"

class Wishlist(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    products = ForeignKey(Product, on_delete=CASCADE)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'products')

    def __str__(self):
        return f"Wishlist for {self.user.first_name} {self.user.last_name} at {self.created_at}"

class Payment(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    order = ForeignKey(Order, on_delete=CASCADE)
    amount = DecimalField(max_digits=10, decimal_places=2)
    payment_method = CharField(max_length=255)
    created_at = DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Payment of {self.amount} for {self.user.first_name} {self.user.last_name} at {self.created_at}"

# class Shipment(Model):
#     order = ForeignKey(Order, on_delete=CASCADE)
#     shipment_method = CharField(max_length=255)
#     tracking_number = CharField(max_length=255)
#     created_at = DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"Shipment for order {self.order.id} with tracking number {self.tracking_number} at {self.created_at}"

# class Discount(Model):
#     code = CharField(max_length=255, unique=True)
#     description = TextField()
#     discount_percentage = DecimalField(max_digits=5, decimal_places=2)
#     created_at = DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"Discount code {self.code} with {self.discount_percentage}% off at {self.created_at}"

