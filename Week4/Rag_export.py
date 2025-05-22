# %% [markdown]
# ## **Pre-read for RAG Module Sessions 1 & 2: Building the Retrieval Foundation**
# 
# This document provides a high-level overview of the first two sessions of the Retrieval-Augmented Generation (RAG) module, covering necessary installations, topics, and key learning objectives. We will focus on building the essential data preparation and retrieval components of a RAG system, with hands-on work centered around using the **Qdrant vector database** in its **local, in-memory configuration** via the `qdrant-client` library.
# 
# ### **Installation Prerequisites**
# 
# To follow along with the practical exercises, you will need Python (3.8+ recommended) and the following libraries installed. We highly recommend using a virtual environment.
# 
# Run the following command in your terminal:
# 
# ```shell
#     pip install langchain-text-splitters langchain-community langchain-huggingface langchain-qdrant sentence-transformers qdrant-client numpy scikit-learn rank_bm25
# ```
# 
# This command installs libraries for:
# 
# * Text splitting (`langchain-text-splitters`).  
# * LangChain integrations for embeddings and vector stores (`langchain-community`, `langchain-huggingface`, `langchain-qdrant`).  
# * Generating vector embeddings (`sentence-transformers`).  
# * Interacting with Qdrant locally (`qdrant-client`).  
# * Numerical operations (`numpy`).  
# * Keyword search concepts (`scikit-learn` for TF-IDF, `rank_bm25` for BM25).
# 
# **Note on Qdrant:** For these sessions, we will use the `qdrant-client` library to run Qdrant entirely in your local process memory (`location=":memory:"`). This requires **no separate Qdrant server installation or Docker setup**.
# 
# ### **Session 1: Foundations \- Introduction to RAG and Document Preparation**
# 
# **Session Goal:** Introduce the core concepts of RAG, explain why it's necessary, outline its workflow, and delve into preparing your data by chunking documents. We will also introduce the basics of keyword search and the fundamental idea of vectorization for semantic understanding.
# 
# **Topics You Will Learn:**
# 
# * **What is RAG and Why Use It?** Understand RAG as an architectural pattern to enhance LLMs by giving them access to external knowledge. Learn how RAG helps overcome LLM limitations like static knowledge, hallucination, and lack of access to private data. Explore various use cases.  
# * **Core RAG Architecture & Workflow:** Identify the main components: External Knowledge Source (Vector Database), Retriever, and Generator (LLM). Understand the Ingestion (data preparation, indexing) and Inference (query processing, retrieval, generation) stages.  
# * **Document Preparation: Chunking:** Learn why large documents must be split into smaller "chunks" due to LLM context window limitations. Understand that chunking strategy impacts retrieval quality.  
# * **Chunking Strategies:** Cover practical methods using LangChain:  
#   * **Fixed-Size Chunking:** Splitting by a fixed character count, with optional overlap.  
#   * **Recursive Character Text Splitting:** Splitting using a list of separators to preserve semantic units.  
#   * *(Other strategies like Semantic or Document-Based chunking will be mentioned conceptually)*.  
# * **Keyword Search Fundamentals:** Basic concepts like TF-IDF and BM25 will be introduced as traditional methods relying on exact word matching. Contrast this with semantic understanding.  
# * **Introduction to Vectorization:** Learn how text is converted into numerical vectors (embeddings) that capture meaning. Understand that texts with similar meanings are close in vector space. Introduction to **Transformer models** and **Sentence Transformers** like `all-MiniLM-L6-v2` for creating these embeddings.
# 
# **Key Takeaways:**
# 
# After Session 1, you should be able to:
# 
# * Explain the purpose and workflow of a RAG system.  
# * Understand the need for and challenges of document chunking.  
# * **Implement fixed-size and recursive text splitting using LangChain**.  
# * Explain the difference between keyword search and semantic search.  
# * Understand the concept of vector embeddings and how they represent text meaning numerically.

# %%
# Installing Prereqs
# pip install -qq langchain-text-splitters langchain-community langchain-huggingface langchain-qdrant sentence-transformers qdrant-client numpy scikit-learn rank_bm25


# %% [markdown]
# The pre-req steps to use the Gemini API key with Python:
# 
# 1.  **Get API Key:** Go to [aistudio.google.com](https://aistudio.google.com/), sign in, and create/copy your API key (secure it immediately).
# 2.  **Install Library:** In your terminal, run `pip install -q -U google-generativeai`.
# 3.  **Set API Key Securely:**
#     * **Recommended:** Set it as an environment variable (e.g., `export GOOGLE_API_KEY="YOUR_KEY"` in terminal/shell config).
#     * **Colab:** Use Colab Secrets to store `GOOGLE_API_KEY`.
# 4.  **Configure in Python:** In your script, retrieve the key (e.g., `os.getenv('GOOGLE_API_KEY')` or `userdata.get('GOOGLE_API_KEY')`) and then use `genai.configure(api_key=YOUR_KEY)`.
# 
# [Gemini API Key](https://aistudio.google.com/u/1/apikey)

# %%
import google.generativeai as genai
from dotenv import load_dotenv  # For loading API key from a .env file
import os
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model_name = 'gemini-2.0-flash'

model = genai.GenerativeModel(model_name)

# %% [markdown]
# ### **What is RAG?**
# 
# RAG is an AI framework that enhances the capabilities of LLMs by enabling them to access, retrieve, and incorporate external, up-to-date, and authoritative information into their responses. It combines the strengths of two distinct paradigms:
# 
# 1. **Retrieval:** The ability to efficiently search and retrieve relevant information from a vast corpus of documents.  
# 2. **Generation:** The LLM's ability to generate coherent and contextually relevant text.
# 
# In essence, RAG acts as a bridge, allowing LLMs to look up information in a knowledge base *before* formulating a response, much like a human would consult a textbook or database to answer a complex question.
# 
# ### **Why is RAG Needed?**
# 
# RAG addresses several critical limitations of standalone LLMs:
# 
# 1. **Mitigating Hallucinations:** One of the most significant challenges with LLMs is their tendency to invent information, especially when they don't have a confident answer. By grounding their responses in retrieved facts, RAG significantly reduces the likelihood of hallucinations, leading to more reliable and trustworthy outputs.  
# 2. **Access to Up-to-Date Information:** LLMs have a knowledge cutoff date, meaning they cannot access information beyond their last training update. RAG allows them to query continually updated databases, ensuring their responses are current and accurate, vital for dynamic fields like news, finance, or scientific research.  
# 3. **Domain-Specific Knowledge:** Pre-trained LLMs are generalists. They lack specific knowledge about a particular company's internal documents, proprietary data, or niche industry information. RAG enables LLMs to tap into these private, domain-specific knowledge bases, making them useful for enterprise-level applications.  
# 4. **Transparency and Explainability:** When using RAG, the generated answer can often be directly linked back to the source documents from which the information was retrieved. This provides a degree of explainability and allows users to verify the claims, building trust in the AI system.  
# 5. **Reduced Training Costs:** Instead of constantly re-training or fine-tuning large models on new data (which is incredibly expensive and time-consuming), RAG offers a more agile way to update an LLM's knowledge by simply updating the external knowledge base.
# 
# ### **How RAG Works (The Process)**
# 
# The RAG process typically involves three main steps:
# 
# 1. **Retrieval:** When a user poses a query (Q), the system first searches a vast external knowledge base (D) (e.g., a vector database containing embeddings of documents, or a conventional search index). The goal is to retrieve the most relevant passages, documents, or snippets (R) related to the query. This step often uses techniques like semantic search, keyword search (BM25), or hybrid approaches.
# 
#     R=Retrieve(Q,D)  
# 2. **Augmentation:** The retrieved information (R) is then concatenated or integrated with the original user query (Q) to form an augmented prompt (). This new, enriched prompt provides the LLM with the necessary context and factual grounding.
# 
#     Paug​=Augment(Q,R)  
# 3. **Generation:** Finally, the augmented prompt (Paug​) is fed into the LLM. The LLM then generates a coherent and accurate answer (A) based on its inherent language understanding capabilities and the specific information provided in the augmented prompt.
# 
#     A=Generate(Paug​,LLM)
# 
# In essence, RAG transforms an LLM from a black box of pre-trained knowledge into a dynamic, fact-checking, and context-aware reasoning engine, making it a powerful tool for building more reliable and sophisticated AI applications.
# 

