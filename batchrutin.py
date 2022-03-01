from app import app
from customerSearchEngine import addDocuments

with app.app_context():
    addDocuments()
