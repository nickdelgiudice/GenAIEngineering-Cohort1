# %% [markdown]
# To truly unlock the potential of Large Language Models (LLMs) in accessing and utilizing specific, up-to-date information, **Retrieval Augmented Generation (RAG)** systems are essential. These systems retrieve relevant data from external knowledge bases to inform the LLM's responses. However, the quality of this retrieval and the subsequent generation heavily depends on sophisticated data processing and retrieval techniques. Two such advancements significantly boosting RAG performance are **Advanced Chunking Strategies** and **RAG Fusion**. These methods refine how information is prepared and how relevant context is identified and synthesized, leading to more accurate, coherent, and contextually aware LLM outputs.
# 
# ---
# ## Advanced Chunking Strategies
# 
# Traditional methods of splitting large documents into smaller pieces, or **chunks**, often rely on simple fixed-size or recursive approaches. While straightforward, these basic techniques can inadvertently sever crucial semantic connections within the text or fail to encapsulate the full context needed for accurate information retrieval. This can lead to fragmented understanding and less relevant results when an LLM queries a vector database.
# 
# **Advanced Chunking Strategies** address these limitations by employing more intelligent segmentation. Techniques include:
# * **Semantic Chunking:** This method groups text segments based on their conceptual similarity, often using embedding models to identify semantic boundaries. This ensures that related ideas stay together.
# * **Content-Aware Chunking:** This approach considers the inherent structure of the document, such as paragraphs, sections, headings, tables, or even code blocks, to create more logical and contextually complete chunks.
# * **Sentence Windowing / Propositional Chunking:** Instead of just using a single sentence or a small group of sentences as a chunk, these methods might create chunks around core propositions or include surrounding sentences (a "window") to provide richer contextual information for each retrieved piece.
# 
# By creating more meaningful, coherent, and contextually rich chunks, advanced strategies ensure that the information retrieved is more likely to be directly relevant and useful for the LLM, thereby improving the quality of its generated responses.
# 
# ---
# ## RAG Fusion
# 
# While advanced chunking improves the quality of indexed data, **RAG Fusion** enhances the retrieval process itself, making it more robust and comprehensive. Standard RAG often relies on a single query pass over the vector database. However, user queries can be ambiguous or multifaceted, and a single retrieval approach might miss relevant information.
# 
# RAG Fusion techniques aim to overcome this by diversifying the search and then intelligently combining, or "fusing," the results. Common approaches include:
# * **Query Expansion/Transformation:** The original user query is rephrased or expanded into multiple variations. For instance, sub-queries might be generated, or synonyms and related concepts might be added. Each variant is then used to search the knowledge base.
# * **Multiple Retrieval Passes:** Different retrieval algorithms or searches across multiple vector indices might be performed.
# * **Re-ranking and Fusion:** The results from these multiple search passes are then collected and re-ranked using algorithms like Reciprocal Rank Fusion (RRF). RRF considers the position of each retrieved document in the different ranked lists to produce a more robust final ranking, prioritizing documents that consistently appear as relevant across various queries or methods.
# 
# By generating diverse search perspectives and intelligently merging their findings, RAG Fusion improves recall (finding more relevant documents) and precision (ensuring those documents are indeed useful). This helps the RAG system handle complex queries better, reduce the impact of poorly phrased initial queries, and ultimately provide the LLM with a richer, more well-rounded set of information to generate its answer.
# 
# Together, advanced chunking and RAG Fusion represent significant strides in optimizing RAG pipelines, leading to more powerful and reliable AI applications.

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
# Load data
# https://www.kaggle.com/datasets/fajobgiua/indian-food-dataset?resource=download
import re
from tqdm.auto import tqdm
import json
import pandas as pd
from langchain_core.documents import Document


tqdm.pandas(desc="Generating Documents")
cleaning_pattern = r'[^a-zA-Z0-9]'

columns = ['TranslatedRecipeName', 'TranslatedIngredients',
           'PrepTimeInMins', 'CookTimeInMins', 'TotalTimeInMins', 'Servings',
           'Cuisine', 'Course', 'Diet', 'TranslatedInstructions', 'URL',
           'ComplexityLevel', 'MainIngredient']

doc_columns = ['score', 'page_content',]

df = pd.read_csv('./IndianFoodDataset.csv', ).set_index('Srno')[columns]


def convert_to_doc(row):
    doc = Document(
        page_content=f'''
# Recipe Name: {row['TranslatedRecipeName']}
> URL: {row['URL']}

## Ingredients:

{row['TranslatedIngredients']}

## Instructions:

{row['TranslatedInstructions']}
''',
        metadata={
            'TranslatedRecipeName': row['TranslatedRecipeName'],
            'PrepTimeInMins': row['PrepTimeInMins'],
            'CookTimeInMins': row['CookTimeInMins'],
            'TotalTimeInMins': row['TotalTimeInMins'],
            'Servings': row['Servings'],
            'Cuisine': row['Cuisine'],
            'Course': row['Course'],
            'Diet': row['Diet'],
            'ComplexityLevel': row['ComplexityLevel'],
            'MainIngredient': row['MainIngredient'],
        }
    )

    return doc


data = df[:].progress_apply(convert_to_doc, axis=1)

df

# %%


numeric_columns = df.describe().columns
# df.info()

data_cols = [col for col in df.columns if col not in numeric_columns]
metadata_friendly_cols = [
    col for col in df[data_cols] if df[col].unique().size < 100]

unique_vals_data = "\n".join(
    [
        f'{col}: {", ".join(df[col].unique())}' for col in metadata_friendly_cols
    ]
)


meta_data_prompt = f'''
Columns which have unique values:

{unique_vals_data}

Columns which have numeric values:
{df.describe().round(2)}
'''


