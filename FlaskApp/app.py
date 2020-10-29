from __init__ import app, db, login_manager
from flask_user import SQLAlchemyAdapter, UserManager
from views import view
from models import Users

db_adapter = SQLAlchemyAdapter(db,  Users)
user_manager = UserManager(db_adapter, app, login_manager=login_manager)

# Routing
app.register_blueprint(view)



if __name__ == "__main__":
    app.run(
        debug=True,
        host="localhost",
        port=5000
    )