# %%
# Without any context

prompt = '''
Given the user query, answer the user to the best of your ability.
Enusre you are polite and helpful.
If you do not know the answer, say "I don't know" and offer to help with something else.

User Query: {user_query}
'''

user_query = 'I need to know which day of the week is the lowest employee attendance.'

response = model.generate_content(prompt.format(user_query=user_query))

print(response.text)

# %%
# With Context

import numpy as np
import pandas as pd

attendance = np.random.randint(0, 2, size=(10, 5))

attendance = pd.DataFrame(
    attendance, columns=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
attendance.index.name = 'Employee ID'

context = attendance.to_markdown()


prompt = '''
Given the user query, answer the user to the best of your ability.
Enusre you are polite and helpful.
If you do not know the answer, say "I don't know" and offer to help with something else.

User Query: {user_query}

Context:

{context}
'''

response = model.generate_content(
    prompt.format(
        user_query=user_query,
        context=context,
    )
)

print(response.text)

# %%
# Loading Sample Dataset
# https://raw.githubusercontent.com/paraschopra/generating-text-small-corpus/refs/heads/master/all_ml_ideas.csv

corpus = pd.read_csv(
    'all_ml_ideas.csv',
    sep='------',
    engine='python',
    header=None,
    names=['text']
)
corpus

# %% [markdown]
# ## Basic Keyword Search
# 
# Keyword search represents the most fundamental and intuitive form of information retrieval, forming the backbone of search engines for decades. At its core, keyword search operates on a simple premise: it matches the specific words (keywords) entered by a user in a query against the words present in a collection of documents. It's often the first interaction point for users seeking information, relying on direct lexical matches rather than deeper semantic understanding.
# 
# ### **The Core Principle**
# 
# When a user inputs a query, a keyword search engine takes these terms and looks for their occurrences within its indexed documents. The primary goal is to identify documents that contain one or more of the specified keywords. For instance, if a user searches for "best Italian restaurant," the system would attempt to find documents containing "best," "Italian," and "restaurant."
# 
# To facilitate rapid searching, keyword search engines typically rely on an **inverted index**. An inverted index is essentially a data structure that maps terms to the documents in which they appear. It looks something like this:
# 
# * "restaurant" \[Document 1, Document 5, Document 12\]  
# * "Italian" → \[Document 1, Document 8, Document 12\]  
# * "best" → \[Document 5, Document 12, Document 20\]
# 
# When a query comes in, the engine quickly consults this index to retrieve a list of documents containing the query terms.
# 
# ### **Basic Ranking and Relevance**
# 
# Once a set of matching documents is identified, they need to be ranked by relevance. In its simplest form, a keyword search might rank documents based on:
# 
# 1. Number of Matching Keywords: Documents containing more of the query terms are considered more relevant. For example, a document containing all three terms ("best," "Italian," "restaurant") would be ranked higher than one containing only "Italian" and "restaurant." A very simple conceptual score could be represented as:  
#    Let Q=q1​,q2​,…,qm​ be the set of keywords in the query, and D be a document.  
# 2. Score(D,Q)=i=1∑m​I(qi​∈D)  
# 3. where I(qi​∈D) is an indicator function that equals 1 if term qi​ is present in document D, and 0 otherwise.  
# 4. **Keyword Proximity:** Documents where the keywords appear closer together are often ranked higher, as this might indicate a more coherent discussion of the topic.  
# 5. **Term Position:** Keywords appearing in important fields like the document title, headings, or metadata might be given more weight than those in the body text.  
# 6. **Boolean Logic:** Users can often refine queries using Boolean operators like AND (all terms must be present), OR (at least one term must be present), and NOT (a term must not be present).
# 
# ### **Advantages of Keyword Search**
# 
# * **Simplicity:** It's easy for users to understand and for developers to implement a basic version.  
# * **Speed:** With well-optimized inverted indexes, keyword searches can be incredibly fast, even across vast document collections.  
# * **Effectiveness for Precise Queries:** When a user knows the exact terms they are looking for, keyword search can be highly effective in retrieving relevant results.
# 
# ### **Limitations of Keyword Search**
# 
# Despite its widespread use, keyword search suffers from significant limitations:
# 
# * **Lack of Semantic Understanding:** This is its most prominent drawback. Keyword search cannot grasp the underlying meaning or intent behind words. It treats "car" and "automobile" as distinct terms, failing to recognize them as synonyms. It also struggles with polysemy (words with multiple meanings, like "bank").  
# * **Ignores Word Order and Context:** Unless explicitly using an exact phrase search (e.g., "machine learning" in quotes), keyword search views text as a "bag of words." It cannot distinguish between "man bites dog" and "dog bites man."  
# * **Recall and Precision Issues:** It can suffer from low **recall** (failing to retrieve all relevant documents if they use different vocabulary) and low **precision** (retrieving irrelevant documents if keywords are too broad or common).  
# * **Spelling Sensitivity:** It is highly sensitive to typos and misspellings; a single incorrect letter can lead to zero results.
# 
# In conclusion, keyword search remains a fundamental component of most search systems due to its speed and simplicity. However, its inherent limitations regarding semantic understanding and contextual awareness have driven the development of more sophisticated techniques like TF-IDF, BM25, and ultimately, neural network-based semantic search models that aim to bridge the gap between keywords and true meaning.
# 
# 

# %%
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
# nltk.download('punkt')
# nltk.download('stopwords')


def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text.lower())
    # Remove stopwords
    tokens = [
        word for word in tokens if word not in stopwords.words('english')]
    # Remove special characters
    tokens = [re.sub(r'[^a-zA-Z0-9]', '', word) for word in tokens]
    # Remove empty strings
    tokens = [word for word in tokens if word != '']
    return tokens


search_query = 'What is the best way to learn machine learning?'

preprocessed_query = preprocess_text(search_query)

search_query, preprocessed_query

