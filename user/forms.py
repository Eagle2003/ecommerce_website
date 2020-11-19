from flask import flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length, AnyOf, ValidationError, EqualTo
from nancy.sqlORM import Query
from datetime import date




def onlyNumeric(form, field) : 
    if not field.data.isdigit() : raise ValidationError("Invalid Characters found !")

def isValidOrderID (form, field):
    def isValidProductID (form, field) :
        order =  Query('orders').get().filter(seller=session['EMAIL']).filter(id=field.data).fetchone()
        if not  order :  raise ValidationError('')
        if order['state'] != 1 : raise ValidationError("")

class profileForm(FlaskForm):
    firstName=StringField("First Name", validators=[DataRequired()])
    lastName=StringField("Last Name", validators=[DataRequired()])
    picture=FileField('Store Image', validators=[FileAllowed(["jpg", "jpeg","png"], 'Images only!') ])

class addressForm(FlaskForm):
    line1 = StringField("Emriate, Locality", validators=[DataRequired()])
    line2 = StringField("Street ", validators=[DataRequired()])
    line3 = StringField("Building Name, Apt. number", validators=[DataRequired()])
    phone = StringField("Conctact number", validators=[DataRequired(), Length(min=8, max=9), onlyNumeric])
    name = StringField("Name", validators=[DataRequired(), Length(max=20)])

class creditCardForm(FlaskForm):
    number = StringField("Credit Card number", validators=[DataRequired(),Length(min=16, max=16), onlyNumeric ])
    holder = StringField("Card Holder name", validators=[DataRequired(), Length(max=20)])
    expiry_month = IntegerField('Expiry Month', validators=[DataRequired()])
    expiry_year =IntegerField('Expiry Year', validators=[DataRequired()])
    card_type = StringField("Card type", validators=[DataRequired(), AnyOf(['VISA', 'MASTERCARD', 'AMERICAN EXPRESS'])])

    def validate(self):
        rv = FlaskForm.validate(self)
        today = date.today()
        if not rv:
            return False

        if  Query('cards').get().filter(email=session['EMAIL']).filter(number=self.number.data).fetchone() :
            flash('The card is alread saved')
            return False
        if (self.expiry_year.data < today.year) or (self.expiry_year.data==today.year and self.expiry_month.data < today.month) :
            flash('Your card has been expired hence invalid')
            return False

        return True        

class manageOrdersForm(FlaskForm):
    orderID = IntegerField("order-id", validators=[DataRequired(),isValidOrderID])
    cancelOrder = SubmitField("CANCEL ORDER")
    returnORder = SubmitField("RETURN ORDER")

class ResetPassword(FlaskForm):
    old_password = password = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField("Repeat Password", validators=[DataRequired()])
    