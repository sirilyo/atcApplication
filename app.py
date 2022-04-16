# from django.shortcuts import render
from flask import Flask, render_template, request, redirect, session
import requests
import boto3
import json
import uuid
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key,Attr


application = Flask(__name__)

application.secret_key = 'secret key'
s3 = boto3.resource('s3')
s3_bucket_name = "atcregisterbucket"

@application.route('/')
@application.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
    #     email = request.form['email']
    #     password = request.form['password']
        
    #     table = dynamodb.Table('user')
    #     response = table.get_item(Key={'email': email})

    #     if 'Item' in response.keys() and password == response['Item']['password']:
    #         session['email'] = email
    #         session['password'] = response['Item']['password']
    #         return render_template('login.html')
    #         # return redirect('/main')
    #     else:
    #         return render_template('login.html',message= msg[0])

    # else:
    #     return render_template('login.html')
        data = {}
        data['email'] = request.form['email_id']
        password = request.form['password']
        url = 'https://ratsmh40r3.execute-api.us-east-1.amazonaws.com/dev/login'
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.get(url, data=json.dumps(data), headers=headers)        
        response = json.loads((response.content).decode("utf-8"))
        #print(response)
        response_body = response["body"]
        response_body = json.loads(response_body)
        #print(response_body)
        if 'Item' in response_body and password == response_body['Item']['password']:
            print("BLAH BLAH`!!!-------------------------")
            #session['email'] = request.form['email']
            #session['userName'] = response_body['Item']['userName']

            print(response_body['Item']['userName'])

            return redirect('/listPosts')
            # session['admin'] = response_body['Item']['admin']

            # if session['admin'] ==True:
            #     return redirect('/adminDashboard')
            # else:
            #     return redirect('/listings')
        else:
            return render_template('login.html', message = "Wrong username or password")     
    else:
        return render_template('login.html')

@application.route('/register', methods = ['GET','POST'])
def register():
    if request.method=='GET':
        return render_template("register.html")
    else:
        data = {}
        data["email"] = request.form["email_id"]
        data["userName"] = request.form["user_name"]
        data["password"] = request.form["password"]
        # data["role"] = request.form["user_type"]
        url = 'https://ratsmh40r3.execute-api.us-east-1.amazonaws.com/dev/register'
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.post(url, data=json.dumps(data), headers=headers)     
        response_body = response.json()
        response_body = response_body["body"]

        return render_template('register.html',message = response_body)

@application.route('/listPosts',methods = ['GET','POST'])
def listings():
    if request.method == 'GET':
        return render_template('listPosts.html')
    else:
        data = {}
        data['from'] = int(request.form['low'])
        data['to'] = int(request.form['high'])
        print(data)
        url = 'https://47ulzl3zh6.execute-api.us-east-1.amazonaws.com/beta/listing/filter'
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response = json.loads((response.content).decode("utf-8"))
        print(response)
        response_body = response["body"]
        response_body = json.loads(response_body)
        
        return render_template('listing.html',listings = response_body)


@application.route('/add', methods = ['GET','POST'])
def addPost():
    if request.method=='POST':
        data = {}
        data['listing_id'] = str(uuid.uuid4())
        # data['image'] = request.form['image']
        data['content'] = request.form['content']
        # data['zipcode'] = request.form['zipcode']
        # data['details'] = request.form['details']
        # data['price'] = request.form['price']
        # data['status'] = request.form['status']
        img = request.files["file"]
        if not img:
            data['image_url'] = 'https://atcregisterbucket.s3.amazonaws.com/DSCF8705.JPG'
        else:
            req_data = img.read()
            filename = (request.files['file'].filename).replace(' ','_')
            s3.Bucket(s3_bucket_name).put_object(Key=filename, Body=req_data)
            image_url = "https://{0}.s3.amazonaws.com/{1}".format(s3_bucket_name, filename)
            data['image_url'] = image_url
        url = 'https://47ulzl3zh6.execute-api.us-east-1.amazonaws.com/beta/listing'
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response = json.loads((response.content).decode("utf-8"))
        return redirect('/adminDashboard')
    else:
        return render_template ('addlisting.html')



if __name__ == "__main__":
    application.run(debug=True)