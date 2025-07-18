# Smart Account Management

A Django-based web application for managing personal finances, accounts, transactions, budgets, and categories with a modern dashboard UI. Includes OCR-powered receipt scanning, Stripe payment integration, and easy cloud deployment on Heroku.

## Features

- User authentication and registration
- Add, edit, and view accounts
- Record income and expense transactions
- Dashboard with monthly overview charts and statistics
- Category breakdown and budget progress
- Responsive design with Bootstrap
- Data visualization using Chart.js
- **Receipt OCR:** Scan receipts and bills using Tesseract OCR for automatic transaction entry
- **Stripe Payments:** Secure online payments and account funding via Stripe
- **Heroku Deployment:** One-click cloud deployment for easy access
- **Heroku Postgres:** Cloud database for scalable storage
  -- **Amazon S3:** Store uploaded receipts and files securely

## Getting Started

### Prerequisites

- Python 3.8+
- Django 4.x
- JavaScript
- Tesseract OCR (for receipt scanning)
- Stripe account (for payment integration)
- Heroku account (for deployment)
- Amazon AWS account (for S3 bucket storage)

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/Dimplektech/Smart-Accounts-Management-Project.git
   cd Smart_Account_Management
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Install Tesseract OCR:
   - **Windows:** Download from [Tesseract at UB Mannheim](https://github.com/tesseract-ocr/tesseract/wiki)
   - **macOS:** `brew install tesseract`
   - **Linux:** `sudo apt-get install tesseract-ocr`
5. Configure Stripe:
   - Set your Stripe API keys in environment variables or `settings.py`
   - See [Stripe Docs](https://stripe.com/docs)
6. Apply migrations:
   ```sh
   python manage.py migrate
   ```
7. Create a superuser (optional):
   ```sh
   python manage.py createsuperuser
   ```
8. Collect static files:
   ```sh
   python manage.py collectstatic --noinput
   ```
9. Run the development server:
   ```sh
   python manage.py runserver
   ```

## Usage

- Access the app at `http://localhost:8000/`
- Register a new user or log in
- Add accounts and transactions
- Scan receipts to auto-fill transactions (OCR)
- Fund accounts or pay bills using Stripe
- View dashboard analytics and manage budgets

## OCR Receipt Scanning

- Upload a photo or PDF of a receipt
- The app uses Tesseract OCR to extract transaction details
- Review and confirm auto-filled transaction data

## Stripe Payment Integration

- Securely fund your account or pay bills
- Stripe handles payment processing and security
- Configure your Stripe keys in the environment

## Heroku Deployment

1. Install the Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
2. Login and create a new Heroku app:
   ```sh
   heroku login
   heroku create your-app-name
   ```
3. Add Heroku Postgres add-on for database:
   ```sh
   heroku addons:create heroku-postgresql:hobby-dev
   ```
   - Update your Django `DATABASES` config to use the Heroku Postgres URL from `heroku config:get DATABASE_URL`
4. Set environment variables (Stripe keys, Django secret key, S3 bucket, etc.):
   ```sh
   heroku config:set STRIPE_SECRET_KEY=your_key STRIPE_PUBLISHABLE_KEY=your_key DJANGO_SECRET_KEY=your_secret AWS_ACCESS_KEY_ID=your-access-key-id AWS_SECRET_ACCESS_KEY=your-secret-access-key AWS_STORAGE_BUCKET_NAME=your-bucket-name AWS_S3_REGION_NAME=your-region
   ```
5. Deploy:
   ```sh
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py collectstatic --noinput
   ```
6. Open your app:
   ```sh
   heroku open
   ```

## Google Cloud Storage Integration

- Store uploaded receipts and files in Amazon S3 buckets
- Configure your bucket name and credentials in environment variables
- Update Django `DEFAULT_FILE_STORAGE` to use `storages.backends.s3boto3.S3Boto3Storage`
- See [django-storages docs](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)

## Project Structure

- `accounts/` - Main Django app for accounts, transactions, categories, budgets
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS)
- `requirements.txt` - Python dependencies
- `Procfile` - Heroku deployment file

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.

## Author

Dimplektech

---

For any issues or questions, please contact the repository owner.
