# accounts/forms.py
from django import forms
from .models import Account, Transaction, Category, Budget, AccountType, Category_type
from decimal import Decimal
from django.contrib.auth.models import User

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'account', 'category', 'amount', 'description', 'date', 'payment_methods']
        widgets = {
            'transaction_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'transactionType'
            }),
            'account': forms.Select(attrs={
                'class': 'form-select',
                'id': 'account'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'category'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter transaction description...'
            }),
            'date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'payment_methods': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'transaction_type': 'Transaction Type',
            'account': 'Account',
            'category': 'Category',
            'amount': 'Amount',
            'description': 'Description',
            'date': 'Date & Time',
            'payment_methods': 'Payment Method',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter accounts and categories by user
        if user:
            self.fields['account'].queryset = Account.objects.filter(user=user, is_active=True)
            self.fields['category'].queryset = Category.objects.filter(user=user)
        
        # Set default date to now
        if not self.instance.pk:  # Only for new transactions
            from django.utils import timezone
            self.fields['date'].initial = timezone.now()
        
        # Set empty labels
        self.fields['transaction_type'].empty_label = "-- Select Type --"
        self.fields['account'].empty_label = "-- Select Account --"
        self.fields['category'].empty_label = "-- Select Category --"
        self.fields['payment_methods'].empty_label = "-- Select Payment Method --"
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'name', 
            'account_type', 
            'account_number', 
            'initial_balance', 
            'bank_name'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Main Checking, Emergency Savings'
            }),
            'account_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1234567890'
            }),
            'initial_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00',
                'min': '0'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Chase Bank, Wells Fargo (optional)'
            }),
        }
        labels = {
            'name': 'Account Name',
            'account_type': 'Account Type',
            'account_number': 'Account Number',
            'initial_balance': 'Initial Balance',
            'bank_name': 'Bank Name',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set field requirements
        self.fields['name'].required = True
        self.fields['account_type'].required = True
        self.fields['initial_balance'].required = True
        self.fields['account_number'].help_text = "optional: Enter your bank account number for reference"
        self.fields['bank_name'].required = False
        
        # Filter account types to only active ones
        self.fields['account_type'].queryset = AccountType.objects.filter(is_active=True)
        self.fields['account_type'].empty_label = "-- Select Account Type --"
        
        # Set help texts
        self.fields['name'].help_text = "Enter a descriptive name for your account"
        self.fields['account_number'].help_text = "Leave blank to auto-generate a unique account number"
        self.fields['initial_balance'].help_text = "Enter the current balance of this account"
        self.fields['bank_name'].help_text = "Optional: Name of the bank or financial institution"

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 2:
            raise forms.ValidationError("Account name must be at least 2 characters long.")
        return name.strip()

    def clean_initial_balance(self):
        balance = self.cleaned_data.get('initial_balance')
        if balance is None:
            raise forms.ValidationError("Initial balance is required.")
        if balance < 0:
            raise forms.ValidationError("Initial balance cannot be negative.")
        return balance

    def clean_account_number(self):
        account_number = self.cleaned_data.get('account_number')
        if account_number:
            account_number = account_number.strip()
            # Check if account number already exists
            if Account.objects.filter(account_number=account_number).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("An account with this number already exists.")
        return account_number


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'category', 'amount', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Monthly Groceries, Entertainment Budget'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
        labels = {
            'name': 'Budget Name',
            'category': 'Category',
            'amount': 'Budget Amount',
            'start_date': 'Start Date',
            'end_date': 'End Date',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter categories by user and expense type
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user, 
                category_type__name='expense'
            )
        
        # Set empty label
        self.fields['category'].empty_label = "-- Select Category --"
        
        # Set help texts
        self.fields['name'].help_text = "Give your budget a descriptive name"
        self.fields['amount'].help_text = "Set the maximum amount for this budget"
        self.fields['start_date'].help_text = "When does this budget period start?"
        self.fields['end_date'].help_text = "When does this budget period end?"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError("End date must be after start date.")
        
        return cleaned_data

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Budget amount must be greater than zero.")
        return amount


# Additional forms if you need them

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'category_type', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Food & Dining, Transportation'
            }),
            'category_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 🍽️, 🚗, 💰'
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set empty label
        self.fields['category_type'].empty_label = "-- Select Type --"


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autofocus': True
        }),
        label='Username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        }),
        label='Password'
    )


class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        }),
        label='Username'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        }),
        label='Email Address'
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        }),
        label='First Name'
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        }),
        label='Last Name'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a strong password'
        }),
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        }),
        label='Confirm Password'
    )

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1 and len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        
        return password2
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def save(self):
        # Create the user
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        return user