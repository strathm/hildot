from app import create_app

# Create the app using the factory function
app = create_app()

if __name__ == "__main__":
    # Run the app in development mode
    app.run(host="127.0.0.1", port=5000, debug=True)
