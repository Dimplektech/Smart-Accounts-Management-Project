
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, date
import json
from .models import Transaction, Account, Category, Budget
from .forms import TransactionForm, AccountForm, BudgetForm, RegistrationForm
from django.db.models.functions import TruncMonth
from django.views.decorators.http import require_POST


@login_required
@require_POST
def delete_transaction_view(request, transaction_id):
    """Delete a transaction and update account balance accordingly."""
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    account = transaction.account
    # Reverse the balance effect
    if transaction.transaction_type == "income":
        account.balance -= transaction.amount
    elif transaction.transaction_type == "expense":
        account.balance += transaction.amount
    account.save()
    transaction.delete()
    messages.success(request, "Transaction deleted successfully.")
    return redirect("accounts:transaction_list")


def login_view(request):
    print("DEBUG: login_view called!")  # Debug print
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back {username}!")
            return redirect("accounts:dashboard")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


@login_required
def dashboard_view(request):
    # Debug: Print current user
    print(
        f"🔍 Dashboard view for user: {request.user.username} (ID: {request.user.id})"
    )

    # Get current user's Accounts
    user_accounts = Account.objects.filter(user=request.user, is_active=True)
    print(f"🔍 User has {user_accounts.count()} accounts")

    # Calculate total balance across all accounts
    total_balance = user_accounts.aggregate(total=Sum("balance"))["total"] or 0
    # For now, just render the dashboard template

    # Get current months date range
    now = timezone.now()
    current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Get next month's first day
    if now.month == 12:
        next_month = current_month.replace(year=now.year + 1, month=1)
    else:
        next_month = current_month.replace(month=now.month + 1)

    current_month_transactions = Transaction.objects.filter(
        user=request.user, date__gte=current_month, date__lt=next_month
    )

    # Calculate total income and expenses for the current month
    monthly_income = (
        current_month_transactions.filter(transaction_type="income").aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    monthly_expenses = (
        current_month_transactions.filter(transaction_type="expense").aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    # Get recent transactions (last 10)
    recent_transactions = current_month_transactions.order_by("-date")[:10]

    # Chart data: Get Spending by Category for chart
    category_spending = (
        current_month_transactions.filter(transaction_type="expense")
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:6]
    )

    # Chart Data: Monthly Income vs Expenses (last 6 months)
    monthly_data = []
    for i in range(6):
        # Calculate proper month boundaries
        if i == 0:
            month_start = current_month
            month_end = next_month
        else:
            # Go back i months from current month
            year = now.year
            month = now.month - i
            if month <= 0:
                month += 12
                year -= 1

            month_start = timezone.now().replace(
                year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0
            )

            # Calculate end of this month
            if month == 12:
                month_end = month_start.replace(year=year + 1, month=1)
            else:
                month_end = month_start.replace(month=month + 1)

        month_transactions = Transaction.objects.filter(
            user=request.user, date__gte=month_start, date__lt=month_end
        )

        month_income = (
            month_transactions.filter(transaction_type="income").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        month_expenses = (
            month_transactions.filter(transaction_type="expense").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        monthly_data.append(
            {
                "month": month_start.strftime("%b %Y"),
                "income": float(month_income),
                "expenses": float(month_expenses),
            }
        )
        print(
            f"🔍 {month_start.strftime('%b %Y')}: Income=${month_income}, Expenses=${month_expenses}"
        )

    monthly_data.reverse()  # Show oldest to newest
    print(f"🔍 Final monthly_data for {request.user.username}: {monthly_data}")

    # Get active budgets with progress
    active_budgets = Budget.objects.filter(
        user=request.user, is_active=True, start_date__lte=now, end_date__gte=now
    )

    # Account balance distribution
    account_distribution = []
    for account in user_accounts:
        if account.balance > 0:
            account_distribution.append(
                {
                    "name": account.name,
                    "balance": float(account.balance),
                    "type": account.account_type.name,
                }
            )

    # Calculate total transactions for the current month
    total_transactions = current_month_transactions.count()

    # Convert total_balance to float
    total_balance = float(total_balance)

    # Convert monthly_income and monthly_expenses to float
    monthly_income = float(monthly_income)
    monthly_expenses = float(monthly_expenses)

    # Convert category_spending amounts to float
    category_spending = [
        {"category__name": item["category__name"], "total": float(item["total"])}
        for item in category_spending
    ]

    context = {
        "accounts": user_accounts,
        "total_balance": total_balance,
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "recent_transactions": recent_transactions,
        "active_budgets": active_budgets,
        "total_transactions": total_transactions,
        "current_month": current_month.strftime("%B %Y"),
        # Chart data
        "category_spending": category_spending,
        "monthly_data": monthly_data,
        "account_distribution": account_distribution,
        # JSON serialized data for JavaScript
        "monthly_data_json": json.dumps(monthly_data),
        "category_spending_json": json.dumps(category_spending),
        "account_distribution_json": json.dumps(account_distribution),
    }

    return render(request, "accounts/dashboard.html", context)


@login_required
def transaction_list_view(request):
    # Get filter parameters from request
    category_filter = request.GET.get("category", "")
    type_filter = request.GET.get("type", "")

    # Base queryset for transactions
    transactions = Transaction.objects.filter(user=request.user)

    # Apply filters if provided
    if category_filter:
        transactions = transactions.filter(category__name=category_filter)

    if type_filter:
        transactions = transactions.filter(transaction_type=type_filter)
    # Order transactions by date, most recent first
    transactions = transactions.order_by("-date")

    # Get all categories for the filter dropdown
    categories = Category.objects.filter(user=request.user).order_by("name")

    context = {
        "transactions": transactions,
        "categories": categories,
        "current_category": category_filter,
        "current_type": type_filter,
    }

    return render(request, "accounts/transaction_list.html", context)


@login_required
def add_transaction_view(request):
    if request.method == "POST":
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()

            # Update account balance
            account = transaction.account
            if transaction.transaction_type == "income":
                account.balance += transaction.amount
            elif transaction.transaction_type == "expense":
                account.balance -= transaction.amount
            account.save()

            messages.success(
                request,
                f"Transaction added successfully! ${transaction.amount} {transaction.transaction_type} to {account.name}.",
            )
            return redirect("accounts:dashboard")  # Add redirect after successful save
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TransactionForm(user=request.user)

    return render(request, "accounts/add_transaction.html", {"form": form})


@login_required
def account_list_view(request):
    accounts = Account.objects.filter(user=request.user, is_active=True)
    total_balance = accounts.aggregate(total=Sum("balance"))["total"] or 0
    total_balance = float(total_balance)
    active_accounts = accounts.count()
    return render(
        request,
        "accounts/account_list.html",
        {
            "accounts": accounts,
            "total_balance": total_balance,
            "active_accounts": active_accounts,
        },
    )


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                username = form.cleaned_data.get("username")

                # Don't auto-login - redirect to login page instead
                messages.success(
                    request,
                    f"Welcome {username}! Your account has been created successfully. Please login to continue.",
                )
                return redirect("accounts:login")

            except Exception as e:
                print(f"❌ Error during user creation: {e}")
                messages.error(request, f"Error creating user: {e}")
        else:
            # Debug: Show specific form errors
            print("❌ Form validation failed:")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"  - {field}: {error}")
                    messages.error(request, f"{field}: {error}")
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def budget_list_view(request):
    """Display all user Budgets"""
    budgets = Budget.objects.filter(user=request.user).order_by("-start_date")

    # Calculate Summary statistics
    total_budgets = budgets.count()
    active_budgets = budgets.filter(is_active=True).count()
    over_budget_count = sum(1 for budget in budgets if budget.is_over_budget)

    context = {
        "budgets": budgets,
        "total_budgets": total_budgets,
        "active_budgets": active_budgets,
        "over_budget_count": over_budget_count,
    }

    return render(request, "accounts/budget_list.html", context)


@login_required
def add_budget_view(request):
    """Add a new Budget"""
    if request.method == "POST":
        form = BudgetForm(request.user, request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, f"Budget {budget.name} created successfully!")
            return redirect("accounts:budget_list")
        else:
            form = BudgetForm(request.user)

    return render(request, "accounts/add_budget.html", {"form": form})


@login_required
def add_account(request):
    if request.method == "POST":
        form = AccountForm(request.POST, user=request.user)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()

            messages.success(
                request,
                f'Account "{account.name}" created successfully with account number {account.account_number}!',
            )
            return redirect("accounts:account_list")  # or wherever you want to redirect
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AccountForm(user=request.user)

    return render(
        request, "accounts/add_account.html", {"form": form, "title": "Add New Account"}
    )


@login_required
def account_detail_view(request, account_id):
    """Display account details"""
    account = get_object_or_404(Account, id=account_id, user=request.user)

    # Get recent transactions for this account
    recent_transactions = Transaction.objects.filter(account=account).order_by("-date")[
        :10
    ]

    # Calculate monthly statistics
    now = timezone.now()
    current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    monthly_income = (
        Transaction.objects.filter(
            account=account, transaction_type="income", date__gte=current_month
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    monthly_expenses = (
        Transaction.objects.filter(
            account=account, transaction_type="expense", date__gte=current_month
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    context = {
        "account": account,
        "recent_transactions": recent_transactions,
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
    }

    return render(request, "accounts/account_detail.html", context)


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("accounts:login")


@login_required
def reports_view(request):
    # Parse dates from GET params, fallback to defaults
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    else:
        start_date = date.today().replace(day=1)
    if end_date_str:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    else:
        end_date = date.today()

    # Get report type from query param, default to 'income_vs_expenses'
    report_type = request.GET.get("type", "income_vs_expenses")

    income_total = (
        Transaction.objects.filter(
            user=request.user,
            transaction_type="income",
            date__gte=start_date,
            date__lte=end_date,
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    expenses_total = (
        Transaction.objects.filter(
            user=request.user,
            transaction_type="expense",
            date__gte=start_date,
            date__lte=end_date,
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    net_income = income_total - expenses_total
    transactions_count = Transaction.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date,
    ).count()

    # Convert QuerySets to lists and Decimals to float
    account_balances = [
        {
            "name": a["name"],
            "balance": float(a["balance"]),
            "account_type": a["account_type__name"],
        }
        for a in Account.objects.filter(user=request.user).values(
            "name", "balance", "account_type__name"
        )
    ]
    category_breakdown = [
        {
            "category": c["category__name"],
            "total": float(c["total"]),
        }
        for c in Transaction.objects.filter(
            user=request.user, date__gte=start_date, date__lte=end_date
        )
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    ]

    monthly_trends = (
        Transaction.objects.filter(
            user=request.user, date__gte=start_date, date__lte=end_date
        )
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )
    monthly_trends_json = json.dumps(
        {
            item["month"].strftime("%Y-%m"): float(item["total"])
            for item in monthly_trends
        }
    )

    # Build monthly_trends_with_change for chart and table
    monthly_trends_list = [
        {"month": item["month"].strftime("%Y-%m"), "total": float(item["total"])}
        for item in monthly_trends
    ]
    monthly_trends_with_change = []
    prev_total = None
    for row in monthly_trends_list:
        change = None if prev_total is None else row["total"] - prev_total
        monthly_trends_with_change.append(
            {"month": row["month"], "total": row["total"], "change": change}
        )
        prev_total = row["total"]
    monthly_trends_with_change_json = json.dumps(monthly_trends_with_change)

    context = {
        "start_date": start_date,
        "end_date": end_date,
        "total_income": float(income_total),
        "total_expenses": float(expenses_total),
        "net_amount": float(net_income),
        "transactions_count": transactions_count,
        "account_balances": account_balances,
        "category_breakdown": category_breakdown,
        "category_breakdown_json": json.dumps(category_breakdown),
        "monthly_trends": monthly_trends_json,
        "monthly_trends_with_change": monthly_trends_with_change,
        "monthly_trends_with_change_json": monthly_trends_with_change_json,
        "report_type": report_type,
    }
    return render(request, "accounts/reports.html", context)


# Edit transaction view
@login_required
def edit_transaction_view(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    old_amount = transaction.amount
    old_type = transaction.transaction_type
    old_account = transaction.account

    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            updated_transaction = form.save(commit=False)
            updated_transaction.user = request.user
            updated_transaction.save()

            # If account, amount, or type changed, update balances
            if old_account != updated_transaction.account:
                # Revert old account
                if old_type == "income":
                    old_account.balance -= old_amount
                elif old_type == "expense":
                    old_account.balance += old_amount
                old_account.save()
                # Apply to new account
                account = updated_transaction.account
                if updated_transaction.transaction_type == "income":
                    account.balance += updated_transaction.amount
                elif updated_transaction.transaction_type == "expense":
                    account.balance -= updated_transaction.amount
                account.save()
            else:
                # Same account, but maybe amount/type changed
                account = updated_transaction.account
                if old_type == "income":
                    account.balance -= old_amount
                elif old_type == "expense":
                    account.balance += old_amount
                if updated_transaction.transaction_type == "income":
                    account.balance += updated_transaction.amount
                elif updated_transaction.transaction_type == "expense":
                    account.balance -= updated_transaction.amount
                account.save()

            messages.success(request, "Transaction updated successfully!")
            return redirect("accounts:transaction_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TransactionForm(instance=transaction, user=request.user)

    return render(
        request,
        "accounts/edit_transaction.html",
        {"form": form, "transaction": transaction},
    )