# %% [markdown]
# ## The Bag-of-Words (BoW) model
# 
# The Bag-of-Words (BoW) model is a foundational and historically significant technique in natural language processing (NLP) and information retrieval. At its core, BoW simplifies text representation by treating a document or query as an unordered collection of its words, essentially like words thrown into a "bag." The key characteristic is that it disregards grammar, syntax, and even the order of words, focusing solely on the presence and frequency of individual words within the text.
# 
# ### **How Bag-of-Words Works for Search**
# 
# For a search engine to utilize a BoW model, it first processes a large collection of documents to build a comprehensive vocabulary – a unique list of all words found across the entire corpus. Each word in this vocabulary becomes a feature or dimension in a vector space.
# 
# When a document is processed, it's converted into a vector where each component corresponds to a word in the vocabulary, and its value typically represents the frequency of that word within the document. For example, if the vocabulary contains "cat," "dog," "chase," and "tree," and a document is "The cat chases the dog," its BoW representation might be {"cat": 1, "dog": 1, "chase": 1} (ignoring common words like "the").
# 
# When a user submits a search query, that query is also transformed into a similar BoW vector. The search engine then calculates the similarity between the query's vector and the vectors of all documents in its index. Common similarity measures include:
# 
# * **Dot Product:** A simple count of shared words.  
# * **Cosine Similarity:** Measures the cosine of the angle between two vectors, indicating how similar their directions are. This is often preferred as it's normalized by document length, preventing longer documents from being unfairly favored just because they contain more words.
# 
# Documents are then ranked based on their similarity scores to the query, with higher scores indicating greater relevance.
# 
# ### **Enhancements to the Basic BoW Model**
# 
# While the core BoW is straightforward, several enhancements improve its effectiveness:
# 
# * **Stop Words Removal:** Common words like "a," "the," "is," "and" are often removed before creating the BoW. These words are frequent but carry little semantic meaning for distinguishing documents. Removing them reduces noise and improves efficiency.  
# * **Stemming and Lemmatization:** To account for variations of words (e.g., "run," "running," "ran"), stemming (reducing words to their root, like "run") or lemmatization (reducing words to their dictionary form, like "am," "is," "are" to "be") is applied. This ensures that different grammatical forms of the same word are treated as identical, improving matching accuracy.  
# * **TF-IDF (Term Frequency-Inverse Document Frequency):** This is a widely used weighting scheme that goes beyond simple word counts.  
#   * **Term Frequency (TF):** Measures how frequently a word appears in a document.  
#   * Inverse Document Frequency (IDF): Measures how rare a word is across the entire document collection. Words that are rare but appear in a specific document are considered more important.  
#     By multiplying TF and IDF, the BoW model gives more weight to words that are both frequent in a specific document and rare across the entire corpus, thus improving the relevance ranking.
# 
# ### **Advantages and Limitations**
# 
# The Bag-of-Words model offers several advantages:
# 
# * **Simplicity and Interpretability:** It's conceptually easy to understand and implement.  
# * **Computational Efficiency:** Building and comparing BoW representations is computationally less demanding compared to more advanced methods.  
# * **Effectiveness:** Despite its simplicity, it performs reasonably well for many fundamental text classification and retrieval tasks, serving as a strong baseline.
# 
# However, BoW also has significant limitations:
# 
# * **Loss of Semantic Meaning and Word Order:** This is its most critical drawback. BoW completely ignores the context, grammar, and order of words. For instance, "The dog bit the man" and "The man bit the dog" would have identical BoW representations, even though their meanings are vastly different. It cannot capture phrases or idiomatic expressions.  
# * **Synonymy and Polysemy:** It struggles with synonyms (e.g., "car" and "automobile" are treated as distinct words) and polysemy (words with multiple meanings, like "bank" – a river bank vs. a financial institution – are treated as the same word).  
# * **High Dimensionality and Sparsity:** For large text corpora, the vocabulary can become enormous, leading to high-dimensional vectors that are mostly empty (sparse), making computations less efficient and potentially impacting accuracy.
# 
# In conclusion, while the Bag-of-Words model remains a foundational concept and is surprisingly effective for its simplicity, its inherent limitation of ignoring word order and deeper semantic relationships has paved the way for more sophisticated NLP techniques like word embeddings (Word2Vec, GloVe) and, more recently, transformer-based models (like BERT, GPT, and Gemini), which are designed to capture contextual and semantic nuances of language.
# 

# %%
# Brute Force Search with Score based ranking

import re
# regex replace only to keep alphanumeric characters
# and remove special characters
pattern = r'[^a-zA-Z0-9\s]'

search_tokens = re.sub(pattern, '', search_query).lower().split()

print(search_tokens)


def score(text, search_tokens):
    score = 0
    for token in search_tokens:
        if token in text:
            score += 1
    return score


def brute_search(corpus, search_tokens):
    corpus = corpus.copy()
    corpus['score'] = corpus['text'].apply(lambda x: score(x, search_tokens))
    return corpus.sort_values(by='score', ascending=False)


print(brute_search(corpus, search_tokens).head(10).to_markdown())

# %% [markdown]
# ## TF-IDF Vectorization and Search
# 
# In the realm of information retrieval and natural language processing, simply counting words (as in the basic Bag-of-Words model) often falls short in determining the true relevance of a document to a search query. This is where TF-IDF, short for Term Frequency-Inverse Document Frequency, emerges as a powerful and widely used statistical measure. TF-IDF provides a numerical statistic that reflects how important a word is to a document in a collection or corpus.
# 
# ### **Breaking Down TF-IDF**
# 
# The TF-IDF score for a word in a document is a product of two components:
# 
# 1. **Term Frequency (TF):** This measures how frequently a term (word) appears within a specific document. The idea is straightforward: if a word appears many times in a document, it's likely to be important to that document's content. However, simply using raw counts can be misleading, as longer documents will naturally have higher term frequencies for most words. To mitigate this, TF is often normalized, for example, by dividing the raw count by the total number of terms in the document. TF(t,d)=Total number of terms in document dNumber of times term t appears in document d​  
# 2. **Inverse Document Frequency (IDF):** While TF highlights words frequent within a document, it doesn't account for the overall importance of the word across the entire collection of documents. Words like "the," "a," and "is" appear frequently in almost all documents but carry little unique meaning or discriminative power. IDF addresses this by assigning a higher weight to terms that are rare across the entire corpus and a lower weight to common terms. IDF(t,D)=log(Number of documents d containing term tTotal number of documents N​) The logarithm helps to scale the values. A higher IDF indicates that the term is rare and therefore more significant.
# 
# ### **The TF-IDF Score and Vectorization**
# 
# The TF-IDF score for a term in a document is then calculated by multiplying its TF and IDF values: TFIDF(t,d,D)=TF(t,d)×IDF(t,D)
# 
# This combined score assigns a high value to terms that appear frequently in a particular document but rarely in the overall corpus. Conversely, terms that are common across many documents (like stop words) or very rare in a single document will have low TF-IDF scores.
# 
# **TF-IDF Vectorization** involves representing each document in a collection as a vector in a high-dimensional space. Each dimension of this vector corresponds to a unique term in the vocabulary of the entire corpus. The value for each dimension in a document's vector is the TF-IDF score of the corresponding term within that document. This process transforms unstructured text into a structured numerical format that machine learning algorithms can easily process.
# 
# ### **TF-IDF for Search**
# 
# When a user submits a search query, the same TF-IDF vectorization process is applied to the query itself. The query is treated as a short document, and its terms are assigned TF-IDF weights based on their frequency in the query and their inverse document frequency across the entire document collection.
# 
# Once both the query and all documents in the collection are represented as TF-IDF vectors, search becomes a problem of **vector space model similarity**. The search engine calculates the similarity between the query vector and each document vector. The most common similarity metric used for this is **Cosine Similarity**, which measures the cosine of the angle between two vectors. A cosine similarity closer to 1 indicates higher similarity (vectors pointing in the same direction), meaning the document is highly relevant to the query.
# 
# The documents are then ranked in descending order of their cosine similarity scores, presenting the most relevant results to the user first.
# 
# ### **Advantages and Limitations**
# 
# **Advantages of TF-IDF:**
# 
# * **Improved Relevance:** By giving more weight to rare and important terms, TF-IDF often produces more relevant search results compared to simple Bag-of-Words counts.  
# * **Handles Common Words:** The IDF component effectively down-weights common, less informative words, preventing them from dominating the similarity scores.  
# * **Simplicity and Scalability:** It's relatively simple to compute and scales well to large document collections.
# 
# **Limitations of TF-IDF:**
# 
# * **Semantic Blindness:** Like the basic BoW model, TF-IDF still operates at the word level and completely ignores the semantic relationships between words (e.g., "car" and "automobile" are treated as distinct terms). It cannot understand context or nuances of language.  
# * **Word Order Ignorance:** It does not consider the order of words, meaning phrases and the grammatical structure of sentences are lost.  
# * **Sparse Vectors:** For very large vocabularies, TF-IDF vectors can be extremely high-dimensional and sparse (mostly zeros), which can be computationally inefficient for some operations.
# 
# Despite its limitations, TF-IDF remains a cornerstone in information retrieval, often used as a baseline or as a feature engineering technique in more complex systems. Its effectiveness and simplicity make it a valuable tool for understanding and processing text data.
# 

