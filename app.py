from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db_config import get_connection  # Import the database connection function
from transformers import pipeline
from chat_pipeline import execute_chat_pipeline

app = FastAPI()  # Initialize FastAPI instance
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", tokenizer="sshleifer/distilbart-cnn-12-6")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Explicitly allow your frontend's origin
    allow_credentials=True,  # Allow cookies or authentication headers
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

# Define the request body schema
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def handle_query(request: QueryRequest):
    print(f"Received query: {request.query}")
    user_query = request.query.lower()
    response = execute_chat_pipeline(user_query)
    print(f"Response generated: {response}")
    return {"response": response}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    return response


@app.get("/")
def root():
    return {"message": "Welcome to the AI-Powered Chatbot API!"}
# Load the summarization model



@app.get("/summarize-suppliers")
def summarize_suppliers():
    connection = get_connection()
    if not connection:
        return {"error": "Failed to connect to the database"}
    
    cursor = connection.cursor()
    cursor.execute("SELECT name, contact_info, product_categories_offered FROM suppliers;")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    # Format the data with validations
    supplier_text = ""
    for row in rows:
        name = row[0]
        contact_info = row[1]
        categories = row[2]
        
        if isinstance(contact_info, dict) and 'email' in contact_info and 'phone' in contact_info:
            email = contact_info['email']
            phone = contact_info['phone']
        else:
            email = "N/A"
            phone = "N/A"

        if isinstance(categories, list):
            categories = ", ".join(categories)

        supplier_text += f"{name} offers {categories}. Contact: email={email}, phone={phone}.\n"

    # Generate the summary
    summary = summarizer(supplier_text.strip(), max_length=60, min_length=30, do_sample=False)
    return {"summary": summary[0]['summary_text']}


@app.get("/suppliers")
def get_suppliers():
    # Get the database connection
    connection = get_connection()
    if not connection:  # Handle connection failure
        return {"error": "Failed to connect to the database"}

    # Query the database for suppliers
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM suppliers;")
    rows = cursor.fetchall()  # Fetch all supplier records

    # Close the connection
    cursor.close()
    connection.close()

    # Format the response
    suppliers = []
    for row in rows:
        suppliers.append({
            "id": row[0],
            "name": row[1],
            "contact_info": row[2],
            "product_categories_offered": row[3],
        })

    return suppliers  # Return the list of suppliers as JSON


@app.get("/products")
def get_products():
    connection = get_connection()
    if not connection:
        return {"error": "Failed to connect to the database"}

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products;")
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    products = []
    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "brand": row[2],
            "price": row[3],
            "category": row[4],
            "description": row[5],
            "supplier_id": row[6],
        })

    return products
