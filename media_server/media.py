from flask import Flask, Blueprint,  make_response, current_app, abort, send_from_directory, session
from werkzeug.utils import secure_filename
import cv2 
import os

from nancy.auth.decrators import login_required
from nancy.seller.middleware import seller_only
from nancy.sqlORM import Query

media_bp = Blueprint(
    "media", 
    __name__,
    template_folder='template',
    static_folder='static'
    )




@media_bp.route('user/profile_pic/<scale>/') 
@login_required
def user_profile(scale):
    pic = Query("users").get(["profile_picture"]).filter(email=session['EMAIL']).fetchone()['profile_picture']
    if not pic : pic = "default.png"
    if scale == "100" : return send_from_directory(current_app.config['USER_PROFILE_FOLDER'],pic)
    path = os.path.join(current_app.config['USER_PROFILE_FOLDER'], pic)
    try : image_data = resize_image(path, int(scale))
    except : return abort(404)
    return  image_data

@media_bp.route('seller/images/<root>/<scale>/<filename>/') 
def images(root, scale, filename='default.jpg'):
    # Get the root directory
    if root=="storeProfile" : root=current_app.config['SELLER_PROFILE_FOLDER']
    elif root=="storeCover" : root=current_app.config['SELLER_COVER_FOLDER']
    elif root=="productImages" : root=current_app.config['THUMBNAILS_FOLDER']
    elif root=='ui' : root=current_app.config["UI_FOLDER"]
    else : abort(404)
    if scale == "100" : return send_from_directory(root, filename)
    
    path = os.path.join(root, secure_filename(filename))
    print(path)
    try : image_data = resize_image(path, int(scale))
    except Exception as e :
        print(e)
        return abort(404)
    return  image_data


@media_bp.route('/shop/banners/<file>')
def banners (file:str) :
    return send_from_directory(current_app.config['BANNERS_FOLDER'], file)

    
# Function to scale down an image
def resize_image(path, scale_percent) :
    if os.path.isfile(path) :
        #Scale Down the Image
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        # resize image
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

        _, buffer = cv2.imencode('.jpg', resized)
        response = make_response(buffer.tobytes())
        response.headers['Content-type'] = "image/jpeg"
        return response
    else : raise Exception("Invlaid path")


    
    
