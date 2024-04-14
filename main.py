from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
MOVIE_URL = "https://api.themoviedb.org/3/search/movie"
API_KEY = "0cd81d8253fee5fd452cfb177c6f307c"
# # create the extension
db = SQLAlchemy()
# # create the app

# # configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# # initialize the app with the extension
db.init_app(app)

class Movie(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250),unique=True, nullable = True)
    year = db.Column(db.Integer, nullable = True)
    description = db.Column(db.String, nullable = True)
    rating = db.Column(db.Float, nullable = False)
    ranking = db.Column(db.Integer, nullable = False )
    review = db.Column(db.String(250), nullable = False)
    img_url = db.Column(db.String(250), nullable = True)

# with app.app_context():
#     db.create_all()


class SearchForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit  = SubmitField('Search Movie')

class DetailsForm(FlaskForm):
    rating = StringField('Your Rating out of 10', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    submit = SubmitField('Done')

# # with app.app_context():
# #     second_movie = Movie(
# #         title="Avatar The Way of Water",
# #         year=2022,
# #         description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
# #         rating=7.3,
# #         ranking=9,
# #         review="I liked the water.",
# #         img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# #     )
#     # db.session.add(second_movie)
#     # db.session.commit()




@app.route("/")
def home():
    all_movies = db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars().all()
    # for movie in all_movies:
    #     print(movie.title)
    for rank in range(len(all_movies)):
        all_movies[rank].ranking = len(all_movies)-rank 
        db.session.commit()
    return render_template("index.html",movies=all_movies)

@app.route("/delete")
def delete():
    
    # movie_to_delete = db.session.execute(db.select(Movie).order_by(Movie.id)).scalar()
    movie_id = request.args.get("id")
    movie_to_delete = db.get_or_404(Movie,movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/select", methods=['POST','GET'])
def select():
    form = SearchForm()
    if form.validate_on_submit():
            # print("Hello!")
            movie_title = form.title.data
            response = requests.get(MOVIE_URL,params={"api_key": API_KEY, "query":movie_title})
            movie_data  = response.json()['results']
            # print(movie_data)
            return render_template("select.html", data = movie_data)

    return render_template("add.html", form = form)
 
@app.route("/add")
def add():
    movie_id = request.args.get('id')
    if movie_id:
      
        response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=0cd81d8253fee5fd452cfb177c6f307c")
        data_movie = response.json()
        new_movie = Movie(title = f"{data_movie['original_title']}",img_url = f"https://image.tmdb.org/t/p/w500{data_movie['poster_path']}", year = f"{data_movie['release_date'].split('-')[0]}", description = f"{data_movie['overview']}")
        db.session.add(new_movie)
        db.session.commit()
        
        return redirect(url_for('edit', id = new_movie.id))
    # return render_template("add.html")

@app.route("/edit", methods=['POST', 'GET'])
def edit():
    details_form = DetailsForm()
    movie_id = request.args.get('id')
    movie_to_update = db.get_or_404(Movie, movie_id)
    if details_form.validate_on_submit():
        
        movie_to_update.rating = float(details_form.rating.data)
        movie_to_update.review = details_form.review.data
    #     # add_movie_data = Movie(ranking=f"{rank}", review=f"{review}")

    #     # or book_to_update = db.get_or_404(Book, book_id)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', form=details_form, movie = movie_to_update)



if __name__ == '__main__':
    app.run(debug=True)
