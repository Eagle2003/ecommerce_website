from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from nancy.sqlORM import Query
#Login Form 

def isEmailAvailable(form, field) :
    if Query("users").get().filter(email=field.data).filter(activated=True).fetchone() : raise ValidationError("The Email is already in use")

def isEmailValid(form, field) :
    if not  Query("users").get().filter(email=field.data).filter(activated=True).fetchone() : raise ValidationError("The Email isnt either Linked iwth Nancy or isnt activated yet !")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message= "Sorry Please Enter a Valid Email")])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

#SignUp Form 
class SignUpForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), isEmailAvailable])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField("Repeat Password", validators=[DataRequired()])
    submit = SubmitField('Register')

# Reset Password 
class ResetPasswordForm(FlaskForm) :
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField("Repeat Password", validators=[DataRequired()])
    submit = SubmitField('Register')

class RequestResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), isEmailValid])
    

    