# %%
# Building a TF-IDF Vectorizer based search engine

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(corpus['text'])


def search_tfidf(corpus, search_query):
    corpus = corpus.copy()
    search_query_vector = vectorizer.transform([search_query])
    similarity = cosine_similarity(search_query_vector, tfidf_matrix).flatten()
    corpus['similarity'] = similarity
    return corpus.sort_values(by='similarity', ascending=False)


print(search_tfidf(corpus, search_query).head(10).to_markdown())

# %% [markdown]
# While TF-IDF (Term Frequency-Inverse Document Frequency) has been a cornerstone of information retrieval for decades, the Okapi BM25 (Best Match 25\) ranking function emerged as a more sophisticated and often more effective approach to calculating document relevance for a given search query. BM25 is a probabilistic retrieval model that builds upon the TF-IDF concept, but with significant improvements, particularly in how it handles term frequency saturation and document length normalization. It's widely used in modern search engines due to its empirical effectiveness.
# 
# ### **How BM25 Works**
# 
# BM25 calculates a relevance score for each document with respect to a search query. This score is a sum of the scores for each term in the query. For a query containing terms q1​,…,qn​, the BM25 score for a document D is typically calculated as:
# 
# $$
# Score(D, Q) = \sum_{i=1}^{n} IDF(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{avgdl}\right)}
# $$
# Let's break down the components:
# 
# 1. **IDF (Inverse Document Frequency):** Similar to TF-IDF, BM25 uses IDF to weigh terms. Rare terms across the corpus contribute more to the total score than common terms. The formula for IDF in BM25 often uses a slightly different variant to the standard log function in TF-IDF, sometimes including smoothing terms to avoid division by zero for terms appearing in no documents. IDF(qi​) is the Inverse Document Frequency of term qi​.  
# 2. **Term Frequency (**f(qi​,D)**):** This represents how many times term qi​ appears in document D. Unlike raw TF, BM25 incorporates parameters k1​ and b to prevent term frequency from saturating.  
#    * **Saturation:** In simple TF, a word appearing 100 times in a document contributes 100 times as much as a word appearing once. BM25 acknowledges that beyond a certain point, additional occurrences of a term provide diminishing returns to relevance. The k1​ parameter controls this saturation point. Higher values of k1​ lead to less saturation.  
#    * The term f(qi​,D)+k1​f(qi​,D)⋅(k1​+1)​ is the core of how BM25 handles term frequency, allowing it to give more weight to more frequent terms up to a point, then the contribution levels off.  
# 3. **Document Length Normalization (**∣D∣ **and** avgdl**):** This part of the formula addresses the issue of longer documents potentially having higher raw term frequencies simply because they are longer.  
#    * ∣D∣ is the length of the document D (e.g., in words).  
#    * avgdl is the average document length in the corpus.  
#    * The parameter b (often between 0 and 1\) controls the degree of document length normalization.  
#      * If b=0, no length normalization is applied.  
#      * If b=1, full length normalization is applied. The term (1−b+b⋅avgdl∣D∣​) scales the denominator, effectively reducing the impact of term frequency in longer documents relative to shorter ones, especially if the term is not particularly frequent in the longer document compared to its overall length.
# 
# ### **BM25 for Search**
# 
# When a query is submitted, each document's BM25 score is calculated based on the query terms. Documents are then ranked by their BM25 scores, from highest to lowest, to present the most relevant results. The parameters k1​ (typically between 1.2 and 2.0) and b (typically around 0.75) are tunable and often optimized based on the specific characteristics of the document corpus and search task.
# 
# ### **Advantages and Limitations**
# 
# **Advantages of BM25:**
# 
# * **Improved Relevance:** BM25 generally outperforms plain TF-IDF in most retrieval scenarios due to its refined handling of term frequency saturation and document length normalization.  
# * **Probabilistic Foundation:** Its roots in probabilistic models provide a more theoretically sound basis for relevance estimation compared to the heuristic nature of raw TF-IDF.  
# * **Robustness:** It is relatively robust and performs well across diverse datasets without extensive tuning.
# 
# **Limitations of BM25:**
# 
# * **Semantic Gap:** Like TF-IDF, BM25 is a keyword-matching algorithm. It still suffers from the "semantic gap" problem, meaning it doesn't understand synonyms (e.g., "car" and "automobile" are treated as distinct) or the deeper meaning and context of words.  
# * **Word Order Ignorance:** It treats the query and documents as a "bag of words," ignoring the order of words and thus failing to capture phrases or idiomatic expressions.  
# * **Parameter Tuning:** While robust, optimal performance can sometimes require careful tuning of k1​ and b for specific corpora.  
# * **Outperformed by Modern Methods:** For complex search tasks requiring deep semantic understanding, BM25 is often surpassed by neural network-based models and dense retrieval methods (like those using word embeddings or transformer models) that capture contextual relationships.
# 
# Despite the emergence of more advanced neural retrieval methods, BM25 remains a highly effective, computationally efficient, and widely used ranking function in many practical search systems, often serving as a strong baseline or even a crucial component in hybrid retrieval architectures.
# 

# %%
# rank_bm25 based search engine
from rank_bm25 import BM25Okapi
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
nltk.download('punkt')
nltk.download('stopwords')


def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text.lower())
    # Remove stopwords
    tokens = [
        word for word in tokens if word not in stopwords.words('english')]
    # Remove special characters
    tokens = [re.sub(r'[^a-zA-Z0-9]', '', word) for word in tokens]
    # Remove empty strings
    tokens = [word for word in tokens if word != '']
    return tokens


corpus['tokens'] = corpus['text'].apply(preprocess_text)
corpus['tokens'].head(10).to_markdown()
# BM25
bm25 = BM25Okapi(corpus['tokens'].tolist())


def search_bm25(corpus, search_query):
    corpus = corpus.copy()
    search_query_tokens = preprocess_text(search_query)
    scores = bm25.get_scores(search_query_tokens)
    corpus['score'] = scores
    return corpus.sort_values(by='score', ascending=False)


print(search_bm25(corpus, search_query).head(10).to_markdown())