def generate_metadata(search_query, metadata, llm):
    meta_prompt = f'''
    Given below the user request for queries, create metadata filter dictionary for the search.

    user query: {search_query}

    > provide only and only a simple phrase for the user query, do not add any other information or context.
    > this output will be used to filter the recipes.

    available metadata:

    {metadata}

    we do exact matches only

    respond with a valid json dictionary, do not add any other information or context.
    '''

    print(meta_prompt)

    resp = llm.generate_content(meta_prompt).text
    metadata = json.loads(resp.split(
        'json')[1].strip().split('```')[0].strip())

    return metadata


search_query = 'I need to have something sweet'

meta_data = generate_metadata(
    search_query,
    meta_data_prompt,
    model
)
print(meta_data)

ret_docs = vector_store_unchunked.similarity_search_with_score(
    search_query,
    k=20,
    score_threshold=0.1,
    filter=meta_data
)

searched_df = pd.DataFrame(
    [
        {
            'score': score,
            **doc.metadata,
            'page_content': doc.page_content,
        } for doc, score in ret_docs
    ],
    columns=doc_columns+columns
)

searched_df

# %%


# %%
# Load models and Initialize Vector Store
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import Qdrant  # Qdrant Vector Store Wrapper
import google.generativeai as genai
from dotenv import load_dotenv  # For loading API key from a .env file
import os
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

model_name = 'gemini-2.0-flash'

model = genai.GenerativeModel(model_name)

# load different dimension embedding models

model_768 = HuggingFaceEmbeddings(
    model_name="sentence-transformers/LaBSE",
)

model_384 = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

model_64 = HuggingFaceEmbeddings(
    model_name="ClovenDoug/tiny_64_all-MiniLM-L6-v2",
)

vector_store_unchunked = Qdrant.from_documents(
    data,
    model_384,
    collection_name="indian-food-metadata",
    location=':memory:',
)

# %% [markdown]
# ## Advanced Chunking Strategies
# 
# 

# %%
# Load Sample Text
sample_text = ''
with open('./sample.md', 'r') as f:
    sample_text = f.read()

# %%
# !pip install langchain langchain-text-splitters
# Sentence Windowing Chunking
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import re


def split_into_sentences_robust(text: str) -> list[str]:
    """
    Splits text into sentences using a more robust regex pattern.
    This handles various sentence terminators and aims to keep them with the sentence.
    """
    if not text:
        return []
    sentences = re.split(
        r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<![A-Z]\.)(?<=\.|\?|\!)\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def sentence_window_chunking(
    text_content: str,
    window_size: int = 1,
    custom_sentence_splitter_func=None
):
    """
    Splits text into chunks using a sentence windowing strategy.
    Each chunk consists of a central sentence plus 'window_size' sentences
    before and after it.

    Args:
        text_content: The text to be chunked.
        window_size: The number of sentences to include before and after
                     the central sentence in each chunk.
        custom_sentence_splitter_func: Optional function to split text into sentences.
                                       If None, a default robust regex splitter is used.

    Returns:
        A list of LangChain Document objects, where each document represents a
        windowed chunk. Metadata includes the central sentence and its original index.
    """
    if not text_content:
        # print("Error: Input text_content is empty.")
        return []
    if window_size < 0:
        # print("Error: window_size cannot be negative.")
        return []

    # print("Splitting text into initial sentences...")
    if custom_sentence_splitter_func:
        sentences = custom_sentence_splitter_func(text_content)
    else:
        sentences = split_into_sentences_robust(text_content)

    if not sentences:
        # print("No sentences found in the text.")
        return [
            Document(
                page_content=text_content,
                metadata={
                    "warning": "Could not split into sentences; treating entire text as one sentence."
                }
            )
        ]

    # print(f"Total sentences initially identified: {len(sentences)}")

    all_chunks = []
    for i, central_sentence_text in enumerate(sentences):
        start_index = max(0, i - window_size)
        # +1 because slice is exclusive at end
        end_index = min(len(sentences), i + window_size + 1)

        # Ensure the central sentence itself is included if window_size is 0
        if window_size == 0:
            current_window_sentences = [central_sentence_text]
        else:
            current_window_sentences = sentences[start_index:end_index]

        windowed_text = " ".join(current_window_sentences)

        metadata = {
            "original_central_sentence": central_sentence_text,
            "original_central_sentence_index": i,
            "window_size": window_size,
            "window_sentence_count": len(current_window_sentences)
        }
        chunk_doc = Document(page_content=windowed_text, metadata=metadata)
        all_chunks.append(chunk_doc)

    # print(
    #     f"\nSuccessfully created {len(all_chunks)} sentence-windowed chunks.")
    return all_chunks


chunks = sentence_window_chunking(sample_text, window_size=1)

for chunk in chunks[:6]:
    print(chunk.page_content)
    print('---')

# %%
# Content Aware Chunking

from langchain_text_splitters import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
    # You can add more levels like ("####", "Header 4") if needed
]
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False
)

chunks = markdown_splitter.split_text(sample_text)

for chunk in chunks[:6]:
    print(chunk.page_content)
    print('---')

# %%
# Semantic Chunking

from langchain_experimental.text_splitter import SemanticChunker


text_splitter = SemanticChunker(model_384)
docs = text_splitter.create_documents([sample_text])

for doc in docs:
    print(doc.page_content)
    print('---')

