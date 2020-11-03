from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, ValidationError, EqualTo, Regexp, Optional
from wtforms.widgets import HiddenInput
from models import Users, Cantakecare
from datetime import date, datetime
from _datetime import timedelta

def is_valid_name(form, field):
    if not all(map(lambda char: char.isalpha(), field.data)):
        raise ValidationError('This field should only contain alphabets')

def is_valid_contact(self, contact):
    contact = (Users.query.filter_by(contact=contact.data).first())
    if contact:
        raise ValidationError('That contact is already being registered. Please choose a different one.')

# def is_valid_number(form, field):
#     if not all(map(lambda char: char.isnumber(), field.data)):
#         raise ValidationError('This field should only contain numbers')
    
# def is_valid_type(form, field):
#     if not all(map(lambda type: type == "pet owner" or type == "admin" or type == "caretaker", field.data)):
#         raise ValidationError('Please input valid user types such as pet owner, admin and caretaker')
    
def agrees_terms_and_conditions(form, field):
    if not field.data:
        raise ValidationError('You must agree to the terms and conditions to sign up')


class RegistrationForm(FlaskForm):
    roles = [('petowner', 'Pet Owner'), ('admin', 'Admin'), ('caretaker', 'Caretaker')]
    username = StringField(
        label='Name',
        validators=[InputRequired(), is_valid_name],
        render_kw={'placeholder': 'Name', 'class': 'input100'}
    )
    usertype = SelectField(
        label='User Type',
        choices=[('caretaker', 'Caretaker'), ('petowner', 'Pet Owner'), ('admin', 'Administrator')],
        validators=[InputRequired()],
        render_kw={'placeholder': 'User Type', 'class': 'input100'}
    )
    contact = IntegerField(
        label='Contact',
        validators=[InputRequired(), is_valid_contact],
        render_kw={'placeholder': 'Contact', 'class': 'input100'}
    )
    password = PasswordField(
        label='Password',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Password', 'class': 'input100'}
    )
    confirm_password = PasswordField(
        label='Confirm Password',
        validators=[InputRequired(), EqualTo('password')],
        render_kw={'placeholder': 'Confirmed Password', 'class': 'input100'}
    )
    credit_card = StringField(
        label='Credit Card',
        render_kw={'placeholder': 'Credit Card', 'class': 'input100'}
    )
    postal_code = IntegerField(
        label='Postal Code',
        render_kw={'placeholder': 'Postal Code', 'class': 'input100'}
    )
    is_part_time = BooleanField(
        label='Is Part Time',
        render_kw={'placeholder': 'Is Part Time'}
    )

class PetForm(FlaskForm):
    petname = StringField(
        label='Pet Name',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Petname', 'class': 'input100'}
    )
    category = StringField(
        label='Category',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Category', 'class': 'input100'}
    )
    age = IntegerField(
        label='Age',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Age', 'class': 'input100'}
    )

class PetUpdateForm(FlaskForm):
    petname = StringField(
        label='Pet Name',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Petname', 'class': 'input100'}
    )
    contact = IntegerField(
        widget=HiddenInput(),
        label='Contact',
        validators=[InputRequired(), is_valid_contact],
        render_kw={'placeholder': 'Contact', 'class': 'input100'}
    )
    category = StringField(
        label='Category',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Crredit Card', 'class': 'input100'}
    )
    age = IntegerField(
        label='Age',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Age', 'class': 'input100'}
    )
    
class UserUpdateForm(FlaskForm):
    username = StringField(
        label='Username',
        render_kw={'placeholder': 'Username', 'class': 'input100'}
    )
    credit_card = StringField(
        label='Category',
        render_kw={'placeholder': 'Credit Card', 'class': 'input100'}
    )
    is_part_time = BooleanField(
        label='Is Part Time',
        render_kw={'placeholder': 'Is Part Time'}
    )
    postal_code = StringField(
        label='Postal Code',
        render_kw={'placeholder': 'Postal Code', 'class': 'input100'}
    )
    password = PasswordField(
        label='New Password',
        render_kw={'placeholder': 'New Password', 'class': 'input100'}
    )
    confirm_password = PasswordField(
        label='Confirm New Password',
        validators=[EqualTo('password')],
        render_kw={'placeholder': 'Confirmed New Password', 'class': 'input100'}
    )

class PetUpdateForm(FlaskForm):	
    petname = StringField(	
        label='Petname',	
        validators=[InputRequired()],	
        render_kw={'placeholder': 'Petname', 'class': 'input100'}	
    )	
    category = StringField(	
        label='Category',	
        validators=[InputRequired()],	
        render_kw={'placeholder': 'Category', 'class': 'input100'}	
    )	
    age = IntegerField(	
        label='Age',	
        validators=[InputRequired()],	
        render_kw={'placeholder': 'Age', 'class': 'input100'}	
    )

class LoginForm(FlaskForm):
    contact = IntegerField(
        label='Contact',
        validators=[InputRequired()],
        
        render_kw={'placeholder': 'Contact', 'class': 'input100'}
    )
    password = PasswordField(
        label='Password',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Password', 'class': 'input100'}
    )

class CaretakerForm(FlaskForm):
        username = StringField(
        label='Username',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Username', 'class': 'input100'}
    )
        password = PasswordField(
        label='Password',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Password', 'class': 'input100'}
    )
        postalcode = StringField(
        label='PostalCode',
        validators=[InputRequired()],
        render_kw={'placeholder': 'PostalCode', 'class': 'input100'}
    )