# %% [markdown]
# ## Vector Embeddings on text
# 
# In the realm of natural language processing (NLP), computers don't inherently understand human language. Words, phrases, and documents are abstract concepts to a machine. **Vector embeddings** are a revolutionary technique that bridges this gap by converting textual data into dense numerical representations, or vectors, in a continuous vector space. These vectors capture the semantic meaning and contextual relationships of words and phrases, allowing machines to process and "understand" language in a way that was previously impossible with traditional methods like Bag-of-Words or TF-IDF.
# 
# ### **What are Vector Embeddings?**
# 
# At its core, a vector embedding is an array of real numbers (e.g., `[0.1, -0.5, 0.8, 0.2, ...]`) that represents a piece of text. Each number in the array corresponds to a dimension in the vector space. The magic lies in how these numbers are assigned: words or phrases that are semantically similar tend to be located closer together in this high-dimensional space, while dissimilar terms are further apart. For instance, the vector for "king" might be close to "queen" and "man," and the vector difference between "king" and "man" could be similar to the difference between "queen" and "woman."
# 
# ### **Why are They Needed?**
# 
# Traditional text representation methods like Bag-of-Words or TF-IDF suffer from significant limitations:
# 
# * **Lack of Semantic Understanding:** They treat words as independent entities, ignoring synonyms, polysemy, and the underlying meaning. "Car" and "automobile" would be seen as entirely different terms.  
# * **High Dimensionality and Sparsity:** For large vocabularies, vectors can become extremely long and mostly filled with zeros, leading to inefficient computation and storage.  
# * **No Contextual Information:** They cannot capture the meaning of a word based on its surrounding words.
# 
# Vector embeddings overcome these limitations by:
# 
# * **Capturing Semantic Similarity:** They embed words with similar meanings close to each other in the vector space.  
# * **Capturing Relationships:** They can learn analogies and relationships between words.  
# * **Reduced Dimensionality:** They represent text in dense, lower-dimensional vectors compared to sparse, high-dimensional representations.
# 
# ### **How are Vector Embeddings Generated?**
# 
# Vector embeddings are typically learned from vast amounts of text data using various machine learning techniques:
# 
# 1. **Context-Independent Embeddings (e.g., Word2Vec, GloVe):** These models learn a single, fixed embedding for each word, regardless of its context. They analyze the co-occurrence patterns of words in a large corpus. If words frequently appear together or in similar contexts, their embeddings will be closer.  
# 2. **Contextual Embeddings (e.g., BERT, GPT, Gemini Embeddings):** More advanced models, particularly those based on the Transformer architecture, generate embeddings that are *context-dependent*. This means the embedding for a word like "bank" would be different if it's used in the context of a "river bank" versus a "financial bank." These models process entire sentences or paragraphs to generate rich, context-aware representations for each word or even for the entire input.
# 
# ### **How are Vector Embeddings Used in Search?**
# 
# Vector embeddings are crucial for **semantic search**, which goes beyond simple keyword matching:
# 
# 1. **Vectorizing Documents:** All documents in a corpus are transformed into their corresponding embedding vectors using a pre-trained embedding model. These vectors are then stored in a specialized database called a **vector database** (or vector index).  
# 2. **Vectorizing Queries:** When a user submits a query, it is also converted into an embedding vector using the *same* embedding model.  
# 3. **Similarity Search:** Instead of matching keywords, the search engine now performs a **similarity search** in the vector space. It finds document vectors that are "closest" to the query vector. The most common metric for measuring this similarity is **Cosine Similarity**: Let and B be two embedding vectors.
# 
# $$
# \text{Cosine Similarity}(A, B) = \frac{A \cdot B}{||A|| \cdot ||B||} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}
# $$
# 
# A cosine similarity score close to 1 indicates high semantic similarity.
# 
# Documents are then ranked based on their cosine similarity scores to the query vector. This allows the search engine to retrieve documents that might not contain the exact keywords but are semantically related to the query, significantly improving search relevance and recall.
# 

# %%
from sklearn.metrics.pairwise import cosine_similarity

from typing import List
from langchain_huggingface import HuggingFaceEmbeddings

HF_EMBEDDING_MODEL = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)


def generate_embeddings(contents: List[str], embedding_model=HF_EMBEDDING_MODEL):
    """
    Generate embeddings for the given content using the Google Gemini model.
    """
    response = embedding_model.embed_documents(contents)
    return np.array(response)


statements = [
    'The King won the battle but lost the war.',
    'The Man won the battle but lost the war.',
    'The Queen won the battle but lost the war.',
    'The Woman won the battle but lost the war.',
]

all_embeddings = generate_embeddings(statements)

similarity = cosine_similarity(all_embeddings, all_embeddings)

_statements = [statement.replace(
    'the battle but lost the war.', '...') for statement in statements]

df = pd.DataFrame(similarity, columns=_statements)

df.index = _statements

df.round(3)

# %% [markdown]
# ## Searching for similar vectors using Cosine Similarity
# 
# In the realm of modern information retrieval and recommendation systems, **vector embeddings** allow us to represent items (like text documents, images, or user preferences) as numerical vectors in a high-dimensional space. Once text is converted into these meaningful vector representations, the task of finding "similar" items transforms into a geometric problem: identifying vectors that are "close" to each other in this space. Among various distance or similarity metrics, **Cosine Similarity** stands out as a popular and effective choice for this purpose.
# 
# ### **The Role of Cosine Similarity**
# 
# Cosine Similarity measures the cosine of the angle between two non-zero vectors. It determines whether two vectors are pointing in roughly the same direction, which indicates semantic similarity, regardless of their magnitude (length). A cosine similarity score ranges from \-1 to 1:
# 
# * **1:** Indicates identical direction (maximum similarity).  
# * **0:** Indicates orthogonality (no correlation).  
# * **\-1:** Indicates diametrically opposite direction (maximum dissimilarity).
# 
# The formula for cosine similarity between two vectors A and B is:
# 
# $$
# \text{Cosine Similarity}(A, B) = \frac{A \cdot B}{||A|| \cdot ||B||}
# $$
# 
# Here, A⋅B is the dot product of the vectors, and ∣∣A∣∣ and ∣∣B∣∣ are their respective magnitudes (Euclidean norms).
# 
# ### **Searching for Similar Vectors**
# 
# The process of searching for similar vectors using cosine similarity typically involves:
# 
# 1. **Embedding Generation:** A query (e.g., a search phrase) is first converted into its corresponding vector embedding using the same model used for embedding the documents or items in your database.  
# 2. **Similarity Calculation:** This query vector is then compared against the pre-computed embedding vectors of all documents or items in your collection. For each comparison, a cosine similarity score is calculated.  
# 3. **Ranking:** The documents/items are then ranked in descending order based on their cosine similarity scores, with those having the highest positive scores considered most similar and thus most relevant to the query.
# 
# This approach allows for semantic search, where results are based on meaning rather than just keyword matching, making it powerful for tasks like question answering, content recommendation, and plagiarism detection.
# 

# %%
sq = 'The Soldier lost all wars'
search_embedding = generate_embeddings([sq])

similarity = cosine_similarity(
    search_embedding.reshape(1, -1), all_embeddings
)

scores = [(score, statement)
          for score, statement in zip(similarity[0].round(3), statements)]

best_matches = sorted(scores, reverse=True, key=lambda x: x[0])

best_matches

# %%

# Vector Based Search Engine
from tqdm.auto import tqdm

tqdm.pandas(desc="Generating embeddings")


def search(
        query: str,
        vector_database: pd.DataFrame,
        number_of_results: int = 10,
        embedding_model=HF_EMBEDDING_MODEL
):
    """
    Search for the most similar content in the vector database.
    """
    search_embedding = generate_embeddings(
        [query],
        embedding_model=embedding_model
    )[0]
    results = vector_database.apply(
        lambda x: cosine_similarity(
            x.embedding.reshape(1, -1), search_embedding.reshape(1, -1)
        )[0][0], axis=1
    ).sort_values(ascending=False).head(number_of_results)

    return pd.DataFrame(
        {
            'text': vector_database.iloc[results.index].text,
            'similarity': results.values,
        }
    )


# Build In Memory Vector Database
vector_database = pd.DataFrame({'text': corpus.text, 'embedding': [
    i for i in generate_embeddings(corpus.text)]})

# Vector Based Search

results = search(query=search_query, vector_database=vector_database)

results