# %% [markdown]
# RAG Fusion is an advanced Retrieval-Augmented Generation (RAG) technique that significantly enhances the quality of responses from Large Language Models (LLMs) by improving the retrieval and ranking of information. It addresses limitations of traditional RAG systems, particularly when dealing with complex or nuanced queries. Two key components often integrated into RAG Fusion for superior performance are **metadata filtering** and **reranking**.
# 
# ### RAG Fusion: An Overview
# 
# At its core, RAG Fusion aims to overcome the "single query" limitation of basic RAG. Instead of relying on a single search query generated from the user's input, RAG Fusion typically involves:
# 
# 1.  **Multi-Query Generation:** The LLM generates several related sub-queries or reformulations of the original user query. This allows for a more comprehensive exploration of different facets and interpretations of the user's intent.
# 2.  **Parallel Retrieval:** Documents are retrieved from the knowledge base for each of these generated queries. This expands the pool of potentially relevant information.
# 3.  **Result Fusion:** The retrieved documents from all sub-queries are combined and re-ranked into a single, optimized list. A common algorithm for this fusion is **Reciprocal Rank Fusion (RRF)**, which effectively combines scores from multiple search results, giving higher weight to documents that appear higher in multiple lists.
# 
# ### Metadata Filtering in RAG Fusion
# 
# Metadata filtering acts as a powerful **pre-retrieval** or **initial filtering** step within a RAG system, including RAG Fusion. It leverages structured information (metadata) associated with documents or chunks in the knowledge base to narrow down the search space *before* the main retrieval process.
# 
# * **How it works:** When a user's query contains explicit or implicit criteria (e.g., "articles from 2023," "reports by John Doe," "documents related to healthcare"), an LLM can be used to extract these filters. These extracted metadata filters are then applied to the vector store or database, effectively reducing the number of documents that need to be subjected to more computationally intensive semantic search or vector similarity search.
# * **Benefits:**
#     * **Improved Relevance:** By filtering out irrelevant documents early, the system ensures that the subsequent retrieval and reranking steps operate on a more focused and pertinent dataset.
#     * **Reduced Noise:** It minimizes the chances of irrelevant information being passed to the LLM, leading to more precise and less "hallucinated" responses.
#     * **Enhanced Efficiency:** Narrowing down the search space reduces computational cost and latency, making the retrieval process faster.
#     * **Context Precision & Recall:** Contributes to better context precision (accuracy of retrieved context) and context recall (proportion of relevant information retrieved).
# 
# ### Reranking in RAG Fusion
# 
# Reranking is a **post-retrieval** step that refines the initial set of retrieved documents, prioritizing the most relevant ones to the user's query.
# 
# * **How it works:** After an initial set of documents (often expanded through multi-query generation and fusion) is retrieved, a more sophisticated reranker model (e.g., a cross-encoder or a fine-tuned LLM) evaluates each retrieved document against the original user query. Unlike initial retrievers that might rely on simpler similarity metrics, rerankers offer a deeper semantic understanding, considering the contextual coherence between the query and the document. They assign new scores or reorder the documents based on this deeper assessment.
# * **Benefits:**
#     * **Higher Precision:** Ensures that the most contextually relevant documents are at the very top of the list provided to the LLM for generation.
#     * **Nuanced Understanding:** Captures subtle semantic relationships that might be missed by initial retrieval methods.
#     * **Improved Answer Quality:** By feeding the LLM with the truly most relevant context, reranking directly leads to more accurate, comprehensive, and helpful generated responses.
#     * **Cost Optimization:** Reduces the amount of unnecessary information the LLM has to process, potentially leading to cost savings on API calls for larger models.
# 
# In summary, RAG Fusion, particularly when augmented with metadata filtering and reranking, represents a powerful evolution in RAG systems. Metadata filtering provides efficient pre-selection, while reranking offers a crucial post-retrieval refinement, together ensuring that the LLM receives the most accurate and relevant context to generate high-quality responses.

