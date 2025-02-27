import os
import cohere
import pdfplumber
import PyPDF2
import nltk
from flask import Flask, render_template, request, jsonify

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



# Initialize Flask app
app = Flask(__name__, static_url_path='/static')  # ✅ Ensures static files are served correctly

# Initialize Cohere API (Replace with your API key)
co = cohere.Client('dSe5i608cTtTQli1JJ15e9N60zmY8uFI8sHRFmau')  # Replace with your Cohere API key

# ✅ Home route (renders the main index.html)
@app.route("/")
def index():
    return render_template("index.html")
# ✅ Route for Cohere Chatbot Interaction
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_input = data.get("question")  # FIXED: Correct JSON key

    if not user_input:
        return jsonify({"answer": "Please enter a question!"}), 400

    try:
        response = co.generate(
            model="command-xlarge-nightly",
            prompt=user_input,
            max_tokens=300,
            temperature=0.7,
            truncate="NONE",
        )

        answer = response.generations[0].text.strip()  # FIXED: Access correct text
        return jsonify({"answer": answer})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"answer": "An error occurred while processing your request."}), 500



# ✅ Routes to serve static pages
@app.route("/bot-selection.html")
def bot_selection():
    return render_template("bot-selection.html")


@app.route("/chatbot.html")
def chatbot():
    return render_template("chatbot.html")

@app.route("/terms.html")
def terms():
    return render_template("terms.html")

@app.route("/pdfchatbot")
def pdfchatbot():
    return render_template("pdfchatbot.html")

@app.route("/school")
def school():
    return render_template("school.html")


# ✅ Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)







# Download NLTK resources
nltk.download("punkt")

# Initialize Flask app
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

# Function to find the most relevant answer
def get_answer_from_text(text, question):
    sentences = nltk.sent_tokenize(text)
    if not sentences:
        return "No readable text found in the PDF."
    
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(sentences + [question])
    similarity = cosine_similarity(vectors[-1], vectors[:-1])
    most_relevant_sentence_index = similarity.argmax()
    
    return sentences[most_relevant_sentence_index]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "pdf" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        pdf_file = request.files["pdf"]
        if pdf_file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_file.filename)
        pdf_file.save(file_path)

        extracted_text = extract_text_from_pdf(file_path)
        return render_template("pdf-chatbot.html", text=extracted_text)

    return render_template("pdf-chatbot.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    pdf_text = data.get("text")
    question = data.get("question")

    if not pdf_text or not question:
        return jsonify({"error": "Missing text or question"}), 400

    answer = get_answer_from_text(pdf_text, question)
    return jsonify({"answer": answer})




# API Endpoint for the Chatbot
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    selected_class = data.get("selected_class")
    selected_subject = data.get("selected_subject")
    user_question = data.get("question")

    if not selected_class or not selected_subject or not user_question:
        return jsonify({"answer": "Please select a class, subject, and enter a question!"}), 400

    try:
        
        # Create a prompt for the AI model
        prompt = (f"As a knowledgeable and engaging teacher for {selected_class} grade students, "f"explain concepts in {selected_subject} in a simple, clear, and concise manner. "f"Ensure your response is easy to understand with relevant examples where needed. "f"Now, answer the following student question: {user_question}")
        
        response = co.generate(
            model="command-xlarge-nightly",
            prompt=prompt,
            max_tokens=300,
            temperature=0.7,
            truncate="NONE",
        )

        answer = response.generations[0].text.strip()
        return jsonify({"answer": answer})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"answer": "An error occurred while processing your request."}), 500
