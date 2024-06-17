from flask import Flask, request, jsonify
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import os
import re
from nltk import SnowballStemmer
import string
from sklearn.metrics import jaccard_score

app = Flask(__name__)

## Carga de estructuras de datos

# Carga de lo necesario para BoW
vectorizer_path_bow = os.path.join(os.path.dirname(__file__), '../API_resources/bow/vectorizer_bow.joblib')
matrix_path_bow = os.path.join(os.path.dirname(__file__), '../API_resources/bow/bow_counts.joblib')
onehot_path = os.path.join(os.path.dirname(__file__), '../API_resources/bow/onehot.joblib')

# Carga de lo necesario para TF-IDF
vectorizer_path_tfidf = os.path.join(os.path.dirname(__file__), '../API_resources/tfidf/vectorizer_tfidf.joblib')
matrix_path_tfidf = os.path.join(os.path.dirname(__file__), '../API_resources/tfidf/tfidf_counts.joblib')

# Stopwords
stpw_path = os.path.join(os.path.dirname(__file__), '../reuters/stopwords.txt')


if os.path.exists(vectorizer_path_bow) and os.path.exists(matrix_path_bow) and os.path.exists(vectorizer_path_tfidf) and os.path.exists(matrix_path_tfidf):
    vectorizer_bow = joblib.load(vectorizer_path_bow)
    bow_loaded = joblib.load(matrix_path_bow)
    onehot_loaded = joblib.load(onehot_path)
    vectorizer_tfidf = joblib.load(vectorizer_path_tfidf)
    tfidf_loaded = joblib.load(matrix_path_tfidf)
else:
    raise FileNotFoundError("Vectorizer or matrix file not found in API_resources/bow or API_resources/tfidf")

with open(stpw_path, 'r', encoding='utf-8') as file:
    stop_words = set(word.strip() for word in file.readlines())

def clean_text(*, text, stopwords):
    text = re.sub(r'\d+', '', text)
    tokens = text.lower().translate(str.maketrans('', '', string.punctuation)).split(" ")
    stemmer = SnowballStemmer("spanish")
    no_stw = [token for token in tokens if token not in stopwords]
    stemmed_tokens = [stemmer.stem(token) for token in no_stw]
    text_cleaned = " ".join(stemmed_tokens)
    return text_cleaned

def calculate_jaccard_similarity(new_doc_bin, docs_bin):
    similarities = []
    for doc_bin in docs_bin:
        similarity = jaccard_score(new_doc_bin.toarray()[0], doc_bin.toarray()[0])
        similarities.append(similarity)
    return similarities

@app.route('/process', methods=['POST'])
def process_query():
    data = request.get_json()
    if 'query' not in data or 'tv' not in data or 'tr' not in data:
        return jsonify({'error': 'Request must contain query, tv, and tr'}), 400
    
    query = data['query']
    tv = data['tv']
    tr = data['tr']
    
    preprocessed_query = clean_text(text=query, stopwords=stop_words)
    query_vector = vectorizer_tfidf.transform([preprocessed_query])
    
    cosine_similarities = cosine_similarity(query_vector, tfidf_loaded).flatten()  # Aplanar la matriz
    
    # Filtrar valores diferentes de 0
    non_zero_similarities = [index for index, similarity in enumerate(cosine_similarities) if similarity > 0]

    response = {
        'query': query,
        'tv': tv,
        'tr': tr,
        'cosine_similarities': non_zero_similarities
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
