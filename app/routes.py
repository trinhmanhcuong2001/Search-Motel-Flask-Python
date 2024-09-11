from app import app
#from app.forms import *
from app.models import *
from flask import render_template, request,flash, redirect, url_for, jsonify
from flask_login import current_user, login_user, logout_user, login_required
# from werkzeug.utils import url_parse
from sqlalchemy import func
import json
from datetime import datetime, timedelta





@app.route('/')
def index():
    motels = Motel.query.all()
    comments = Comment.query.order_by(Comment.date.desc()).limit(5).all()
    users = User.query.all()
    return render_template('index.html', motels=motels, comments=comments, users=users)

@app.route('/login_register')
def login_register():
    return render_template('login.html')



@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    users = User.query.all()
    NewUser = User(name=name, email=email, password=password)
    for user in users:
        if user.email == email:
            flash('Email đã tồn tại!')
            return redirect('login_register')
    NewUser.set_password(password)
    db.session.add(NewUser)
    db.session.commit()
    flash('Đăng ký thành công!')
    return redirect('login_register')       


@app.route('/update_account', methods=['GET'])
def update_account():
    user = User.query.get(current_user.id)
    return render_template('users-profile.html',user=user)


@app.route('/update_account_result', methods=['POST'])
def update_account_result():
    name = request.form.get('fullName')
    job = request.form.get('job')
    city = request.form.get('country')
    sdt = request.form.get('phone')
    email = request.form.get('email')
    user = User.query.get(current_user.id)
    user.name = name
    user.job = job
    user.city = city
    user.sdt = sdt
    user.email = email
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/update_password_result', methods=['POST'])
def update_password_result():
    password = request.form.get('password')
    newPassword = request.form.get('newPassword')
    re_newPassword = request.form.get('reNewPassword')
    user = User.query.get(current_user.id)
    if not user.check_password(password):
        flash('Mật Khẩu Sai!')
        return redirect(url_for('update_account'))
    if newPassword != re_newPassword:
        flash('Mật khẩu mới không trùng nhau!')
        return redirect(url_for('update_account'))
    user.password = newPassword
    user.set_password(newPassword)
    db.session.commit()
    return redirect(url_for('index'))





@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email ).first()
    if user is None or not user.check_password(password):
        flash('Thông tin tài khoản hoặc mật khẩu không chính xác!')
        return redirect('login_register')
    login_user(user, remember= True)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/add_motel')
def add_motel():
    return render_template('newPost.html')


@app.route('/add_motel_result', methods=['POST'])
def add_motel_result():
    name = request.form.get('name')
    name_master = request.form.get('name-master')
    phone_number = request.form.get('phone')
    address = request.form.get('address')
    describe = request.form.get('describe')
    price = request.form.get('price')
    image = request.files['image'].read()
    geomInput = 'Point(' + request.form.get("lng") + " " + request.form.get("lat") + ')'
    newMotel = Motel(name=name, name_master=name_master,phone_number=phone_number,address=address,describe=describe,price=price,image=image,
                     geom=func.ST_GeomFromText(geomInput,4326))
    db.session.add(newMotel)
    db.session.commit()
    newMotel.save_image(image,newMotel.id)
    flash('Thêm nhà trọ thành công!')
    return redirect(url_for('add_motel'))


@app.route('/newList')
@app.route('/newList/page/<int:page>')
def newList(page=1):
    count_motels = Motel.query.count()
    motels = Motel.query.order_by(Motel.id).limit(5).offset((page - 1) * 5)
    num_pages = int(count_motels/5) if count_motels % 5 ==0 else int(count_motels/5)+1
    return render_template('newsList.html',motels=motels, num_pages=num_pages, page=page)


@app.route('/updateList/<int:motel_id>')
def updateList(motel_id):
    motel = Motel.query.get(motel_id)
    return render_template('updateList.html',motel=motel)


@app.route('/updateList_result', methods=['POST'])
def updateList_result():
    id = request.form.get('id')
    name = request.form.get('name')
    name_master = request.form.get('name-master')
    phone_number = request.form.get('phone')
    address = request.form.get('address')
    describe = request.form.get('describe')
    price = request.form.get('price')
    image = request.files['image'].read()
    geomInput = 'Point(' + request.form.get("lng") + " " + request.form.get("lat") + ')'
    motel = Motel.query.get(id)
    motel.name = name
    motel.name_master = name_master
    motel.phone_number = phone_number
    motel.address = address
    motel.describe = describe
    motel.price = price
    motel.image = image
    motel.geom = func.ST_GeomFromText(geomInput,4326)
    db.session.commit()
    motel.save_image(image,motel.id)
    flash('Cập nhật thành công !')
    return redirect(url_for('updateList',motel_id=id))


