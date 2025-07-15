EXPENSE_CATEGORIES = [
    # Food & Dining
    ('Food & Dining', 'expense', '🍽️', '#EF4444'),   # Red - Food/Appetite
    ('Groceries', 'expense', '🛒', '#F97316'),        # Orange - Fresh/Essential
    ('Coffee & Drinks', 'expense', '☕', '#A3A3A3'),  # Gray - Daily Habits
    
    # Transportation
    ('Transportation', 'expense', '🚗', '#1F2937'),   # Dark Gray - Automotive
    ('Gas & Fuel', 'expense', '⛽', '#DC2626'),       # Red - Energy/Fuel
    ('Public Transport', 'expense', '🚌', '#2563EB'), # Blue - Public Service
    
    # Shopping & Personal
    ('Shopping', 'expense', '🛍️', '#EC4899'),        # Pink - Retail/Fashion
    ('Clothing', 'expense', '👕', '#8B5CF6'),        # Purple - Fashion/Style
    ('Personal Care', 'expense', '💄', '#F472B6'),   # Light Pink - Beauty/Care
    
    # Entertainment & Recreation
    ('Entertainment', 'expense', '🎬', '#7C3AED'),   # Purple - Fun/Leisure
    ('Travel', 'expense', '✈️', '#0EA5E9'),          # Sky Blue - Adventure/Freedom
    ('Gym & Fitness', 'expense', '💪', '#059669'),   # Green - Health/Strength
    ('Sports & Hobbies', 'expense', '⚽', '#F59E0B'), # Amber - Activity/Fun
    
    # Bills & Utilities
    ('Bills & Utilities', 'expense', '💡', '#FBBF24'), # Yellow - Light/Energy
    ('Rent/Mortgage', 'expense', '🏠', '#92400E'),     # Brown - Home/Stability
    ('Internet', 'expense', '🌐', '#0891B2'),         # Teal - Technology/Connection
    ('Phone', 'expense', '📱', '#6366F1'),            # Indigo - Communication
    ('Insurance', 'expense', '🛡️', '#374151'),        # Dark Gray - Protection
    
    # Health & Education
    ('Healthcare', 'expense', '🏥', '#DC2626'),       # Red - Medical/Emergency
    ('Education', 'expense', '📚', '#1D4ED8'),        # Blue - Knowledge/Learning
    ('Subscriptions', 'expense', '📱', '#8B5CF6'),    # Purple - Digital Services
    
    # Home & Maintenance
    ('Home & Garden', 'expense', '🏠', '#059669'),    # Green - Growth/Nature
    ('Maintenance & Repairs', 'expense', '🔧', '#6B7280'), # Gray - Tools/Fixing
    
    # Financial & Miscellaneous
    ('Taxes', 'expense', '🏛️', '#374151'),           # Dark Gray - Government
    ('Charity & Donations', 'expense', '❤️', '#EF4444'), # Red - Love/Giving
    ('Bank Fees', 'expense', '🏦', '#6B7280'),        # Gray - Banking Costs
    ('Other Expenses', 'expense', '🔧', '#64748B'),   # Slate Gray - Miscellaneous
]

INCOME_CATEGORIES = [
    ('Salary', 'income', '💰', '#10B981'),           # Green - Growth/Money
    ('Freelance', 'income', '💻', '#3B82F6'),        # Blue - Technology/Professional
    ('Investment Returns', 'income', '📈', '#059669'), # Dark Green - Success/Growth
    ('Side Business', 'income', '🏪', '#7C3AED'),     # Purple - Creativity/Business
    ('Gifts', 'income', '🎁', '#EC4899'),            # Pink - Joy/Celebration
    ('Bonus', 'income', '🎉', '#F59E0B'),            # Amber - Achievement/Reward
    ('Refunds', 'income', '💸', '#06B6D4'),          # Cyan - Return/Flow
    ('Bank Interest', 'income', '🏦', '#065F46'),     # Dark Green - Banking/Stability
    ('Rental Income', 'income', '🏘️', '#7C2D12'),    # Brown - Property/Real Estate
    ('Other Income', 'income', '💵', '#16A34A'),      # Green - General Money
]

# accounts/models.py
class Category(models.Model):
    # Icon choices for the admin dropdown
    ICON_CHOICES = [
        # Income Icons
        ('💰', '💰 Money'),
        ('💻', '💻 Laptop'),
        ('📈', '📈 Chart Up'),
        ('🏪', '🏪 Store'),
        ('🎁', '🎁 Gift'),
        ('🎉', '🎉 Party'),
        ('💸', '💸 Money with Wings'),
        ('💵', '💵 Dollar Bill'),
        ('🏦', '🏦 Bank'),
        ('💎', '💎 Diamond'),
        ('🤝', '🤝 Handshake'),
        ('🎯', '🎯 Target'),
        
        # Expense Icons - Food & Dining
        ('🍽️', '🍽️ Fork and Knife'),
        ('🍕', '🍕 Pizza'),
        ('☕', '☕ Coffee'),
        ('🍔', '🍔 Hamburger'),
        ('🥗', '🥗 Salad'),
        ('🍜', '🍜 Noodles'),
        ('🍺', '🍺 Beer'),
        ('🛒', '🛒 Shopping Cart'),
        
        # Transportation
        ('🚗', '🚗 Car'),
        ('⛽', '⛽ Fuel'),
        ('🚌', '🚌 Bus'),
        ('🚇', '🚇 Metro'),
        ('✈️', '✈️ Airplane'),
        ('🚕', '🚕 Taxi'),
        ('🚲', '🚲 Bicycle'),
        ('🛵', '🛵 Scooter'),
        
        # Shopping & Entertainment
        ('🛍️', '🛍️ Shopping Bags'),
        ('👕', '👕 T-Shirt'),
        ('👟', '👟 Shoes'),
        ('🎬', '🎬 Movie'),
        ('🎮', '🎮 Gaming'),
        ('🎵', '🎵 Music'),
        ('📚', '📚 Books'),
        ('🎪', '🎪 Circus'),
        
        # Bills & Utilities
        ('💡', '💡 Light Bulb'),
        ('🏠', '🏠 House'),
        ('📱', '📱 Mobile Phone'),
        ('💻', '💻 Laptop'),
        ('🌐', '🌐 Internet'),
        ('📺', '📺 Television'),
        ('🔥', '🔥 Fire (Gas)'),
        ('💧', '💧 Water'),
        
        # Health & Personal Care
        ('🏥', '🏥 Hospital'),
        ('💊', '💊 Pill'),
        ('💄', '💄 Lipstick'),
        ('🧴', '🧴 Lotion'),
        ('💪', '💪 Muscle (Gym)'),
        ('🦷', '🦷 Tooth'),
        ('👓', '👓 Glasses'),
        ('💅', '💅 Nail Polish'),
        
        # Miscellaneous
        ('🛡️', '🛡️ Shield'),
        ('🎓', '🎓 Graduation Cap'),
        ('🏖️', '🏖️ Beach'),
        ('🎨', '🎨 Art'),
        ('🔧', '🔧 Wrench'),
        ('📊', '📊 Chart'),
        ('🎊', '🎊 Confetti'),
        ('🌟', '🌟 Star'),
    ]
   