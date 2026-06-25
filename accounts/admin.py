from django.contrib import admin
from .models import *


admin.site.register(User)
admin.site.register(Profile)
admin.site.register(UserWallet)
admin.site.register( WalletIndexCounter)
admin.site.register(ApprovalRequest)
admin.site.register(SweepTask)