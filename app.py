#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, render_template, request, redirect, flash
from flask import session
from flask_sqlalchemy import SQLAlchemy
import mysql.connector as sqltor
import math
import os
from flask_mail import Mail
import json
from datetime import datetime



x=open("D:\config.json",'r')
c=x.read()
y=json.loads(c)
params=y["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'somu205e@gmail.com',
    MAIL_PASSWORD=  params['mail']
)
mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user='root', password='', server='localhost', database='blogforeveryone')

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)
class Question(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    qname = db.Column(db.String(80), nullable=False)
    que = db.Column(db.String(12), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    aname = db.Column(db.String(20), nullable=True)
    ans = db.Column(db.String(20), nullable=True)
    adate = db.Column(db.String(12), nullable=True)
class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    subtitle=db.Column(db.String(500), nullable=True)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)
    useful = db.Column(db.String(12), nullable=True)
class Comment(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String(80), nullable=False)
    emailid = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(50), primary_key=False)
@app.route("/subscribe", methods = ['GET', 'POST'])
def comment():
    if(request.method=='POST'):
        cname = request.form.get('cname')
        emailid=request.form.get('emailid')
        password = request.form.get('password')
        entry = Comment(cname=cname, emailid=emailid,password=password )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New subscriber  ' + str(cname),
                            sender=emailid,
                            recipients =['somu209e@gmail.com'] ,
                            body = str(password) + "\n"+str(emailid) 
                            )
        flash('Thanks For Subscribing.Have A Nice Day', "success")
    return render_template('subscribe.html', params=params)

    

    
    
    
@app.route("/addque", methods = ['GET', 'POST'])
def addquestion():
    if(request.method=='POST'):
        qname = request.form.get('qname')
        que = request.form.get('que')
        date=datetime.now()
        aname=""
        ans=""
        adate=datetime.now()
        entry = Question(qname=qname,que=que, date=date, aname= aname,ans=ans,adate=adate)
        db.session.add(entry)
        db.session.commit()
    return render_template('q.html', params=params)

@app.route("/quesans", methods=['GET'])
def questionsanswers():
    question = Question.query.order_by(Question.date.desc()).all()
    return render_template('que.html',params=params,question=question)

@app.route("/ques/<string:sno>", methods=['GET'])
def qestion_route(sno):
    question = Posts.query.filter_by(sno=sno).first()
    return render_template('singleq.html',params=params,question=question)

@app.route("/add/<string:sno>", methods=['GET', 'POST'])    
def addanswer(sno):
    if(request.method=='POST'):
        aname=request.form.get('aname')
        ans=request.form.get('ans')
        if sno != '0':
            question=Question.query.filter_by(sno=sno).first()
            question.qname=""
            question.que=""
            question.aname = aname
            question.ans = ans
            question.adate=datetime.now()
            db.session.commit()
            return render_template('addanswer.html', params=params)
    question=Question.query.filter_by(sno=sno).first()           
    return render_template('addanswer.html', params=params,question=question)
    

@app.route("/")
def home():
    flash("Welcome to ChiruBlogger.com", "success")
    posts = Posts.query.order_by(Posts.date.desc()).limit(3).all()
    return render_template('index.html', params=params, posts=posts)

@app.route("/post/")
def post():
    posts = Posts.query.order_by(Posts.date.desc()).all()
    #filter_by().all()[0:]
    return render_template('index.html', params=params, posts=posts)

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params,post=post)


@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['usern']):
        if (request.method == 'POST'):
            f= request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))
            return "Uploaded successfully"



@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')
    









@app.route("/about")
def about():
    return render_template('about.html', params=params)
@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():
    if ('user' in session and session['user']==params['usern']):
        posts = Posts.query.filter_by().all()
        return render_template('dashboard.html', params=params,post=post)
    
    
    if(request.method=='POST'):
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username==params['usern'] and userpass==params['userp']):
            session['user'] = "uname"
            posts = Posts.query.filter_by().all()
            return render_template('dashboard.html', params=params,post=post)
   
    return render_template('login.html', params=params)

@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if(request.method=='POST'):
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        slug = request.form.get('slug')
        content = request.form.get('content')
        
        date= datetime.now()
        img_file = request.form.get('img_file')
        if sno != '0':
            post=Posts.query.filter_by(sno=sno).first()
            post.title = title
            post.subtitle = subtitle
            post.slug = slug
            post.content = content
            post.img_file = img_file
            post.date = date
            db.session.commit()
            return redirect('/edit/'+sno)
    post = Posts.query.filter_by(sno=sno).first()
    return render_template('edit.html', params=params, post=post, sno=sno)
@app.route("/add", methods = ['GET', 'POST'])
def add():
    if(request.method=='POST'):
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        slug = request.form.get('slug')
        content = request.form.get('content')
        date= datetime.now()
        img_file = request.form.get('img_file')
        entry =Posts(title=title,subtitle=subtitle,slug=slug,content=content,date=date,img_file=img_file)
        db.session.add(entry)
        db.session.commit()
    return render_template('add.html', params=params)
        
        



@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        if(request.method=='POST'):
            phone = request.form.get('phone')
            email=request.form.get('email')
            message = request.form.get('message')
            entry = Contacts(name=name, phone_num = phone, msg = message, date= datetime.now(),email =email )
            db.session.add(entry)
            db.session.commit()
            mail.send_message('New message from ' + str(name),
                              sender=email,
                              recipients =['somu209e@gmail.com'] ,
                              body = str(message) + "\n" + str(phone)
                              )
            flash('Thanks For Submitting The Form. We Will Reply You Soon.Have A Nice Video', "success")
    return render_template('contact.html', params=params)






app.run(debug=False)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




