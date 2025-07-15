from django.contrib import admin
from .models import UserProfile, AccountType, Account, Category_type, Category, Transaction, Budget, SavingsGoal, RecurringTransaction


admin.site.register(UserProfile)
admin.site.register(AccountType)
admin.site.register(Account)
admin.site.register(Category_type)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(Budget)
admin.site.register(SavingsGoal)
admin.site.register(RecurringTransaction)