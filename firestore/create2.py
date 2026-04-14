import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "王冠元2",
  "mail": "roger478460@gmail.com",
  "lab": 579
}

doc_ref = db.collection("靜宜資管2026a")
doc_ref.add(doc)