# %% [markdown]
# **Vector databases** are a specialized type of database designed specifically to store, manage, and efficiently query **vector embeddings**. Unlike traditional relational or NoSQL databases that excel at storing structured data or documents and querying by exact matches or specific attributes, vector databases are optimized for **similarity search** in high-dimensional vector spaces.
# 
# The need for vector databases arose with the proliferation of vector embeddings in AI applications. As text, images, audio, and other data types are converted into dense numerical vectors that capture their semantic meaning, there's a critical requirement to quickly find vectors (and thus the underlying data) that are "similar" to a given query vector. Traditional databases are not built for this kind of approximate nearest neighbor (ANN) search, which involves computing distances or similarities between many vectors.
# 
# Vector databases employ advanced indexing algorithms (like HNSW \- Hierarchical Navigable Small Worlds, or IVF \- Inverted File Index) to organize these embeddings. When a query vector is submitted, the database rapidly identifies vectors dk​ from its stored collection $D=d_1​,d_2​,…,d_N​$ that are most similar to q. The objective is often to find $d_k​ \in D$ such that $Similarity(q,dk​)$ is maximized (or $Distance(q,dk​)$ is minimized).
# 
# These databases are foundational to modern AI systems, powering applications like:
# 
# * **Semantic Search:** Finding results based on meaning, not just keywords.  
# * **Retrieval-Augmented Generation (RAG):** Providing LLMs with relevant context.  
# * **Recommendation Systems:** Suggesting items similar to what a user likes.  
# * **Anomaly Detection:** Identifying outliers in data.
# 
# By enabling lightning-fast similarity lookups for millions or billions of vectors, vector databases unlock the true potential of embedding-based AI applications.
# 

# %%
# Qdrant Vector Database

from qdrant_client import QdrantClient
import qdrant_client
from qdrant_client.http.models import Distance
from qdrant_client.http.models import VectorParams
from qdrant_client.http.models import CollectionStatus
from qdrant_client.http.models import PointStruct

# qdrant_client = QdrantClient(
#     url='http://localhost:6333',  # url version
#     # http_port=6333,
# )
qdrant_client = QdrantClient(location=':memory:')

if qdrant_client.collection_exists("ml_ideas"):
    print('cleaning existing collection')
    qdrant_client.delete_collection("ml_ideas")

qdrant_client.create_collection(
    collection_name="ml_ideas",
    vectors_config=VectorParams(
        size=768,
        distance=Distance.COSINE
    ),
)

qdrant_client.get_collection("ml_ideas").status == CollectionStatus.GREEN

# %% [markdown]
# Converting raw string data, such as text documents, articles, or even short sentences, into a format that can be efficiently stored and queried for semantic similarity is a crucial step in building intelligent AI applications. This is where the process of generating **vector embeddings** and storing them in a **vector database** like Qdrant comes into play.
# 
# Traditional databases are not optimized for searching based on the *meaning* of text. They excel at exact keyword matches or structured queries. However, with the rise of large language models (LLMs) and semantic search, the ability to find information based on contextual relevance, even if exact keywords aren't present, has become paramount.
# 
# The process typically involves:
# 
# 1. **Embedding Generation:**  
#    * The string data is passed through an **embedding model** (e.g., a dedicated text embedding model from Google, OpenAI, Hugging Face, or even an LLM itself if it provides embedding capabilities).  
#    * This model transforms the unstructured string into a high-dimensional numerical vector, where semantically similar strings are mapped to vectors that are geometrically close in the embedding space. For instance, the phrase "solar panel efficiency" and "improving photovoltaic output" would yield vectors that are very close to each other, despite using different words.  
#    * Each string is converted into its corresponding embedding vector VS​=$v_1​,v_2,…,v_n​$, where n is the dimensionality of the embedding space (e.g., 768, 1024, or more).  
# 2. **Storage in a Vector Database (e.g., Qdrant):**  
#    * Once the embeddings are generated, they are stored in a specialized vector database. Qdrant is an excellent example of such a database, designed for high-performance similarity search.  
#    * In Qdrant, you create a "collection" (similar to a table) where each "point" (record) consists of the vector embedding and optionally, an associated payload (the original string data or metadata related to it).  
#    * Qdrant then uses efficient Approximate Nearest Neighbor (ANN) algorithms (like HNSW) to index these vectors. This allows for extremely fast searches for vectors that are closest to a given query vector.
# 
# When a user performs a semantic search, their query string is also converted into an embedding. This query vector is then sent to Qdrant, which quickly finds and returns the most similar document vectors based on metrics like Cosine Similarity:
# 
# $Cosine Similarity(VQ​,VD​)=∣∣VQ​∣∣⋅∣∣VD​∣∣VQ​⋅VD​​$
# 
# where VQ​ is the query vector and VD​ is the document vector.
# 
# 
# This returned set of similar vectors points back to the original string data in the payload, enabling powerful semantic search, retrieval-augmented generation (RAG), and recommendation systems.
# 

# %%
# inserting data into qdrant

from langchain_qdrant import Qdrant  # Qdrant Vector Store Wrapper

vector_store = Qdrant.from_texts(
    corpus.text,
    HF_EMBEDDING_MODEL,
    collection_name="ml_ideas",
    location=':memory:',
)

results = vector_store.search(
    query=search_query,
    search_type="similarity",
    k=10
)

[
    result.page_content
    for result in results
]

# %% [markdown]
# ---
# 
# ## Session 2

# %% [markdown]
# ## Dimensionality of Vector Embeddings
# 
# The dimensionality of a vector embedding refers to the number of numerical values (or features) in the vector that represents a piece of data, such as text. For instance, a 768-dimensional embedding is an array of 768 numbers. This dimension size significantly impacts the effectiveness and efficiency of similarity search operations.
# 
# Lower-dimensional embeddings (e.g., 64, 128, 256\) are computationally efficient, requiring less memory storage and leading to faster search queries. They are suitable for simpler datasets or tasks where fine-grained semantic distinctions are less critical. However, they might lose some nuanced information during compression, potentially reducing search accuracy for complex relationships, as they have fewer "slots" to encode detailed meaning.
# 
# Higher-dimensional embeddings (e.g., 768, 1024, 1536, or more) can capture more complex and subtle semantic relationships within the data. This often leads to higher search accuracy and relevance. However, they come at a cost: increased memory consumption, higher computational overhead for distance calculations (like Cosine Similarity), and slower search speeds. Extremely high dimensions can also lead to the "curse of dimensionality," where data becomes sparse, and distances between vectors lose their meaningful distinction.
# 
# The goal is to find an optimal balance where the dimension is sufficient to capture necessary semantic information for accurate search without incurring excessive computational burden. The effectiveness of search relies on being able to accurately measure similarity between vectors, often using:
# 
# $Cosine Similarity(A,B)=∣∣A∣∣⋅∣∣B∣∣A⋅B​$
# 
# Choosing the right dimensionality depends on the specific use case, the complexity of the data, and available computational resources.
# 

# %%
# load different dimension embedding models

from langchain_huggingface import HuggingFaceEmbeddings

model_768 = HuggingFaceEmbeddings(
    model_name="sentence-transformers/LaBSE",
)

model_384 = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

model_64 = HuggingFaceEmbeddings(
    model_name="ClovenDoug/tiny_64_all-MiniLM-L6-v2",
)


v64, v384, v768 = (
    model_64.embed_query(search_query),
    model_384.embed_query(search_query),
    model_768.embed_query(search_query),
)

print(len(v64), len(v384), len(v768))

