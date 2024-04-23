from flask import Flask, render_template, request, jsonify, url_for
from data import db_session, users_resources
from data.users import User
from forms.user import RegisterForm, LoginForm, EditForm
from werkzeug.utils import redirect
from flask import make_response
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_restful import abort, Api
from text import *


# создание flask-приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
# создание объект RESTful-API
api = Api(app)
# для списка объектов
api.add_resource(users_resources.UsersListResource, '/api/v2/users')
# для одного объекта
api.add_resource(users_resources.UsersResource, '/api/v2/users/<int:users_id>')
db_session.global_init("db/blogs.db")
login_manager = LoginManager()
login_manager.init_app(app)
class_animals = ClassAnimals()
region_animals = RegionsAnimals()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def route():
    return render_template('index.html')


# страница раздела "классы"
@app.route('/class', methods=['GET', 'POST'])
def route_class():
    class_id = classes[class_animals.id_class]
    if request.method == 'POST':
        f = request.form.get('input-select')
        class_animals.id_class = f
        class_id = classes[f]
    return render_template('class.html', animals=animals_classes, class_id=class_id)


# переход на страницу с теорией из раздела "классы"
@app.route('/animal_class/<id_animal>')
def animal_class(id_animal):
    f = class_animals.get_text(id_animal)
    text = f[0]
    img = f[1]
    return render_template('animal_teori.html', name=id_animal, text=text, img=img)


# страница раздела "регионы"
@app.route('/regions', methods=['GET', 'POST'])
def route_regions():
    region_animals.set_animals()
    region = regions[region_animals.id_region]
    if request.method == 'POST':
        f = request.form.get('input-select')
        region_animals.id_region = f
        region = regions[f]
        region_animals.set_animals()
    return render_template('regions.html', region=region, animals=region_animals.animals_regions,
                           animals_test=region_animals.animals_regions_test_name)


# переход на страницу с теорией из раздела "регионы"
@app.route('/animal_regions/<id_animal>')
def animal_regions(id_animal):
    f = region_animals.get_text(id_animal)
    text = f[0]
    img = f[1]
    return render_template('animal_teori.html', name=id_animal, text=text, img=img)


# переход на страницу с тестом из раздела "классы"
@app.route('/animal_regions_test/<id_animal>')
def animal_regions_test(id_animal):
    f = region_animals.animals_regions_test[id_animal]
    return render_template("animals_regions/" + f, name=id_animal)


# страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def reqister():
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
            image="Icon_prof.svg",
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


# страница авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


# страница редактирования профиля
@app.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_users(id):
    form = EditForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if user:
            form.name.data = user.name
            form.email.data = user.email
            form.image.data = user.image
        else:
            abort(404)
    elif request.method == 'POST':
        f = request.files['file']
        f.save(f"static/img/users_av/{f.filename}")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id).first()
        if user:
            user.name = form.name.data
            user.email = form.email.data
            user.image = f.filename
            user.set_password(form.password.data)
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('edit_user.html', title='Редактирование профиля', form=form)


# выход из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


app.run()
