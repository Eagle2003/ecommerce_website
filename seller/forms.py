from flask import session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField,  FileAllowed, FileRequired
from wtforms import StringField, SubmitField, FloatField, IntegerField, MultipleFileField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Email, regexp,  ValidationError, NumberRange, InputRequired
from nancy.sqlORM import Query


def isStoreNameAvailable(form, field):
        if  Query('sellers').get().filter(name=field.data).fetchone() : raise ValidationError('Sorry the name is already taken !')

def isTradeLicenseUsed(form, field):
    if Query('sellers').get().filter(trade_license = field.data).fetchone() : raise ValidationError("The Trade lIcense is in use ")

def isValidProductID (form, field) : 
        if not Query('products').get().filter(seller=session['SELLER_NAME']).filter(id=field.data).fetchone() : 
            raise ValidationError('Ivnalid Product ID')

def isValidOrderID (form, field):
    def isValidProductID (form, field) :
        order =  Query('orders').get().filter(seller=session['SELLER_NAME']).filter(id=field.data).fetchone()
        if not  order :  raise ValidationError('')
        if order['state'] != 1 : raise ValidationError("")

    

class AddProduct(FlaskForm) :
    name = StringField("Product Name", validators=[DataRequired()])
    category = StringField("Category", validators=[DataRequired()])
    subCategory = StringField("Sub-Category", validators=[DataRequired()])
    item = StringField("Item Type", validators=[DataRequired()])
    price = FloatField("Item Price", validators=[DataRequired()])
    quantity = IntegerField("Availble Quantity", validators=[InputRequired()])
    manufacturer = StringField("Manufacturer", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=20, max=200)])
    images = MultipleFileField("Images", validators=[DataRequired(), FileAllowed(["jpg", "jpeg","png"], 'Images only!')])

    
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if not Query("categories").get().filter(name=self.category.data).fetchone()  :
            self.category.errors += ["Invalid Category"]
        elif not Query("subcategories").get().filter(name=self.subCategory.data).filter(parent=self.category.data).fetchone() :
            self.subCategory.errors += ["Invalid Sub-category "]
        elif (not Query("items").get().filter(name=self.item.data).filter(name=self.subCategory.data).fetchone()) or Query("items").get().filter(name=self.item.data).fethcone() : 
            self.item.errors += ['Sorry this Item Type is already in use']
        

        return True

class EditProductsForms(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    active = BooleanField("Product Acitve ?")
    price = FloatField("Item Price", validators=[DataRequired()])
    discount = FloatField("Discount", validators=[DataRequired(), NumberRange(min=0, max=99)])
    quantity = IntegerField("Availble Quantity", validators=[InputRequired()])
    manufacturer = StringField("Manufacturer", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=20, max=200)])
    images = MultipleFileField("Images", validators=[FileAllowed(["jpg", "jpeg","png"], 'Images only!')])

class UpdateSellerForm(FlaskForm):
    name = StringField("Store Name", validators=[DataRequired()])
    profile_image = FileField('Store Image', validators=[ FileAllowed(["jpg", "png"], 'Images only!') ])
    cover_image = FileField('Cover Image', validators=[FileAllowed(["jpg", "png"], 'Images only!') ])

class OrdersForm(FlaskForm):
    order_id = IntegerField("", validators=[DataRequired(), isValidOrderID])
    cancelOrder = SubmitField("Cancel Order Request ")
    orderPrepared = SubmitField("Order Ready For Collection")

class NewSeller(FlaskForm):
    name = StringField('Seller Name', validators=[DataRequired(), isStoreNameAvailable])
    tradeLicense = StringField('Trade License', validators=[DataRequired(), Length(min=10, max=10), isTradeLicenseUsed])
    image = FileField('Store Image', validators=[FileRequired(), FileAllowed(["jpg", "png"], 'Images only!') ])
    submit = SubmitField('Submit')

    
    
    



