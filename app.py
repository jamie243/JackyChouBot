from flask import Flask, request, jsonify, render_template
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Setting the environment
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"  # Make sure this points to your DuckDB directory

# Initialize ChromaDB client with DuckDB persistence
try:
    chroma_client = chromadb.Client(settings=chromadb.config.Settings(
        chroma_db_impl="duckdb+parquet",  # Explicitly specify DuckDB
        persist_directory=CHROMA_PATH
    ))
except Exception as e:
    print(f"Error initializing ChromaDB client: {e}")
    raise

# Create or get collection
try:
    collection = chroma_client.get_or_create_collection(name="SEO_Info")
    print("Collection retrieved or created successfully.")
except Exception as e:
    print(f"Error getting or creating collection: {e}")
    raise

# Check if the collection actually contains data
if collection.count() == 0:
    print("Warning: The collection is empty. Make sure you've loaded data into it.")

# Initialize OpenAI client
client = OpenAI()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    try:
        user_query = request.form.get('query')

        if not user_query:
            raise ValueError("No query provided")

        # Query the collection
        results = collection.query(
            query_texts=[user_query],
            n_results=25,
            include=["documents", "metadatas"]
        )

        # Extract the top 3 metadata sources
        top_metadata = results['metadatas'][:3]
        top_results_titles = [os.path.basename(meta['source']) for meta in top_metadata[0]]

        system_prompt = f"""
        You are a helpful assistant. You answer questions about Search engine optimization (SEO) and focus on talking exactly how the person in the transcripts provided does using their phrases and keeping it casual. 
        You only answer based on knowledge I'm providing you and inferring what the person in the transcript would recommend using multiple examples from the data if necessary. You don't use any internal 
        knowledge and you don't make things up.

        If you don't know the answer, say what the person in the data would say given their opinion on similar topics or related issues while still speaking and acting exactly like the person in the transcript.
        If something will hurt your SEO significantly say you will get clapped.
        Dont be broad be very specific and if helpful use examples from the data and when applicable also say what not to do.
        You dont have to worry about being too harsh say it how it is if the person in the transcript would say something is a bad idea say it and make it clear.
        In summary you talk conversationally and exactly like the person in the transcript provided and provide the most likely response they would with as many concrete examples as possible and without being vague at all.
        dont sound like someone trying to act hip and young just normal.
        --------------------

        The data:

        {str(results['documents'])}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]
        )

        ai_response = response.choices[0].message.content
        return jsonify({"response": ai_response, "top_results": top_results_titles})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
