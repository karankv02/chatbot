from sklearn.feature_extraction.text import TfidfVectorizer
from langgraph.graph import StateGraph
from langgraph.constants import START
from typing_extensions import TypedDict
from sqlalchemy.sql import text
from typing import List
import json
import spacy
from sqlalchemy import create_engine, text 
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz



# Setup database connection
engine = create_engine("mysql+mysqlconnector://karan_kv:march0203@localhost/ai_chatbot_db")

# Load spaCy model for intent detection
nlp = spacy.load("en_core_web_sm")

# Load the summarization model and tokenizer with the PyTorch weights
model_name = "sshleifer/distilbart-cnn-12-6"

# Manually load model and tokenizer
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

with engine.connect() as connection:
    result = connection.execute(
        text("SELECT DISTINCT product_categories_offered FROM suppliers;")
    )
    categories = result.fetchall()
# Create the pipeline using the specified model and tokenizer
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

import json

def fetch_product_categories():
    """Fetch distinct product categories from the database."""
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT DISTINCT product_categories_offered FROM suppliers;")
            )
            
            categories = set()
            for row in result.fetchall():
                raw_string = row[0]
                try:
                    # Convert JSON-like string into a list
                    category_list = json.loads(raw_string)
                    categories.update([cat.strip() for cat in category_list])
                except json.JSONDecodeError:
                    print(f"Error decoding JSON string: {raw_string}")
            
            if not categories:  # Handle empty categories
                print("No categories found in the database.")
                return []
            return list(categories)
    except Exception as e:
        print(f"Error fetching product categories: {e}")
        return []


# Define state schema
class State(TypedDict):
    user_query: str
    intent: str
    category: str
    supplier_data: List[str]
    response: str
    next_node: str  # Add 'next_node' in the state schema for decision making

# Define node functions
def process_input(state: State) -> State:
    """Preprocess the user query and set the next node to 'Detect Intent'."""
    print("Processing user input...")
    user_query = state["user_query"].lower()
    # Set the next node for intent detection
    return {**state, "user_query": user_query, "next_node": "Detect Intent"}



def detect_intent_advanced(state: dict) -> dict:
    """Detect intent using similarity scores for user queries and intent descriptions."""
    user_query = state["user_query"]
    categories = fetch_product_categories()  # e.g., ['Laptops', 'Tablets', 'Monitors', etc.]

    # Define possible intents with example phrases
    intents = {
        "find_suppliers": [
            "Where can I buy laptops",
            "Find suppliers for laptops", 
            "Who supplies laptops", 
            "Laptop supplier",
            "Find suppliers for laptops, tablets, etc.",
            "Who provides laptops and related products"
        ],
        # Add more intents here as needed
    }

    # Define synonyms for 'suppliers', 'vendors', etc.
    synonyms = {
        "suppliers": ["suppliers", "vendors", "providers", "sellers", "distributors"],
    }

    # Prepare data for vectorization (flatten list of phrases for the intent)
    intent_phrases = [user_query] + [item for sublist in intents.values() for item in sublist]

    # Vectorize text using CountVectorizer
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(intent_phrases).toarray()

    # Calculate similarity using cosine similarity
    similarity_scores = cosine_similarity(vectors)

    # Initialize variables
    detected_intent = "unknown"  # Default intent

    if similarity_scores.shape[0] > 1:  # Check if there are multiple scores
        query_scores = similarity_scores[0, 1:]

        if query_scores.size > 0:
            max_score_idx = query_scores.argmax()  # Get the max score index
            max_score = query_scores[max_score_idx]

            # Check if max score is sufficient to detect intent
            if max_score > 0.5:  # Threshold, you can adjust this value based on your use case
                # Get the detected intent based on max_score_idx
                detected_intent = list(intents.keys())[0]  # Always taking first element here - fix below
            else:
                detected_intent = "unknown"
        else:
            detected_intent = "unknown"
    else:
        detected_intent = "unknown"

    # Handle synonym detection - check if user query contains synonyms for suppliers
    if detected_intent == "unknown":
        for synonym in synonyms["suppliers"]:
            if synonym.lower() in user_query.lower():
                detected_intent = "find_suppliers"  # Match suppliers intent
                break
    
    # Initialize category detection
    detected_category = None

    # Check for category matches using fuzzy matching
    if detected_intent == "find_suppliers":
        for category in categories:
            match_score = fuzz.partial_ratio(category.lower(), user_query.lower())
            if match_score > 80:  # Threshold for close enough match
                detected_category = category.capitalize()  # Ensure correct formatting
                break

    state.update({
        "intent": detected_intent,
        "category": detected_category if detected_intent == "find_suppliers" else "",
        "next_node": "Query Database" if detected_category else "Unknown Intent"
    })

    return state




def detect_intent(state: State) -> State:
    """Detect intent and determine product category dynamically from the database."""
    user_query = state["user_query"]
    categories = fetch_product_categories()

    if not categories:
        print("No categories found in the database.")
        return {**state, "intent": "unknown", "category": "", "next_node": "Unknown Intent"}
    
    detected_category = None
    for category in categories:
        if category.lower() in user_query.lower():
            detected_category = category.capitalize()
            break

    if "supplier" in user_query.lower() and detected_category:
        return {
            **state,
            "intent": "find_suppliers",
            "category": detected_category,
            "next_node": "Query Database",  # Move to database querying
        }

    return {**state, "intent": "unknown", "category": "", "next_node": "Unknown Intent"}




