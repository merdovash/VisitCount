from flask import render_template, send_from_directory
from flask_wtf import FlaskForm
from wtforms import SubmitField, validators, StringField, PasswordField
from flask_material import Material

from Server.Server import app
from DataBase2 import Session, Auth

Material(app)


class SignInForm(FlaskForm):
    user_name = StringField('Логин', [validators.required()])
    password = PasswordField('Пароль', [validators.required()])

    submit = SubmitField('Вход')

    def auth(self)->Auth:
        session = Session()

        user = session.query(Auth).filter(Auth.login==self.user_name.data).filter(Auth.password==self.password.data).first()

        return user


@app.route('/cabinet', methods=['GET', 'POST'])
def cabinet():
    form = SignInForm()

    user = form.auth()
    print(form.user_name, user)
    if user is not None:
        return send_from_directory('templates', 'cabs.html')
    return render_template('signin.html', form=form)

