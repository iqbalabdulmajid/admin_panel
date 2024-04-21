from ntpath import join
from posixpath import dirname
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request,flash, url_for 
from pymongo import DESCENDING, MongoClient
import os
import datetime

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]



def save_image(image):
    if image:
        save_to = 'static/uploads'
        if not os.path.exists(save_to):
            os.makedirs(save_to)
        
        today = datetime.datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
        
        ext = image.filename.split('.')[-1]
        filename = f'fruit-{mytime}-{ext}'
        image.save(f"{save_to}/{filename}")
        return filename
    return None

def delete_image(image_path):
    if os.path.exists(image_path):
        os.remove(image_path)

@app.route('/')
def dashboard():
    fruit_collection = list(db.fruits.find().sort('_id', DESCENDING))
    return render_template('dashboard.html', fruit_collection=fruit_collection)

@app.route('/add-fruit', methods=['GET','POST'])
def add_fruits():
    if request.method== "GET":
        return render_template('add-fruit.html')
    else :
        name = request.form.get('name')
        price = int(request.form.get('price'))
        description =request.form.get('description')
        image = request.files['image']
        filename = ''
        if image:
            save_to = 'static/uploads'
            if not os.path.exists(save_to):
                os.makedirs(save_to)
            ext = image.filename.split('.')[-1]
            filename = f"fruit-{datetime.datetime.now().strftime('%H-%M-%S')}.{ext}"
            image.save(f"{save_to}/{filename}")
        db.fruits.insert_one({
            'name': name, 'price': price, 'description': description, 'image': filename
        })
        flash('Berhasil menambahkan data buah!')
        return redirect(url_for('fruits'))

@app.route('/edit-fruit/<id>',methods=['GET','POST'])
def edit_fruit(id):
    fruit = db.fruits.find_one({'_id': ObjectId(id)})
    if request.method == "GET":
        return render_template('edit-fruit.html', fruit=fruit)
    else:
        name = request.form.get('name')
        price = int(request.form.get('price'))
        description = request.form.get('description')
        image = request.files['image']
        
        fruit = db.fruits.find_one({'_id': ObjectId(id)})
        target = f"static/uploads/{fruit['image']}" 
        
        if image:
            filename = save_image(image)
            delete_image(target)
            db.fruits.update_one({'_id': ObjectId(id)}, {'$set': {
            'name': name, 'price': price, 'description': description, 'image': filename
        }})
        
        flash('Data buah berhasil diubah!')
        return redirect(url_for('fruits'))

@app.route('/fruits')
def fruits():
    fruit_collection = list(db.fruits.find().sort('_id', DESCENDING))
    return render_template('fruits.html',fruit_collection=fruit_collection)

@app.route('/fruit-delete/<id>',methods=['POST'])
def fruit_delete(id):
    fruit=db.fruits.find_one({'_id': ObjectId(id)})
    target= f"static/uploads/{fruit['image']}"
    if os.path.exists(target):
        os.remove(target)
    db.fruits.delete_one({'_id': ObjectId(id)})
    flash('Data buah berhasil dihapus!')
    return redirect(url_for('fruits'))
    
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5000")