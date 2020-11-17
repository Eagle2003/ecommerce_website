from flask import Blueprint, render_template, flash, redirect, session, url_for, Flask, current_app, abort, request
from functools import wraps
from hashlib import sha224
from secrets import token_urlsafe
from flask_mail import Mail, Message
from nancy.sqlORM import Query
from nancy.mailer import sendActivationMail, sendPasswordResetMail
from .decrators import login_required, not_logged_in
from .forms import LoginForm, SignUpForm, ResetPasswordForm, RequestResetPasswordForm
from mysql.connector.errors import IntegrityError
from datetime import datetime, timedelta


auth_bp = Blueprint(
    'auth',
     __name__,
    template_folder='templates',
    static_folder='static')


mail = Mail(current_app)


# Login Route
def deltaTime(hours) :
    delta_time = datetime.now() - timedelta(hours=hours)
    strof_delta_time  = delta_time.strftime('%Y-%m-%d  %H:%M:%S')
    return strof_delta_time

@auth_bp.route('/login', methods=["GET","POST"])
@not_logged_in
def login():
    # Direct user to landing if logged in 
    if session.get('AUTHENTICATED',None) : return redirect(url_for('shop.landing'))
    redirect_url = request.args.get("redirect", None)
    form = LoginForm()
    
    # Check form validation
    if form.validate_on_submit() : 
        user = Query("users").get().filter(email=form.email.data).fetchone()

        if not user  :
            form.email.errors = ["Sorry we couldnt find a account linked to your id"]
         
        elif not user['password'] == sha224(form.password.data.encode('UTF-8')).hexdigest() :
            form.password.errors = ["The password is not valid for the give email"]
        
        elif not user['activated']  :
            flash("Please activate your account from the link to sent your registred email adresss")
        
        else : 
            flash("Wlecome back, " + user['name'])
            session['AUTHENTICATED'] = True
            session['EMAIL'] = user['email']
            session['PROFILE_PICTURE'] = user['profile_picture']
            session['USER_TYPE'] = user['user_type']
            return redirect(redirect_url) if redirect_url else  redirect(url_for('shop.landing'))
            

    
    #Return back to index if invalid 
    return   render_template("auth/login.html", form  = form)
    
@auth_bp.route('/logout')
@login_required
def logout():
    session['AUTHENTICATED'] = False
    session['EMAIL'] = None
    session['USERNAME'] = None
    flash('Youve been Succesfully Logged out !')
    return redirect(url_for('auth.login'))

#Regestration
@auth_bp.route('/register', methods=["GET","POST"])
@not_logged_in
def register():
    form = SignUpForm()
    
    if form.validate_on_submit() :
        # First clear off all the unactivated accounts for late an hour
        Query('users').delete().filter(date_of_join__ltHour = 4).filter(activated=False).execute().commit()
        # addUser(form.email.data,  form.password.data)
        hashed_password = sha224(form.password.data.encode()).hexdigest()
        Query('users').insert(email = form.email.data, password=hashed_password).commit()
    
        token = form.email.data + token_urlsafe(32)
        Query('activation').insert(activation_code = token, email = form.email.data).commit()
     
        #Initiate a messages to user to activate account
        sendActivationMail(form.email.data, token)
        flash("You're Sign Up is Successful. Please activate your account from the link sent to your mail.")
        return redirect('login')
        

    return render_template("auth/register.html", form = form)

# activates the account from the token
@auth_bp.route('activate/<token>')
def activate(token) :
    email = Query('activation').get(columns="email").filter(activation_code = token).fetchone()
    if email :
        email = email['email']
        Query('users').update(activated=True).filter(email=email).execute()
        Query('activation').delete().filter(activation_code=token).execute().commit()
    else : 
        flash('Youre account is alredy activated !')
        return redirect(url_for('auth.login'))
    flash('Youre account has been activatesd ')
    return redirect(url_for('auth.login'))


@auth_bp.route('reset', methods=["GET","POST"])
def requestResetPassword():
    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        token = form.email.data + token_urlsafe(32)
        Query("reset_password").delete().filter(time_of_issue__lt=deltaTime(4), email=form.email.data).execute() #Delee request of the givrn email or of time delta 4 hourss
        Query("reset_password").insert(email=form.email.data, token=token).commit()
        sendPasswordResetMail(form.email.data, token)
        flash('A Password Reset mail has been send to you mail id')

    return render_template('auth/request_reset_password.html', form=form)


@auth_bp.route('reset/<token>', methods=["POST","GET"])
def resetPassword(token):
    form = ResetPasswordForm()
    print(token)
    if form.validate_on_submit() :
        email = Query("reset_password").get().filter(token=token).fetchone()
        Query("reset_password").delete().filter(time_of_issue__ltHour=5).execute()

        if email : 
            email = email['email']
            Query("reset_password").delete().filter(email=email).execute()

            password = sha224(form.password.data.encode()).hexdigest()
            Query("users").update(password=password).filter(email=email).execute().commit()
            flash('Youre password has been updated !')
            return redirect(url_for('auth.login'))
        else : 
            flash('Your Password Reset Link has expired')
    
    return render_template('auth/reset_password.html', form=form)
