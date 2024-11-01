import os
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdatabase.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

class Book(db.Model):
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)

    def __repr__(self):
        return "<Title: {}>".format(self.title)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String(80), db.ForeignKey('book.title'), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<Feedback for {}: {}>".format(self.book_title, self.content)

@app.route('/', methods=["GET", "POST"])
def home():
    books = None
    if request.form:
        try:
            book = Book(title=request.form.get("title"))
            db.session.add(book)
            db.session.commit()
        except Exception as e:
            print("Failed to add book")
            print(e)
    books = Book.query.all()
    return render_template("index.html", books=books)

@app.route("/update", methods=["POST"])
def update():
    try:
        newtitle = request.form.get("newtitle")
        oldtitle = request.form.get("oldtitle")
        book = Book.query.filter_by(title=oldtitle).first()
        book.title = newtitle
        db.session.commit()
    except Exception as e:
        print("Couldn't update book title")
        print(e)
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    title = request.form.get("title")
    book = Book.query.filter_by(title=title).first()
    db.session.delete(book)
    db.session.commit()
    return redirect("/")

# Adicione a função de feedback aqui
@app.route("/feedback/<title>", methods=["GET", "POST"])
def feedback(title):
    if request.method == "POST":
        feedback_content = request.form.get("feedback")
        feedback_entry = Feedback(book_title=title, content=feedback_content)
        db.session.add(feedback_entry)
        db.session.commit()
        return redirect(f"/feedback/{title}")

    feedbacks = Feedback.query.filter_by(book_title=title).all()
    return render_template("feedback.html", title=title, feedbacks=feedbacks)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

# Código para criar as tabelas
from app import db, app

with app.app_context():
    db.create_all()
