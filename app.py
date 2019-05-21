from flask import Flask, render_template, request, redirect, jsonify
from flask_mail import Mail, Message
import datetime
import urllib
import json
import pytz # timezone 
import requests
import os
import feedparser
from qaamus2 import Qaamus



app = Flask(__name__)
additional_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ.get('EMAIL_USER', 'theuser'),
    "MAIL_PASSWORD": os.environ.get('EMAIL_PASSWORD', 'thepassword'),
    "RECAPTCHA_SECRET_KEY": os.environ.get('RECAPTCHA_SECRET_KEY'),
}
app.config['JSON_AS_ASCII'] = False
app.config.update(additional_settings)
mail = Mail(app)


@app.route('/api/qaamus', methods=['GET', 'POST'])
def qaamus():
    query = request.args.get('query', '')
    method = request.args.get('method', 'munawwir')

    instance = Qaamus(method)
    try:
        hasil = instance.terjemah(query).hasil()

        return jsonify(arab=hasil.arab, indo=hasil.indo, url=hasil.url)
    except ValueError as e:
        return jsonify(error=str(e))
    except Exception as e:
        return jsonify(error=str(e))


@app.route('/qaamus')
def qaamus_frontend():
    return render_template('qaamus.html')


@app.route('/mail', methods=['POST'])
def script_mail():
    data = request.form
    email = data.get('email')
    subject = data.get('subject')
    message = data.get('message')

    # captcha validation
    recaptcha_response = data.get('g-recaptcha-response')
    values = {
        'secret': app.config.get('RECAPTCHA_SECRET_KEY'),
        'response': recaptcha_response
    }
    print(recaptcha_response)
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request('https://www.google.com/recaptcha/api/siteverify', data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    print(result)
    # end captcha validation

    if not result.get('success'):
        return render_template('email_sent.html', **{'success': False})

    text = f"""
Email: {email}
Subject: {subject}
-------------------

{message}
-------------------
from ihfazh.com
    """
    msg = Message(
            subject='[ihfazh.com bot] Email Received',
            sender=app.config.get('MAIL_USERNAME'),
            recipients=['mihfazhillah@gmail.com'],
            body=text
            )
    mail.send(msg)
    return render_template('email_sent.html')


@app.route('/', methods=['GET'])
def home_page():
    return render_template('index.html', **{'index': True})

@app.route('/articles', methods=['GET'])
def articles():
    parsed = feedparser.parse('https://blog.ihfazh.com/feeds/all.atom.xml')
    entries = parsed.get('entries')
    return jsonify(entries)


@app.route('/<name>')
def profile(name):
	return render_template('index.html', name=name)


@app.route('/add_numbers', methods=['GET','POST'])
def add_numbers_post():
	  # --> ['5', '6', '8']
	  # print(type(request.form['text']))
	  if request.method == 'GET':
	  	return render_template('add_numbers.html')
	  elif request.method == 'POST':
  	      print(request.form['text'].split())
  	      total = 0
  	      try:
  	      	for str_num in request.form['text'].split():
  	      		total += int(str_num)
  	      	return render_template('add_numbers.html', result=str(total))
  	      except ValueError:
  	      	return "Easy now! Let's keep it simple! 2 numbers with a space between them please"


@app.route('/shopping_list', methods=['GET','POST'])
def shopping_list_post():
	  # --> ['5', '6', '8']
	  # print(type(request.form['text']))

    if request.method == 'GET':
      return render_template('shopping_list.html')
    elif request.method == 'POST':
          print(request.form['text'].split())
          
          shop_list = []
          try:
            for item in request.form['text'].split():
              
              shop_list.append(item)

              
              
            return render_template('shopping_list.html', result="\n".join([str(item) for item in shop_list]))
          except ValueError:
            return "Easy now! Let's keep it simple! Just words with a space between them"
          
  	      
@app.route('/time', methods=['GET','POST'])
def time_post():
    # --> ['5', '6', '8']
    # print(type(request.form['text']))

    if request.method == 'GET':
      return render_template('time.html')
    elif request.method == 'POST':
          print(request.form['text'].split())
          
          for item in request.form['text'].split():
            answer = (datetime.datetime.now(pytz.timezone("Europe/Dublin")).strftime('Time = ' + '%H:%M:%S' + ' GMT ' + ' Year = ' + '%d-%m-%Y'))
            #answer = datetime.datetime.now().strftime('Time == ' + '%H:%M:%S' + ' Year == ' + '%d-%m-%Y')
            #answer = datetime.datetime.now().strftime('%Y-%m-%d \n %H:%M:%S')

              
              
            return render_template('time.html', result=answer)

         

@app.route('/python_apps')
def python_apps_page():
	# testing stuff
	return render_template('python_apps.html')


@app.route('/blog', methods=['GET'])
def blog_page():
  return render_template('blog.html')


if __name__ == '__main__':
	app.run(debug=True)