# %% [markdown]
# 
# ### Metadata Filtering: A Deeper Dive
# 
# Metadata filtering is the process of using structured, descriptive information (metadata) associated with your data chunks or documents to narrow down the search space *before* or *during* the retrieval phase in a RAG pipeline. This is distinct from purely semantic search, which relies on the meaning or context embedded in the text itself.
# 
# **What is Metadata?**
# 
# Metadata is "data about data." In the context of RAG, it refers to attributes or tags assigned to each document, chunk, or piece of information in your knowledge base. Examples include:
# 
# * **Categorical:** `document_type` (e.g., "report," "email," "article"), `department` (e.g., "HR," "Finance," "Legal"), `product_line`, `industry`.
# * **Temporal:** `creation_date`, `last_modified_date`, `year_of_publication`, `event_date`.
# * **Geographical:** `region`, `country`, `city`.
# * **Authorship/Source:** `author`, `source_system`, `publisher`, `security_level`.
# * **Numeric:** `version_number`, `price_range` (for product catalogs), `sentiment_score`.
# * **Relationships:** If using a knowledge graph, metadata can also represent relationships between entities (e.g., "mentions," "produced_by," "related_to").
# 
# **How Metadata is Used in RAG:**
# 
# 1.  **Metadata Extraction/Tagging:**
#     * **Manual:** For smaller datasets, metadata can be manually assigned.
#     * **Automated:** This is the most common approach for large-scale RAG.
#         * **Rule-based:** Simple patterns or keywords can be used to extract metadata (e.g., extracting a year from the filename).
#         * **LLM-based (Intelligent Metadata Extraction):** This is a powerful technique. An LLM (often a smaller, faster model) can be prompted to analyze the user's natural language query and identify explicit or implicit metadata filters. For example, if the query is "What were the sales figures for the Asia Pacific region in Q3 2023?", the LLM can extract "Asia Pacific" as `region` and "Q3 2023" as a `date_range` or `quarter_year` filter. Similarly, when ingesting documents, LLMs can be used to automatically identify and tag documents with relevant metadata (e.g., identifying the author or document type from the content).
# 
# 2.  **Filtering Mechanisms:**
# 
#     * **Pre-filtering (or Filter-First):** This is the most common and often most efficient approach. The metadata filters are applied to the entire knowledge base *before* any vector similarity search occurs. This significantly reduces the dataset on which the computationally intensive vector search needs to operate.
#         * *Example:* If a user asks for "HR policies from 2024," the system first filters all documents to only those tagged with `department: "HR"` AND `year: 2024`. Only then are embeddings created for the remaining query (e.g., "policies") and used to search within this much smaller, pre-filtered subset.
#         * *Advantages:* Highly efficient, precise, reduces noise.
#         * *Considerations:* If the filters are too restrictive, it might exclude relevant documents that semantic search alone might have found (e.g., if a document mentions "HR policies" but isn't strictly tagged with `department: "HR"`).
# 
#     * **Post-filtering (or Search-First):** In this approach, a broader vector similarity search is performed first, retrieving a larger set of semantically relevant documents. Then, metadata filters are applied to this *retrieved set* to narrow it down.
#         * *Example:* A general semantic search for "policies" might retrieve documents from various departments and years. Then, filters like `department: "HR"` and `year: 2024` are applied to this retrieved set.
#         * *Advantages:* Less prone to missing semantically relevant documents due to strict early filtering.
#         * *Considerations:* Can be less efficient as the initial vector search operates on a larger dataset.
# 
#     * **Hybrid Filtering (Pre + Post or Combined Queries):** Many modern vector databases and RAG frameworks support sophisticated combined queries where metadata filters and vector similarity search can be applied simultaneously or in a smart, optimized order. This often involves applying the filter first for efficiency and then performing the vector search on the filtered subset. Some systems can even dynamically decide whether to pre-filter or post-filter based on the cardinality of the filter (how many documents it's likely to filter out).
# 
# 3.  **Integration with Vector Databases:**
#     Most vector databases (e.g., Pinecone, Weaviate, Qdrant, ChromaDB, Milvus) have built-in capabilities to store metadata alongside vector embeddings and support efficient metadata filtering operations. This allows for powerful combined queries that leverage both semantic similarity and structured filtering.
# 
# **Benefits of Metadata Filtering:**
# 
# * **Increased Precision and Relevance:** Directly addresses the user's explicit criteria, ensuring the retrieved context is highly targeted and pertinent.
# * **Reduced Noise and Irrelevant Information:** Prevents the LLM from being exposed to data that doesn't meet specific criteria, leading to more accurate and less "hallucinated" responses.
# * **Improved Efficiency and Scalability:** By reducing the search space, it lowers the computational cost and latency of retrieval, especially for large knowledge bases.
# * **Enhanced Control and Trustworthiness:** Allows for enforcing access controls (e.g., `security_level`), ensuring compliance (e.g., `regulatory_body`), or prioritizing certain sources (e.g., `peer_reviewed: true`).
# * **Better Context Recall:** By precisely defining the subset of data to search, it can improve the likelihood of retrieving all relevant information within that subset.
# * **Handles Ambiguity:** Can resolve ambiguity in user queries by adding specific constraints (e.g., "apple" could refer to the fruit or the company; a `company_name: "Apple Inc."` filter clarifies).
# 
# Metadata filtering is a critical tool in building robust and effective RAG systems, enabling more precise, efficient, and controlled information retrieval.

# %%
search_query = 'Non vegetarian, healthy, spicy, easy to cook, non oily, quick, 10 minutes, 2 servings, Indian food'

# %%
# Simple search
ret_docs = vector_store_unchunked.similarity_search_with_score(
    search_query,
    k=20,
)

searched_df = pd.DataFrame(
    [
        {
            'score': score,
            **doc.metadata,
            'page_content': doc.page_content,
        } for doc, score in ret_docs
    ],
    columns=doc_columns+columns
)

searched_df

# %%
# RAG With Score Threshold

ret_docs = vector_store_unchunked.similarity_search_with_score(
    search_query,
    k=20,
    score_threshold=0.5,
)

searched_df = pd.DataFrame(
    [
        {
            'score': score,
            **doc.metadata,
            'page_content': doc.page_content,
        } for doc, score in ret_docs
    ],
    columns=doc_columns+columns
)

searched_df

# %%
# metadata filtering with single metadata filter

ret_docs = vector_store_unchunked.similarity_search_with_score(
    search_query,
    k=20,
    score_threshold=0.5,
    filter={
        'Cuisine': 'Indian',
    }
)

searched_df = pd.DataFrame(
    [
        {
            'score': score,
            **doc.metadata,
            'page_content': doc.page_content,
        } for doc, score in ret_docs
    ],
    columns=doc_columns+columns
)

searched_df

# %%
# metadata filtering with multiple filters

ret_docs = vector_store_unchunked.similarity_search_with_score(
    search_query,
    k=20,
    score_threshold=0.5,
    filter={
        'Cuisine': 'Indian',
        'PrepTimeInMins': 10
    }
)

searched_df = pd.DataFrame(
    [
        {
            'score': score,
            **doc.metadata,
            'page_content': doc.page_content,
        } for doc, score in ret_docs
    ],
    columns=doc_columns+columns
)

searched_df

