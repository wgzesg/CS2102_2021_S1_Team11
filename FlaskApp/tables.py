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
    edit = LinkCol('Edit ', 'view.render_caretaker_available_edit', url_kwargs=dict(startday='startday', endday='endday'))
    delete = ButtonCol('Delete', 'view.render_caretaker_available_delete', url_kwargs=dict(startday='startday', endday='endday'))

class ownerHomePage(Table):
    username = Col('Caretaker Name ')
    contact = Col('Contact ')
    postalcode = Col('Postal Code ')
    bid = LinkCol('Bid', 'view.render_owner_bid_new', url_kwargs=dict(username='username', ccontact='contact', postalcode='postalcode', edit='contact'), url_kwargs_extra=dict(edit='edit'), column_html_attrs = {'class': 'bid-button'})


class biddingTable(Table):
    pcontact = Col('Owner Contact')	
    ccontact = Col('Caretaker Contact')	
    petname	= Col('Pet name')
    startday = Col('Start date')
    endday = Col('End date')
    paymentmode = Col('Payment mode')
    deliverymode = Col('Delivery mode')
    status = Col('Status')

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

class caretakerCantakecare(Table):
    category = Col('Category')
    dailyprice = Col('Daily Price')
    delete = ButtonCol('Delete', 'view.render_caretaker_cantakecare_delete', url_kwargs=dict(category='category', dailyprice='dailyprice'))

class profileTable(Table):
    username = Col('Username')
    contact = Col('Contact')
    usertype = Col('User Type')
    card = Col('Card')
    postalcode = Col('Postal Code')

class CaretakersBidTable(Table):
    pcontact = Col('pcontact')
    petname = Col('petname')
    category = Col('category')
    startday = Col('startday')
    endday = Col('enddays')