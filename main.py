from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
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
        title = db.Column(db.String(80), unique=True, nullable=False)
        year = db.Column(db.Integer, nullable=False)
        description = db.Column(db.String(200), nullable=False)
        rating = db.Column(db.Float, nullable=False)
        ranking = db.Column(db.Integer, nullable=False)
        review = db.Column(db.String(100), nullable=False)
        img_url = db.Column(db.String(100), nullable=False)

        def __repr__(self):
            return f'<Book {self.title}>'


    db.create_all()
    def update():
        movie = Movie(
            title="Phone Booth",
            year=2002,
            description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
            rating=7.3,
            ranking=10,
            review="My favourite character was the caller.",
            img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
        )
        db.session.add(movie)
        db.session.commit()


@app.route("/")
def home():
    if request.method == 'POST':
        update()
        new_movie = Movie.query.all()
        return render_template("index.html", movie=new_movie)

    new_movie = Movie.query.all()
    return render_template("index.html", movie=new_movie)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    my_form = FormEdit()
    id_ = request.args.get("id_")
    if request.method == 'POST':
        movie_id = id_
        current_movie = Movie.query.get(movie_id)
        current_movie.rating = request.form['rating']
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
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['GET', 'POST'])
def add():
    movie_form = MovieB()
    if request.method == 'POST':
        header = {
            "Authorization": "Bearer you api key"
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


if __name__ == '__main__':
    app.run(debug=True)
