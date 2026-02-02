
# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import matplotlib
matplotlib.use('Agg') # Necessary for server-side graph generation
import matplotlib.pyplot as plt
import io
import os
try:
    import google.generativeai as genai  # New import for AI
except Exception:
    genai = None

# --- Custom Modules ---
from scraper.scraper_manager import ScraperManager
from ocr_processor import OCRProcessor
from utils.currency_converter import CurrencyConverter
from utils.product_matcher import ProductMatcher

# --- App Setup ---
app = Flask(__name__)

# Improved security: Use environment variables for sensitive data
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security improvements
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Additional security headers
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# --- Database Setup ---
db = SQLAlchemy(app)

# --- Auto-create database tables (Gunicorn / Render safe) ---
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables ensured at startup.")
    except Exception as e:
        print(f"❌ Database init error: {e}")


# --- Login Manager Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- AI Configuration ---
# SECURITY WARNING: Never share API keys publicly or commit them to GitHub.
# Prefer setting `GOOGLE_API_KEY` in the environment (e.g. via system env or .env).
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    print("Warning: `GOOGLE_API_KEY` not set. Gemini AI features will be disabled.")

if genai is None:
    print("Warning: `google.generativeai` package not available. Install `google-generative-ai` to enable Gemini features.")
else:
    if GOOGLE_API_KEY:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
        except Exception as e:
            print(f"Failed to configure genai: {e}")

# --- Database Models ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(500), nullable=False)
    product_url = db.Column(db.String(1000), nullable=False, unique=True)
    image_url = db.Column(db.String(1000))
    website = db.Column(db.String(100))
    current_price = db.Column(db.Float, nullable=False)
    target_price = db.Column(db.Float) # User's target price
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price_history = db.relationship('PriceHistory', backref='item', lazy=True, cascade="all, delete-orphan")

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    item_id = db.Column(db.Integer, db.ForeignKey('wishlist_item.id'), nullable=False)


# --- Initialize Components ---
scraper_manager = ScraperManager()
ocr_processor = OCRProcessor()
currency_converter = CurrencyConverter()
product_matcher = ProductMatcher()

scraped_data = []

# --- Authentication Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first() 
        
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.', 'warning')
            return redirect(url_for('login'))
            
        login_user(user)
        session.permanent = True
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'warning')
            return redirect(url_for('register'))
        
        user_by_email = User.query.filter_by(email=email).first()
        user_by_username = User.query.filter_by(username=username).first()

        if user_by_email:
            flash('Email address is already in use.', 'warning')
            return redirect(url_for('register'))
        if user_by_username:
            flash('Username is already taken. Please choose another.', 'warning')
            return redirect(url_for('register'))

        new_user = User(
            username=username, 
            email=email, 
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        session.permanent = True
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

# --- Main App Routes ---

@app.route('/')
@login_required
def home():
    if 'recent_searches' not in session:
        session['recent_searches'] = []
    
    recommendations = ["iPhone 15", "Samsung S24 Ultra", "Sony WH-1000XM5", "Laptop"]
    recent_searches = session['recent_searches']

    wishlist_count = WishlistItem.query.filter_by(user_id=current_user.id).count()
    price_targets = WishlistItem.query.filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.target_price != None
    ).count()
    price_updates = db.session.query(PriceHistory).join(WishlistItem).filter(
        WishlistItem.user_id == current_user.id
    ).count()

    hero_stats = [
        {"label": "Reports Run", "value": f"{len(recent_searches)}", "icon": "bi-graph-up-arrow", "colors": ("#10b981", "#059669")},
        {"label": "Wishlist Items", "value": f"{wishlist_count}", "icon": "bi-bookmark-heart", "colors": ("#3b82f6", "#1d4ed8")},
        {"label": "Price Targets", "value": f"{price_targets}", "icon": "bi-bullseye", "colors": ("#8b5cf6", "#7c3aed")},
        {"label": "Price Updates", "value": f"{price_updates}", "icon": "bi-lightning-charge", "colors": ("#f59e0b", "#d97706")},
    ]
    
    return render_template(
        'home.html', 
        recent_searches=recent_searches,
        recommendations=recommendations,
        hero_stats=hero_stats
    )

@app.route('/search')
@login_required  
def search_page():
    if 'recent_searches' not in session:
        session['recent_searches'] = []
    
    recommendations = ["iPhone 15", "Samsung S24 Ultra", "Sony WH-1000XM5", "Laptop"]
    query = request.args.get('q', '')
    
    # Get stats for the cards
    total_searches = len(session['recent_searches'])
    wishlist_count = WishlistItem.query.filter_by(user_id=current_user.id).count()
    platforms_scanned = 4
    avg_savings = 2450
    
    return render_template(
        'search.html',
        recent_searches=session['recent_searches'],
        recommendations=recommendations,
        query=query,
        total_searches=total_searches,
        wishlist_count=wishlist_count,
        platforms_scanned=platforms_scanned,
        avg_savings=avg_savings
    )

