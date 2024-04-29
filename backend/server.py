from flask import Flask, request, jsonify, send_file, send_from_directory, session
from flask_cors import CORS
from PIL import Image
import os
import io
from io import BytesIO
import pymysql
import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import hashlib
import shutil
import time

rds_host = "database.cxowqa2qwlms.us-east-2.rds.amazonaws.com"
rds_username = "admin"
rds_password = "password1"
rds_db_name = "databasexyz"

conn = pymysql.connect(host=rds_host, user=rds_username, passwd=rds_password, db=rds_db_name, connect_timeout=5)

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_here' 
CORS(app)

UPLOAD_FOLDER = 'user_upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

current_user = ""


def copy_files(src_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    for file_name in os.listdir(src_dir):
        full_file_name = os.path.join(src_dir, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, dest_dir)

def remove_files(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def getusername():
    return current_user

@app.route('/api/details/<int:item_id>', methods=['GET'])
def get_item_details(item_id):
    conn = pymysql.connect(host=rds_host, user=rds_username, passwd=rds_password, db=rds_db_name, connect_timeout=5)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        r.id, r.file_name, 
        r.item_1, r.url_1, ir1.image_link as image_link_1,
        r.item_2, r.url_2, ir2.image_link as image_link_2,
        r.item_3, r.url_3, ir3.image_link as image_link_3,
        r.item_4, r.url_4, ir4.image_link as image_link_4,
        r.item_5, r.url_5, ir5.image_link as image_link_5,
        r.created_at, r.inpic
    FROM Recommendations r
    LEFT JOIN ItemRating ir1 ON r.url_1 = ir1.url
    LEFT JOIN ItemRating ir2 ON r.url_2 = ir2.url
    LEFT JOIN ItemRating ir3 ON r.url_3 = ir3.url
    LEFT JOIN ItemRating ir4 ON r.url_4 = ir4.url
    LEFT JOIN ItemRating ir5 ON r.url_5 = ir5.url
    WHERE r.id = %s
""", (item_id,))

    item_details = cursor.fetchone()
    cursor.close()
    conn.close()
    print("Raw item details from DB:", item_details)
    if item_details:
        response = {
            "id": item_details[0],
            "filename": item_details[1],
            "items": [
                {"name": item_details[2], "url": item_details[3], "image": item_details[4]},
                {"name": item_details[5], "url": item_details[6], "image": item_details[7]},
                {"name": item_details[8], "url": item_details[9], "image": item_details[10]},
                {"name": item_details[11], "url": item_details[12], "image": item_details[13]},
                {"name": item_details[14], "url": item_details[15], "image": item_details[16]},
            ],
            "created_at": item_details[17],
            "inpic": item_details[18] 
        }
        print()
        print()
        print(response)

        return jsonify(response)
    else:
        return jsonify({"error": "Item not found"}), 404



@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('user_upload', filename)

CELEBRITY_FOLDER = 'celebrities'
if not os.path.exists(CELEBRITY_FOLDER):
    os.makedirs(CELEBRITY_FOLDER)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    inspiration = request.form.get('inspiration')
    gender = request.form.get('gender')

    copy_files(CELEBRITY_FOLDER, 'celebrities_backup')
    remove_files(CELEBRITY_FOLDER)

    if inspiration:
        first_name, last_name = inspiration.split()

        pinterest_url = f"https://www.pinterest.com/search/pins/?q={first_name}%20{last_name}%20style&rs=typed"
        insta_url = f"https://www.instagram.com/explore/search/keyword/?q={first_name}%{last_name}%20style"
        fetch_and_save_images_selenium(pinterest_url, CELEBRITY_FOLDER)
        fetch_and_save_images_selenium(insta_url, CELEBRITY_FOLDER)

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    itemandlink = {}
    recs, inpic = getrecs(gender)
    num = 1
    conn = pymysql.connect(host=rds_host, user=rds_username, passwd=rds_password, db=rds_db_name, connect_timeout=5)
    for recommendation in recs:
        start = time.time()
        if num > 5:
            break
        num += 1
        print("Attempt to get Amazon product for: " + recommendation)

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM LinkCache WHERE search = %s", (recommendation,))
        item_details = cursor.fetchone()
        cursor.close()

        if item_details:
            item_link = item_details[1]
            itemandlink[recommendation] = item_link
            #cached item get timing
            end = time.time()
            roundtrip = end - start
            cursor = conn.cursor()
            # Check if the record exists and insert if it does not
            query = """
            INSERT INTO FetchTime (url, seconds, rating_type)
            VALUES (%s, %s, 'cache')
            ON DUPLICATE KEY UPDATE url=url;
            """
            cursor.execute(query, (item_link, roundtrip))
            conn.commit()
            cursor.close()
        else:
            product_details = best_amazon_product(recommendation)
            if product_details:
                print(product_details)
                item_link = product_details['link']
                item_image = product_details['image']
                itemandlink[recommendation] = item_link
                cursor = conn.cursor()
                cursor.execute("INSERT INTO LinkCache (search, link) VALUES (%s, %s)", (recommendation, item_link))
                conn.commit()
                cursor.close()

                cursor = conn.cursor()
                end = time.time()
                roundtrip = end - start
                query = """
                INSERT INTO FetchTime (url, seconds, rating_type)
                VALUES (%s, %s, 'rainforest')
                ON DUPLICATE KEY UPDATE url=url;
                """
                cursor.execute(query, (item_link, roundtrip))
                conn.commit()
                cursor.close()
                #add to here

# CREATE TABLE IF NOT EXISTS ItemRating (
#     url VARCHAR(255) PRIMARY KEY,
#     positive INT,
#     negative INT
# );
                cursor = conn.cursor()
                cursor.execute("INSERT INTO ItemRating (url, positive, negative, image_link) VALUES (%s, %s, %s, %s)", (item_link, 0, 0, item_image))
                conn.commit()
                cursor.close()
            else:
                print("Failed to fetch Amazon product for: " + recommendation)

    user_upload_folder = "user_upload/"

    files = os.listdir(user_upload_folder)

    files = [file for file in files if os.path.isfile(os.path.join(user_upload_folder, file))]

    user_image = max(files, key=lambda x: os.path.getmtime(os.path.join(user_upload_folder, x)))

    insert_query = """
            INSERT INTO Recommendations (file_name, item_1, url_1, item_2, url_2, item_3, url_3, item_4, url_4, item_5, url_5, inpic, username)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    print(itemandlink)
    print(insert_query)
    data = (
        user_image,  # file_name
        recs[0], itemandlink[recs[0]],  # item_1 and url_1
        recs[1], itemandlink[recs[1]],  # item_2 and url_2
        recs[2], itemandlink[recs[2]],  # item_3 and url_3
        recs[3], itemandlink[recs[3]],  # item_4 and url_4
        recs[4] , itemandlink[recs[4]],   # item_5 and url_5
        inpic,
        get_username()
    )
    conn = pymysql.connect(host=rds_host, user=rds_username, passwd=rds_password, db=rds_db_name, connect_timeout=5)
    cursor = conn.cursor()
    cursor.execute(insert_query, data)
    conn.commit()
    cursor.close()
    print(cursor.lastrowid)
    return jsonify({'success': 'File uploaded successfully', 'id': cursor.lastrowid}), 201

@app.route('/api/rate', methods=['POST'])
def rate_item():
    data = request.get_json()
    print("Received data:", data) 
    item_url = data.get('itemUrl')
    rating_type = data.get('rating')

    print("Item URL:", item_url)  
    print("Rating Type:", rating_type) 


    if not item_url or not rating_type:
        print("error")
        return jsonify({'error': 'Missing parameters'}), 400

    conn = pymysql.connect(host=rds_host, user=rds_username, passwd=rds_password, db=rds_db_name, connect_timeout=5)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT rating_type FROM UserItemRating WHERE username = %s AND item_url = %s", (get_username(), item_url))
            existing_rating = cursor.fetchone()
            if existing_rating:
                print("User has already rated this item")
                return jsonify({'error': 'You have already rated this item'}), 409

            if rating_type == 'like':
                update_query = "UPDATE ItemRating SET positive = positive + 1 WHERE url = %s"
            elif rating_type == 'dislike':
                update_query = "UPDATE ItemRating SET negative = negative + 1 WHERE url = %s"
            else:
                return jsonify({'error': 'Invalid rating type'}), 400
            
            cursor.execute(update_query, (item_url,))
            conn.commit()

            cursor.execute("INSERT INTO UserItemRating (username, item_url, rating_type) VALUES (%s, %s, %s)", (get_username(), item_url, rating_type))
            conn.commit()
            return jsonify({'message': 'Rating updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/user-ratings', methods=['GET'])
def user_ratings():
    username = get_username()
    conn = pymysql.connect(host=rds_host, user=rds_username, passwd=rds_password, db=rds_db_name, connect_timeout=5)
    with conn.cursor() as cursor:
        cursor.execute("SELECT item_url FROM UserItemRating WHERE username = %s", (username,))
        user_ratings = cursor.fetchall()
    conn.close()
    ratings_list = [item_url[0] for item_url in user_ratings]

    return jsonify(ratings_list)


def fetch_and_save_images_selenium(url, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(5)
        images = driver.find_elements(By.TAG_NAME, 'img')

        for i, img in enumerate(images):
            src = img.get_attribute('src')
            try:
                response = requests.get(src)
                image = Image.open(BytesIO(response.content))
                image_format = image.format if image.format else 'PNG'
                image_path = os.path.join(folder, f'image_{i}.{image_format.lower()}')
                if image_format == 'JPEG':
                    resized_image = image.resize((300, 800))
                    resized_image.save(image_path)
            except Exception as e:
                print(f"Error saving image: {e}")
    finally:
        driver.quit()





@app.route('/get_highest_id', methods=['GET'])
def get_highest_id():
    try:
        conn = pymysql.connect(host=rds_host, user=rds_username, passwd=rds_password, db=rds_db_name, connect_timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM Recommendations")
        highest_id = cursor.fetchone()[0]
        cursor.close()
        return jsonify({'highest_id': highest_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


    
@app.route('/api/past-results')
def get_past_results():
    conn = pymysql.connect(host=rds_host, user=rds_username, passwd=rds_password, db=rds_db_name, connect_timeout=5)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Recommendations where username = %s", get_username())
    past_results = cursor.fetchall()
    cursor.close()
    return jsonify(past_results)




def getrecs(gender):
    user_upload_folder = "user_upload/"

    files = os.listdir(user_upload_folder)

    files = [file for file in files if os.path.isfile(os.path.join(user_upload_folder, file))]

    user_image = max(files, key=lambda x: os.path.getmtime(os.path.join(user_upload_folder, x)))

    user_image = "user_upload/" + user_image

    celeb_images = os.listdir(f"celebrities/")
    
    from utils import (
        segment,
        get_items_from_segmentation,
        get_custom_recommendations,
        build_context,
    )
    context = []
    for file in celeb_images:
        image, mask = segment("celebrities/"+file)
        context += get_items_from_segmentation(image, mask)
    context = build_context(context)

    image, mask = segment(user_image)
    user_items = get_items_from_segmentation(image, mask)
    
    recommendations = get_custom_recommendations(
        user_items,
        context,
        gender=gender
    )
    recommendations = [
        gender+" "+recommendation for recommendation in recommendations
    ]

    return recommendations, ", ".join(user_items)

users = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_username(username):
    with open('current_user.txt', 'w') as file:
        file.write(username)

def get_username():
    try:
        with open('current_user.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

@app.route('/current_user', methods=['GET'])
def current_user():
    username = get_username()
    if username:
        return jsonify({'username': username}), 200
    else:
        return jsonify({'error': 'No user logged in'}), 404

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    hashed_password = hash_password(password)

    conn = pymysql.connect(host=rds_host, user=rds_username, passwd=rds_password, db=rds_db_name, connect_timeout=5)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM LoginInformation WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result and result[0] == hashed_password:
        save_username(username)  # Save username
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 403


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data['username']
    password = data['password']
    hashed_password = hash_password(password)

    conn = pymysql.connect(host=rds_host, user=rds_username, passwd=rds_password, db=rds_db_name, connect_timeout=5)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO LoginInformation (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except pymysql.err.IntegrityError:
        return jsonify({'message': 'User already exists'}), 409
    finally:
        cursor.close()
        conn.close()


RAINFOREST_API_KEY = 'C1050E88009D4B6585D74809E901F760'#'AA29B5C34DDF4513BCA018F896C3C62D'

def best_amazon_product(search_term):
    url = 'https://api.rainforestapi.com/request'
    params = {
        'api_key': RAINFOREST_API_KEY,
        'type': 'search',
        'amazon_domain': 'amazon.com',
        'search_term': search_term
    }
    response = requests.get(url, params=params)
    products = response.json().get('search_results', [])

    if products:
        first_product = products[0]
        product_details = {
            'title': first_product['title'],
            'asin': first_product['asin'],
            'link': first_product['link'],
            'price': first_product['price']['value'] if 'price' in first_product else None,
            'review_count': first_product['reviews']['total_reviews'] if 'reviews' in first_product else 0,
            'image': first_product['image'] if 'image' in first_product else None #image amazon url link
        }
        return product_details
    else:
        return None

if __name__ == '__main__':
    app.run(debug=True)

