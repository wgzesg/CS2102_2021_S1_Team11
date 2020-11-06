from flask import Blueprint, redirect, flash, url_for, render_template, request
from flask_login import current_user, login_required, login_user, logout_user
from flask_user import roles_required
from flask_table import Table, Col
from flask_paginate import Pagination, get_page_parameter
from __init__ import db, login_manager, bcrypt
from forms import LoginForm, RegistrationForm, BiddingForm, PetForm, ProfileForm, AvailableForm, CanTakeCareForm
from forms import AvailableUpdateForm, PetUpdateForm, UserUpdateForm, Bid, SearchCaretakerForm, ReviewUpdateForm, DailyPriceForm
from models import Users, Role, Pets, Available, Biddings, Cantakecare, Canparttime, Reviews, Dailyprice
from tables import userInfoTable, editPetTable, ownerHomePage, biddingCaretakerTable, biddingTable, \
    caretakerCantakecare, editAvailableTable, profileTable, CaretakersBidTable, ReviewTable, canparttimeTable, SalaryTable, DailyPriceTable
from datetime import timedelta, date, datetime
from sqlalchemy import exc
import sys

view = Blueprint("view", __name__)

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

        # DON"T CHANGE THIS. linked to other flask librarys like login_manager
        user1 = Users(username=username, usertype=user_type, contact=contact, card=credit_card, postalcode=postal_code, password=hashed_password)
        #roleQuery = "SELECT name FROM role WHERE name = '{}' LIMIT 1".format(user_type)
        # usage of ORM as it has hidden properties related to flask that allows us to verify roles and get current_user
        role = Role.query.filter_by(name=user_type).first()
        #role = db.session.execute(roleQuery).fetchall()
        user1.roles.append(role)
        db.session.add(user1)
        db.session.commit()
        if(user_type == 'caretaker'):
            salery = 0 if is_part_time else 3000
            canparttime1 = Canparttime(ccontact=contact, isparttime=is_part_time, avgrating=5.0, petday= 0, salary=salery)
            db.session.add(canparttime1)
            db.session.commit()
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
            return redirect(next_page)
        elif current_user.usertype == "admin":
            return redirect("/admin")
        elif current_user.usertype == "petowner":
            return redirect("/owner")
        elif current_user.usertype == "caretaker":
            return redirect("/caretaker")
        else:
            return redirect("/profile")
    form = LoginForm()
    if form.validate_on_submit():
        print("submited", flush=True)
        # DON"T CHANGE THIS. linked to other flask librarys like login_manager
        user = Users.query.filter_by(contact=form.contact.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif current_user.usertype == "admin":
                return redirect("/admin")
            elif current_user.usertype == "petowner":
                return redirect("/owner")
            elif current_user.usertype == "caretaker":
                return redirect("/caretaker")
            else:
                return redirect("/profile")
        else:
            flash('Login unsuccessful. Please check your contact and password', 'danger')
    return render_template("realLogin.html", form=form)


@view.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect("/")


# ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN


@view.route("/admin", methods=["GET"])
@roles_required('admin')
def render_admin_page(page=1):
    print(current_user, flush=True)
    contact = current_user.contact
    countquery = "SELECT COUNT(*) FROM users WHERE contact = '{}' AND usertype = 'admin'".format(contact)
    count = db.session.execute(countquery).fetchone()
    total = count[0]

    # PER_PAGE = 10 
    # page = request.args.get(get_page_parameter(), type=int, default=1)
    # start = (page-1)*PER_PAGE
    # end = page * PER_PAGE
    pagination = Pagination(bs_version=3, page=page, total=total, per_page=10, record_name='admin')

    page_offset = (page - 1) * 10
    if total < page * 10:
        page_display = total % 10
        pagequery = """SELECT * FROM users WHERE contact = '{}' AND usertype = 'admin'
                         LIMIT '{}' OFFSET '{}'""".format(contact, page_display, page_offset)
    else:
        pagequery = """SELECT * FROM users WHERE contact = '{}' AND usertype = 'admin'
                         LIMIT 10 OFFSET '{}'""".format(contact, page_offset)

    results = profileTable(db.session.execute(pagequery))
    return render_template('adminSummary.html', results=results, pagination=pagination, username=current_user.username + " admin")


@view.route("/admin/summary", methods=["GET"])
@roles_required('admin')
def render_admin_summary_page():
    countquery = """SELECT COUNT(*) FROM canparttime"""
    count = db.session.execute(countquery).fetchone()
    total = count[0]

    # PER_PAGE = 10 
    page = request.args.get(get_page_parameter(), type=int, default=1)
    # start = (page-1)*PER_PAGE
    # end = page * PER_PAGE
    pagination = Pagination(bs_version=3, page=page, total=total, per_page=10, record_name='canparttime')

    page_offset = (page - 1) * 10
    if total < page * 10:
        page_display = total % 10
        pagequery = """SELECT ccontact, salary FROM canparttime
                         OFFSET '{}' LIMIT '{}'""".format(page_offset, page_display)
    else:
        pagequery = """SELECT ccontact, salary FROM canparttime
                         OFFSET '{}' LIMIT 10 """.format(page_offset)
    result_salary = db.session.execute(pagequery)
    salaryTable = SalaryTable(result_salary)
    return render_template("adminSummary.html", salaryTable=salaryTable, pagination=pagination, username=current_user.username + " owner")

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
    #admin = Users.query.filter_by(contact=contact).first()
    adminQuery = "SELECT * FROM Users WHERE contact = '{}' LIMIT 1".format(contact)
    admin = db.session.execute(adminQuery).fetchall()
    if admin:
        form = UserUpdateForm(obj=admin)
        if request.method == 'POST' and form.validate_on_submit():
            #profile = Users.query.filter_by(contact=contact).first()
            profileQuery = "SELECT * FROM Users WHERE contact = '{}' LIMIT 1".format(contact)
            profile = db.session.execute(profileQuery).fetchall()
            profile.username = form.username.data
            profile[0] = form.username.data
            profile.password = form.password.data
            db.session.commit()
            print("Admin profile has been updated", flush=True)
            return redirect(url_for('view.render_admin_profile'))
        return render_template("update.html", form=form, username=current_user.username + " admin")


@view.route("/admin/dailyprice", methods=["GET", "POST"])
@roles_required('admin')
def render_admin_dailyprice():
    countquery = """SELECT COUNT(*) FROM dailyprice"""   
    count = db.session.execute(countquery).fetchone()
    total = count[0]

    # PER_PAGE = 10 
    page = request.args.get(get_page_parameter(), type=int, default=1)
    # start = (page-1)*PER_PAGE
    # end = page * PER_PAGE
    pagination = Pagination(bs_version=3, page=page, total=total, per_page=10)

    page_offset = (page - 1) * 10
    if total < page * 10:
        page_display = total % 10
        pagequery = """SELECT * FROM dailyprice ORDER BY category, rating
                         OFFSET '{}' LIMIT '{}' """.format(page_offset, page_display)
    else:
        pagequery = """SELECT * FROM dailyprice ORDER BY category, rating
                         OFFSET '{}' LIMIT 10 """.format(page_offset)
    dailyprices = db.session.execute(pagequery)
    print(dailyprices, flush=True)
    table = DailyPriceTable(dailyprices)
    return render_template("adminDailyPrice.html", table=table, pagination=pagination, username=current_user.username + " admin")

@view.route("/admin/dailyprice/update", methods=["GET", "POST"])
@roles_required('admin')
def render_dailyprice_update():
    cat = request.args.get('category')
    rat= request.args.get('rating')
    #price = Dailyprice.query.filter_by(category=cat, rating=rat).first()
    priceQuery = "SELECT * FROM Dailyprice WHERE category = '{}' AND rating = '{}'LIMIT 1".format(cat, rat)
    price = db.session.execute(priceQuery).fetchall()
    if price:
        form = DailyPriceForm(obj=price)
        if request.method == 'POST' and form.validate_on_submit():
            #thisprice = Dailyprice.query.filter_by(category=cat, rating=rat).first()
            thispriceQuery = "SELECT * FROM Dailyprice WHERE category = '{}' AND rating = '{}'LIMIT 1".format(cat, rat)
            thisprice = db.session.execute(thispriceQuery).fetchall()
            thisprice.price = int(form.price.data)
            db.session.commit()
            return redirect(url_for('view.render_admin_dailyprice'))
        return render_template("dailyPriceUpdate.html", form=form, username=current_user.username + " admin")




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
    table2 = CaretakersBidTable(results)

    query = "SELECT canparttime.ccontact, canparttime.avgrating, canparttime.salary FROM canparttime WHERE ccontact = '{}'".format(contact)
    results = db.session.execute(query)
    table1 = canparttimeTable(results)
    return render_template('caretaker.html', table1=table1, table2 = table2, username=current_user.username + " caretaker")


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
    parttimeQuery = "SELECT * FROM canparttime WHERE ccontact = '{}' LIMIT 1".format(contact)
    parttime = db.session.execute(parttimeQuery).fetchall()
    #parttime = Canparttime.query.filter_by(ccontact=contact).first()


    bidQuery = "SELECT * FROM biddings WHERE pcontact = '{}', ccontact = '{}', petname = '{}', startday = '{}', endday = '{}' LIMIT 1".format(request.args.get('ownerContact'),
                                                                                                                                      request.args.get('ccontact'),
                                                                                                                                      request.args.get('petName'),
                                                                                                                                      request.args.get('startDay'),
                                                                                                                                      request.args.get('endDay'))
    bid = db.session.query(bidQuery).fetchall()
    #bid = Biddings.query.filter_by(pcontact=request.args.get('ownerContact'),
    #    ccontact=request.args.get('ccontact'),  petname=request.args.get('petName'),
    #    startday=request.args.get('startDay'), endday=request.args.get('endDay')).first()
    def daterange(startday, endday):
        for n in range(int((endday - startday).days)):
            yield startday + timedelta(n)
    
    flag = True
    for selected in daterange(datetime.strptime(startday, '%Y-%m-%d'), datetime.strptime(endday, '%Y-%m-%d')):
        query = """SELECT COUNT (*) FROM biddings WHERE '{}' - startday >= 0 AND endday - '{}' >= 0 
            AND ccontact = '{}' AND status = 'success' LIMIT 1""".format(selected, selected, ct)
        count = db.session.execute(query).fetchall()
        if parttime.isparttime == True and parttime.avgrating < 3:
            if count[0] > 2:
                flag = False
                count[0] = 0
                break
        else:
            if count[0] > 5:
                flag = False
                count[0] = 0
                break
    
    if flag == False:
        flash("You are not allowed to take more than five pets at the same time.")
        return redirect(url_for('view.render_caretaker_biddings'))
    if bid:
        bid.status = "success"
        db.session.commit()

    return redirect(url_for('view.render_caretaker_biddings'))

@view.route("/caretaker/biddings/finish", methods=["POST"])
@roles_required('caretaker')
def render_caretaker_biddings_finish():
    contact = current_user.contact
    startday = request.args.get('startDay')
    endday = request.args.get('endDay')
    ct = request.args.get('ccontact')
         
    #bid = Biddings.query.filter_by(pcontact=request.args.get('ownerContact'),
    #    ccontact=request.args.get('ccontact'),  petname=request.args.get('petName'),
    #    startday=request.args.get('startDay'), endday=request.args.get('endDay')).first()
    bidQuery = "SELECT * FROM biddings WHERE pcontact = '{}', ccontact = '{}', petname = '{}', startday = '{}', endday = '{}' LIMIT 1".format(
        request.args.get('ownerContact'), request.args.get('ccontact'), request.args.get('petName'), request.args.get('startDay'), request.args.get('endDay')
    )
    bid = db.session.execute(bidQuery).fetchall()
    if bid:
    #     datetime.strptime(endday, '%Y-%m-%d') < datetime.today():
    #     flash("You are not allowed to terminate the bidding before end date.")
    # elif bid:
        bid.status = "end"
        db.session.commit()

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
    caretakerQuery = "SELECT * FROM users WHERE contact='{}' LIMIT 1".format(contact)
    #caretaker = Users.query.filter_by(contact=contact).first()
    ct = db.session.execute(caretakerQuery)
    if ct:
        form = UserUpdateForm(obj=ct)
        if request.method == 'POST' and form.validate_on_submit():
            profile = ct
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
    applicationType = "leave"
    ptquery = "SELECT isparttime FROM canparttime WHERE ccontact = '{}'".format(contact)
    isPt = db.session.execute(ptquery).fetchone()
    if isPt == (True,):
        applicationType = "availability"
    query = "SELECT * FROM available WHERE ccontact = '{}'".format(contact)
    availables = db.session.execute(query)
    table = editAvailableTable(availables)
    return render_template('availableWithEdit.html', table=table, applicationType=applicationType, username=current_user.username + " caretaker")


@view.route("/caretaker/available/edit", methods=["GET", "POST"])
@roles_required('caretaker')
def render_caretaker_available_edit():
    ac = current_user.contact
    astart = request.args.get('startday')
    aend = request.args.get('endday')
    #available = Available.query.filter_by(startday=astart,endday=aend,ccontact=ac).first()
    availableQuery = "SELECT * FROM available WHERE startday = '{}', endday = '{}', ccontact = '{}'".format(astart, aend, ac)
    available = db.session.execute(availableQuery).fetchall()
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
    #available = Available.query.filter_by(startday=astart,endday=aend,ccontact=ac).first()
    availableQuery = "SELECT * FROM available WHERE startday = '{}', endday = '{}', ccontact = '{}'".format(astart, aend, ac)
    available = db.session.execute(availableQuery).fetchall()
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
        fullTimeQuery = "SELECT isparttime FROM Canparttime WHERE ccontact = '{}' LIMIT 1".format(ccontact)
        isPartTime = db.session.execute(fullTimeQuery).fetchall()
        print(isPartTime, flush=True)
        if not isPartTime[0]:
            overlapQuery = """
            SELECT 1
            FROM   (SELECT min(st) as st, max(en) as en
                    FROM (SELECT st, en,
                        max(new_start) OVER (ORDER BY st,en) AS left_edge
                    FROM (SELECT st, en,
                            CASE WHEN st < max(le) OVER (ORDER BY st,en) THEN null ELSE st END AS new_start
                    FROM (SELECT startday AS st, endday AS en, lag(endday) OVER (ORDER BY startday, endday)
                         AS le FROM biddings WHERE ccontact = '{}') s1) s2) s3
                    GROUP BY left_edge) AS f2
            WHERE tsrange('{}', '{}', '[]') && tsrange(f2.st, f2.en, '[]');
            """.format(ccontact, startday, endday)
            hasOverlap = db.session.execute(overlapQuery).fetchone()
            print(hasOverlap, flush=True)
            if(hasOverlap):
                flash("You have work to do during that period")
                return render_template('availableNew.html', form = form, username=current_user.username + " caretaker")
            
            checkContinuous = """
            SELECT SUM(diff)
            FROM
            (
            SELECT FLOOR(COALESCE(EXTRACT(DAY FROM (f2.st - date_trunc('year', f2.st))), 365) / 150) diff
            from (
            (SELECT startday AS st, endday AS en FROM available WHERE ccontact = :cc)
            UNION (SELECT :startday, :endday)
            ORDER BY st LIMIT 1
            ) AS f2

            UNION

            SELECT FLOOR(COALESCE(f2.st - lag(f2.en) over (order by f2.st, f2.en), 0) / 150) diff
            FROM (
            SELECT min(st) as st, max(en) as en
            FROM (SELECT st, en,
                    max(new_start) OVER (ORDER BY st,en) AS left_edge
                    FROM (SELECT st, en,
                        CASE WHEN st < max(le) OVER (ORDER BY st,en) THEN null ELSE st END AS new_start
                        FROM (
                            ((SELECT startday AS st, endday AS en, lag(endday) OVER (ORDER BY startday,endday) AS le FROM available WHERE ccontact = :cc)
                            UNION (SELECT :startday, :endday, :endday))) s1) s2) s3
                    GROUP BY left_edge
            LIMIT 1
            ) AS f2

            UNION

            SELECT FLOOR(COALESCE(EXTRACT( DAY FROM (date_trunc('year',f2.en) + INTERVAL '1' YEAR) - f2.en), 365) / 150)
            FROM (
            (SELECT startday AS st, endday AS en
            FROM available WHERE ccontact = :cc) UNION
            (SELECT :startday, :endday)
            ORDER BY en DESC LIMIT 1
            ) AS f2) AS everything
            """
            parameters = dict(cc = ccontact, startday = startday, endday = endday)
            numberOfperiods = db.session.execute(checkContinuous, parameters).fetchone()
            if numberOfperiods[0] < 2:
                flash("You have not worked for 2 continuous 150 days")
                return render_template('availableNew.html', form = form, username=current_user.username + " caretaker")
            
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
    query = "SELECT * FROM cantakecare WHERE category = '{}' AND ccontact = '{}'".format(category, contact)
    thispet = db.session.execute(query).first()
    if thispet:
        if request.method == 'POST':
            delelte = "DELETE FROM cantakecare WHERE category = '{}' AND ccontact = '{}'".format(category, contact)
            db.session.execute(delelte)
            db.session.commit()
        return redirect(url_for('view.render_caretaker_cantakecare'))
# END OF CARETAKER END OF CARETAKER END OF CARETAKER END OF CARETAKER END OF CARETAKER END OF CARETAKER

# PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER PETOWNER


@view.route("/owner", methods=["GET", "POST"])
#@login_required
@roles_required('petowner')
def render_owner_page():
    countquery = """SELECT COUNT(*) FROM users WHERE users.usertype = 'caretaker'
                         AND EXISTS (SELECT 1 FROM pets 
                         WHERE pcontact = '{}' AND 
                         category in (SELECT category FROM cantakecare WHERE ccontact = users.contact))""".format(current_user.contact)
    
    count = db.session.execute(countquery).fetchone()
    total = count[0]

    # PER_PAGE = 10 
    page = request.args.get(get_page_parameter(), type=int, default=1)
    # start = (page-1)*PER_PAGE
    # end = page * PER_PAGE
    pagination = Pagination(bs_version=3, page=page, total=total, per_page=10, record_name='caretakers')

    page_offset = (page - 1) * 10
    if total < page * 10:
        page_display = total % 10
        pagequery = """SELECT * FROM users u WHERE u.usertype = 'caretaker'
                         AND EXISTS (SELECT 1 FROM pets 
                         WHERE pcontact = '{}' AND 
                         category in (SELECT category FROM cantakecare WHERE ccontact = u.contact))
                         OFFSET '{}' LIMIT '{}' """.format(current_user.contact, page_offset, page_display)
    else:
        pagequery = """SELECT * FROM users u WHERE u.usertype = 'caretaker'
                         AND EXISTS (SELECT 1 FROM pets 
                         WHERE pcontact = '{}' AND 
                         category in (SELECT category FROM cantakecare WHERE ccontact = u.contact))
                         OFFSET '{}' LIMIT 10 """.format(current_user.contact, page_offset)
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
                         category in (SELECT category FROM cantakecare WHERE ccontact = users.contact))
        """.format(current_user.contact)
        parameters = dict(cc = cc, postal_code = postal_code)
        selectedCareTakers = db.session.execute(query, parameters)
        caretable = ownerHomePage(selectedCareTakers)

    contact = current_user.contact
    query = "SELECT * FROM users WHERE contact = '{}'".format(contact)
    profile = db.session.execute(query)
    usertable = userInfoTable(profile)

    return render_template("owner.html", form=form, profile=profile, caretable=caretable, usertable=usertable, pagination=pagination, username=current_user.username + " owner")


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
    userQuery = "SELECT * FROM users WHERE contact = '{}'".format(contact)
    petowner = db.session.execute(userQuery).fetchone()
    if petowner:
        form = UserUpdateForm(obj=petowner)
        if request.method == 'POST' and form.validate_on_submit():
            update = """UPDATE users
                    SET username = '{}', password = '{}', card = '{}', postalcode = '{}'
                    WHERE contact = '{}'""".format(form.username.data, bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
                    form.credit_card.data, form.postal_code.data, contact)
            db.session.execute(update)
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
    petquery = "SELECT * FROM pets WHERE petname = '{}' AND pcontact = '{}'".format(pn, pc)
    pet = db.session.execute(petquery).fetchone()
    if pet:
        form = PetUpdateForm(obj=pet)
        if request.method == 'POST' and form.validate_on_submit():
            updateQuery = """
            UPDATE pets
            SET petname = '{}', category = '{}', age = '{}'
            WHERE pcontact = '{}' AND petname = '{}'
            """.format(form.petname.data, form.category.data, int(form.age.data),
            pc, pn)
            db.session.execute(updateQuery)
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
                    FROM (SELECT startday AS st, endday AS en, lag(endday) OVER (ORDER BY startday, endday)
                         AS le FROM available WHERE ccontact = '{}') s1) s2) s3
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
                    FROM (SELECT startday AS st, endday AS en, lag(endday) OVER (ORDER BY startday, endday) 
                        AS le FROM available WHERE ccontact = '{}') s1) s2) s3
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
        db.session.execute(query)
        db.session.commit()
        return redirect(url_for('view.render_owner_bid'))
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
    pcontact = current_user.contact
    query = "SELECT * FROM Reviews WHERE pcontact = {}".format(pcontact)
    results = db.session.execute(query)
    reviewTable = ReviewTable(results)
    return render_template("ownerReview.html", reviewTable=reviewTable, username=current_user.username + " owner")
   
@view.route("/owner/review/update", methods=["GET", "POST"])
@roles_required('petowner')
def render_owner_review_update():
    pc = current_user.contact
    pn = request.args.get('petname')
    cc = request.args.get('ccontact')
    startday = request.args.get('startday')
    endday = request.args.get('endday')
    reviewQuery = "SELECT * FROM reviews WHERE petname = '{}' AND pcontact = '{}' AND ccontact = '{}' AND startday = '{}' AND endday = '{}'"\
        .format(pn, pc, cc, startday, endday)
    review = db.session.execute(reviewQuery).fetchone()
    if review:
        form = ReviewUpdateForm(obj=review)
        if request.method == 'POST' and form.validate_on_submit():
            reivewUpdate = """
            UPDATE reviews
            SET review = '{}', rating = '{}'
            WHERE petname='{}' AND pcontact= '{}' AND ccontact= '{}' AND startday= '{}' AND endday= '{}'
            """.format(form.review.data, int(form.rating.data), pn, pc, cc, startday, endday)
            db.session.execute(reivewUpdate)
            db.session.commit()
            return redirect(url_for('view.render_owner_review'))
        return render_template("ownerReviewUpdate.html", form=form, username=current_user.username + " owner")
    return redirect(url_for('view.render_owner_review'))
# END OF PETOWNER END OF PETOWNER END OF PETOWNER END OF PETOWNER END OF PETOWNER END OF PETOWNER END OF PETOWNER


@view.route("/profile")
@login_required
def render_profile_page():
    return render_template('profile.html', username=current_user.username + "profile")