import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "楊子青",
  "mail": "tcyang@pu.edu.tw",
  "lab": 579
}

collection_ref = db.collection("靜宜資管2026a")
collection_ref.add(doc)
