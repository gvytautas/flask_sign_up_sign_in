from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
import main


class AddClientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])


class CreateProductForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    categories = QuerySelectMultipleField(
        query_factory=main.Category.query.all, allow_blank=False, get_label='name', get_pk=lambda obj: str(obj)
    )


class CreateStockForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    product_id = QuerySelectField(
        query_factory=main.Product.query.all, allow_blank=True, get_label='name', get_pk=lambda obj: str(obj)
    )


class CreateCategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password1 = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password1')])

    def validate_username(self, username):
        user = main.User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('User name already exists!')


class SignInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
