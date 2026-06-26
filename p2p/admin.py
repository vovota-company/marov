from django.contrib import admin
from .models import *


admin.site.register(PaymentMethod)
admin.site.register(MyPaymentMethod)
admin.site.register(Currency)

admin.site.register(SellOffer)
admin.site.register(BuyOffer)

admin.site.register(SellOrder)
admin.site.register(BuyOrder)