from flask import Blueprint, render_template, request, abort, session, current_app, flash, redirect, url_for
from nancy.auth.decrators import login_required
from nancy.seller.middleware import seller_only
from nancy.sqlORM import Query
from nancy.diskIO import saveFormDataToDisk, deleteFromDisk
from flask_mysql_connector import MySQL
from .forms import NewSeller, AddProduct, EditProductsForms, OrdersForm, UpdateSellerForm
import json
import os
import uuid

seller_bp = Blueprint(
    'seller',
    __name__,
    template_folder='templates',
)

mysql = MySQL(current_app)

@seller_bp.route('join', methods=["POST", "GET"])
@login_required
def join (): 
    form = NewSeller()
    if form.validate_on_submit() :
        #Write the image to disk
        image_data = form.image.data
        image_ext = image_data.filename.split(".")[-1]
        file_name  = uuid.uuid4().hex +"."+ image_ext
        path = os.path.join(current_app.config['SELLER_PROFILE_FOLDER'], file_name)
        image_data.save(path)
    
        Query("sellers").insert(name=form.name.data, email=session['EMAIL'], trade_license=form.tradeLicense.data, image=file_name)
        Query("users").update(user_type='seller').filter(email=session['EMAIL']).execute().commit()
        session['USER_TYPE'] = "seller"
        return redirect(url_for('seller.dashboard'))
        
    return render_template("seller/join.html", form = form)

@seller_bp.route('dashboard', methods=["POST","GET"])
@login_required
@seller_only
def dashboard():
    store = Query('sellers').get().filter(email=session['EMAIL']).fetchone()
    form = UpdateSellerForm()
    if form.validate_on_submit() : 
        print('form validated !')
        update = {}
        # Update Store Name
        if form.name.data != store['name'] : update['name'] = form.name.data
        #Update Store Image
        if request.files.getlist('profile_image')[0].filename != '' : 
            image = request.files.getlist('profile_image')[0]
            update['image'] = saveFormDataToDisk(current_app.config['SELLER_PROFILE_FOLDER'], image)
            deleteFromDisk(current_app.config['SELLER_PROFILE_FOLDER'], store['image'])
        #update Store Cover
        if request.files.getlist('cover_image')[0].filename != '' : 
            image = request.files.getlist('cover_image')[0]
            if store['cover_image'] == 'default.jpg'or deleteFromDisk(current_app.config['SELLER_COVER_FOLDER'], store['cover_image']) : 
                update['cover_image'] = saveFormDataToDisk(current_app.config['SELLER_COVER_FOLDER'], image)
        #Execute an update if there is a change !
        if len(update) != 0 :  
            Query('sellers').update(**update).filter(name=session['SELLER_NAME']).execute().commit()
            flash('Your Profile Has Been Updated !')
            return redirect(url_for('seller.dashboard'))
    else : print(form.errors)
            
    user = Query('users').get().filter(email=session['EMAIL']).fetchone()
    return render_template('seller/dashboard.html', user=user, store=store, form=form)


