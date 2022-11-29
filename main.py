"""
-flask-login
-sign up
-sign in (authentication)
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

db = SQLAlchemy()
login_manager = LoginManager()
app = Flask(__name__)
app.config['SECRET_KEY'] = "?``§=)()%``ÄLÖkhKLWDO=?)(_:;LKADHJATZQERZRuzeru3rkjsdfLJFÖSJ"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_database?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager.init_app(app)
db.init_app(app)
migrate = Migrate(app, db)

product_category = db.Table(
    'product_category', db.metadata,
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


class Client(db.Model):
    __tablename__ = 'client'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    address = db.Column(db.String)


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String)
    stock = db.relationship('Stock', back_populates='product')
    categories = db.relationship('Category', secondary=product_category, back_populates='products')


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    products = db.relationship('Product', secondary=product_category, back_populates='categories')


class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', back_populates='stock')


class UserOrder(db.Model):
    __tablename__ = 'user_order'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # product = db.relationship('Product', back_populates='product')
    # user = db.relationship('User', back_populates='us')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


with app.app_context():
    import forms

    db.create_all()


@app.route('/')
def index():
    return render_template('homepage.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password1.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Registration succeeded, {user.username}, now you can sign in.', 'success')
        return redirect(url_for('index'))
    return render_template('sign_up.html', form=form)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = forms.SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash(f'User {form.username.data} does not exist!', 'error')
            return redirect(url_for('sign_in'))
        if not form.password.data == user.password:
            flash(f'User / password do not match!', 'error')
            return redirect(url_for('sign_in'))
        login_user(user)
        flash(f'Welcome, {user.username}', 'success')
        return redirect(url_for('index'))
    return render_template('sign_in.html', form=form)


@app.route('/sign_out')
def sign_out():
    flash(f'See you next time, {current_user.username}')
    logout_user()
    return redirect(url_for('index'))


@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    form = forms.AddClientForm()
    if request.method == 'POST':
        name = form.name.data
        client = Client(name=name)
        db.session.add(client)
        db.session.commit()
        return redirect(url_for('show_clients'))

    return render_template('add_client.html', form=form)


@app.route('/clients')
def show_clients():
    clients = db.session.execute(db.select(Client)).scalars()
    return render_template('clients.html', data=clients)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = forms.CreateProductForm()
    if request.method == 'POST':
        product = Product(name=form.name.data, code=form.code.data)
        for category in form.categories.data:
            cat = Category.query.get(category.id)
            product.categories.append(cat)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_product.html', form=form)


@app.route('/add_stock', methods=['GET', 'POST'])
def add_stock():
    form = forms.CreateStockForm()
    if request.method == 'POST':
        stock = Stock(quantity=form.quantity.data, product_id=form.product_id.data.id)
        db.session.add(stock)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_stock.html', form=form)


@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    form = forms.CreateCategoryForm()
    if request.method == 'POST':
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_category.html', form=form)


@app.route('/show_stock')
def show_stock():
    stock = Stock.query.all()
    return render_template('show_stock.html', data=stock)


@app.route('/show_product_item/<product_id>')
def show_product_item(product_id):
    product = Product.query.get(product_id)
    return render_template('show_product_item.html', product=product)


@app.route('/show_products')
def show_products():
    products = Product.query.all()
    return render_template('show_products.html', products=products)


if __name__ == '__main__':
    app.run(debug=True)
