# AI Chatbot for Supplier Query

This repository contains an AI-powered chatbot for detecting intents and fetching suppliers for different product categories based on user input. The chatbot processes natural language queries to identify the intent and category, with additional support for synonym matching and fuzzy text comparison.

## Features

- Intent detection using cosine similarity on query and predefined phrases.
- Synonym support to improve detection (e.g., recognizing "vendors" or "providers" as "suppliers").
- Fuzzy matching to identify categories (e.g., Laptops, Tablets, etc.).
- Ability to query supplier data based on detected category.

## Technologies Used
  - React.js
  - Python
  - MySQL (database)
  - SQLAlchemy
  - LangGraph (structure the AI chatbot workflow and decision-making process (via StateGraph).)
  - Scikit-learn (for NLP)
  - Fuzzywuzzy (for fuzzy matching)
  - Uvicorn



## Backend Setup (Python)

1. **Install Python 3.x**:
   - Download and install Python from [python.org](https://www.python.org/).

2. **Install necessary Python packages**:
   - Navigate to the backend directory and install the required packages using the following command:
     ```bash
     pip install -r requirements.txt
     ```

3. **Set up the MySQL database**:
   - Set up your MySQL database using the provided schema (see SQL file for table creation and sample data).

4. **Configure your MySQL credentials**:
   - In the `db_setup.py` file, update your MySQL credentials such as username, password, and database name in the connection setup.

5. **Start the backend server**:
   - Run the backend server using the following command:
     ```bash
     uvicorn app:app --reload
     ```

## Frontend Setup (React)

1. **Install Node.js**:
   - Download and install Node.js from [nodejs.org](https://nodejs.org/).

2. **Navigate to the frontend directory**:
   - Change the directory to `frontend`:
     ```bash
     cd frontend
     ```

3. **Install dependencies**:
   - Install the necessary dependencies for the frontend:
     ```bash
     npm install
     ```

4. **Start the React app**:
   - Run the React app on the local server:
     ```bash
     npm start
     ```

## How to Use

- Open your browser and go to [http://localhost:3000](http://localhost:3000) to access the React frontend.
- Interact with the chatbot by asking questions such as:
  - "Find suppliers for laptops"
  - "Who provides laptops?"
  - "Laptop suppliers?"

## Contributing

Feel free to fork this repository, submit issues, and make pull requests. All contributions are welcome!