@seller_bp.route('products', methods=["POST", "GET"])
@login_required
@seller_only
def products():
    state = request.args.get("State")
    category = request.args.get("Category")
    SubCategory = request.args.get("SubCategory")
    item = request.args.get("item")
    minimum = request.args.get("Minimum Price")
    maximum = request.args.get("Maximumum Price")
    page = request.args.get('page')
    page = int(page) if page else 0
    limit = 10
    
    q = Query("products", multiple=True).get(limit=limit, offset=page*limit).filter(seller=session['SELLER_NAME'])
    if state == "Active": q.filter(active=True)
    elif state == "Out Of Stock" : q.filter(quantity = 0)
    elif state == "De-Activated" : q.filter(active=False)
    if category  : q.filter(category=category)
    if SubCategory  : q.filter(SubCategory=SubCategory)
    if item  : q.filter(item=item)
    if minimum  : q.filter(display_price__gte=minimum)
    if maximum : q.filter(display_price__get=maximum)

    products = q.fetchall(images=json.loads)
    pages = (q.get("count(*) AS count").fetchone()['count']//limit)+1
    filters= {
        "options" : {
            'State' : ["Active", "Out Of Stock", "Disabled"],
            'Category' :  Query("products", dictionary=False).get(columns=["category"], distinct=True).filter(seller=session['SELLER_NAME']).fetchall(flatten=True),
            'SubCategory' :  Query("products", dictionary=False).get(columns=["subcategory"], distinct=True).filter(seller=session['SELLER_NAME']).fetchall(flatten=True),
            "item" :   Query("products", dictionary=False).get(columns=["item"], distinct=True).filter(seller=session['SELLER_NAME']).fetchall(flatten=True),
        },
        "range" :  ["Minimum Price", "Maximum Price"]        
    }

    return render_template('seller/products.html', products=products, filters=filters, pages=pages, current_page=page)


@seller_bp.route('products/add', methods=["POST","GET"])
@login_required
@seller_only
def addProduct() : 
    form = AddProduct()
    if form.validate() :
        images = []
        if not Query("items").get().filter(name=form.item.data).fetchone():
            Query("items").insert(name=form.item.data, parent=form.subCategory.data)
        for image in request.files.getlist('images'): 
            images.append(saveFormDataToDisk(current_app.config['THUMBNAILS_FOLDER'], image))
        insert = {
            "name" : form.name.data,
            "seller" : session['SELLER_NAME'],
            "category" : form.category.data,
            "subcategory" : form.subCategory.data,
            "item" : form.item.data,
            "list_price" : form.price.data,
            "display_price" : form.price.data,
            "discount" : 0, 
            "quantity" : form.quantity.data,
            "description" : form.description.data,
            "manufacturer" : form.manufacturer.data,
            "images" : json.dumps(images),

        }
        product_id = Query("products").insert(**insert).lastInsertId
        Query.commit()
        return render_template('seller/addProductSuccess.html', product_id=product_id)

    elif (request.method == "POST") : flash("Your Form has some errors, please review")
    print(form.errors)
    categories = Query('categories').get().fetchall()
    return render_template ('seller/addProduct.html', form=form, categories=categories)

@seller_bp.route('products/update/<productID>', methods=["POST","GET"])
@login_required
@seller_only
def updateProduct(productID) :
    if not productID.isdigit() : abort(404)
    form = EditProductsForms()
    product = Query("products").get().filter(seller=session['SELLER_NAME']).filter(id=int(productID)).fetchone(images=json.loads)

    if form.validate_on_submit() : 
        update = {
            "name" : form.name.data,
            "active" : form.active.data,
            "list_price" : form.price.data,
            "quantity" : form.quantity.data,
            "discount" : form.discount.data,
            "display_price__exp" : "list_price-(list_price*(discount/100))",
            "manufacturer" : form.manufacturer.data,            
        }

        if request.files.getlist('images')[0].filename != '' : 
            images =[]
            for image in request.files.getlist('images'): 
                images.append(saveFormDataToDisk(current_app.config['THUMBNAILS_FOLDER'], image))
            for image in product['images'] : 
                deleteFromDisk(current_app.config['THUMBNAILS_FOLDER'], image)
            update['images'] = json.dumps(images)
        Query("products").update(**update).filter(seller=session['SELLER_NAME']).filter(id=productID).execute().commit()
        flash("Product Updated")
        return redirect(url_for('seller.products'))
    
    else : print(form.errors)                     
    return render_template("seller/updateProduct.html", form=form, product=product) if product else abort (404)



@seller_bp.route('orders', methods=["POST","GET"])
@login_required
@seller_only
def orders():
    form = OrdersForm()
    state = request.args.get("Order State")
    category = request.args.get("Category")
    subcategory = request.args.get("SubCategory")
    items= request.args.get("item")
    page = request.args.get('page')
    page = int(page) if page and page.isdigit() else 0
    limit = 10

    if form.validate_on_submit() :
        if form.cancelOrder.data :
            q = Query("orders").update(state=-1, status="Order Has Been Cancelled By The Seller", date_of_return__exp="current_timestamp")
            flash("Order has been cancelled !")
        elif form.orderPrepared.data :
            q = Query("orders").update(state=4, status="Order Has Been Delivered", date_of_completion__exp="current_timestamp")
            flash("Collection for the order will arrive shortly")
        q.filter(seller=session['SELLER_NAME']).filter(id=form.order_id.data).execute().commit()
        return redirect(url_for('seller.orders'))
    
    # The Order Query
    columns = ["id", "buyer", "status", "date_of_completion", "date_of_return", "sale_price", "date_of_issue"]
    order = Query('orders', multiple=True).get(columns=columns, limit=limit, offset=page*limit).filter(seller=session['SELLER_NAME']).sort(column='date_of_issue')
    # The Product Query
    columns = [("id", "product_id"), "name", "images", "category", "subcategory", "item"]
    product = Query("products").get(columns=columns)
    # The Address Query
    columns = ["line1", "line2", "line3"]
    address = Query('addresses').get(columns=columns)
    

    if state == 'Completed'  : order.filter(state__in=[4, -1, -2, -4])
    elif state == 'Proccesing'  : order.filter(state__not_in=[4, -1, -2, -4])
    if category : product.filter(category=category)
    if subcategory : product.filter(subcategory=subcategory)
    if items : product.filter(item=items)

    #The Join
    orders = order.join(product, "products.id = orders.product_id").join(address, "addresses.id = orders.address_id").fetchall(images=json.loads)
    pages = (order.get(columns='count(*) as count').fetchone()['count']//limit)+1

    #Get the disitncts
    order = Query("orders").get().filter(seller=session['SELLER_NAME'])
    filters= {
       "options" : {
            'Order State' : ["Completed", "Proccesing"],
            'Category' :  Query("products", dictionary=False).get(columns=["category"]).join(order, "orders.product_id = products.id", distinct=True).fetchall(flatten=True),
            'SubCategory' :  Query("products", dictionary=False).get(columns=["subcategory"]).join(order, "orders.product_id = products.id", distinct=True).fetchall(flatten=True),
            "item" :   Query("products", dictionary=False).get(columns=["item"]).join(order, "orders.product_id = products.id", distinct=True).fetchall(flatten=True)
       },
    }
    return render_template('seller/orders.html', orders=orders, form=form, filters=filters, pages=pages, current_page=page)



@seller_bp.route('sellerAPI')
@login_required
def sellerAPI() :
    storeName = request.args.get('store', None )
    if storeName : 
        store = Query("sellers").get().filter(name=storeName).fetchone()
        return json.dumps(store)
    else : abort(404)



                                                                               