# %% [markdown]
# Let's expand on reranking, a critical step in enhancing the quality and relevance of retrieved documents in Retrieval-Augmented Generation (RAG) systems.
# 
# ### Reranking: A Deeper Dive
# 
# Reranking is a post-retrieval process that takes an initial list of documents (or chunks) retrieved by a primary retrieval method (e.g., vector similarity search, keyword search, or a fused list from RAG Fusion) and reorders them based on a more sophisticated and nuanced understanding of their relevance to the original query. The goal is to elevate the most pertinent documents to the top of the list, ensuring the Large Language Model (LLM) receives the absolute best context for generating its response.
# 
# **Why is Reranking Necessary?**
# 
# Initial retrieval methods, especially dense vector retrievers, are excellent at finding semantically similar documents. However, they can sometimes fall short in:
# 
# 1.  **Nuance and Specificity:** A vector search might find documents that are broadly related but lack the precise information needed for the user's specific query. For example, a search for "best practices for secure coding" might retrieve many documents about "coding" or "security" but not necessarily those that directly address "secure coding best practices."
# 2.  **Contextual Coherence:** The initial retriever might return documents that are individually semantically similar but don't collectively form a coherent context for the LLM.
# 3.  **Ambiguity:** Certain queries can have multiple interpretations. A reranker, with its deeper understanding, can often disambiguate and prioritize documents aligning with the most likely intent.
# 4.  **Long-Tail Relevance:** Sometimes, the most relevant information might be buried deeper in the initial retrieval list due to the limitations of the primary similarity metric.
# 5.  **Efficiency Trade-offs:** Primary retrievers often need to be fast and scalable, sometimes sacrificing a bit of precision for speed. Rerankers can afford to be more computationally intensive because they operate on a much smaller, pre-filtered set of documents.
# 
# **How Reranking Works:**
# 
# Reranking models are typically more powerful and sophisticated than the embedding models used for initial retrieval. They often employ a "cross-encoder" architecture or are specialized transformer models.
# 
# 1.  **Input:** The reranker takes two primary inputs for each document:
#     * The original user query.
#     * A retrieved document (or chunk of a document).
# 
# 2.  **Scoring Mechanism:** Unlike a vector similarity search that calculates a distance or dot product between query and document embeddings, a reranker directly encodes *both* the query and the document (or a concatenated pair of them) into a single representation. It then produces a relevance score, indicating how well the document matches the query's intent. This joint encoding allows the model to understand the interaction and specific contextual relationship between the query and the document content.
# 
# 3.  **Model Architectures:**
#     * **Cross-Encoders:** These are a popular choice for reranking. They pass the concatenated query and document text through a transformer encoder (like BERT or RoBERTa). The output layer then predicts a single relevance score. Because the query and document are processed together, the model can capture very fine-grained interactions.
#     * **Bi-Encoders with Stronger Models:** While less common for dedicated rerankers, a bi-encoder (where query and document are encoded separately into embeddings) can also be used for reranking if the encoder model is very powerful and the similarity metric is robust. However, cross-encoders generally achieve higher performance for reranking due to their interactive nature.
#     * **Fine-tuned LLMs:** For very advanced setups, a smaller, fine-tuned LLM can act as a reranker, not just scoring but potentially also providing a brief summary of why a document is relevant.
# 
# 4.  **Ranking:** After assigning a relevance score to each document in the initial retrieved set, the documents are then sorted in descending order of their scores, with the highest-scoring documents placed at the top. The top-N documents from this reranked list are then passed to the main LLM for response generation.
# 
# **Key Benefits of Reranking:**
# 
# * **Significant Improvement in Precision:** This is the primary benefit. Reranking ensures that the most semantically aligned and contextually relevant information is presented to the LLM, leading to more accurate and specific answers.
# * **Enhanced Contextual Understanding:** Cross-encoder rerankers capture nuanced semantic relationships and interactions between the query and documents that simpler similarity metrics might miss.
# * **Reduced LLM Hallucination:** By providing highly relevant and focused context, reranking minimizes the chances of the LLM generating incorrect or irrelevant information.
# * **Better Use of LLM Context Window:** LLMs have limited context windows. Reranking ensures that these precious tokens are filled with the *most useful* information, maximizing the quality of the generated response.
# * **Improved User Experience:** Users receive more precise and satisfying answers, leading to higher trust in the RAG system.
# * **Handles Complex Queries:** Reranking shines when dealing with intricate or multi-faceted queries that require a deeper understanding beyond simple keyword or semantic similarity.
# 
# **Integration into RAG Fusion:**
# 
# In the context of RAG Fusion, reranking plays an even more crucial role. After multiple queries have been generated and documents retrieved from each, and potentially fused using techniques like Reciprocal Rank Fusion (RRF), the resulting combined list can still benefit immensely from a final, high-fidelity reranking step. This ensures that the top-N documents presented to the LLM are not just a broad collection of relevant items but the absolute best ones, taking into account the full complexity of the initial query and its sub-queries.
# 
# Reranking is a non-negotiable component for achieving state-of-the-art performance in sophisticated RAG pipelines, acting as the final quality control gate for the retrieved context.

# %%
# rerank with 768 dim embedding

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

new_doc_embeddings = np.array(
    model_768.embed_documents(searched_df.page_content)
)

query_embedding = np.array(
    model_768.embed_query(search_query)
)

similarity_scores = cosine_similarity(
    query_embedding.reshape(1, -1),
    new_doc_embeddings
)

searched_df['rerank_score'] = similarity_scores[0].tolist()

searched_df[['score', 'rerank_score', 'TranslatedRecipeName', ]].sort_values(
    'rerank_score', ascending=False, )

# %%
# rerank with 64 dim embedding

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

new_doc_embeddings = np.array(
    model_64.embed_documents(searched_df.page_content)
)

query_embedding = np.array(
    model_64.embed_query(search_query)
)

similarity_scores = cosine_similarity(
    query_embedding.reshape(1, -1),
    new_doc_embeddings
)

searched_df['rerank_score'] = similarity_scores[0].tolist()

searched_df[['score', 'rerank_score', 'TranslatedRecipeName', ]].sort_values(
    'rerank_score', ascending=False, )

