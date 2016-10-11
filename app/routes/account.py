from datetime import date
from app import app, db, bcrypt
from app.forms.account import SignUpForm
from app.models.user import UserModel
from app.util.form import validate_on_submit
from flask import render_template, request, redirect, url_for, jsonify


@app.route('/', methods=['GET', 'POST'])
def main():
    data = {"test": "hello"}
    return jsonify(data)

# TODO: 회원가입 페이지 아직 안만들어짐
@app.route('/account/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm(request.form)
    this_year = date.today().year

    if validate_on_submit(form):
        new_user = UserModel(
            username=form.username.data,
            password=bcrypt.generate_password_hash(form.password.data),
            name=form.name.data,
            nickname=form.nickname.data,
            email=form.email.data,
            gender=form.gender.data,
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('signup_complete'))

    return render_template('signup.html', form=form, this_year=this_year)


@app.route('/account/signup/complete')
def signup_complete():
    return render_template('signup_complete.html')
