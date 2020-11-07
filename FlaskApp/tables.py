from flask_table import Table, Col, ButtonCol, LinkCol

class userInfoTable(Table):
    username = Col('Username ')
    contact = Col('Contact ')
    card = Col('Card ')
    usertype = Col('User Type ')
    postalcode = Col('Postal Code')

class editPetTable(Table):
    petname = Col('Pet Name ')
    pcontact = Col('Contact ')
    category = Col('Pet Name ')
    age = Col('Age ')
    edit = ButtonCol('Edit ', 'view.render_owner_pet_update', url_kwargs=dict(petname='petname', category='category', age='age'))
    delete = ButtonCol('Delete', 'view.render_owner_pet_delete', url_kwargs=dict(petname='petname'))

class editAvailableTable(Table):
    startday = Col('Start Date ')
    endday = Col('End Date ')
    ccontact = Col('Contact')
    edit = LinkCol('Edit ', 'view.render_caretaker_available_edit', url_kwargs=dict(startday='startday', endday='endday'), column_html_attrs = {'class': 'edit table-button'})
    delete = ButtonCol('Delete', 'view.render_caretaker_available_delete', url_kwargs=dict(startday='startday', endday='endday'), column_html_attrs = {'class': 'delete table-button'})

class ownerHomePage(Table):
    username = Col('Caretaker Name ')
    contact = Col('Contact ')
    postalcode = Col('Postal Code ')
    bid = LinkCol('Bid', 'view.render_owner_bid_new', url_kwargs=dict(username='username', ccontact='contact', postalcode='postalcode', edit='contact'),
                     url_kwargs_extra=dict(edit='edit'), column_html_attrs = {'class': 'bid-button'})


class biddingTable(Table):
    pcontact = Col('Owner Contact')	
    ccontact = Col('Caretaker Contact')	
    petname	= Col('Pet name')
    startday = Col('Start date')
    endday = Col('End date')
    paymentmode = Col('Payment mode')
    deliverymode = Col('Delivery mode')
    status = Col('Status')
    #finish = ButtonCol('Done', 'view.render_caretaker_biddings_finish', url_kwargs=dict(ownerContact='pcontact',
    #    ccontact='ccontact', petName='petname', startDay='startday', endDay='endday'))

class biddingCaretakerTable(Table):
    pcontact = Col('Owner Contact')	
    ccontact = Col('Caretaker Contact')	
    petname	= Col('Pet name')
    startday = Col('Start date')
    endday = Col('End date')
    paymentmode = Col('Payment mode')
    deliverymode = Col('Delivery mode')
    status = Col('Status')
    accept = ButtonCol('Accept', 'view.render_caretaker_biddings_accept', url_kwargs=dict(ownerContact='pcontact', 
        ccontact='ccontact', petName='petname', startDay='startday', endDay='endday'))
    finish = ButtonCol('Done', 'view.render_caretaker_biddings_finish', url_kwargs=dict(ownerContact='pcontact',
        ccontact='ccontact', petName='petname', startDay='startday', endDay='endday'))

class caretakerCantakecare(Table):
    category = Col('Category')
    delete = ButtonCol('Delete', 'view.render_caretaker_cantakecare_delete', url_kwargs=dict(category='category'), column_html_attrs = {'class': 'delete-button'})

class profileTable(Table):
    username = Col('Username')
    contact = Col('Contact')
    usertype = Col('User Type')
    card = Col('Card')
    postalcode = Col('Postal Code')

class canparttimeTable(Table):
    ccontact = Col('Contact')
    avgrating = Col('Overall Rating')
    petday = Col('Petday')
    salary = Col('Salary of the month')

class CaretakersBidTable(Table):
    pcontact = Col('petowner contact')
    petname = Col('petname')
    category = Col('category')
    startday = Col('startday')
    endday = Col('endday')

class ReviewTable(Table):
    ccontact = Col('pcontact')
    petname = Col('petname')
    startday = Col('startday')
    endday = Col('endday')
    rating = Col('rating')
    review = Col('review')
    edit = LinkCol('Edit ', 'view.render_owner_review_update', url_kwargs=dict(ccontact = 'ccontact', petname = 'petname', startday = 'startday', endday = 'endday'))

class SalaryTable(Table):
    ccontact = Col('ccontact')
    salary = Col('salary')

class DailyPriceTable(Table):
    category = Col('category')
    rating = Col('rating')
    price = Col('price')
    edit = LinkCol('Edit ', 'view.render_dailyprice_update', url_kwargs=dict(category = 'category', rating = 'rating', price = 'price'))

class DeleteProfileTable(Table):
    username = Col('username')
    contact = Col('contact')
    usertype = Col('user type')
    delete = LinkCol('Delete ', 'view.render_dailyprice_update', url_kwargs=dict(username = 'username', contact = 'contact', usertype = 'usertype'))