# %% [markdown]
# Query transformation and expansion are critical techniques in Retrieval-Augmented Generation (RAG) systems designed to bridge the semantic gap between a user's natural language query and the content stored in a knowledge base. The goal is to maximize the chances of retrieving highly relevant documents, even if the initial query isn't perfectly formulated or lacks sufficient detail.
# 
# ### Query Transformation: Refining the User's Intent
# 
# **Query transformation** involves modifying or rephrasing the original user query to make it more effective for retrieval. This step often aims to improve the clarity, conciseness, or specificity of the query, or to align it better with the language used in the knowledge base.
# 
# **Common Transformation Techniques:**
# 
# 1.  **Rephrasing/Simplification:**
#     * **Goal:** To create a more direct and unambiguous search query.
#     * **How it works:** An LLM analyzes the original user query and generates one or more alternative phrasings that might be more effective for keyword or semantic search.
#     * **Example:**
#         * **Original Query:** "What are the steps one should take to set up a new email account?"
#         * **Transformed Query:** "email account setup steps" or "how to configure new email."
#     * **Benefit:** Removes conversational filler, focuses on keywords, and standardizes phrasing.
# 
# 2.  **Decomposition:**
#     * **Goal:** To break down a complex, multi-faceted query into simpler, more manageable sub-queries.
#     * **How it works:** If a user asks a question that touches upon several distinct topics, an LLM can identify these sub-topics and generate individual queries for each.
#     * **Example:**
#         * **Original Query:** "Tell me about the history of AI and its impact on healthcare."
#         * **Transformed Queries:** "history of artificial intelligence," "AI applications in healthcare," "impact of AI on medical industry."
#     * **Benefit:** Allows the system to retrieve highly specific information for each part of the query, leading to more comprehensive answers.
# 
# 3.  **Reformulation for Specific Search Types:**
#     * **Goal:** To tailor the query for different retrieval mechanisms.
#     * **How it works:** If the RAG system uses both keyword search and vector search, an LLM might generate a keyword-optimized query and a separate, more semantically rich query for vector search.
#     * **Example:**
#         * **Original Query:** "When was the last major financial crisis?"
#         * **Keyword Query:** "financial crisis date," "stock market crash year."
#         * **Semantic Query:** "recent global economic downturn events."
#     * **Benefit:** Leverages the strengths of different retrieval methods.
# 
# ### Query Expansion: Broadening the Search Horizon
# 
# **Query expansion** involves adding more terms, synonyms, or related concepts to the original query. The aim is to increase the recall of the retrieval system, meaning it can find more potentially relevant documents that might not use the exact phrasing of the original query.
# 
# **Common Expansion Techniques:**
# 
# 1.  **Synonym and Related Term Addition:**
#     * **Goal:** To capture documents that use alternative vocabulary for the same concept.
#     * **How it works:** An LLM or a thesaurus/knowledge graph identifies synonyms, hyponyms (more specific terms), hypernyms (more general terms), or closely related concepts to the terms in the original query.
#     * **Example:**
#         * **Original Query:** "Benefits of exercise."
#         * **Expanded Query:** "Benefits of exercise, physical activity, workout, training, fitness."
#     * **Benefit:** Widens the net for retrieval, especially useful when the knowledge base uses diverse terminology.
# 
# 2.  **Paraphrasing/Generating Multiple Queries (RAG Fusion):**
#     * **Goal:** To generate multiple plausible interpretations or rephrased versions of the query to cover different angles. This is a core component of RAG Fusion.
#     * **How it works:** An LLM generates several distinct yet semantically similar queries from the original user input. Each of these queries is then used for parallel retrieval.
#     * **Example:**
#         * **Original Query:** "How does quantum computing work?"
#         * **Expanded Queries:** "principles of quantum computation," "explanation of quantum algorithms," "fundamentals of qubits."
#     * **Benefit:** Drastically increases the chance of finding relevant documents, particularly for complex or ambiguous queries. The results from these parallel searches are then fused (e.g., using Reciprocal Rank Fusion).
# 
# 3.  **Adding Contextual Keywords:**
#     * **Goal:** To implicitly add context that might be missing from a short query.
#     * **How it works:** An LLM infers the broader domain or intent and adds relevant keywords.
#     * **Example:**
#         * **Original Query (user searching medical database):** "Headache remedies."
#         * **Expanded Query:** "Headache remedies, migraine treatment, pain relief medication, symptom management."
#     * **Benefit:** Guides the retriever towards the correct domain.
# 
# **Integration into RAG Pipelines:**
# 
# Query transformation and expansion steps are typically performed **before** the primary retrieval step. The generated queries are then sent to the vector database or search engine to retrieve documents. In advanced RAG systems like RAG Fusion, these techniques are integral, as the system relies on generating multiple effective queries to achieve superior retrieval performance.
# 
# By strategically transforming and expanding user queries, RAG systems can overcome linguistic variations, improve the precision and recall of retrieved information, and ultimately provide more accurate and comprehensive answers to complex user questions.

# %%
# Query rewrite + metadata filtering

prompt = f'''
Given below the user request for queries regarding Indian food recipes, rephrase and expand the query to a more search friendly term.

user query: {search_query}

> provide only and only a simple phrase for the user query, do not add any other information or context.
> this output will be used to search the database for recipes.
'''
resp = model.generate_content(prompt).text

print(resp)

ret_docs = vector_store_unchunked.similarity_search_with_score(
    resp,
    k=20,
    score_threshold=0.1,
    filter={
        'Cuisine': 'Indian',
        'PrepTimeInMins': 10
    }
)

searched_df = pd.DataFrame(
    [
        {
            'score': score,
            **doc.metadata,
            'page_content': doc.page_content,
        } for doc, score in ret_docs
    ],
    columns=doc_columns+columns
)

searched_df[['score', 'TranslatedRecipeName', ]]

# %%
# Query rewriting + Metadata filtering + reranking

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

prompt = f'''
Given below the user request for queries regarding Indian food recipes, rephrase and expand the query to a more search friendly term.

user query: {search_query}

> provide only and only a simple phrase for the user query, do not add any other information or context.
> this output will be used to search the database for recipes.
'''
resp = model.generate_content(prompt).text

print(resp)

ret_docs = vector_store_unchunked.similarity_search_with_score(
    resp,
    k=20,
    score_threshold=0.1,
    filter={
        'Cuisine': 'Indian',
        'PrepTimeInMins': 10
    }
)

