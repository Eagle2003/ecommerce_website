from flask import Blueprint, render_template, url_for, request, redirect, url_for, abort, flash, session
from nancy.sqlORM import Query, mysql
from nancy.auth.decrators import login_required
from .forms import cartForm, orderForm
from nancy.user.forms import addressForm
import json


shop_bp = Blueprint(
    'shop',    
     __name__,
    template_folder='templates',
    static_folder='static')

@shop_bp.route('/')
def landing():
    #Deinfe the promos 
    columns=["title", "content", "icon", "link"]
    # promos = [Query, getPromo(2,columns), getPromo(3, columns)]
    promos = Query('promos').get().filter(id__in = [1,2,3,4]).fetchall()
    
    #Define the showcase to be displayed 
    columns = ["id", "images"]
    image_loader = json.loads
    carousels = {
        "Jam to Great Tunes with Great Deals on Audio Producsts" : Query('products').get(columns=columns, limit=20).filter(subcategory="Audio").fetchall(images=image_loader),
        "This IPL season, get you'r game on with the Big Screen Action" : Query('products').get(columns=columns, limit=20).filter(subcategory="television").fetchall(images=image_loader) ,
        "Great Polos for all year round ": Query('products').get(columns=columns, limit=20).filter(item="Polos").fetchall(images=image_loader)
    }

    return render_template('shop/shop.html', searchbar = True, promos = promos,  carousels = carousels)

@shop_bp.route('/search')
def search():
    keyword = request.args.get('search', False)
    API = request.args.get('API')
    keyword = request.args.get('search', False)
    limit = request.args.get('limit', 20)
    offset = request.args.get('offset', 0)
    speed = request.args.get('speed')
    category = request.args.get('category')
    subCategory = request.args.get('subcategory')
    item = request.args.get('item')
    max_price = request.args.get('max_price')
    min_price = request.args.get('min_price')

    q = Query('products', multiple=True, dictionary=False).searchFor(key=keyword, columns=['name', 'description', 'item', 'subCategory', 'category'])
    filters = {
        "category" : q.get(columns="category", distinct=True).fetchall(),
        "subcategory" : q.get(columns="subcategory", distinct=True).fetchall(),
        "item" : q.get(columns="item", distinct=True).fetchall(),
    }
    if not keyword : return abort(404) 
    elif API  and speed=='DEEP' : 
        columns = "id, name, list_price, images, display_price, discount"
        q = Query('products').get(columns=columns, limit=limit, offset=offset).searchFor(key=keyword, columns=['name', 'description', 'item', 'subCategory', 'category'])
        if category : q = q.filter(category=category)
        if subCategory : q = q.filter(subcategory=subCategory)
        if item : q = q.filter(item=item)
        if max_price and max_price.isdigit() : q = q.filter(display_price__lt=int(max_price))
        if min_price and min_price.isdigit() : q = q.filter(display_price__gt=int(min_price))
        products = q.fetchall(images=json.loads)
        return json.dumps(products)
    elif API  and  speed=='QUICK' :
        keyword = "%"+keyword+"%" #Prepare teh kwywords
        name =  Query("products").get(columns="name").filter(name__like=keyword) 
        items = Query("items").get(columns="name").filter(name__like=keyword)
        subcategory = Query("subcategories").get(columns="name").filter(name__like=keyword)
        keys = Query("products", dictionary=False).union(name, items, subcategory, offset=0 , limit=20).fetchall()
        return json.dumps(keys)
    elif API and category : 
        val = json.dumps(Query('subcategories').get().filter(parent=keyword).fetchall())
        return val
    elif API and subCategory : 
        return json.dumps(Query('items').get().filter(parent=keyword).fetchall())
 
    return render_template('shop/search.html',searchbar= True,  keyword = keyword, filters=filters)


@shop_bp.route('product/<productID>', methods=["GET","POST"])
def product(productID ):
    form = cartForm()
    if form.validate_on_submit() :

        if not  session['AUTHENTICATED'] :
            flash("Please Login First before buying")
            redirect_url = url_for("auth.login") + "?redirect=" + url_for("shop.product", productID=productID)
            return redirect(redirect_url)

        available_quantity = Query("products").get(columns="quantity").filter(id=productID).fetchone()['quantity']
        request_quantity = form.quantity.data

        if available_quantity < request_quantity : 
            flash("Sorry Invalid Quantity")  
        else :                
            Query("cart").delete().filter(product_id=productID).filter(email=session['EMAIL']).execute()
            Query("cart").insert(email=session['EMAIL'], product_id=productID, quantity=form.quantity.data).commit()
            flash("Product added to cart, you can now continue shopping !")

    product = Query("products").get().filter(id=productID).fetchone(images=json.loads)
    return render_template('shop/product.html', searchbar= True,  product=product, form=form)
    

