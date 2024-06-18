from flask import Flask, request, jsonify
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import os
import re
from nltk import SnowballStemmer
import string
import numpy as np
from scipy.sparse import csr_matrix
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
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

# doc names
docs_path = os.path.join(os.path.dirname(__file__), '../API_resources/documents.joblib')


if os.path.exists(vectorizer_path_bow) and os.path.exists(matrix_path_bow) and os.path.exists(vectorizer_path_tfidf) and os.path.exists(matrix_path_tfidf):
    vectorizer_bow = joblib.load(vectorizer_path_bow)
    bow_loaded = joblib.load(matrix_path_bow)
    vectorizer_tfidf = joblib.load(vectorizer_path_tfidf)
    tfidf_loaded = joblib.load(matrix_path_tfidf)
    documents = joblib.load(docs_path)
    document_names = list(documents.keys())
    documents_contents = list(documents.values())
else:
    raise FileNotFoundError("Vectorizer or matrix file not found in API_resources/bow or API_resources/tfidf")

with open(stpw_path, 'r', encoding='utf-8') as file:
    stop_words = set(word.strip() for word in file.readlines())

# Ejemplo para convertir un ndarray en una lista de csr_matrix
corpus_list = [csr_matrix(doc) for doc in bow_loaded]

def clean_text(*, text, stopwords):
    text = re.sub(r'\d+', '', text)
    tokens = text.lower().translate(str.maketrans('', '', string.punctuation)).split(" ")
    stemmer = SnowballStemmer("english")
    no_stw = [token for token in tokens if token not in stopwords]
    stemmed_tokens = [stemmer.stem(token) for token in no_stw]
    text_cleaned = " ".join(stemmed_tokens)
    return text_cleaned

def jaccard_similarity(query_vector, corpus_matrix):
    # Convertir la consulta a un conjunto de índices de términos presentes
    query_set = set(query_vector.indices)

    # Convertir el corpus a un conjunto de conjuntos de índices de términos presentes
    corpus_sets = [set(doc.indices) for doc in corpus_matrix]

    jaccard_similarities = []

    for doc_set in corpus_sets:
        intersection = len(query_set & doc_set)
        union = len(query_set | doc_set)
        similarity = intersection / union if union != 0 else 0
        jaccard_similarities.append(similarity)

    return np.array(jaccard_similarities)

@app.route('/process/tfidf/', methods=['POST'])
def process_query_tfidf():
    data = request.get_json()

    query = data['query']

    preprocessed_query = clean_text(text=query, stopwords=stop_words)
    query_vector = vectorizer_tfidf.transform([preprocessed_query])
    
    cosine_similarities = cosine_similarity(query_vector, tfidf_loaded).flatten()
    
    umbral = 0.2

    non_zero_similarities = []

    for index, similarity in enumerate(cosine_similarities):
        if similarity > umbral:
            doc_name = document_names[index]
            doc_content = documents_contents[index]
            non_zero_similarities.append((doc_name, float(similarity), doc_content))

    # Ordenar por similitud de mayor a menor
    non_zero_similarities.sort(key=lambda x: x[1], reverse=True)

    response = {
        'query': query,
        'cosine_similarities': non_zero_similarities
    }
    
    return jsonify(response)


@app.route('/process/bow/', methods=['POST'])
def process_query_bow():
    data = request.get_json()
    query = data['query']

    preprocessed_query = clean_text(text=query, stopwords=stop_words)
    query_vector = vectorizer_bow.transform([preprocessed_query])
    
    jaccard_similarities = jaccard_similarity(query_vector, corpus_list).flatten()
    
    umbral = 0.010
    non_zero_similarities = []
    for index, similarity in enumerate(jaccard_similarities):
        if similarity > umbral:
            doc_name = document_names[index]  # Asumiendo que document_names está cargado
            doc_content = documents_contents[index]
            non_zero_similarities.append((doc_name, float(similarity), doc_content))  # Convertimos a float para serialización JSON

    # Ordenar por similitud de mayor a menor
    non_zero_similarities.sort(key=lambda x: x[1], reverse=True)

    response = {
        'query': query,
        'jaccard_similarities': non_zero_similarities
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