searched_df = pd.DataFrame(
    [
        {
            'score': score,
            **doc.metadata,
            'page_content': doc.page_content,
        } for doc, score in ret_docs
    ],
    columns=doc_columns+columns
)


new_doc_embeddings = np.array(
    model_768.embed_documents(searched_df.page_content)
)

query_embedding = np.array(
    model_768.embed_query(search_query)
)

similarity_scores = cosine_similarity(
    query_embedding.reshape(1, -1),
    new_doc_embeddings
)

searched_df['rerank_score'] = similarity_scores[0].tolist()

searched_df[
    ['score', 'rerank_score', 'TranslatedRecipeName', ]
].sort_values('rerank_score', ascending=False, )

# %%
# Asking the model to create metadata filters

meta_prompt = f'''
Given below the user request for queries, create metadata filter dictionary for the search.

user query: {search_query}

> provide only and only a simple phrase for the user query, do not add any other information or context.
> this output will be used to filter the recipes.

available metadata:
- 'Cuisine': string: ['Indian', 'Kerala Recipes', 'Oriya Recipes', 'Continental',
       'Chinese', 'Konkan', 'Chettinad', 'Mexican', 'Kashmiri',
       'South Indian Recipes', 'North Indian Recipes', 'Andhra',
       'Gujarati Recipes']
- 'Diet': string: ['Vegetarian', 'High Protein Vegetarian', 'Non Vegeterian',
       'Eggetarian', 'Diabetic Friendly', 'High Protein Non Vegetarian',
       'Gluten Free', 'Sugar Free Diet', 'No Onion No Garlic (Sattvic)',
       'Vegan']
- 'ComplexityLevel': string: ['Medium', 'Hard']

We can do exact match only.

respond with a valid json dictionary, do not add any other information or context.
'''
resp = model.generate_content(meta_prompt).text
metadata = json.loads(resp.split('json')[1].strip().split('```')[0].strip())

print('metadata:', metadata)

ret_docs = vector_store_unchunked.similarity_search_with_score(
    search_query,
    k=20,
    score_threshold=0.1,
    filter=metadata
)

searched_df = pd.DataFrame(
    [
        {
            'score': score,
            **doc.metadata,
            'page_content': doc.page_content,
        } for doc, score in ret_docs
    ],
    columns=doc_columns+columns
)

searched_df[['score', 'TranslatedRecipeName', ]]

# %%
# Asking the model to Break down the query into multiple subqueries and rerank

subquery_prompt = f'''
Given below the user request for queries, break down the query into multiple subqueries.
user query: {search_query}
> provide only and only a simple phrase for the user query, do not add any other information or context.
> this output will be used to search the database for recipes.

> respond with a valid json array of strings, do not add any other information or context.
'''

resp = model.generate_content(subquery_prompt).text
subqueries = json.loads(resp.split('json')[1].strip().split('```')[0].strip())
print('subqueries:', subqueries)

ret_docs = []

for subquery in subqueries:
    ret_docs += vector_store_unchunked.similarity_search_with_score(
        subquery,
        k=20,
        score_threshold=0.1,
    )
searched_df = pd.DataFrame(
    [
        {
            'score': score,
            **doc.metadata,
            'page_content': doc.page_content,
        } for doc, score in ret_docs
    ],
    columns=doc_columns+columns
)

# rerank the results
new_doc_embeddings = np.array(
    model_768.embed_documents(searched_df.page_content)
)
query_embedding = np.array(
    model_768.embed_query(search_query)
)
similarity_scores = cosine_similarity(
    query_embedding.reshape(1, -1),
    new_doc_embeddings
)
searched_df['rerank_score'] = similarity_scores[0].tolist()
print(
    searched_df[
        ['rerank_score', 'TranslatedRecipeName', ]
    ].drop_duplicates().sort_values(
        'rerank_score',
        ascending=False,
    ).head(10).to_markdown(
        index=False,
    )
)

# %%
# Going Full RAG Fusion
# Process:
# - Model based Query Rewriting > Breakdown
# - Model based Metadata Filtering
# - Vector DB Search > Rerank
# Asking the model to Break down the query into multiple subqueries and rerank

def generate_metadata(search_query, model):
    meta_prompt = f'''
    Given below the user request for queries, create metadata filter dictionary for the search.

    user query: {search_query}

    > provide only and only a simple phrase for the user query, do not add any other information or context.
    > this output will be used to filter the recipes.

    available metadata:
    - 'Cuisine': string: ['Indian', 'Kerala Recipes', 'Oriya Recipes', 'Continental',
        'Chinese', 'Konkan', 'Chettinad', 'Mexican', 'Kashmiri',
        'South Indian Recipes', 'North Indian Recipes', 'Andhra',
        'Gujarati Recipes']
    - 'Diet': string: ['Vegetarian', 'High Protein Vegetarian', 'Non Vegeterian',
        'Eggetarian', 'Diabetic Friendly', 'High Protein Non Vegetarian',
        'Gluten Free', 'Sugar Free Diet', 'No Onion No Garlic (Sattvic)',
        'Vegan']
    - 'ComplexityLevel': string: ['Medium', 'Hard']

    We can do exact match only.

    respond with a valid json dictionary, do not add any other information or context.
    '''

    resp = model.generate_content(meta_prompt).text
    metadata = json.loads(resp.split(
        'json')[1].strip().split('```')[0].strip())

    print('metadata:', metadata)
    return metadata


def rewrite_query(search_query, model):
    prompt = f'''
    Given below the user request for queries regarding Indian food recipes, rephrase and expand the query to a more search friendly term.

    user query: {search_query}

    > provide only and only a simple phrase for the user query, do not add any other information or context.
    > this output will be used to search the database for recipes.
    '''
    resp = model.generate_content(prompt).text
    print('rewritting query: ', resp)
    return resp