@shop_bp.route('/cart', methods=["POST", "GET"])
@login_required
def cart():
    redirect_url = request.args.get("redirect", None)
    form = cartForm()
    productID = form.productID.data
    
    #Form to edit the cart
    if form.validate_on_submit() : 

        # To Add to cart
        if form.add_to_cart.data and form.quantity.data :
            quantity = form.quantity.data 
            available_quantity = Query("products").get(columns="quantity").filter(id=productID).fetchone()['quantity']
            if available_quantity < quantity : 
                flash("Sorry Invalid Quantity")  
            else :                
                Query("cart").delete().filter(product_id=productID).filter(email=session['EMAIL']).execute()
                Query("cart").insert(email=session['EMAIL'], product_id=productID, quantity=quantity).commit()
                flash("Product Added To Cart")
        
        #Update quantity
        elif form.update_quantity.data and form.quantity.data :
            quantity = form.quantity.data
            Query("cart").update(quantity=quantity).filter(product_id=productID).filter(email=session['EMAIL']).execute().commit()
            flash("Qunatity Updated !")

        # To Delete form the cart
        elif form.delete_from_cart.data :
            Query("cart").delete().filter(product_id=productID).filter(email=session['EMAIL']).execute().commit()
            flash("Product Removed From Cart")

        # Save item for later
        elif form.saved_for_later.data  :
            Query("cart").update(saved_for_later=True).filter(product_id=productID).filter(email=session['EMAIL']).execute().commit()
            flash("Product Saved For later")
        
        # Move item back to cart
        elif form.move_to_cart.data :
            Query("cart").update(saved_for_later=False).filter(product_id=productID).filter(email=session['EMAIL']).execute().commit()
            flash("Product Added Back To Cart") 


        if redirect_url : return redirect(redirect_url)

    # Prepare the cart Info
    columns = ['product_id', 'quantity', 'saved_for_later']
    cart = Query("cart").get(columns=columns).filter(email=session['EMAIL'])
    #The Product Table 
    columns = ['name', 'images', 'display_price',  ('quantity','available_quantity'), ['ROUND(display_price*cart.quantity, 2) AS price'],]
    product = Query("products").get(columns=columns)
    #Join The Queries
    products  = cart.join(product, "products.id=cart.product_id").fetchall(images=json.loads)

    # Segreagte to cart and svaed for later
    cart = [product for product in products  if not product['saved_for_later'] ]
    saved_for_later =  [product for product in products if product['saved_for_later'] ]
    # Pricing
    pricing = {
        "Products Cost" : round(sum([ product['price'] for product in cart  ]),2),
        "Delivery Charges" : 10
    }
    
    total_bill = sum(price for price in pricing.values())

    return render_template(
        "shop/cart.html",
        form=form,
        cart=cart,
        saved_for_later=saved_for_later,
        total_bill = total_bill,
        pricing = pricing
        )

@shop_bp.route('/checkout', methods=["POST", "GET"])
@login_required
def checkout():
    product = request.args.get("productID")
    quantity = request.args.get("quantity")
    form = orderForm() 
    # Load a releveant product from get request else load from cart
    if product and  product.isdigit() and quantity and quantity.isdigit(): 
        product = Query("products").get().filter(id=int(product)).fetchone(images=json.loads)
        quantity = int(quantity)
    else : product = None

    if product  and  quantity  <= product['quantity']:
        product['product_id'] = product['id']
        product['quantity'] = quantity
        product['price'] = round(quantity*product['display_price'], 2)
        cart = [product]
    else : 
        # Prepare the cart Info
        columns = ['product_id', 'quantity', 'saved_for_later']
        cart = Query("cart").get(columns=columns).filter(email=session['EMAIL']).filter(saved_for_later=False)
        #The Product Table 
        columns = ['name', 'seller', 'images', 'display_price', 'list_price',   ('quantity','available_quantity'), ['ROUND(display_price*cart.quantity, 2) AS price'],]
        product = Query("products").get(columns=columns)
        #Join The Queries
        cart  = cart.join(product, "products.id=cart.product_id").fetchall(images=json.loads)
    
    # Detemine the pricing
    pricing = {
        "Products Cost" : round(sum([ product['price'] for product in cart  ]),2),
        "Delivery Charges" : 10
    }
    total_bill = sum(price for price in pricing.values())

    # Ensure there is something to buy
    if len(cart) == 0 : 
        flash("Please add something to the cart first !")
        return redirect(url_for('shop.cart'))

    # Process the payment
    if form.validate_on_submit() :
        columns = ["buyer", "seller", "product_id", "sale_price", "discount", "quantity", "status", "card_id", "address_id"]
        rows = []
        # Prepare the data to insert into cart 
        for item in cart  :
            Query("products").update(quantity__sub=item['quantity']).filter(id=item['product_id']).execute()
            rows.append([
                session["EMAIL"], 
                item['seller'], 
                item['product_id'], 
                item['price'], 
                round((item['list_price']*item['quantity'] - item['price']), 2), 
                item['quantity'], 
                "Order Placed", 
                form.card.data, 
                form.address.data ])
        
        ids = Query("orders").insertMany(columns, *rows).lastInsertId  #Insert Data to orders
        Query("cart").delete().filter(email=session['EMAIL']).filter(saved_for_later=False).execute() #Delete the ordes from the cart
        Query.commit()   #Finally Commit the changes
        l =  len(rows)-1
        ids = [i for i in range(ids-l, ids+1)]
        
        #To prepare the order success page
        # Prepare the cart Info
        columns = ['product_id', 'quantity', 'sale_price', 'status']
        order = Query("orders").get(columns=columns).filter(buyer=session['EMAIL']).filter(id__in = ids)
        #The Product Table 
        columns = ['name', 'seller', 'images', 'display_price', 'list_price',   ('quantity','available_quantity'), ['ROUND(display_price*orders.quantity, 2) AS price'],]
        product = Query("products").get(columns=columns)
        #Join The Queries
        orders  = order.join(product, "products.id=orders.product_id").fetchall(images=json.loads)

        return render_template("shop/order_sccessful.html", orders=orders)
        
            

    # Get user info
    cards = Query('cards').get().filter(email=session['EMAIL']).fetchall()
    addresses = Query('addresses').get().filter(email=session['EMAIL']).fetchall()

    return render_template('shop/checkout.html', cart=cart, pricing=pricing, total_bill=total_bill, cards=cards, addresses=addresses, form=form)