# %% [markdown]
# Choosing the right vector dimension size for your embeddings is a crucial step in building effective RAG systems, as it directly impacts performance, cost, and accuracy. Vector dimensions refer to the length of the numerical arrays (vectors) that represent your text data.
# 
# ---
# ## The Balancing Act: Nuance vs. Efficiency
# 
# **Higher dimensions** (e.g., 1536 for OpenAI's `text-embedding-ada-002` or 3072 for `text-embedding-3-large`) can capture more nuance and semantic detail from the text. This can lead to more accurate retrieval in complex scenarios. However, they come with trade-offs:
# * **Increased computational cost:** Calculating distances and performing searches over higher-dimensional vectors takes more processing power and time.
# * **Higher storage requirements:** Larger vectors naturally consume more storage space.
# * **Potential for noise:** Very high dimensions can sometimes capture irrelevant details or noise, potentially degrading performance if not matched by the complexity of the data and task (the "curse of dimensionality").
# 
# **Lower dimensions** (e.g., 768 for E5 models or even reduced dimensions like 256 or 512 for newer OpenAI models) offer several benefits:
# * **Faster search and retrieval:** Smaller vectors are quicker to process.
# * **Reduced storage costs:** They take up less space.
# * **Lower computational overhead:** Less demanding on resources.
# However, if the dimensionality is too low, the embeddings might lose critical information, leading to less precise retrieval.
# 
# ---
# ## Model Capabilities and Practical Choices
# 
# Different **embedding models** produce vectors of varying default sizes, and some newer models allow you to customize the output dimension. For instance, OpenAI's `text-embedding-3-large` can be shortened (e.g., to 1024 or 256) while still retaining strong performance, sometimes even outperforming older models with higher native dimensions.
# 
# When choosing, consider:
# 1.  **Task Complexity & Data:** Highly nuanced tasks with complex data might benefit from higher dimensions, while simpler tasks might do well with lower ones.
# 2.  **Embedding Model:** Start with the default dimension of your chosen model. If the model supports it, experiment with reducing the dimensions. Benchmarks like MTEB can offer insights, but real-world performance on your specific data is key.
# 3.  **Performance vs. Cost:** Evaluate the trade-off. Is the incremental accuracy gain from higher dimensions worth the increased latency and storage costs? Often, a well-chosen model with a moderate dimension size (e.g., 512-1024) offers a good balance.
# 
# Ultimately, experimentation is key. Start with sensible defaults, evaluate retrieval quality and system performance, and then iterate on the dimension size if necessary.

# %%
# 64 dimensional embedding

vector_store = Qdrant.from_texts(
    corpus.text,
    model_64,
    collection_name="ml_ideas_64",
    location=':memory:',
)

results = vector_store.search(
    query=search_query,
    search_type="similarity",
    k=10
)

[
    result.page_content
    for result in results
]

# Output:
# ['Can a machine learn to teach?',
#  'Machine Learning In JavaScript',
#  'A Machine Learning Approach for Future Career Planning',
#  'Motor Skill Learning',
#  'Automated Curriculum Learning',
#  'Modeling Protein Interactions Using Bayesian Networks',
#  'Exploring Potential for Machine Learning on Dataset about K-12 Teacher Professional Development',
#  'Learning to Test',
#  'What Can You Learn From Accelerometer Data',
#  'Adversarial Machine Learning against Keystroke Dynamics']

# %%
# 384 dimensional embedding
vector_store = Qdrant.from_texts(
    corpus.text,
    model_384,
    collection_name="ml_ideas_384",
    location=':memory:',
)

results = vector_store.search(
    query=search_query,
    search_type="similarity",
    k=10
)

[
    result.page_content
    for result in results
]

# Output:
# ['Finding Your Way, Courtesy of Machine Learning',
#  'Machine Learning In JavaScript',
#  'How can machine learning help stock investment?',
#  'Parallelizing Machine Learning Algorithms',
#  'Exploring the Efficacy of Machine Learning in General Game Playing',
#  'Can a machine learn to teach?',
#  'Can Machines Learn Genres',
#  'Machine Learning in Stock Price Trend Forecasting',
#  'An Empirical Study of Machine Learning Techniques used for Enhancer Classification',
#  'Implementing Machine Learning to Earthquake Engineering']

# %%
# 768 dimensional embedding
vector_store = Qdrant.from_texts(
    corpus.text,
    model_768,
    collection_name="ml_ideas_768",
    location=':memory:',
)

results = vector_store.search(
    query=search_query,
    search_type="similarity",
    k=10
)

[
    result.page_content
    for result in results
]

# Output:
# ['Can a machine learn to teach?',
#  'How can machine learning help stock investment?',
#  'A study of ensemble methods in machine learning',
#  'Better Reading Levels through Machine Learning',
#  'How well do people learn?',
#  'Machine Learning Techniques for Optimal Sampling-Based Motion Planning',
#  'Machine Learning Methods for News Popularity Prediction',
#  'The Price is Right? Estimating Medical Costs with Machine Learning',
#  'Optimizing Leakage Power using Machine Learning',
#  'Improving Tictoc With Machine Learning']

# %% [markdown]
# ## Choosing a Vector Database
# 
# Selecting the appropriate vector database is a critical decision that profoundly impacts the performance, scalability, cost, and maintainability of your AI application, especially when building solutions like semantic search engines or Retrieval-Augmented Generation (RAG) systems. There's no one-size-fits-all solution; the "right" choice depends heavily on your specific needs.
# 
# Key factors to consider include:
# 
# 1. **Scale and Data Volume:**  
#    * How many vectors do you need to store (millions, billions, trillions)?  
#    * What is the dimensionality of your embeddings (e.g., 384, 768, 1536)?  
#    * What is your expected growth rate? These factors dictate the storage and indexing capabilities required.  
# 2. **Performance Requirements:**  
#    * **Query Latency:** How quickly do you need search results (e.g., milliseconds for real-time applications)?  
#    * **Throughput:** How many queries per second (QPS) do you anticipate?  
#    * **Indexing Speed:** How fast can new data be added and indexed? High-performance demands often necessitate specialized indexing algorithms and optimized architectures.  
# 3. **Features and Functionality:**  
#    * **Filtering and Metadata:** Can you filter searches based on associated metadata (e.g., search for documents from a specific date range or category)?  
#    * **Hybrid Search:** Does it support combining vector search with keyword search?  
#    * **Scalability Model:** Is it horizontally scalable?  
#    * **Deployment Options:** Cloud-managed service, self-hosted, on-premise?  
#    * **Data Consistency & Durability:** What are the guarantees for data integrity and availability?  
# 4. **Cost:**  
#    * This includes infrastructure costs (for self-hosting), managed service fees, and operational overhead.  
#    * Consider the total cost of ownership, not just licensing fees.  
# 5. **Ecosystem and Integrations:**  
#    * Does the database integrate well with your existing tech stack, particularly with popular NLP frameworks like LangChain or LlamaIndex, and your chosen embedding models?  
#    * What community support or enterprise support is available?
# 
# Popular choices include dedicated vector databases like **Pinecone** (managed service), **Weaviate**, **Qdrant**, and **Milvus** (open-source, self-hostable options). Each offers a different set of trade-offs across these criteria. Thorough evaluation, often involving prototyping with a representative dataset, is crucial to ensure the selected database aligns with both your current needs and future growth.
# 
# *Note: The "choosing" process itself doesn't inherently involve specific mathematical equations beyond evaluating performance metrics like latency or throughput, which are outcomes of the database's internal algorithms.*
# 

# %%
# https://www.kaggle.com/datasets/fajobgiua/indian-food-dataset?resource=download

from tqdm.auto import tqdm
import json
import pandas as pd

tqdm.pandas(desc="Generating Documents")

columns = ['TranslatedRecipeName', 'TranslatedIngredients',
           'PrepTimeInMins', 'CookTimeInMins', 'TotalTimeInMins', 'Servings',
           'Cuisine', 'Course', 'Diet', 'TranslatedInstructions', 'URL',
           'ComplexityLevel', 'MainIngredient']

df = pd.read_csv('./IndianFoodDataset.csv', ).set_index('Srno')

data = df[:].progress_apply(
    lambda x: x.to_markdown(),
    axis=1
)

df

# %%

vector_store_unchunked = Qdrant.from_texts(
    data,
    model_384,
    collection_name="indian-food",
    location=':memory:',
)

# %%
results = vector_store_unchunked.similarity_search(
    'Andhra Dish with Onion and No Ginger', k=5)
for result in results:
    print(len(result.page_content))
    print(result.page_content)
print()