def break_query(search_query, model):
    subquery_prompt = f'''
    Given below the user request for queries, break down the query into multiple subqueries.
    user query: {search_query}
    > provide only and only a simple phrase for the user query, do not add any other information or context.
    > this output will be used to search the database for recipes.

    > respond with a valid json array of strings, do not add any other information or context.
    '''

    resp = model.generate_content(subquery_prompt).text
    subqueries = json.loads(resp.split(
        'json')[1].strip().split('```')[0].strip())
    print('subqueries:', subqueries)
    return subqueries


def rerank_results(search_query, searched_df, ):
    new_doc_embeddings = np.array(
        model_768.embed_documents(searched_df.page_content)
    )

    query_embedding = np.array(
        model_768.embed_query(search_query)
    )

    similarity_scores = cosine_similarity(
        query_embedding.reshape(1, -1),
        new_doc_embeddings
    )
    searched_df['rerank_score'] = similarity_scores[0].tolist()
    return searched_df


# begin
print('search query:', search_query)
cleaned_query = rewrite_query(search_query, model)
metadata = generate_metadata(cleaned_query, model)
subqueries = break_query(cleaned_query, model)


ret_docs = []
for subquery in subqueries:
    ret_docs += vector_store_unchunked.similarity_search_with_score(
        subquery,
        k=20,
        score_threshold=0.1,
        filter=metadata
    )
searched_df = pd.DataFrame(
    [
        {
            'score': score,
            **doc.metadata,
            'page_content': doc.page_content,
        } for doc, score in ret_docs
    ],
    columns=doc_columns+columns
)

searched_df = searched_df.groupby('TranslatedRecipeName').first().reset_index()

reranked_df = rerank_results(
    search_query,
    searched_df,
).sort_values(
    'rerank_score',
    ascending=False,
)

# reranked_df = reranked_df.drop_duplicates()
print(
    reranked_df[
        ['rerank_score', 'TranslatedRecipeName', ]
    ].head(10).to_markdown(
        index=False,
    )
)

# %% [markdown]
# ### Mid Session Assignment
# 
# Do the following:
# - Query transformation and expansion
# - `Use BM25 based search`
# - Apply Reranking
# 
# Compare Results

# %% [markdown]
# Building a RAG (`Retrieval Augmented Generation`) based chatbot allows Large Language Models (LLMs) to provide answers grounded in specific, up-to-date information, significantly enhancing factual accuracy and reducing "hallucinations." This approach creates chatbots that can converse intelligently about domain-specific knowledge not present in their original training data.
# 
# The process begins with establishing a **Knowledge Base**. This involves collecting relevant documents—such as FAQs, product manuals, articles, or internal wikis—and then breaking them down into smaller, manageable pieces called **chunks**. Effective chunking is crucial; strategies like semantic or context-aware chunking help ensure that these pieces retain their meaning and relevant context.
# 
# Next, these text chunks are transformed into numerical representations known as **embeddings** using a specialized embedding model. These embeddings capture the semantic essence of the text and are stored and indexed in a **vector database**, which is optimized for quick similarity searches.
# 
# When a user interacts with the chatbot, the **Retrieval** phase is triggered. The user's query is also converted into an embedding. This query embedding is then used to search the vector database, retrieving the most semantically similar (and thus most relevant) chunks from the indexed knowledge base.
# 
# Finally, in the **Augmentation and Generation** stage, these retrieved chunks are combined with the original user query and a carefully crafted prompt. This enriched input is then passed to an LLM. The LLM uses the provided contextual information from the retrieved documents to formulate a coherent, accurate, and relevant response. This allows the chatbot to "cite" or base its information on the provided documents, leading to more trustworthy and informative conversational experiences.

# %%
# Simple Chat Bot
chat_messages = []

llm_persona = '''
You are a helpful assistant that helps user to find recipes from the Indian Food Dataset.
Your pesona is polite, friendly and helpful.
You are not a chef, you are a recipe search assistant.

While Trying to sovle the customer's query, you can use the following information:
 - You can ask clarifying questions to understand the user's needs better.
 - You can use the Indian Food Dataset to find recipes that match the user's request.
 - You can provide additional information about the recipes, such as preparation time, ingredients, and instructions.
 - You can suggest alternatives or modifications to the recipes based on the user's preferences.

You are not allowed to:
 - Provide medical or dietary advice.
 - Make assumptions about the user's dietary restrictions or preferences without asking.
 - Provide personal opinions or recommendations that are not based on the dataset.
 - Provide recipes that are not in the Indian Food Dataset.
 - Provide recipes that are not relevant to the user's query.
'''

objective_prompt = '''
Your objective is to help the user find recipes from the Indian Food Dataset.
Your hidden side task is also to suggest, cross sell and/upsell dishes.
'''

prompt = '''
Your persona:
{llm_persona}

Your objective:
{objective_prompt}

current user message: {user_message}

Current chat history:
{chat_history}
'''

# %%
user_test_messages = [
    'I want to eat something spicy, non oily and quick to cook.',
    'I am looking for a recipe that is healthy and easy to cook.',
    'I want to eat something that is non vegetarian, quick to cook and spicy.',
    'I am looking for a recipe that is gluten free and easy to cook.',
    'I want to eat something that is diabetic friendly and quick to cook.',
    'I am looking for a recipe that is high protein vegetarian and easy to cook.',
]

for user_message in user_test_messages:
    chat_messages.append({
        'role': 'user',
        'content': user_message,
    })

    prompt = prompt.format(
        llm_persona=llm_persona,
        objective_prompt=objective_prompt,
        user_message=user_message,
        chat_history='\n'.join(
            [
                f"{msg['role']}: {msg['content']}"
                for msg in chat_messages
            ]
        ),
        # json.dumps(chat_messages, indent=2)
    )

    resp = model.generate_content(prompt).text
    print('response:', resp)
    chat_messages.append({
        'role': 'assistant',
        'content': resp,
    })


