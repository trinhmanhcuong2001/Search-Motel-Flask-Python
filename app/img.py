# Import các module cần thiết
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

# Khởi tạo Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname' # Thay đổi địa chỉ CSDL cho phù hợp
db = SQLAlchemy(app)

# Tạo model cho bảng chứa ảnh
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    mimetype = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)

# Tạo form để cho phép người dùng tải lên tệp ảnh
class ImageForm(FlaskForm):
    image = FileField('image', validators=[FileRequired()])

# Xử lý yêu cầu tải lên tệp ảnh
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = ImageForm()

    if form.validate_on_submit():
        # Lưu tệp ảnh tạm thời trong thư mục tạm của hệ thống
        f = form.image.data
        filename = secure_filename(f.filename)
        mimetype = f.content_type
        tmp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(tmp_path)

        # Đọc dữ liệu từ tệp ảnh tạm thời và lưu trữ nó vào CSDL bằng Flask ORM
        with open(tmp_path, 'rb') as f:
            data = f.read()
            image = Image(filename=filename, mimetype=mimetype, data=data)
            db.session.add(image)
            db.session.commit()

        #
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    image = db.Column(db.LargeBinary)


<form method="POST" action="{{ url_for('add_product') }}" enctype="multipart/form-data">
    <input type="text" name="name" placeholder="Product Name">
    <input type="file" name="image">
    <button type="submit">Add Product</button>
</form>

from flask import request

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    image = request.files['image'].read()
    product = Product(name=name, image=image)
    db.session.add(product)
    db.session.commit()
    return 'Product added successfully!'





