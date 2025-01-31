# Gord1-RamsAI

## Introduction
Gord1-RamsAI is a web application that helps users generate recipes based on available ingredients. Users can input ingredients, specify the type of meal they want, and let the app generate recipes using OpenAI's GPT. The application provides a user-friendly interface for adding and removing ingredients, and it suggests recipes that users can prepare with the given ingredients.

## Getting Started
To run Gord1-RamsAI, follow these steps:

### 1. Open in a Container
Ensure you have Docker installed. Run the following command to build and start the container:

```sh
docker-compose up --build
```

If you are running it manually, ensure your Python environment is set up correctly.

### 2. Install Dependencies
Once inside the project folder, install dependencies using Poetry:

```sh
poetry install
```

Activate the virtual environment:

```sh
poetry shell
```

### 3. Add Your OpenAI API Key
Before running the application, you need to make an `.env` following the `.env_example` file and add your OpenAI API key:

```sh
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

Replace `your_api_key_here` with your actual OpenAI API key.

### 4. Run the Application
Start the Flask application by running:

```sh
python application/app.py
```

### 5. Open in a Browser
Once the application in a browser


## Features
- Add and remove ingredients
- Generate recipes based on available ingredients
- Get random recipe suggestions
- Interactive and user-friendly UI

