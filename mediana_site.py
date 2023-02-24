from flask import Flask
from flask import redirect, render_template, request, url_for
from flask import session
from flask_socketio import SocketIO, send, emit

from get import stat_rec

import send_message_email
import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '27adc9f91f3245bcb28fa0adbfbcd4f8'

ADMIN_CONF_NAME = "admin"
ADMIN_CONF_PASSWORD = "hashpassw"
ADMIN_CONF_EMAIL = "noemail@noserv.com"
ADMIN_CONF_PHONE = 1111
ADMIN_CONF_FULL_NAME = "ADMINISTRATION of MEDIANA"

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String)
    username = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.Integer)
    password = db.Column(db.String)

    def __repr__(self, id):
        return '<Client %r>' % self.id

class Messages(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    msg_author = db.Column(db.String())
    msg_content = db.Column(db.Text())
    chat_room = db.Column(db.String())

class Chat_rooms(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    msg_author = db.Column(db.String())

@app.route("/")
@app.route("/main")
def main_page():
    if 'name' in session:
        this_account_session = session['name']
        clients_list = Client.query.all()
        return render_template("index.html", clients_list=clients_list, this_acc=this_account_session)
    
    return redirect("/reg")

@app.route("/reg", methods=['GET', 'POST'])
def reg_page():
    if social_service := request.args.get('from'):
        stat_rec.set_to_media(social_service)
        return redirect('/reg')

    if request.method == "POST":
        telephone_hole = request.form["number"]
        username_hole = request.form["username"]
        password_hole = request.form["password"]
        fullname_hole = request.form["fullname"]

        USERNAME_CHECKER  = Client.query.filter(Client.username == username_hole).all()
        TELEPHONE_CHECKER = Client.query.filter(Client.phone == telephone_hole).all()
        
        if not USERNAME_CHECKER and not TELEPHONE_CHECKER:
            session['name'] = username_hole

            client = Client(
                phone=telephone_hole, 
                username=username_hole, 
                password=password_hole,
                fullname=fullname_hole
            )

            try:
                db.session.add(client)
                db.session.commit()
                
                return redirect("/")
            except:
                return "404"
        else:
            already_ex_err = "Sorry this account already exist"
            return render_template("reg.html", already_ex_err=already_ex_err)
    
    return render_template("reg.html")

@app.route("/auth", methods=['POST', 'GET'])
def auth_page():
    if request.method == "POST":
        username_hole = request.form["username"]
        password_hole = request.form["password"]

        USERNAME_CHECKER = Client.query.filter(Client.username == username_hole).all()
        PASSWORD_CHECKER = Client.query.filter(Client.password == password_hole).all()

        if USERNAME_CHECKER and PASSWORD_CHECKER:
            session["name"] = username_hole
            return redirect("/")
        else:
            already_ex_err = "Wrong password or username"
            return render_template("auth.html", ex_err=already_ex_err)
    
    return render_template("auth.html")

@app.route("/space/<int:id>/<string:username>")
def space_page(id, username):
    isAuthor = False
    isAdmin = False

    if 'name' in session:
        if session['name'] == username: isAuthor=True
        if session['name'] == ADMIN_CONF_NAME: isAdmin=True

    user_info = Client.query.filter_by(username=username).first()
    return render_template("space.html", user=user_info, isAuthor=isAuthor, isAdmin=isAdmin)

@app.route('/send/<int:id>', methods=['POST'])
def send_email(id):
    if session['name'] == 'admin':
        today_time = datetime.datetime.now()
        today_time_format = f'{(today_time.hour)+1}:{today_time.min}'
        
        user_email = Client.query.filter_by(id=id).first()
        
        message_toEmail = user_email.email
        message_content = f"Мы приняли заявку вашу приходите в {today_time_format}"
        message_subject = "Успешно"

        return send_message_email.send_to_email(message_content, message_toEmail, message_subject)

    return "Access denied | Отказ доступа"

@app.route('/admin')
def admin_panel():
    if 'name' in session:
        if session['name'] == ADMIN_CONF_NAME:
            query = request.args.get('query')

            if (reset := request.args.get('reset')) == 'True':
                stat_rec.reset('instagram')
                stat_rec.reset('facebook')
                stat_rec.reset('telegram')

                return redirect('/admin?query=stat')

            if query == 'chats':
                chats = Chat_rooms.query.all()
                return render_template('chats.html', rooms=chats)

            if query == 'stat':
                instagram = stat_rec.get_to_media('instagram')
                facebook = stat_rec.get_to_media('facebook')
                telegram = stat_rec.get_to_media('telegram')

                return render_template('stat.html', instagram=instagram, facebook=facebook, telegram=telegram)

    return "ACCESS DENIED ERROR"

@app.route('/chat/<username>', methods=['POST', 'GET'])
def chat(username):
    isAuthor = session['name'] == username
    isAdmin = session['name'] == ADMIN_CONF_NAME

    if isAuthor or isAdmin:
        if request.method == 'POST':

            room_checker = Chat_rooms.query.filter(Chat_rooms.msg_author == username).all()
            if not room_checker:
                set_chat_room = Chat_rooms(msg_author=username)
                db.session.add(set_chat_room)
                db.session.commit()

            message = request.form['message_content']
            message_author = session['name']

            post_message = Messages(
                msg_content=message,
                msg_author=message_author,
                chat_room=username
            )

            db.session.add(post_message)
            db.session.commit()
            return redirect(f'/chat/{username}')
        
        chat = Messages.query.filter(Messages.chat_room == username)
        return render_template('chat.html', msg_chat=chat)
    
@app.route("/logout")
def logout_page():
    if 'name' in session:
        del session['name']
        return redirect("/")
    else:
        return "you dont have account"

if __name__ == "__main__":
    def set_adm():
        USERNAME_CHECKER = Client.query.filter(Client.username == ADMIN_CONF_NAME).all()
        PASSWORD_CHECKER = Client.query.filter(Client.password == ADMIN_CONF_PASSWORD).all()

        if not USERNAME_CHECKER and not PASSWORD_CHECKER:
            set_admin = Client(
                username=ADMIN_CONF_NAME,
                fullname=ADMIN_CONF_FULL_NAME,
                phone=ADMIN_CONF_PHONE, 
                password=ADMIN_CONF_PASSWORD
            )
            db.session.add(set_admin)
            db.session.commit()

    db.init_app(app)

    with app.app_context():
        db.create_all()
        set_adm()
        app.run(host='localhost', port=8000)