@app.route('/features')
def features_page():
    return render_template('features.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

def check_price_alerts():
    """Check for price drops and create alerts."""
    items_to_alert = WishlistItem.query.filter(
        WishlistItem.user_id == current_user.id,
        WishlistItem.target_price != None,
        WishlistItem.current_price <= WishlistItem.target_price
    ).all()
    
    for item in items_to_alert:
        alert_message = f"Price Drop Alert! '{item.product_name[:50]}...' is now Rs.{item.current_price} (your target was Rs.{item.target_price})."
        flash(alert_message, 'warning')
        
        item.target_price = None
        db.session.commit()

def get_deal_status(item):
    """Analyzes price history for a wishlist item to determine deal quality."""
    try:
        thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        
        history = PriceHistory.query.filter(
            PriceHistory.item_id == item.id,
            PriceHistory.date >= thirty_days_ago
        ).all()

        if not history or len(history) < 2:
            return {'avg_price': None, 'status': 'New Item', 'badge_color': 'secondary'}

        prices = [h.price for h in history]
        avg_price = round(sum(prices) / len(prices), 2)
        min_price = min(prices)
        
        current_price = item.current_price
        
        if current_price <= min_price:
            return {'avg_price': avg_price, 'status': 'Lowest Price!', 'badge_color': 'danger'}
        
        percent_diff = ((avg_price - current_price) / avg_price) * 100
        
        if percent_diff > 15:
            return {'avg_price': avg_price, 'status': f'Epic Deal! ({round(percent_diff)}% off avg.)', 'badge_color': 'success'}
        if percent_diff > 5:
            return {'avg_price': avg_price, 'status': f'Good Deal ({round(percent_diff)}% off)', 'badge_color': 'primary'}
        
        return {'avg_price': avg_price, 'status': 'Avg. Price', 'badge_color': 'info'}

    except Exception as e:
        print(f"Error calculating deal status: {e}")
        return {'avg_price': None, 'status': 'N/A', 'badge_color': 'secondary'}


@app.route('/wishlist')
@login_required
def wishlist():
    print(f"👤 Wishlist accessed by user: {current_user.id} ({current_user.email})")
    check_price_alerts()
    
    items_from_db = WishlistItem.query.filter_by(user_id=current_user.id).order_by(WishlistItem.id.desc()).all()
    print(f"🔍 Found {len(items_from_db)} items for this user")
    
    items_with_status = []
    for item in items_from_db:
        print(f"  Processing item: {item.product_name[:30]}...")
        try:
            deal_info = get_deal_status(item)
            item.avg_price = deal_info['avg_price']
            item.deal_status = deal_info['status']
            item.badge_color = deal_info['badge_color']
            items_with_status.append(item)
            print(f"    Added to list. Current list size: {len(items_with_status)}")
        except Exception as e:
            print(f"    ERROR processing item: {e}")
            # Add item with default values if processing fails
            item.avg_price = None
            item.deal_status = "Tracking"
            item.badge_color = "secondary"
            items_with_status.append(item)
    
    print(f"📤 Sending {len(items_with_status)} items to template")
    print(f"📋 Items type: {type(items_with_status)}")
    print(f"📋 Items content: {[item.product_name[:20] for item in items_with_status]}")
    return render_template('wishlist.html', items=items_with_status)


@app.route('/analytics')
@login_required
def analytics():
    # Get analytics data
    total_searches = len(session.get('recent_searches', []))
    wishlist_count = WishlistItem.query.filter_by(user_id=current_user.id).count()
    
    # Calculate average savings (mock data for demo)
    avg_savings = 2450
    platforms_scanned = 4
    
    return render_template('analytics.html', 
                         total_searches=total_searches,
                         wishlist_count=wishlist_count,
                         avg_savings=avg_savings,
                         platforms_scanned=platforms_scanned,
                         recent_searches=session.get('recent_searches', []))

@app.route('/history')
@login_required
def history():
    searches = session.get('recent_searches', [])
    return render_template('history.html', searches=searches)

@app.route('/add_to_wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    try:
        print(f"🛒 Add to wishlist - Current user: {current_user.id} ({current_user.email})")
        data = request.json
        product_url = data.get('url')

        if not product_url:
            return jsonify({'success': False, 'error': 'Product URL is missing.'})

        existing_item = WishlistItem.query.filter_by(product_url=product_url, user_id=current_user.id).first()
        if existing_item:
            return jsonify({'success': False, 'error': 'Product already in wishlist.'})

        new_item = WishlistItem(
            product_name=data.get('name'),
            product_url=product_url,
            current_price=data.get('price'),
            image_url=data.get('image'),
            website=data.get('website'),
            user_id=current_user.id
        )
        db.session.add(new_item)
        db.session.commit()
        
        history_entry = PriceHistory(price=new_item.current_price, item_id=new_item.id)
        db.session.add(history_entry)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Product added to Wishlist!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/remove_from_wishlist/<int:item_id>', methods=['POST'])
@login_required
def remove_from_wishlist(item_id):
    item = WishlistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('Item removed from wishlist.', 'success')
    return redirect(url_for('wishlist'))

@app.route('/set_target_price/<int:item_id>', methods=['POST'])
@login_required
def set_target_price(item_id):
    item = WishlistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    try:
        target_price = request.form.get('target_price')
        if target_price:
            item.target_price = float(target_price)
            db.session.commit()
            flash(f"Alert set for '{item.product_name[:30]}...' below Rs.{target_price}", 'success')
        else:
            flash('Please enter a valid price.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Error setting alert: {e}', 'danger')
    return redirect(url_for('wishlist'))

# --- OLD ROUTE (Static Image) - Kept for backup ---
@app.route('/get_price_history_chart/<int:item_id>')
@login_required
def get_price_history_chart(item_id):
    item = WishlistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    history = PriceHistory.query.filter_by(item_id=item.id).order_by(PriceHistory.date.asc()).all()
    
    if len(history) < 2:
        return "Not enough price history to generate a chart.", 404

    dates = [h.date for h in history]
    prices = [h.price for h in history]

    try:
        plt.figure(figsize=(8, 4))
        plt.plot(dates, prices, marker='o', linestyle='-')
        plt.title(f"Price History: {item.product_name[:40]}...", fontsize=12)
        plt.ylabel("Price (₹)")
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d-%b'))
        plt.gcf().autofmt_xdate()
        
        min_price = min(prices)
        plt.axhline(y=min_price, color='green', linestyle='--', label=f'Lowest: Rs.{min_price}')
        plt.legend()
        
        img_io = io.BytesIO()
        plt.savefig(img_io, format='png', bbox_inches='tight')
        plt.close()
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        print(f"Error generating chart: {e}")
        return "Error generating chart.", 500

# --- NEW ROUTE (Interactive JSON Data) ---
@app.route('/api/price_history/<int:item_id>')
@login_required
def api_price_history(item_id):
    """
    Returns JSON data for Chart.js instead of a static image.
    """
    try:
        item = WishlistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
        history = PriceHistory.query.filter_by(item_id=item.id).order_by(PriceHistory.date.asc()).all()
        
        if not history:
            return jsonify({'error': 'No history found'}), 404

        # Prepare data for frontend
        dates = [h.date.strftime('%d %b') for h in history]
        prices = [h.price for h in history]
        
        return jsonify({
            'success': True,
            'product_name': item.product_name,
            'dates': dates,
            'prices': prices,
            'website': item.website
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Scraper API Routes ---

@app.route('/search', methods=['POST'])
@login_required
def search():
    try:
        product_name = request.form.get('product_name', '').strip()
        
        # Input validation and sanitization
        if not product_name:
            return jsonify({'error': 'Please enter a product name'}), 400
        
        if len(product_name) < 2:
            return jsonify({'error': 'Product name must be at least 2 characters long'}), 400
            
        if len(product_name) > 100:
            return jsonify({'error': 'Product name too long (max 100 characters)'}), 400
            
        # Basic sanitization - remove potentially harmful characters
        import html
        product_name = html.escape(product_name)
        
        # Remove excessive whitespace and special characters
        import re
        product_name = re.sub(r'[<>"\']', '', product_name)
        product_name = ' '.join(product_name.split())  # Normalize whitespace
            
        print(f"[SEARCH] Searching for: {product_name} (User: {current_user.email})")
        
        if 'recent_searches' not in session: session['recent_searches'] = []
        if product_name in session['recent_searches']: session['recent_searches'].remove(product_name)
        session['recent_searches'].insert(0, product_name)
        session['recent_searches'] = session['recent_searches'][:5]
        session.modified = True

        # Updated to use parallel scraper
        products = scraper_manager.search_all_websites(product_name, max_products=5)
        
        if products:
            final_products = product_matcher.group_products_for_display(products)
            
            # --- Auto-update Price History ---
            try:
                with app.app_context():
                    today = datetime.date.today()
                    for product in final_products:
                        if not product.get('url'): 
                            continue
                        
                        try:
                            item = WishlistItem.query.filter_by(
                                product_url=product.get('url'),
                                user_id=current_user.id
                            ).first()
                            
                            # Update existing wishlist items' current price and add a price history entry when price changes
                            current_price = None
                            if product.get('price') is not None:
                                try:
                                    current_price = float(product.get('price'))
                                except (ValueError, TypeError):
                                    current_price = None

                            if item and current_price is not None and abs(item.current_price - current_price) > 0.01:
                                item.current_price = current_price
                                db.session.add(item)
                                
                                history_entry = PriceHistory(price=current_price, item_id=item.id)
                                db.session.add(history_entry)
                                db.session.commit()
                                
                        except Exception as db_error:
                            print(f"Error updating price for product {product.get('url', 'unknown')}: {db_error}")
                            db.session.rollback()
                            continue
                            
            except Exception as e:
                print(f"Error in price history update: {e}")
                # Don't fail the entire search if price history update fails

            # Return search results
            return jsonify({
                'success': True,
                'products': final_products,
                'count': len(final_products),
                'websites': len(set(p['website'] for p in final_products)),
                'product_groups': len(set(p['group_key'] for p in final_products))
            })
        else:
            return jsonify({'success': False, 'error': 'No products found on any website'})
            
    except Exception as e:
        print(f"Error in /search: {e}")
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

@app.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    try:
        if 'image' not in request.files: return jsonify({'error': 'No image file'})
        image_file = request.files['image']
        if image_file.filename == '': return jsonify({'error': 'No image selected'})
            
        product_name = ocr_processor.extract_text_from_image(image_file)
        
        if 'recent_searches' not in session: session['recent_searches'] = []
        if product_name in session['recent_searches']: session['recent_searches'].remove(product_name)
        session['recent_searches'].insert(0, product_name)
        session['recent_searches'] = session['recent_searches'][:5]
        session.modified = True

        return jsonify({'success': True, 'product_name': product_name})
    except Exception as e:
        return jsonify({'success': False, 'error': f'OCR processing failed: {str(e)}'})


# --- NEW: Gemini AI Chatbot Logic ---
def process_chat_message(message):
    """
    Hybrid Chatbot: 
    1. Checks for specific app commands (Search, Navigation).
    2. If no command found, asks Gemini AI for a smart response.
    """
    msg = message.lower()
    
    # --- Priority 1: App Actions (Search & Navigation) ---
    if "search" in msg or "find" in msg or "price of" in msg:
        # Extract product name
        clean_msg = msg.replace("search for", "").replace("find", "").replace("price of", "").replace("search", "").strip()
        
        if len(clean_msg) < 2:
            return {"text": "What product should I search for? (e.g., 'Search for iPhone 15')", "action": None}
            
        return {
            "text": f"Searching for '{clean_msg}' across Amazon, Flipkart, and Croma...",
            "action": "search",
            "query": clean_msg
        }

    elif "wishlist" in msg or "saved items" in msg:
        return {
            "text": "Opening your wishlist...",
            "action": "navigate",
            "url": "/wishlist"
        }
    
    elif "history" in msg:
        return {
            "text": "Here is your search history.",
            "action": "navigate",
            "url": "/history"
        }

    # --- Priority 2: Gemini AI (General Conversation) ---
    # If the genai package or API key is not available, skip AI and return a helpful fallback message.
    if genai is None or not GOOGLE_API_KEY:
        return {
            "text": "Gemini AI is currently unavailable. I can still help you search for products — what would you like to find?",
            "action": None
        }

    try:
        candidate_models = [
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash",
            "models/gemini-1.5-flash"
        ]
        last_error = None

        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(model_name)
                system_context = (
                    "You are PriceBot, a helpful assistant for a price comparison app. "
                    "You help users save money. Keep your answers short, friendly, and related to shopping/tech. "
                    f"User says: {message}"
                )

                response = model.generate_content(system_context)
                ai_reply = getattr(response, "text", None)
                if not ai_reply:
                    raise ValueError("Empty response from AI model")

                return {
                    "text": ai_reply,
                    "action": None
                }
            except Exception as model_err:
                last_error = model_err
                print(f"AI Error with {model_name}: {model_err}")
                continue

        print(f"AI fallback: all candidate models failed. Last error: {last_error}")
        return {
            "text": "Chat assistant is in development. I can still help you search for products!",
            "action": None
        }

    except Exception as e:
        print(f"Chat fallback error: {e}")
        return {
            "text": "Chat assistant is in development. I can still help you search for products!",
            "action": None
        }

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        if not user_message:
            return jsonify({'text': 'Please enter a message.', 'action': None})
        response = process_chat_message(user_message)
        return jsonify(response)
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'text': 'Sorry, I encountered an error. Please try again.', 'action': None})


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('base.html'), 403

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, port=port, host='0.0.0.0')

