import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("./demoproject-f7ba1-firebase-adminsdk-rmw9y-ea1e60aa5e.json")
# Later on make it in a way that it will read from the environment variables

firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://demoproject-f7ba1-default-rtdb.firebaseio.com/'
})

# DB Records
demo = db.reference("/demo")
demo_chat_history = db.reference("/demo_history")

# It is used as keys only
#demo_users = demo.child("users")

