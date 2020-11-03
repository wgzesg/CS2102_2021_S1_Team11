from flask import Blueprint, redirect, flash, url_for, render_template, request
from flask_login import current_user, login_required, login_user, logout_user
from flask_user import roles_required
from flask_table import Table, Col
from flask_paginate import Pagination, get_page_parameter
from __init__ import db, login_manager, bcrypt
from forms import LoginForm, RegistrationForm, BiddingForm, PetForm, ProfileForm, AvailableForm, CanTakeCareForm
from forms import AvailableUpdateForm, PetUpdateForm, UserUpdateForm, Bid, SearchCaretakerForm, ReviewForm, ReviewUpdateForm
from models import Users, Role, Pets, Available, Biddings, Cantakecare, Canparttime
from tables import userInfoTable, editPetTable, ownerHomePage, biddingCaretakerTable, biddingTable, \
    caretakerCantakecare, editAvailableTable, profileTable, CaretakersBidTable, ReviewTable
from datetime import timedelta, date, datetime
from sqlalchemy import exc
import sys

view = Blueprint("view", __name__)

# @login_manager.user_loader
# def load_user(contact):
#     contact = ((Admins.query.filter_by(contact=contact.data).first()) or
#                 (Petowners.query.filter_by(contact=contact.data).first()) or
#                 (Caretakers.query.filter_by(contact=contact.data).first()))
#     return current_user or contact


@view.route("/", methods=["GET"])
def render_dummy_page():
    return render_template("welcome.html", title='Welcome')


@view.route("/registration", methods=["GET", "POST"])
def render_registration_page():
    form = RegistrationForm()
    if form.validate_on_submit():
        print("sumitted", flush=True)
        username = form.username.data
        password = form.password.data
        user_type = form.usertype.data
        contact = form.contact.data
        credit_card = form.credit_card.data
        is_part_time = form.is_part_time.data
        postal_code = form.postal_code.data
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # query = "INSERT INTO users(username, contact, card, password, usertype, isPartTime, postalcode) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
        #     .format(username, contact, credit_card, hashed_password, user_type, is_part_time, postal_code)
        # db.session.execute(query)
        # db.session.commit()

        user1 = Users(username=username, usertype=user_type, contact=contact, card=credit_card, postalcode=postal_code, password=hashed_password)
        role = Role.query.filter_by(name=user_type).first()
        user1.roles.append(role)
        db.session.add(user1)
        
        #query = "SELECT * FROM role WHERE name = '{}'".format(user_type)
        #givenRole = db.session.execute(query).fetchone()
        #query = "INSERT INTO user_roles(contact, usertype) VALUES ('{}', '{}')".format(contact, user_type)
        #db.session.execute(query)
        db.session.commit()
        if(user_type == 'caretaker'):
            canparttime1 = Canparttime(ccontact=contact, isparttime=is_part_time, avgrating=0, salary=0)
            db.session.add(canparttime1)
            db.session.commit()
        #query = "INSERT INTO users(username, contact, card, password, usertype, isPartTime, postalcode) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
        #    .format(username, contact, credit_card, hashed_password, user_type, is_part_time, postal_code)
        # print(query, flush=True)
        # db.session.execute(query)
        # print("done", flush=True)
        # db.session.commit()
        print("commited", flush=True)
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect("/login")
    print("rendered", flush=True)
    return render_template("registration.html", title='Registration', form=form)


