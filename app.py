from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade

from model import db, seedData


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/Bank'
db.app = app
db.init_app(app)
migrate = Migrate(app, db)


@app.route("/")
def startpage():
    #trendingCategories = Category.query.all()
    #trendingCategories=trendingCategories
    return render_template("index.html")

@app.route("/charts")
def charts():
    return render_template("pages/charts/chartjs.html")

@app.route("/category/<id>")
def category(id):
    products = Product.query.all()
    return render_template("category.html", products=products)


if __name__ == "__main__":
    with app.app_context():
        upgrade()

    app.run(host="127.0.0.1", port=5000, debug=True)
    seedData(db)
