import random
from datetime import timedelta, date, datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Account, Category, Transaction, Budget
from django.utils import timezone


class Command(BaseCommand):
    help = "Generate random demo data for all models."

    def handle(self, *args, **options):
        # Clear existing demo data (optional, for repeatable runs)
        Transaction.objects.all().delete()
        Account.objects.all().delete()
        Category.objects.all().delete()
        Budget.objects.all().delete()
        User.objects.filter(username__startswith="demo").delete()

        # Create demo users
        users = []
        for i in range(1, 3):
            user = User.objects.create_user(
                username=f"demo{i}", email=f"demo{i}@example.com", password="demo1234"
            )
            users.append(user)

        # Create category types if not exist
        from accounts.models import Category_type

        income_type, _ = Category_type.objects.get_or_create(name="income")
        expense_type, _ = Category_type.objects.get_or_create(name="expense")
        # Create accounts with higher initial balances
        account_types = ["Checking", "Savings", "Credit Card"]
        accounts = []
        for idx, user in enumerate(users):
            for i, acc_type in enumerate(account_types):
                # demo1: higher starting balance, demo2: moderate
                if idx == 0:
                    start_balance = Decimal(str(random.uniform(5000, 15000)))
                else:
                    start_balance = Decimal(str(random.uniform(2000, 7000)))
                acc = Account.objects.create(
                    user=user,
                    name=f"{acc_type} {i+1}",
                    balance=start_balance,
                    account_type_id=1,  # Adjust if you have AccountType model
                )
                accounts.append(acc)
        self.stdout.write(self.style.SUCCESS(f"Created {len(accounts)} accounts."))
        category_map = [
            ("Salary", income_type),
            ("Business", income_type),
            ("Investment", income_type),
            ("Gift", income_type),
            ("Other Income", income_type),
            ("Groceries", expense_type),
            ("Rent", expense_type),
            ("Utilities", expense_type),
            ("Transport", expense_type),
            ("Dining", expense_type),
            ("Shopping", expense_type),
            ("Health", expense_type),
            ("Education", expense_type),
            ("Other", expense_type),
        ]
        # Create categories for each user
        categories = []
        for user in users:
            for name, cat_type in category_map:
                cat = Category.objects.create(
                    user=user, name=name, category_type=cat_type
                )
                categories.append(cat)

        # Generate transactions for each user
        months_back = 6
        today = timezone.now().date()
        for idx, user in enumerate(users):
            user_accs = Account.objects.filter(user=user)
            user_cats = Category.objects.filter(user=user)
            # Track running balances for each account
            acc_balances = {acc.id: acc.balance for acc in user_accs}
            for m in range(months_back):
                month_start = today.replace(day=1) - timedelta(days=30 * m)
                for i in range(20):
                    if idx == 0:
                        t_type = "income" if random.random() < 0.7 else "expense"
                    else:
                        t_type = "income" if random.random() < 0.3 else "expense"
                    amount = Decimal(str(round(random.uniform(50, 2000), 2)))
                    if t_type == "income":
                        cat = (
                            user_cats.filter(category_type__name="income")
                            .order_by("?")
                            .first()
                        )
                    else:
                        cat = (
                            user_cats.filter(category_type__name="expense")
                            .order_by("?")
                            .first()
                        )
                    acc = random.choice(list(user_accs))
                    # Prevent negative balances for expenses
                    if t_type == "expense" and acc_balances[acc.id] - amount < 0:
                        continue  # skip this transaction
                    # Update running balance
                    if t_type == "income":
                        acc_balances[acc.id] += amount
                    else:
                        acc_balances[acc.id] -= amount
                    Transaction.objects.create(
                        user=user,
                        account=acc,
                        category=cat,
                        transaction_type=t_type,
                        amount=amount,
                        date=month_start + timedelta(days=random.randint(0, 27)),
                        description=f"{t_type.title()} for {cat.name}",
                    )
            # Update account balances in DB
            for acc in user_accs:
                acc.balance = acc_balances[acc.id]
                acc.save()
        self.stdout.write(self.style.SUCCESS("Created demo transactions."))

        # Create budgets
        for user in users:
            for cat in Category.objects.filter(user=user)[:3]:
                Budget.objects.create(
                    user=user,
                    category=cat,
                    amount=random.uniform(500, 2000),
                    start_date=today.replace(day=1),
                    end_date=(today.replace(day=1) + timedelta(days=90)),
                    is_active=True,
                )
        self.stdout.write(self.style.SUCCESS("Created demo budgets."))

        self.stdout.write(self.style.SUCCESS("Demo data generation complete!"))