# %% [markdown]
# ## Choosing the Right Chunking Strategy for RAG
# 
# Effective chunking is foundational to a successful Retrieval-Augmented Generation (RAG) system. It involves breaking down large documents into smaller, semantically meaningful pieces that are then embedded and indexed for retrieval. The choice of strategy significantly impacts retrieval relevance, context preservation, and ultimately, the quality of the LLM's generated response.
# 
# **Common Chunking Strategies:**
# 
# * **Fixed-Size Chunking:** The simplest method, splitting text into chunks of a defined character or token count. Adding an **overlap** (e.g., 10-20% of chunk size) between consecutive chunks helps retain context that might otherwise be lost at chunk boundaries. While easy to implement, it can awkwardly split sentences or ideas.
# * **Recursive Character Splitting:** A more refined approach that attempts to split text based on a hierarchy of separators (e.g., paragraphs, then sentences, then words) while respecting a target chunk size. This often leads to more semantically coherent chunks than basic fixed-size splitting.
# * **Content-Aware Chunking:** These strategies leverage the inherent structure or meaning within the data.
#     * **Document-Specific:** Utilizing existing structures like Markdown headers, HTML tags, or code function/class definitions to define chunk boundaries.
#     * **Sentence Splitting:** Treating individual sentences as chunks, suitable for highly factual information where sentence-level retrieval is precise.
#     * **Semantic Chunking:** Employs embedding similarity to identify natural breakpoints between sentences or groups of sentences, ensuring that each chunk contains semantically related content. This is often more computationally intensive upfront but can yield highly relevant chunks.
# 
# **Factors Influencing Your Choice:**
# 
# 1.  **Document Structure:** Highly structured documents (e.g., FAQs, code files) may benefit from document-specific or simple sentence/paragraph splitting. Unstructured prose often requires more nuanced approaches like recursive or semantic chunking.
# 2.  **Content Type & Query Nature:** For pinpointing specific facts, smaller, more granular chunks (like sentences) might be optimal. For understanding broader themes, larger chunks that encapsulate more context could be better.
# 3.  **Embedding Model Limits:** Chunks must not exceed the maximum input token limit of your chosen embedding model.
# 4.  **Computational Resources:** Simpler strategies are faster to implement and run, while semantic chunking requires more processing for embedding sentences and calculating similarity.
# 
# There's no universal "best" strategy. Experimentation is key. Test different methods, chunk sizes, and overlaps with your specific dataset and expected user queries. Evaluate the relevance of retrieved chunks to determine the optimal approach for your RAG application, balancing context preservation with retrieval precision.

# %%
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000,
    chunk_overlap=500,
    length_function=len
)

docs = text_splitter.create_documents(data,)

print(len(docs))

vector_store = Qdrant.from_documents(
    docs,
    model_384,
    collection_name="indian-food-chunked",
    location=':memory:',
)

# %%
_docs = vector_store.similarity_search(
    'Jain Food', k=10
)

for doc in _docs:
    print(len(doc.page_content))
    print(doc.page_content)

# %%

prompt = '''
Given the user query, answer the user to the best of your ability.
Enusre you are polite and helpful.
If you do not know the answer, say "I don't know" and offer to help with something else.

User Query: {user_query}

Context:

{context}
'''

user_query = 'I am a Non-Vegetarian. Can you suggest me something healthy and non oily?'

# %%

_docs = vector_store.similarity_search(
    user_query,
    k=10
)

context = '\n\n'.join(
    [doc.page_content for doc in _docs]
)

print(
    '--------------------------------',
    prompt.format(
        user_query=user_query,
        context=context,
    ),
    '--------------------------------',
    sep='\n'
)

response = model.generate_content(
    prompt.format(
        user_query=user_query,
        context=context,
    )
)

print(response.text)

# %%

_docs = vector_store_unchunked.similarity_search(
    user_query,
    k=10
)

context = '\n\n'.join(
    [doc.page_content for doc in _docs]
)

print(
    '--------------------------------',
    prompt.format(
        user_query=user_query,
        context=context,
    ),
    '--------------------------------',
    sep='\n'
)

response = model.generate_content(
    prompt.format(
        user_query=user_query,
        context=context,
    )
)

print(response.text)

# %%

prompt = '''
Given the user query, answer the user to the best of your ability.
Enusre you are polite and helpful.

DO NOT ANSWER ANYTHING WITHOUT CONTEXT. If you do not know the answer, say "I don't know" and offer to help with something else.

provide a detailed repsonse and list down the ingredients and preparation steps, step by step.

User Query: {user_query}

Context:

{context}
'''

user_query = 'I am a Non-Vegetarian. Can you suggest me something healthy and non oily?'

print(prompt.format(
    user_query=user_query,
    context=context,
))

# %%


_docs = vector_store.similarity_search(
    user_query,
    k=10
)

context = '\n\n'.join(
    [doc.page_content for doc in _docs]
)

response = model.generate_content(
    prompt.format(
        user_query=user_query,
        context=context,
    )
)

print(response.text)

# %%


_docs = vector_store_unchunked.similarity_search(
    user_query,
    k=5
)

context = '\n\n'.join(
    [doc.page_content for doc in _docs]
)

response = model.generate_content(
    prompt.format(
        user_query=user_query,
        context=context,
    )
)

print(response.text)

# %% [markdown]
# 
# ## Choosing the Right LLM Size for Your Project
# 
# Selecting an appropriately sized Large LanguageModel (LLM) is a critical decision in any Generative AI project, especially for Retrieval-Augmented Generation (RAG) systems. "Size" typically refers to the number of parameters (e.g., 7 billion, 70 billion), which correlates with the model's capacity for understanding, reasoning, and generation.
# 
# Larger LLMs generally offer more sophisticated language comprehension, better handling of complex queries, and the ability to generate more nuanced and coherent text. They often possess a broader inherent knowledge base, though in RAG, the focus is on their ability to synthesize provided context. However, this increased capability comes at a cost: larger models demand more computational resources, leading to higher inference latency and operational expenses, whether through API calls or self-hosting infrastructure (significant VRAM and GPU power).
# 
# Conversely, smaller LLMs are faster, cheaper to run, and require less memory, making them attractive for applications with strict latency or budget constraints. While potentially less powerful for highly complex, open-ended tasks, they can be very effective, especially when fine-tuned for specific domains or when the RAG system's retrieval component is highly accurate. The trend also shows newer, optimized smaller models often matching the performance of older, larger ones.
# 
# When choosing, consider:
# 1.  **Task Complexity:** Does your RAG task require deep reasoning on the retrieved context, or more straightforward synthesis?
# 2.  **Performance Needs:** How critical is low latency?
# 3.  **Budget & Resources:** What are your API cost limits or available hardware capabilities?
# 4.  **Context Window:** Ensure the model can handle the amount of retrieved information you intend to pass.
# 5.  **Fine-tuning:** Smaller models are often more accessible for custom fine-tuning.
# 
# Ultimately, "bigger isn't always better." Start by evaluating a few options against your specific RAG task, measuring output quality, speed, and cost to find the optimal balance.

# %%
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen3-0.6B"

# load the tokenizer and the model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)

# prepare the model input
prompt = prompt.format(
    user_query=user_query,
    context=context,
)
messages = [
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    # Switches between thinking and non-thinking modes. Default is True.
    enable_thinking=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

# conduct text completion
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=32768
)
output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

# parsing thinking content
try:
    # rindex finding 151668 (</think>)
    index = len(output_ids) - output_ids[::-1].index(151668)
except ValueError:
    index = 0

thinking_content = tokenizer.decode(
    output_ids[:index], skip_special_tokens=True).strip("\n")
content = tokenizer.decode(
    output_ids[index:], skip_special_tokens=True).strip("\n")

print("thinking content:", thinking_content)
print("content:", content)

# %%



