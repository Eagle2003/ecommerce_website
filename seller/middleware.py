from functools import wraps
from flask import session, flash, redirect, url_for, current_app
from nancy.sqlORM import Query

def seller_only(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if  session.get("USER_TYPE") == "seller" : 
            seller =Query("sellers").get(columns=["name", "image", "cover_image"]).filter(email=session['EMAIL']).fetchone()
            session['SELLER_NAME'] = seller['name']
            session['SELLER_IMAGE'] = seller['image']
            session['SELLER_COVER'] = seller['cover_image']

            return f(*args, **kwargs)
        else : 
            flash("Please Join As A Seller")

            return redirect(url_for('seller.join'))
    return wrap