class Bid:
    def __init__(self, pcontact, ccontact):
        self.pcontact = pcontact
        self.ccontact = ccontact
        self.petname = None
        self.startday = None
        self.endday = None
        self.paymentmode = None
        self.deliverymode = None

class BiddingForm(FlaskForm):
    ccontact = IntegerField(
        label='Ccontact',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Ccontact', 'class': 'input100'}
    )   
    
    
    # ccontact = SelectField(
    #     u'Cantakecare',
    #     coerce=int
    # )
    
    petname = StringField(
        label='Petname',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Petname', 'class': 'input100'}
    )
    startday = DateField(
        label='startday',
        validators=[InputRequired()],
        render_kw={'placeholder': 'startday', 'class': 'input100'}
    )
    endday = DateField(
        label='endday',
        validators=[InputRequired()],
        render_kw={'placeholder': 'endday', 'class': 'input100'}
    )
    paymentmode = StringField(
        label='Paymentmode',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Paymentmode', 'class': 'input100'}
    )
    deliverymode = StringField(
        label='Deliverymode',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Deliverymode', 'class': 'input100'}
    )
    # def edit_user(request, ccontact, petname):
    #     caretaker = Cantakecare.query.get(ccontact)
    #     category = Pets.query.filter_by(petname = petname.data)
    #     form = BiddingForm(request.POST, obj=caretaker)
    #     form.ccontact.choices = [(x.ccontact, x.ccontact) for x in Cantakecare.query.order_by('ccontact').filter_by(category=category)]
    
    def validate_on_submit(self):
        result = super(BiddingForm, self).validate()
        if (self.startday.data - self.endday.data >= timedelta(minutes=1)):
            flash("End date cannot be earlier than Start date.")
            return False
        elif (date.today() - self.startday.data >= timedelta(minutes=1)):
            flash("Start date cannot be earlier than current date.")
            return False
        else:
            return True
   
class ReviewForm(FlaskForm):
    pcontact = StringField(
    label='Pcontact',
    validators=[InputRequired()],
    render_kw={'placeholder': 'Pcontact', 'class': 'input100'}
    )
    ccontact = IntegerField(
        label='Ccontact',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Ccontact', 'class': 'input100'}
    )
    petname = StringField(
        label='Petname',
        validator=[(InputRequired())],
        render_kw={'placeholder': 'Petname', 'class': 'input100'}
    )
    rating = IntegerField(
        label='Petname',
        validators=[InputRequired()],
        render_kw={'placeholder': 'rating'}
    )
    review = StringField(
        label='Review',
        validators=[InputRequired()],
        render_kw={'placeholder': 'Review', 'class': 'input200'}
    )

class ProfileForm(FlaskForm):
    username = StringField(
        label='Name',
        validators=[InputRequired(), is_valid_name],
        render_kw={'placeholder': 'Name', 'class': 'input100'}
    )

    
class AvailableForm(FlaskForm):
    startday = DateField(
        label='startday',
        validators=[InputRequired()],
        default=date.today(), 
        format='%Y-%m-%d',
        render_kw={'placeholder': 'startday', 'class': 'input100'}
    )
    endday = DateField(
        label='endday',
        validators=[InputRequired()],
        default=date.today(), 
        format='%Y-%m-%d',
        render_kw={'placeholder': 'endday', 'class': 'input100'}
    )
    def validate_on_submit(self):
        result = super(AvailableForm, self).validate()
        if (self.startday.data - self.endday.data >= timedelta(minutes=1)):
            flash("End date cannot be earlier than Start date.")
            return False
        elif (date.today() - self.startday.data >= timedelta(minutes=1)):
            flash("Start date cannot be earlier than current date.")
            return False
        else:
            return True

class AvailableUpdateForm(FlaskForm):
    startday = DateField(
        label='startday',
        validators=[InputRequired()],
        default=date.today(), 
        format='%Y-%m-%d',
        render_kw={'placeholder': 'startday', 'class': 'input100'}
    )
    endday = DateField(
        label='endday',
        validators=[InputRequired()],
        default=date.today(), 
        format='%Y-%m-%d',
        render_kw={'placeholder': 'endday', 'class': 'input100'}
    )
    def validate_on_submit(self):
        result = super(AvailableUpdateForm, self).validate()
        if (self.startday.data - self.endday.data >= timedelta(minutes=1)):
            raise ValidationError("End date cannot be earlier than Start date.")
            return False
        elif (date.today() - self.startday.data >= timedelta(minutes=1)):
            flash("Start date cannot be earlier than current date.")
            return False
        else:
            return True

class SearchCaretakerForm(FlaskForm):
    ccontact = IntegerField(
        label='Contact',
        validators=[Optional()],
        default=None,
        render_kw={'placeholder': 'Contact', 'class': 'input100'}
    )
    postal_code = StringField(
        label='Postal Code',
        validators=[Optional()],
        default=None,
        render_kw={'placeholder': 'Postal Code', 'class': 'input100'}
    )
    category = StringField(	
        label='Category',
        validators=[Optional()],
        default=None,	
        render_kw={'placeholder': 'Category', 'class': 'input100'}	
    )
    
    def validate_on_submit(self):
        return super(SearchCaretakerForm, self).validate()
            
class CanTakeCareForm(FlaskForm):
    category = StringField(	
        label='Category',	
        validators=[InputRequired()],	
        render_kw={'placeholder': 'Category', 'class': 'input100'}	
    )

