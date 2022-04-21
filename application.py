from flask import Flask, render_template, request, redirect, session
import requests
import boto3
import json
import uuid
# from botocore.exceptions import ClientError
# from boto3.dynamodb.conditions import Key,Attr


application = app = Flask(__name__)

application.secret_key = 'secret key'
s3 = boto3.resource('s3')
s3_bucket_name = "atcregisterbucket"

@application.route('/')
@application.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        data = {}
        data['email'] = request.form['email_id']
        password = request.form['password']
        url = 'https://ratsmh40r3.execute-api.us-east-1.amazonaws.com/dev/login'
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.get(url, data=json.dumps(data), headers=headers)        
        response = json.loads((response.content).decode("utf-8"))
        response_body = response["body"]
        response_body = json.loads(response_body)
        if 'Item' in response_body and password == response_body['Item']['password']:
            return redirect('/listposts')
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
        url = 'https://ratsmh40r3.execute-api.us-east-1.amazonaws.com/dev/register'
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.post(url, data=json.dumps(data), headers=headers)     
        response_body = response.json()
        response_body = response_body["body"]
        # return render_template('register.html',message = response_body)
        return render_template('login.html', message = response_body)


@application.route('/listposts',methods = ['GET','POST'])
def listings():
    if request.method == 'GET':
        url = ' https://ratsmh40r3.execute-api.us-east-1.amazonaws.com/dev/listposts'
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.get(url, headers=headers)
        response = json.loads((response.content).decode("utf-8"))
        response_body = response["body"]
        response_body = json.loads(response_body)
        return render_template('listPosts.html',posts = response_body['Items'])
    else:
        data = {}
        data['from'] = int(request.form['low'])
        data['to'] = int(request.form['high'])
        url = 'https://ratsmh40r3.execute-api.us-east-1.amazonaws.com/dev/listposts'
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response = json.loads((response.content).decode("utf-8"))
        response_body = response["body"]
        response_body = json.loads(response_body)
        return render_template('listPosts.html',listings = response_body)


@application.route('/add', methods = ['GET','POST'])
def addPost():

    if request.method=='GET':
        return render_template("addpost.html")
    else:
        data = {}
        data["post_id"] = str(uuid.uuid4())
        data["content"] = request.form["content"]
        img = request.files["file"]
        if not img:
            data["image"] = 'https://atcregisterbucket.s3.amazonaws.com/coming-soon-hour-glass.png'
        else:
            req_data = img.read()
            filename = (request.files["file"].filename).replace(' ','_')
            s3.Bucket(s3_bucket_name).put_object(Key=filename, Body=req_data)
            image_url = "https://{0}.s3.amazonaws.com/{1}".format(s3_bucket_name, filename)
            data["image"] = image_url
            url = 'https://ratsmh40r3.execute-api.us-east-1.amazonaws.com/dev/add'
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            response = requests.post(url, data=json.dumps(data), headers=headers)
            response_body = response.json()
            response_body = response_body["body"]
        return redirect ('/listposts')


@application.route('/logout')
def logout():
    return redirect("/login")


if __name__ == "__main__":
    application.run(port = 8000, debug=True)