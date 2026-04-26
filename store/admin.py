from django.contrib import admin

from store.models import CartItem, Categories, Contact, Newsletter, Order, OrderItem, Payment, Product, Profile, Review, Wishlist

# Register your models here.
admin.site.register(Product)
admin.site.register(Categories)
admin.site.register(Profile)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Contact)
admin.site.register(Newsletter)
admin.site.register(Wishlist)
admin.site.register(Payment)