@app.route('/deleteList/<int:motel_id>')
def deleteList(motel_id):
    motel = Motel.query.get(motel_id)
    db.session.delete(motel)
    db.session.commit()
    flash('Xóa thành công!')
    return redirect(url_for('newList'))


@app.route('/api/v1/motels')
def motels():
    motels = db.session.query(Motel.id,Motel.name,Motel.describe,Motel.name_master,Motel.address,Motel.phone_number,Motel.price,
                              func.ST_AsGeoJSON(Motel.geom).label('geometry')).all()
    motelFeatures = []
    for motel in motels:
        motel_temp={}
        motel_temp['type'] = "Feature"
        motel_temp['properties'] = {
            "id": motel.id,
            "name": motel.name,
            "name_master": motel.name_master,
            "phone_number": motel.phone_number,
            "address": motel.address,
            "describe":motel.describe,
            "price": motel.price,
        }
        motel_temp['geometry'] = json.loads(motel.geometry)
        motelFeatures.append(motel_temp)

    return jsonify({
        "features": motelFeatures,
    })


@app.route('/api/v2/motel/<int:id>')
def motel(id):
    motel = db.session.query(Motel.id,Motel.name,Motel.describe,Motel.name_master,Motel.address,Motel.phone_number,Motel.price,
                              func.ST_AsGeoJSON(Motel.geom).label('geometry')).filter(Motel.id == id).first()
    motelFeatures = []
    motel_temp={}
    motel_temp['type'] = "Feature"
    motel_temp['properties'] = {
        "id": motel.id,
        "name": motel.name,
        "name_master": motel.name_master,
        "phone_number": motel.phone_number,
        "address": motel.address,
        "describe":motel.describe,
        "price": motel.price,
        }
    motel_temp['geometry'] = json.loads(motel.geometry)
    motelFeatures.append(motel_temp)

    return jsonify({
        "features": motelFeatures,
    })

#phân trang bằng hàm paginate
@app.route('/list_motel')
@app.route('/list_motel/page/<int:page>')
def list_motel(page=1):
    motels = Motel.query.order_by(Motel.id.desc()).paginate(page=page, per_page=2, error_out=False)
    motels_1 = Motel.query.all()
    return render_template('properties.html',motels=motels,motels_1=motels_1)


#phân trang bằng logic
@app.route('/list_motels')
@app.route('/list_motels/page/<int:page>')
def list_motels(page=1):
    motels_1 = Motel.query.all()
    count_motels = Motel.query.count()
    motels = Motel.query.order_by(Motel.id).limit(3).offset((page - 1) * 3)
    num_pages = int(count_motels/3) if count_motels % 3 ==0 else int(count_motels/3)+1
    return render_template('properties.html',motels=motels,num_pages=num_pages, page=page, motels_1=motels_1)


@app.route('/property_single/<int:motel_id>')
def property_single(motel_id):
    motel = Motel.query.get(motel_id)
    users = User.query.all()
    comments = Comment.query.all()
    for comment in comments:
        time_diff = datetime.now() - comment.date
        # Tổng số giây
        seconds = time_diff.total_seconds()
        if seconds<60:
            comment.relative_time = "vừa xong"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            comment.relative_time = f"{minutes} phút trước"
        elif seconds < 86400:
            # Nếu chưa đến 1 ngày, tính số giờ đã trôi qua
            hours = int(seconds // 3600)
            comment.relative_time = f"{hours} giờ trước"
        else:
            # Nếu đã qua 1 ngày, tính số ngày đã trôi qua
            days = int(seconds // 86400)
            comment.relative_time = f"{days} ngày trước"
    return render_template('property-single.html',motel=motel,comments=comments, users=users)


@app.route('/add_comment/<int:motel_id>', methods=['POST'])
def add_comment(motel_id):
    user_id = current_user.id
    content = request.form.get('comment')
    newComment = Comment(content=content, user_id=user_id,motel_id=motel_id) 
    db.session.add(newComment)
    db.session.commit()
    return redirect(url_for('property_single',motel_id=motel_id))




    


