from flask_wtf import FlaskForm
from flask import session, flash
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from nancy.sqlORM import Query





class cartForm(FlaskForm):
    productID = IntegerField('product-id', validators=[DataRequired()])
    quantity = IntegerField('quantity')
    add_to_cart = SubmitField('Add To Cart')
    update_quantity = SubmitField("Upadate Quantity")
    delete_from_cart = SubmitField('Delete Item')
    saved_for_later = SubmitField('Save Item For Later')
    move_to_cart = SubmitField("Move back to cart")

class orderForm(FlaskForm) :
    address = IntegerField('address', validators=[DataRequired()])
    card = IntegerField('card', validators=[DataRequired()])


