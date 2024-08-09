from flask import Flask, request, jsonify, render_template
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# setting the environment
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="SEO_Help")

client = OpenAI()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_query = request.form.get('query')

    results = collection.query(
        query_texts=[user_query],
        n_results=25
    )

    system_prompt = f"""
    You are a helpful assistant. You answer questions about Search engine optimization (SEO) talking exactly how the person in the transcripts provided does using their phrases and keeping it casual. 
    You only answer based on knowledge I'm providing you and inferring what the person in the transcript would recommend using multiple examples from the data if necessary. You don't use any internal 
    knowledge and you don't make things up.

    If you don't know the answer, say what the person in the data would say given their opinion on similar topics or related issues while still speaking and acting exactly like the person in the transcript.
    If something will hurt your SEO significantly say you will get clapped.
    Dont be broad be very specific and if helpful use examples from the data and when applicable also say what not to do.
    You dont have to worry about being too harsh say it how it is if the person in the transcript would say something is a bad idea say it and make it clear.
    --------------------

    The data:

    {str(results['documents'])}

    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages = [
            {"role":"system","content":system_prompt},
            {"role":"user","content":user_query}    
        ]
    )

    ai_response = response.choices[0].message.content
    return jsonify({"response": ai_response})

if __name__ == '__main__':
    app.run(debug=True)
