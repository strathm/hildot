# Use the Flutter SDK Docker image
FROM cirrusci/flutter:latest

# Set working directory
WORKDIR /app

# Copy Flutter project files
COPY . /app

# Get Flutter dependencies
RUN flutter pub get

# Expose the port for Flutter web (default: 8000)
EXPOSE 8000

# Run Flutter web server
CMD ["flutter", "run", "-d", "web", "--web-port=8000", "--release"]
