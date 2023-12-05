from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR SECRET KEY'
Bootstrap(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"

db = SQLAlchemy(app)


class MovieB(FlaskForm):
    title = StringField('Movie Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


class FormEdit(FlaskForm):
    rating = StringField('rating', validators=[DataRequired()])
    review = StringField('review', validators=[DataRequired()])
    submit = SubmitField('Submit')


with app.app_context():
    class Movie(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(80), unique=True)
        year = db.Column(db.Integer)
        description = db.Column(db.String(200))
        rating = db.Column(db.Float)
        ranking = db.Column(db.Integer)
        review = db.Column(db.String(100))
        img_url = db.Column(db.String(100))

        def __repr__(self):
            return f'<Book {self.title}>'


    db.create_all()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i

    db.session.commit()
    return render_template("index.html", movie=all_movies)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    my_form = FormEdit()
    id_ = request.args.get("id_")
    if id_:
        pass
    else:
        id_ = request.args.get("id_")
    if my_form.validate_on_submit():
        movie_id = id_
        current_movie = Movie.query.get(movie_id)
        current_movie.rating = request.form.get('rating')
        current_movie.review = request.form['review']
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', form=my_form)


@app.route('/delete')
def delete():
    # my_form = FormEdit()
    id_ = request.args.get("id_")
    movie_id = id_

    current_movie = Movie.query.get(movie_id)
    db.session.delete(current_movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['GET', 'POST'])
def add():
    movie_form = MovieB()
    if movie_form.validate_on_submit():
        header = {
            "Authorization": "Bearer SECRET APIKEY"
        }
        body = {
            'query': request.form['title'],
            'include_adult': False,
            'language': 'en-US'

        }
        response = requests.get("https://api.themoviedb.org/3/search/movie", headers=header, params=body)
        movie_data = response.json()['results']
        return render_template('select.html', data=movie_data)

    return render_template('add.html', form=movie_form)


@app.route('/find')
def find_movie():
    movie_id = request.args.get("id")
    header_ = {
        "Authorization": "Bearer SECRET APIKEY"}
    body_ = {
        'language': 'en-US'
    }
    if movie_id:
        res = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}", headers=header_, params=body_)
        data = res.json()
        movie = Movie(
            id=data['id'],
            title=data['title'],
            year=data["release_date"].split("-")[0],
            img_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(movie)
        db.session.commit()
        return redirect(url_for('edit', id_=data['id']))


if __name__ == '__main__':
    app.run(debug=True)
