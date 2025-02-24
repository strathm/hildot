from app import create_app
from flask_migrate import Migrate
from app import db


# Create the Flask app instance
app = create_app()

# Initialize Flask-Migrate for handling database migrations
migrate = Migrate(app, db)

if __name__ == '__main__':
    # Run the Flask app with debugging enabled for development
    app.run(debug=True, host='0.0.0.0', port=5000)