@view.route("/login", methods=["GET", "POST"])
def render_login_page():
    if current_user.is_authenticated:
        next_page = request.args.get('next')
        if next_page:
            print("nextpage", flush=True)
            return redirect(next_page)
        elif current_user.usertype == "admin":
            print("admin", flush=True)
            return redirect("/admin")
        elif current_user.usertype == "petowner":
            print("current", flush=True)
            return redirect("/owner")
        elif current_user.usertype == "caretaker":
            print("caret", flush=True)
            return redirect("/caretaker")
        else:
            print("nothing mtaches", flush=True)
            return redirect("/profile")
    form = LoginForm()
    if form.validate_on_submit():
        print("submited", flush=True)
        user = Users.query.filter_by(contact=form.contact.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print("found", flush=True)
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if next_page:
                print("nextpage", flush=True)
                return redirect(next_page)
            elif current_user.usertype == "admin":
                print("admin", flush=True)
                return redirect("/admin")
            elif current_user.usertype == "petowner":
                print("current", flush=True)
                return redirect("/owner")
            elif current_user.usertype == "caretaker":
                print("caret", flush=True)
                return redirect("/caretaker")
            else:
                print("nothing matches", flush=True)
                return redirect("/profile")
        else:
            print("not found", flush=False)
            flash('Login unsuccessful. Please check your contact and password', 'danger')
    return render_template("realLogin.html", form=form)


@view.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect("/")


# ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN


@view.route("/admin", methods=["GET"])
@roles_required('admin')
def render_admin_page():
    print(current_user, flush=True)
    contact = current_user.contact
    query = "SELECT * FROM users WHERE contact = '{}' AND usertype = 'admin'".format(contact)
    results = profileTable(db.session.execute(query))
    return render_template('admin.html', results=results, username=current_user.username + " admin")


@view.route("/admin/summary", methods=["GET"])
@roles_required('admin')
def render_admin_summary_page():
    query = "SELECT * FROM users WHERE usertype = 'caretaker'"
    results = db.session.execute(query).fetchall()
    return render_template("profile.html", results=results, username=current_user.username + " owner")

@view.route("/admin/profile", methods=["GET"])
@roles_required('admin')
def render_admin_profile():
    print(current_user, flush=True)
    contact = current_user.contact
    query = "SELECT * FROM users WHERE contact = '{}'".format(contact)
    results = db.session.execute(query)
    table = profileTable(results)
    return render_template('profileAdmin.html', table=table, username=current_user.username + " admin")


@view.route("/admin/profile/update", methods=["GET", "POST"])
@roles_required('admin')
def render_admin_update_profile():
    contact = current_user.contact
    admin = Users.query.filter_by(contact=contact).first()
    if admin:
        form = UserUpdateForm(obj=admin)
        if request.method == 'POST' and form.validate_on_submit():
            profile = Users.query.filter_by(contact=contact).first()
            profile.username = form.username.data
            profile.password = form.password.data
            db.session.commit()
            print("Admin profile has been updated", flush=True)
            return redirect(url_for('view.render_admin_profile'))
        return render_template("update.html", form=form, username=current_user.username + " admin")


@view.route("/caretaker", methods=["GET"])
#@login_required
@roles_required('caretaker')
def render_caretaker_page():
    contact = current_user.contact
    #insert query to show this caretaker's total working hours and this month's pay.
    query = "SELECT biddings.pcontact, biddings.petname, Pets.category, startday, endday FROM biddings INNER JOIN Pets ON\
        Pets.petname = biddings.petname and Pets.pcontact = biddings.pcontact WHERE ccontact = '{}'".format(contact)
    results = db.session.execute(query)
    print(results, flush=True)
    table = CaretakersBidTable(results)
    return render_template('caretaker.html', table=table, username=current_user.username + " caretaker")


@view.route("/caretaker/biddings", methods=["GET", "POST"])
@roles_required('caretaker')
def render_caretaker_biddings():
    form = BiddingForm()
    contact = current_user.contact
    query = "SELECT * FROM biddings WHERE ccontact = '{}'".format(contact)
    results = db.session.execute(query).fetchall()
    table = biddingCaretakerTable(results)
    return render_template("caretakerBid.html", table=table, username=current_user.username + " caretaker")

@view.route("/caretaker/biddings/accept", methods=["POST"])
@roles_required('caretaker')
def render_caretaker_biddings_accept():
    contact = current_user.contact
    startday = request.args.get('startDay')
    endday = request.args.get('endDay')
    ct = request.args.get('ccontact')
     
    bid = Biddings.query.filter_by(pcontact=request.args.get('ownerContact'), 
        ccontact=request.args.get('ccontact'),  petname=request.args.get('petName'),
        startday=request.args.get('startDay'), endday=request.args.get('endDay')).first()
    def daterange(startday, endday):
        for n in range(int((endday - startday).days)):
            yield startday + timedelta(n)
    flag = True
    n = 0
    for selected in daterange(datetime.strptime(startday, '%Y-%m-%d'), datetime.strptime(endday, '%Y-%m-%d')):
        query = "SELECT COUNT (*) FROM biddings WHERE '{}' - startday >= 0 AND endday - '{}' >= 0 AND ccontact = '{}' AND status = 'success'".format(selected, selected, ct)
        count = db.session.execute(query).fetchone()
        print("day " + n + " : " + count[0])
        n = n + 1
        if count[0] > 5:
            flag = False
            break
    
    if flag == False:
        flash("You are not allowed to take more than five pets at the same time.")
        return redirect(url_for('view.render_caretaker_biddings'))
    if bid:
        bid.status = "success"
        db.session.commit()
        print("Bidding status has been updated", flush=True)
    return redirect(url_for('view.render_caretaker_biddings'))

@view.route("/caretaker/profile", methods=["GET"])
@roles_required('caretaker')
def render_caretaker_profile():
    print(current_user, flush=True)
    contact = current_user.contact
    query = "SELECT * FROM users WHERE contact = '{}'".format(contact)
    results = db.session.execute(query)
    table = profileTable(results)
    return render_template('profileCaretaker.html', table=table, username=current_user.username + " caretaker")


@view.route("/caretaker/profile/update", methods=["GET", "POST"])
@roles_required('caretaker')
def render_caretaker_update_profile():
    contact = current_user.contact
    caretaker = Users.query.filter_by(contact=contact).first()
    if caretaker:
        form = UserUpdateForm(obj=caretaker)
        if request.method == 'POST' and form.validate_on_submit():
            profile = Users.query.filter_by(contact=contact).first()
            profile.username = form.username.data
            profile.password = form.password.data
            profile.card = form.credit_card.data
            profile.isparttime = form.is_part_time.data
            profile.postalcode = form.postal_code.data
            db.session.commit()
            print("Caretaker profile has been updated", flush=True)
            return redirect(url_for('view.render_caretaker_profile'))
        return render_template("update.html", form=form, username=current_user.username + " caretaker")


@view.route("/caretaker/available", methods=["GET", "POST"])
@roles_required('caretaker')
def render_caretaker_available():
    contact = current_user.contact
    query = "SELECT * FROM available WHERE ccontact = '{}'".format(contact)
    availables = db.session.execute(query)
    table = editAvailableTable(availables)
    return render_template('availableWithEdit.html', table=table, username=current_user.username + " caretaker")


@view.route("/caretaker/available/edit", methods=["GET", "POST"])
@roles_required('caretaker')
def render_caretaker_available_edit():
    ac = current_user.contact
    astart = request.args.get('startday')
    aend = request.args.get('endday')
    available = Available.query.filter_by(startday=astart,endday=aend,ccontact=ac).first()
    if available:
        form = AvailableUpdateForm(obj=available)
        if request.method == 'POST' and form.validate_on_submit():
            thisavailable = Available.query.filter_by(startday=astart,endday=aend,ccontact=ac).first()
            thisavailable.startday = form.startday.data
            thisavailable.endday = form.endday.data
            db.session.commit()
            return redirect(url_for('view.render_caretaker_available'))
    return render_template('availableNew.html', form=form, username=current_user.username + " caretaker")


@view.route("/caretaker/available/delete", methods=["POST"])
@roles_required('caretaker')
def render_caretaker_available_delete():
    ac = current_user.contact
    astart = request.args.get('startday')
    aend = request.args.get('endday')
    available = Available.query.filter_by(startday=astart,endday=aend,ccontact=ac).first()
    if available:
        if request.method == 'POST':
            db.session.delete(available)
            db.session.commit()
    return redirect(url_for('view.render_caretaker_available'))


@view.route("/caretaker/available/new", methods=["GET", "POST"])
@roles_required('caretaker')
def render_caretaker_available_new():
    form = AvailableForm()
    contact = current_user.contact
    if request.method == 'POST' and form.validate_on_submit():
        startday = form.startday.data
        endday = form.endday.data
        ccontact = contact
        query = "INSERT INTO available(startday, endday, ccontact) VALUES ('{}', '{}', '{}')" \
        .format(startday, endday, ccontact)
        db.session.execute(query)
        db.session.commit()
        return redirect(url_for('view.render_caretaker_available'))
    return render_template('availableNew.html', form = form, username=current_user.username + " caretaker")


@view.route("/caretaker/cantakecare", methods=["GET", "POST"])
@roles_required('caretaker')
def render_caretaker_cantakecare():
    contact = current_user.contact
    query = "SELECT * FROM cantakecare WHERE ccontact = '{}'".format(contact)
    canTakeCare = db.session.execute(query)
    table = caretakerCantakecare(canTakeCare)
    return render_template('caretakerCantakecare.html', table=table, username=current_user.username + " caretaker")

@view.route("/caretaker/cantakecare/new", methods=["GET", "POST"])
@roles_required('caretaker')
def render_caretaker_cantakecare_new():
    cn = request.args.get('ccontact')
    contact = current_user.contact
    form = CanTakeCareForm()
    if request.method == 'POST' and form.validate_on_submit():
        category = form.category.data
        query = "INSERT INTO cantakecare(ccontact, category) VALUES ('{}', '{}')" \
        .format(contact, category)
        db.session.execute(query)
        db.session.commit()
        return redirect(url_for('view.render_caretaker_cantakecare'))
    return render_template('caretakerCantakecareNew.html', form=form, username=current_user.username + " caretaker")

@view.route("/caretaker/cantakecare/delete", methods=["POST"])
@roles_required('caretaker')
def render_caretaker_cantakecare_delete():
    contact = current_user.contact
    category = request.args.get('category')
    thispet = Cantakecare.query.filter_by(category=category, ccontact=contact).first()
    if thispet:
        if request.method == 'POST':
            db.session.delete(thispet)
            db.session.commit()
        return redirect(url_for('view.render_caretaker_cantakecare'))
# END OF CARETAKER END OF CARETAKER END OF CARETAKER END OF CARETAKER END OF CARETAKER END OF CARETAKER

# PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER


@view.route("/owner", methods=["GET", "POST"])
#@login_required
@roles_required('petowner')
def render_owner_page(page=1):
    countquery = """SELECT COUNT(*) FROM users u WHERE u.usertype = 'caretaker'
                         AND EXISTS (SELECT 1 FROM pets 
                         WHERE pcontact = '{}' AND 
                         category in (SELECT category FROM cantakecare WHERE ccontact = u.contact))""".format(current_user.contact)
    
    count = db.session.execute(countquery).fetchone()
    total = count[0]

    # PER_PAGE = 10 
    # page = request.args.get(get_page_parameter(), type=int, default=1)
    # start = (page-1)*PER_PAGE
    # end = page * PER_PAGE
    # pagination = Pagination(bs_version=3, page=page, total=total, per_page=10, record_name='caretakers')

    page_offset = (page - 1) * 10
    if total < page * 10:
        page_display = total % 10
        pagequery = """SELECT * FROM users u WHERE u.usertype = 'caretaker'
                         AND EXISTS (SELECT 1 FROM pets 
                         WHERE pcontact = '{}' AND 
                         category in (SELECT category FROM cantakecare WHERE ccontact = u.contact))
                         LIMIT '{}' OFFSET '{}'""".format(current_user.contact, page_display, page_offset)
    else:
        pagequery = """SELECT * FROM users u WHERE u.usertype = 'caretaker'
                         AND EXISTS (SELECT 1 FROM pets 
                         WHERE pcontact = '{}' AND 
                         category in (SELECT category FROM cantakecare WHERE ccontact = u.contact))
                         LIMIT 10 OFFSET '{}'""".format(current_user.contact, page_offset)
    caretaker_page = db.session.execute(pagequery)
    caretable = ownerHomePage(caretaker_page)

    form = SearchCaretakerForm()

    if request.method == 'POST' and form.validate_on_submit():
        cc = request.form.get('ccontact')
        postal_code = request.form.get('postal_code')
        if cc == '':
            cc = None
        if postal_code == '':
            postal_code = None
        query = """
            SELECT *
            FROM users
            WHERE
                usertype = 'caretaker'
                AND
                (:cc is null or contact=:cc)
                AND
                (:postal_code is null or postalcode / 1000 = :postal_code / 1000 )
                AND EXISTS (SELECT 1 FROM pets 
                         WHERE pcontact = '{}' AND 
                         category in (SELECT category FROM cantakecare WHERE ccontact = u.contact))
        """.format(current_user.contact)
        parameters = dict(cc = cc, postal_code = postal_code)
        selectedCareTakers = db.session.execute(query, parameters)
        caretable = ownerHomePage(selectedCareTakers)

    contact = current_user.contact
    query = "SELECT * FROM users WHERE contact = '{}'".format(contact)
    profile = db.session.execute(query)
    table = userInfoTable(profile)

    return render_template("owner.html", form=form, profile=profile, caretable=caretable, table=table, username=current_user.username + " owner")


@view.route("/owner/summary", methods=["GET", "POST"])
@roles_required('petowner')
def render_owner_summary():
    contact = current_user.contact
    query = "SELECT * FROM users WHERE contact = '{}'".format(contact)
    results = db.session.execute(query).fetchone()
    return render_template("profile.html", results=results, username=current_user.username + " owner")


@view.route("/owner/profile", methods=["GET", "POST"])
@roles_required('petowner')
def render_owner_profile():
    form = ProfileForm()
    contact = current_user.contact
    query = "SELECT * FROM users WHERE contact = '{}'".format(contact)
    profile = db.session.execute(query).fetchone()
    return render_template("profileOwner.html", profile=profile, form=form, username=current_user.username + " owner")


@view.route("/owner/profile/update", methods=["GET", "POST"])
@roles_required('petowner')
def render_owner_profile_update():
    contact = current_user.contact
    petowner = Users.query.filter_by(contact=contact).first()
    if petowner:
        form = UserUpdateForm(obj=petowner)
        if request.method == 'POST' and form.validate_on_submit():
            profile = Users.query.filter_by(contact=contact).first()
            profile.username = form.username.data
            profile.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            profile.card = form.credit_card.data
            profile.postalcode = form.postal_code.data
            db.session.commit()
            print("Owner profile has been updated", flush=True)
            return redirect(url_for('view.render_owner_profile'))
        return render_template("update.html", form=form, username=current_user.username + " owner")


@view.route("/owner/pet", methods=["GET", "POST"])
@roles_required('petowner')
def render_owner_pet():
    contact = current_user.contact
    query = "SELECT * FROM pets WHERE pcontact = '{}'".format(contact)
    pets = db.session.execute(query)
    print(pets, flush=True)
    table = editPetTable(pets)
    return render_template("ownerPetWithEdit.html", table=table, pets=pets, username=current_user.username + " owner")


@view.route("/owner/pet/new", methods=["GET", "POST"])
@roles_required('petowner')
def render_owner_pet_new():
    form = PetForm()
    contact = current_user.contact
    if request.method == 'POST' and form.validate_on_submit():
        petname = form.petname.data
        category = form.category.data
        age = form.age.data

        query = "INSERT INTO pets(petname, pcontact, age, category) VALUES ('{}', '{}', '{}', '{}')" \
        .format(petname, contact, age, category)
        try:
            db.session.execute(query)
            db.session.commit()
            return redirect(url_for('view.render_owner_pet'))
        except exc.IntegrityError:
            db.session.rollback()
            flash("You already have a pet with the same name!")
    return render_template("petNew.html", form=form, username=current_user.username + " owner")


@view.route("/owner/pet/update", methods=["GET", "POST"])
@roles_required('petowner')
def render_owner_pet_update():
    pc = current_user.contact
    pn = request.args.get('petname')
    pet = Pets.query.filter_by(petname=pn, pcontact=pc).first()
    if pet:
        form = PetUpdateForm(obj=pet)
        if request.method == 'POST' and form.validate_on_submit():
            thispet = Pets.query.filter_by(petname=pn, pcontact=pc).first()
            thispet.petname = form.petname.data
            thispet.category = form.category.data
            thispet.age = int(form.age.data)
            db.session.commit()
            return redirect(url_for('view.render_owner_pet'))
        return render_template("pet.html", form=form, username=current_user.username + " owner")


@view.route("/owner/pet/delete", methods=["GET","POST"])
@roles_required('petowner')
def render_owner_pet_delete():
    pc = current_user.contact
    pn = request.args.get('petname')
    pet = Pets.query.filter_by(petname=pn, pcontact=pc).first()
    if pet:
        form = PetUpdateForm(obj=pet)
        if request.method == 'POST' and form.validate_on_submit():
            petname = form.petname
            thispet = Pets.query.filter_by(petname=pn, pcontact=pc).first()
            db.session.delete(thispet)
            db.session.commit()
            return redirect(url_for('view.render_owner_pet'))
        return render_template("pet.html", form=form, username=current_user.username + " owner")

@view.route("/owner/bid", methods=["GET", "POST"])
@roles_required('petowner')
def render_owner_bid():
    contact = current_user.contact
    query = "SELECT * FROM biddings WHERE pcontact= '{}'".format(contact)
    bidding = db.session.execute(query).fetchall()
    table = biddingTable(bidding)
    return render_template("ownerBid.html", table=table, username=current_user.username + " owner")


@view.route("/owner/bid/new", methods=["GET", "POST"])
@roles_required('petowner')
def render_owner_bid_new():
    cn = request.args.get('ccontact')
    contact = current_user.contact
    form = BiddingForm()
    petNameQuery = """SELECT petname FROM pets 
                      WHERE pcontact = '{}' AND 
                      category in (SELECT category FROM cantakecare WHERE ccontact = '{}')""".format(contact, cn)
    petNames = db.session.execute(petNameQuery).fetchall()
    form.petname.choices = [(petname[0], petname[0]) for petname in petNames]
    form.ccontact.data = cn

    if request.method == 'POST' and form.validate_on_submit():
        petname = form.petname.data
        pcategory = Pets.query.filter_by(petname = petname).first()
        ccategories = Cantakecare.query.filter_by(ccontact = cn).all()
        startday = form.startday.data
        endday = form.endday.data
        paymentmode = form.paymentmode.data
        deliverymode = form.deliverymode.data
        isValidPeriod = True
        fullTimeQuery = "SELECT isparttime FROM Canparttime WHERE ccontact = '{}'".format(cn)
        isPartTime = db.session.execute(fullTimeQuery).fetchone()
        print(isPartTime, flush=True)
        if not isPartTime[0]:
            overLapQuery = """
            SELECT 1
            FROM   (SELECT min(st) as st, max(en) as en
                    FROM (SELECT st, en,
                        max(new_start) OVER (ORDER BY st,en) AS left_edge
                    FROM (SELECT st, en,
                            CASE WHEN st < max(le) OVER (ORDER BY st,en) THEN null ELSE st END AS new_start
                    FROM (SELECT startday AS st, endday AS en, lag(endday) OVER (ORDER BY startday, endday) AS le FROM available WHERE ccontact = '{}') s1) s2) s3
                    GROUP BY left_edge) AS f2
            WHERE tsrange('{}', '{}', '[]') && tsrange(f2.st, f2.en, '[]');
            """.format(cn, startday, endday)
            hasOverlap = db.session.execute(overLapQuery).fetchone()
            print(hasOverlap, flush=True)
            if(hasOverlap):
                isValidPeriod = False
        else:
            intersection = """
            SELECT 1
            FROM   (SELECT min(st) as st, max(en) as en
                    FROM (SELECT st, en,
                        max(new_start) OVER (ORDER BY st,en) AS left_edge
                    FROM (SELECT st, en,
                            CASE WHEN st < max(le) OVER (ORDER BY st,en) THEN null ELSE st END AS new_start
                    FROM (SELECT startday AS st, endday AS en, lag(endday) OVER (ORDER BY startday, endday) AS le FROM available WHERE ccontact = '{}') s1) s2) s3
                    GROUP BY left_edge) AS f2
            WHERE tsrange('{}', '{}', '[]') * tsrange(f2.st, f2.en, '[]') = tsrange('{}', '{}', '[]');
            """.format(cn, startday, endday, startday, endday)
            hasFullOverage = db.session.execute(intersection).fetchone()
            print(hasFullOverage, flush=True)
            if(not hasFullOverage):
                isValidPeriod = False
        if(isValidPeriod == False):
            flash("The caretaker is not available during this period")
            return render_template("ownerBidNew.html", target=cn, form=form, username=current_user.username + " owner")
        query = "INSERT INTO biddings(pcontact, ccontact, petname, startday, endday, paymentmode, deliverymode, status) VALUES ('{}', '{}', '{}', '{}','{}', '{}', '{}', '{}')" \
        .format(contact, cn, petname, startday, endday, paymentmode, deliverymode, "pending")
        try:
            db.session.execute(query)
            db.session.commit()
            return redirect(url_for('view.render_owner_bid'))
        except exc.IntegrityError:
            db.session.rollback()
            flash("Some of your input is not valid. Make sure your pet name is valid!")
    return render_template("ownerBidNew.html", target=cn, form=form, username=current_user.username + " owner")


@view.route("/owner/bid/update", methods=["GET", "POST"])
@roles_required('petowner')
def render_owner_bid_update():
    query = "SELECT * FROM users WHERE usertype = 'caretaker'"
    results = db.session.execute(query)
    return render_template("profile.html", results=results, username=current_user.username + " owner")


@view.route("/owner/bid/delete", methods=["GET", "POST"])
@roles_required('petowner')
def render_owner_bid_delete():
    query = "SELECT * FROM users WHERE usertype = 'caretaker'"
    results = db.session.execute(query)
    return render_template("profile.html", results=results, username=current_user.username + " owner")

@view.route("/owner/review", methods=["GET", "POST"])
@roles_required('petowner')
def render_owner_review():
    pcontact = request.args.get(pcontact)
    query = "SELECT * FROM Reviews WHERE pcontact = {}".format(pcontact)
    results = db.session.execute(query)
    return render_template("review.html", results=results, username=current_user.username + " owner")
    contact = current_user.contact
    #placeholder query
    query = "SELECT * FROM reviews WHERE pcontact = '{}'".format(contact)
    bidding = db.session.execute(query).fetchall()
    reviewTable = ReviewTable(bidding)
    return render_template("ownerReview.html", reviewTable=reviewTable, username=current_user.username + " owner")


@view.route("/owner/review/update", methods=["GET", "POST"])
@roles_required('petowner')
def render_owner_review_update():
    pc = current_user.contact
    pn = request.args.get('petname')
    cc = request.args.get('ccontact')
    startday = request.args.get('startday')
    endday = request.args.get('endday')
    review = Reviews.query.filter_by(petname=pn, pcontact=pc, ccontact=cc, startday=startday, endday=endday).first()
    if review:
        form = ReviewUpdateForm(obj=review)
        if request.method == 'POST' and form.validate_on_submit():
            thisreview = Reviews.query.filter_by(petname=pn, pcontact=pc, ccontact=cc, startday=startday, endday=endday).first()
            thisreview.review = form.review.data
            thisreview.rating = int(form.rating.data)
            db.session.commit()
            return redirect(url_for('view.render_owner_review'))
    
    return render_template("reviewReview.html", results=results, username=current_user.username + " owner")
# END OF PETOWNER END OF PETOWNER END OF PETOWNER END OF PETOWNER END OF PETOWNER END OF PETOWNER END OF PETOWNER


@view.route("/profile")
@login_required
def render_profile_page():
    return render_template('profile.html', username=current_user.username + "profile")