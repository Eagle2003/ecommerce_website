from flask import Blueprint, render_template, url_for, request, redirect, url_for, abort, flash, session, current_app
from datetime import date
from hashlib import sha224
import json
import uuid
import os

from nancy.sqlORM import Query
from nancy.auth.decrators import login_required
from nancy.sqlORM import Query
from nancy.diskIO import saveFormDataToDisk, deleteFromDisk
from .forms import addressForm, creditCardForm, profileForm, manageOrdersForm, ResetPassword



user_bp = Blueprint(
    'user',    
     __name__,
    template_folder='templates',
    static_folder='static')


@user_bp.route('dashboard', methods=["POST","GET"])
@login_required
def dashboard ():
    user = Query("users").get().filter(email=session['EMAIL']).fetchone()
    orders_stats = Query("orders").get(columns="ROUND(SUM(discount),2) as saved, COUNT(*) as count ").filter(buyer=session['EMAIL']).fetchone()
    form = profileForm()
    
    # To update user profile
    if form.validate_on_submit():
        
        insert = {
            "name" : form.firstName.data,
            "last_name" : form.lastName.data
        }

        if form.picture.data : 
            insert['profile_picture'] = saveFormDataToDisk(current_app.config['USER_PROFILE_FOLDER'], form.picture.data)
            deleteFromDisk(current_app.config['USER_PROFILE_FOLDER'],  user['profile_picture'])
            session['PROFILE_PICTURE'] = insert['profile_picture']
        
        Query("users").update(**insert).filter(email=session['EMAIL']).execute().commit()
        flash('Profile Updated')
        return redirect(url_for('user.dashboard'))
    
        

    return render_template("user/dashboard.html", user=user, orders_stats=orders_stats, form=form)

@user_bp.route('reset_password', methods=["POST", "GET"])
@login_required
def reset_password() :
    form = ResetPassword()
    if form.validate_on_submit() : 
        password = sha224(form.old_password.data.encode()).hexdigest()
        print(password)
        if Query("users").get(['password']).filter(email=session['EMAIL']).fetchone()['password'] == password:
            password = sha224(form.password.data.encode()).hexdigest()
            Query("users").update(password=password).filter(email=session['EMAIL']).execute().commit()
            flash("Pssword Has Been Updated !")
            return redirect(url_for('user.dashboard'))
        else : 
            form.old_password.errors += ["Invlaid Password !"]
    
    return render_template("user/reset_password.html", form=form)

@user_bp.route('address', methods=["POST", "GET"])
@login_required
def address():
    redirect_url = request.args.get("redirect",None)
    form = addressForm()
    form.validate_on_submit()
    delete = request.args.get('delete')
    if delete : 
        try :
            address_id = int(delete)
            Query("addresses").delete().filter(email=session['EMAIL']).filter(id=address_id).execute().commit()
            flash("Address has been deleted !")
            return redirect(url_for('user.address'))
        except Exception as e : print("Couldnt Delete Card", e)
    
    if form.validate_on_submit() :
        print('form validated')
        Query("addresses").insert(email=session['EMAIL'], name=form.name.data, line1=form.line1.data, line2=form.line2.data, line3=form.line3.data, phone=form.phone.data).commit()
        flash("Adress has been succesfully saved !")
    elif request.method == "POST" :
        key, error = list(form.errors.items())[0]
        key = form[key].name
        flash(f"Adding address failed because in {key} field, {error[0]}")
        
    saved_addresses = Query("addresses").get().filter(email=session["EMAIL"]).fetchall()
    return redirect(redirect_url) if redirect_url else render_template("user/address.html", addresses=saved_addresses, form=form)

@user_bp.route('cards', methods=["POST", "GET"])
@login_required
def cards():
    form = creditCardForm()
    redirect_url = request.args.get('redirect')
    delete = request.args.get('delete')
    if delete : 
        try :
            card_id = int(delete)
            Query("cards").delete().filter(email=session['EMAIL']).filter(id=card_id).execute().commit()
            flash("Card has been deleted !")
            return redirect(url_for('user.cards'))
        except Exception as e : print("Couldnt Delete Card", e)
    if form.validate() :
        insert = {
            "email": session['EMAIL'],
            "number" : form.number.data,
            "holder" : form.holder.data,
            "card_type" : form.card_type.data,
            "expiry_month" : form.expiry_month.data,
            "expiry_year" : form.expiry_year.data
        }
        Query('cards').insert(**insert).commit()
        flash('Your card has been saved')
    
    cards = Query('cards').get().filter(email=session['EMAIL']).fetchall()
    return redirect(redirect_url) if redirect_url else render_template('user/cards.html',cards=cards, form=form)

@user_bp.route('orders', methods=["POST", "GET"])
@login_required
def orders():
    
    form = manageOrdersForm()
    columns = ["id", "product_id", "quantity", "state", "date_of_return", "date_of_completion",  "sale_price", "date_of_issue", "status"]
    orders = Query('orders').get(columns=columns).filter(buyer=session['EMAIL']).sort("date_of_issue",order="DESC")
    product = Query('products').get(columns=['images', 'name'])
    orders = orders.join(product, "orders.product_id = products.id").fetchall(images=json.loads)


    if form.validate_on_submit() : 
        if form.cancelOrder.data : 
            Query('orders').update(state=-1, status="User has cancelled Order", date_of_return__exp='current_timestamp').filter(buyer=session['EMAIL']).filter(id=form.orderID.data).execute()
            product_id = Query("orders").get(columns="product_id").filter(buyer=session['EMAIL']).filter(id=form.orderID.data).fetchone()['product_id']
            Query('products').update(quantity__add=1).filter(id=product_id).execute().commit()
            flash('Order Cancelled')
        elif form.returnOrder.data : 
            Query('orders').update(state=-3, status="User has Requested For the Item to be returned", date_of_return__exp='current_timestamp').filter(buyer=session['EMAIL']).filter(id=form.orderID.data).execute().commit()
            flash('Order Return Requested')
        return redirect(url_for('user.orders'))

    
    return render_template("user/orders.html", orders=orders, form=form)

@user_bp.route('history', methods=["POST", "GET"])
@login_required
def history():
    return "Youre viewing history"

@user_bp.route('watchlist', methods=["POST", "GET"])
@login_required
def watchlist():
    return "Youre viewing history"