def query_database(state: State) -> State:
    """Fetch supplier data from the database."""
    category = state.get("category")
    print(f"Querying database for category: {category}")  # Debugging
    
    if not category:
        # If no category, terminate or handle it as an unknown intent
        state["next_node"] = "Unknown Intent"
        return state

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text(
                    "SELECT name, product_categories_offered, contact_info "
                    "FROM suppliers WHERE product_categories_offered LIKE :category"
                ),
                {"category": f"%{category}%"},  # Use parameterized queries for safety
            )
            suppliers = result.fetchall()

        print(f"Suppliers fetched: {suppliers}")  # Debugging output

        supplier_data = [
            f"{supplier[0]} provides {supplier[1]}. Contact: {supplier[2]}"
            for supplier in suppliers
        ] if suppliers else ["No suppliers found for the specified category."]
        
        state.update({
            "supplier_data": supplier_data,
            "next_node": "Summarize Data"  # Move to summarization after success
        })

    except Exception as e:
        error_msg = f"Error querying database: {e}"
        print(error_msg)  # Log the error
        state.update({
            "supplier_data": [error_msg],
            "next_node": "Unknown Intent"  # Fallback to an error node
        })

    return state



def summarize_data(state: dict) -> dict:
    """Summarize supplier data to generate a readable response."""
    try:
        supplier_data = state.get("supplier_data", [])
        print(f"Entering summarize_data with supplier data: {supplier_data}")

        # Prepare supplier summary text explicitly
        summarized_suppliers = []
        for supplier_entry in supplier_data:
            # Parse supplier and details
            supplier_name = supplier_entry.split(" provides ")[0].strip()
            supplier_details = supplier_entry.split(" provides ")[1].strip()

            # Create readable summary with bullet points
            summarized_suppliers.append(
                f"- {supplier_name} offers categories: {supplier_details}"
            )

        # Join the summaries into a readable response with line breaks
        summarized_text = "\n".join(summarized_suppliers)

        # Construct the final output
        if summarized_text.strip():
            state["response"] = f"Suppliers:\n{summarized_text}"
        else:
            state["response"] = "No valid supplier data found."

        print(f"Exiting summarize_data with state: {state}")
        state["next_node"] = ""  # Mark pipeline as complete
    except Exception as e:
        print(f"Error in summarize_data: {e}")
        state["response"] = "Error while summarizing supplier data."
        state["next_node"] = ""

    return state




def unknown_intent(state: State) -> State:
    """Handle unknown intents."""
    state["response"] = "Sorry, I couldn't understand your query. Please try rephrasing."
    state["next_node"] = ""  # Terminate the pipeline
    return state


def decide_intent_path(state: State) -> State:
    """Redirect flow based on detected intent."""
    if state["intent"] == "find_suppliers":
        # Set next node to query database if the intent is 'find_suppliers'
        state["next_node"] = "Query Database"
    else:
        # Otherwise, move to 'Unknown Intent'
        state["next_node"] = "Unknown Intent"
    print(f"Next node set to: {state['next_node']}")  # Log transition
    return state


def query_graph(state: State) -> State:
    """Decide which node to move to next and process accordingly."""
    if state["next_node"] == "Query Database":
        return query_database(state)
    elif state["next_node"] == "Unknown Intent":
        return unknown_intent(state)
    elif state["next_node"] == "Summarize Data":
        return summarize_data(state)
    else:
        state["next_node"] = ""  # End state or missing functionality
    return state


# Build the graph
builder = StateGraph(State)

# Add nodes to the graph
builder.add_node("Process Input", process_input)
builder.add_node("Detect Intent", detect_intent_advanced)
builder.add_node("Decide Intent Path", decide_intent_path)
builder.add_node("Query Database", query_database)
builder.add_node("Summarize Data", summarize_data)
builder.add_node("Unknown Intent", unknown_intent)


# Define edges between nodes
builder.add_edge(START, "Process Input")  # Connect START node to "Process Input"
builder.add_edge("Process Input", "Detect Intent")
builder.add_edge("Detect Intent", "Decide Intent Path")
builder.add_edge("Decide Intent Path", "Query Database")
builder.add_edge("Decide Intent Path", "Unknown Intent")

# Compile the graph
graph = builder.compile()

# Execution function
def execute_chat_pipeline(user_query: str) -> str:
    """Run the chat pipeline."""
    print(f"Starting chat pipeline for query: {user_query}")
    
    initial_state = {
        "user_query": user_query,
        "intent": "",
        "category": "",
        "supplier_data": [],
        "response": "",
        "next_node": "Process Input",  # Start from 'Process Input'
    }
    
    state = initial_state
    print(f"Initial state: {state}")

    node_functions = {
        "Process Input": process_input,
        "Detect Intent": detect_intent_advanced,
        "Decide Intent Path": decide_intent_path,
        "Query Database": query_database,
        "Summarize Data": summarize_data,
        "Unknown Intent": unknown_intent,
    }
    
    while state["next_node"]:  # Loop until next_node is empty
        node_name = state["next_node"]
        print(f"Processing node: {node_name}")
        
        # Call the corresponding function
        node_function = node_functions.get(node_name)
        if node_function:
            state = node_function(state)
            print(f"State after {node_name}: {state}")
        else:
            print(f"Invalid node: {node_name}. Terminating pipeline.")
            break  # Break the loop if an invalid node is encountered

        # Update the next node
        state["next_node"] = state.get("next_node", "")

    print(f"Final state: {state}")
    return state.get("response", "Sorry, something went wrong.")


# # Example Usage
# if __name__ == "__main__":
#     user_query = "Which suppliers provide laptops?"
#     response = execute_chat_pipeline(user_query)
#     print(f"User: {user_query}\nBot: {response}")
