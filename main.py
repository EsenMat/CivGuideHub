import os
from flask import Flask, render_template, redirect, request
from data import db_session
from data.guides import Guides
from forms.user import RegisterForm, LoginForm, ProfileForm
from data.users import User
from data.images import Image
from forms.guide import GuideForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User,user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == current_user.email).first()

        user.name=form.name.data
        user.about=form.about.data

        db_sess.commit()
        return redirect('/')
    if request.method == 'GET':
        form.name.data = current_user.name
        form.about.data = current_user.about
    return render_template('profile.html', title='Профиль', form=form)


@app.route("/guides")
def guides():
    db_sess = db_session.create_session()
    guides = db_sess.query(Guides).filter(Guides.type == 'guide')
    return render_template("guides.html", guides=guides)


@app.route("/guides/<int:id>")
def guide(id):
    db_sess = db_session.create_session()
    guide = db_sess.query(Guides).filter(Guides.id == id).first()
    images = db_sess.query(Image).filter(Image.guide_id == id)
    return render_template('guide.html', item=guide, images=images)


@app.route("/challenges")
def challenges():
    db_sess = db_session.create_session()
    challenges = db_sess.query(Guides).filter(Guides.type == 'challenge')
    return render_template("challenges.html", guides=challenges)


@app.route('/add_guides', methods=['GET', 'POST'])
def add_guides():
    form = GuideForm()
    db_sess = db_session.create_session()
    used_images = [img.path for img in db_sess.query(Image).filter(Image.guide_id != None)]

    directory = os.path.dirname(os.path.abspath(__file__))
    files = [f for f in os.listdir(f'{directory}/static/img')]

    images = [file for file in files if file not in used_images]
    form.images.choices = images

    if form.validate_on_submit():
        guide = Guides(
            type=form.type.data,
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id
        )
        db_sess.add(guide)
        db_sess.flush()
        for img in images:
            guide_image = db_sess.query(Image).filter(Image.path == img).first()
            if not guide_image:
                guide_image = Image(path=img)
                db_sess.add(guide_image)
            guide_image.guide_id = guide.id
        db_sess.commit()
        return redirect('/guides')
    return render_template('add_guide.html', title='Добавление гайда', form=form)


@app.route("/guides/<int:id>/delete")
def delete_guide(id):
    db_sess = db_session.create_session()
    guide = db_sess.query(Guides).filter(Guides.id == id).first()
    images = db_sess.query(Image).filter(Image.guide_id == id)
    for img in images:
        img.guide_id = None
    db_sess.delete(guide)
    db_sess.commit()
    return redirect('/guides')


@app.route("/guides/<int:id>/refactor", methods=['GET', 'POST'])
def refactor_guide(id):
    form = GuideForm()
    db_sess = db_session.create_session()
    guide = db_sess.query(Guides).filter(Guides.id == id).first()
    used_images = [img.path for img in db_sess.query(Image).filter(Image.guide_id != None)]

    directory = os.path.dirname(os.path.abspath(__file__))
    files = [f for f in os.listdir(f'{directory}/static/img')]
    this_guide_images = [img.path for img in db_sess.query(Image).filter(Image.guide_id == id)]

    images = [file for file in files if file not in used_images] + this_guide_images
    form.images.choices = images

    if form.validate_on_submit():
        guide.title=form.title.data
        guide.content=form.content.data

        for img in this_guide_images:
            image = db_sess.query(Image).filter(Image.path == img).first()
            image.guide_id = None
        db_sess.flush()
        for img in form.images.data:
            guide_image = db_sess.query(Image).filter(Image.path == img).first()
            if not guide_image:
                guide_image = Image(path=img)
                db_sess.add(guide_image)
            guide_image.guide_id = guide.id

        db_sess.commit()
        return redirect('/guides')
    if request.method == 'GET':
        form.title.data = guide.title
        form.content.data = guide.content
        form.images.choices = [img for img in images]
    return render_template('refactor_guide.html', title='Изменение гайда', form=form)



def main():
    db_session.global_init("db/civ.db")
    app.run(port=7070)


if __name__ == '__main__':
    main()