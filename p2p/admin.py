from django.contrib import admin
from .models import * 


admin.site.register(PaymentMethod)
admin.site.register(Currency)
admin.site.register(SellOffer)
admin.site.register(BuyOffer)