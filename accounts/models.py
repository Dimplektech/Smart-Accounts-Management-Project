from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout



# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True)
    currency = models.CharField(max_length=3, default="GBP")  # Default to GBP
    timezone = models.CharField(max_length=50, default="GMT")  # Default to GMT
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class AccountType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
    account_type = models.ForeignKey(
        AccountType, on_delete=models.CASCADE, related_name="accounts_type"
    )
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20, unique=True, blank=True,null=True,help_text="Optional: Enter your bank account number for reference")
    balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00")
    )
    initial_balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00")
    )
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.account_number} - ${self.balance}"

    def update_balance(self):
        """
        Update the account balance based on the transactions associated with this account.
        This method should be called after saving a transaction to ensure the balance is accurate.
        """
        from django.db.models import Sum

        income = self.transactions.filter(transaction_type="income").aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")
        expenses = self.transactions.filter(transaction_type="expense").aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")
        transfers_out = self.transactions.filter(transaction_type="transfer").aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        transfers_in = Transaction.objects.filter(
            transfer_to_account=self, transaction_type="transfer"
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        self.balance = (
            self.initial_balance + income - expenses - transfers_out + transfers_in
        )
        self.save()

    def save(self, *args, **kwargs):
        # When creating a new account, set balance to initial_balance
        if not self.pk:  # New account (no primary key yet)
            self.balance = self.initial_balance
        
        super().save(*args, **kwargs)
    
    

class Category_type(models.Model):
    CATEGORY_TYPES = [
        ("income", "Income"),
        ("expense", "Expense"),
        ("transfer", "Transfer"),
    ]
    name = models.CharField(max_length=50, choices=CATEGORY_TYPES, unique=True)

    def __str__(self):
        return self.get_name_display()


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    category_type = models.ForeignKey(
        Category_type, on_delete=models.CASCADE, related_name="categories"
    )
    color = models.CharField(max_length=7, default="#007bff")  # Default to blue color
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ["user", "name", "category_type"]
        ordering = ["category_type", "name"]

    def __str__(self):
        return f"{self.name} ({self.category_type.name})"

    def total_amount_this_month(self):
        """Calculate the total amount for this category in the current month."""

        from django.utils import timezone
        from datetime import datetime

        now = timezone.now()
        start_of_month = datetime(now.year, now.month, 1)

        return self.transactions.filter(
            date__gte=start_of_month,
            date__lt=now
        ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("income", "Income"),
        ("expense", "Expense"),
        ("transfer", "Transfer"),
    ]

    PAYMENT_METHODS = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("bank_transfer", "Bank Transfer"),
        ("online", "Online Payment"),
        ("check", "Check"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="transactions"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="transactions"
    )

    # Transaction details
    description = models.CharField(max_length=200, blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    payment_methods = models.CharField(
        max_length=20, choices=PAYMENT_METHODS, default="cash"
    )

    # Dates
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # optional fields
    notes = models.TextField(blank=True)
    receipt_image = models.ImageField(upload_to="receipts/", blank=True)
    location = models.CharField(max_length=200, blank=True)

    # For recurring transactions
    is_recurring = models.BooleanField(default=False)
    recurring_parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )

    # For Transfers
    transfer_to_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transfer_transactions",
    )

    class Meta:
        ordering = ["-date", "-created_at"]
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.description} - {self.amount} - {self.transaction_type} - {self.date.strftime('%Y-%m-%d %H:%M:%S')}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update account balance after saving the transaction
        self.account.update_balance()
        if self.transfer_to_account:
            # If this is a transfer, update the balance of the receiving account
            self.transfer_to_account.update_balance()


class Budget(models.Model):
    BUDGET_PERIODS = [
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="budgets"
    )
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    period = models.CharField(max_length=10, choices=BUDGET_PERIODS, default="monthly")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Budgets"
        unique_together = ["user", "category", "start_date", "end_date"]
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} - {self.amount}"

    def spent_amount(self):
        """Calculate the total amount spent in this budget period."""

        return self.category.transactions.filter(
            date__gte=self.start_date,
            date__lte=self.end_date,
            transaction_type="expense",
        ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")

    def remaining_amount(self):
        """Calculate the remaining amount in this budget period."""

        spent = self.spent_amount()
        return self.amount - spent

    def percentage_used(self):
        """Calculate the percentage of the budget that has been used."""

        spent = self.spent_amount()
        if self.amount > 0:
            return float((spent / self.amount) * 100)
        return 0

    @property
    def is_over_budget(self):
        """Check if the budget has been exceeded."""

        return self.spent_amount() > self.amount


class SavingsGoal(models.Model):
    GOAL_TYPES = [
        ("emergency_fund", "Emergency Fund"),
        ("vacation", "Vacation"),
        ("car", "Car Purchase"),
        ("house", "House Down Payment"),
        ("education", "Education"),
        ("retirement", "Retirement"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="savings_goals"
    )
    name = models.CharField(max_length=100)
    goal_type = models.CharField(max_length=50, choices=GOAL_TYPES, default="other")
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00")
    )
    target_date = models.DateField()
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="goals/", blank=True)
    is_achieved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - £{self.current_amount}/£{self.target_amount}"

    def percentage_complete(self):
        """Calculate the percentage of the savings goal that has been achieved."""
        if self.target_amount > 0:
            return float((self.current_amount / self.target_amount) * 100)
        return 0

    def remaining_amount(self):
        """Calculate the remaining amount needed to achieve the savings goal."""
        return self.target_amount - self.current_amount

    def days_remaining(self):
        """Calculate the number of days remaining to achieve the savings goal."""
        from django.utils import timezone

        today = timezone.now().date()

        if self.target_date > today:
            return (self.target_date - today).days
        return 0


class RecurringTransaction(models.Model):
    FREQUENCY_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("bi_weekly", "Bi-Weekly"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recurring_transactions"
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(
        max_length=10, choices=Transaction.TRANSACTION_TYPES
    )

    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_due_date = models.DateField()
    is_active = models.BooleanField(default=True)
    

    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"

    def create_next_transaction(self):
        """Create the next transaction in the series."""
        if self.is_active and self.next_due_date:
            Transaction.objects.create(
                user=self.user,
                account=self.account,
                category=self.category,
                description=self.description,
                amount=self.amount,
                transaction_type=self.transaction_type,
                date=self.next_due_date,
                is_recurring=True,
                recurring_parent_id=self.id,
            )

            # Update the next due date based on the frequency
            self.update_next_due_date()

    def update_next_due_date(self):
        """Update the next due date based on the frequency."""

        from dateutil.relativedelta import relativedelta
        from datetime import timedelta

        if self.frequency == "daily":
            self.next_due_date += timedelta(days=1)
        elif self.frequency == "weekly":
            self.next_due_date += timedelta(weeks=1)
        elif self.frequency == "bi_weekly":
            self.next_due_date += timedelta(weeks=2)
        elif self.frequency == "monthly":
            self.next_due_date += relativedelta(months=1)
        elif self.frequency == "quarterly":
            self.next_due_date += relativedelta(months=3)
        elif self.frequency == "yearly":
            self.next_due_date += relativedelta(years=1)

        self.save()
