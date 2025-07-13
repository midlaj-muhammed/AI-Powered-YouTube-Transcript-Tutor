"""
Text processing utilities for document handling and vector store operations.
"""

import os
import logging
from typing import List, Optional, Dict, Any
try:
    from langchain_openai import OpenAIEmbeddings, OpenAI
except ImportError:
    from langchain_community.embeddings import OpenAIEmbeddings
    from langchain_community.llms import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
import pickle

logger = logging.getLogger(__name__)

class SimpleVectorStore:
    """
    Simple text-based vector store that works without embeddings.
    Uses basic text search and keyword matching.
    """

    def __init__(self, documents: List[Document]):
        self.documents = documents
        self.texts = [doc.page_content for doc in documents]

    def as_retriever(self, search_type: str = "similarity", search_kwargs: dict = None):
        """Return a simple retriever."""
        return SimpleRetriever(self.documents, search_kwargs or {})

class SimpleRetriever:
    """Simple text-based retriever."""

    def __init__(self, documents: List[Document], search_kwargs: dict):
        self.documents = documents
        self.k = search_kwargs.get('k', 4)

    def get_relevant_documents(self, query: str) -> List[Document]:
        """Get relevant documents using simple text matching."""
        query_words = query.lower().split()
        scored_docs = []

        for doc in self.documents:
            content = doc.page_content.lower()
            score = sum(1 for word in query_words if word in content)
            if score > 0:
                scored_docs.append((doc, score))

        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored_docs[:self.k]]

class FallbackQAChain:
    """
    Fallback QA chain that works without OpenAI API.
    Provides basic text search and simple answers.
    """

    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.documents = []

        # Extract documents from vectorstore
        try:
            if isinstance(vectorstore, SimpleVectorStore):
                self.documents = vectorstore.documents
            elif hasattr(vectorstore, 'docstore') and hasattr(vectorstore.docstore, '_dict'):
                self.documents = list(vectorstore.docstore._dict.values())
        except:
            pass

    def __call__(self, inputs: Dict[str, str]) -> Dict[str, Any]:
        """
        Process a query and return an answer.

        Args:
            inputs (Dict[str, str]): Input dictionary with 'query' key

        Returns:
            Dict[str, Any]: Result dictionary with 'result' and 'source_documents'
        """
        query = inputs.get('query', '').lower()

        # Simple keyword-based search
        relevant_docs = []
        for doc in self.documents:
            if hasattr(doc, 'page_content'):
                content = doc.page_content.lower()
                # Simple relevance scoring based on keyword matches
                query_words = query.split()
                matches = sum(1 for word in query_words if word in content)
                if matches > 0:
                    relevant_docs.append((doc, matches))

        # Sort by relevance and take top results
        relevant_docs.sort(key=lambda x: x[1], reverse=True)
        top_docs = [doc for doc, _ in relevant_docs[:3]]

        # Generate simple answer
        if top_docs:
            # Combine relevant text
            combined_text = " ".join([doc.page_content[:200] for doc in top_docs])
            answer = f"Based on the transcript, here's what I found: {combined_text[:500]}..."
        else:
            answer = "I couldn't find specific information about that in the transcript. Please try rephrasing your question or ask about different topics covered in the video."

        return {
            'result': answer,
            'source_documents': top_docs
        }

class TextProcessor:
    """Handles text processing, document splitting, and vector store operations."""
    
    def __init__(self, openai_api_key: str):
        """
        Initialize TextProcessor with OpenAI API key.
        
        Args:
            openai_api_key (str): OpenAI API key
        """
        self.openai_api_key = openai_api_key
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = OpenAI(openai_api_key=openai_api_key, temperature=0.7)
        
    def create_documents_from_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Document]:
        """
        Create LangChain documents from text with metadata.
        
        Args:
            text (str): Input text
            metadata (Dict[str, Any]): Document metadata
            
        Returns:
            List[Document]: List of LangChain documents
        """
        if metadata is None:
            metadata = {}
            
        # Use RecursiveCharacterTextSplitter for better text splitting
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Create a document and split it
        doc = Document(page_content=text, metadata=metadata)
        docs = text_splitter.split_documents([doc])
        
        return docs
    
    def create_vector_store(self, documents: List[Document]) -> Optional[FAISS]:
        """
        Create FAISS vector store from documents with fallback options.

        Args:
            documents (List[Document]): List of documents

        Returns:
            Optional[FAISS]: FAISS vector store or None if failed
        """
        try:
            if not documents:
                logger.error("No documents provided for vector store creation")
                return None

            # Try with OpenAI embeddings first
            try:
                vectorstore = FAISS.from_documents(documents, self.embeddings)
                return vectorstore
            except Exception as openai_error:
                logger.warning(f"OpenAI embeddings failed: {openai_error}")

                # Fallback to simple text-based search
                logger.info("Using simple text-based fallback")
                return self._create_simple_fallback_store(documents)

        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            return None

    def _create_simple_fallback_store(self, documents: List[Document]) -> Optional['SimpleVectorStore']:
        """
        Create a simple fallback vector store using basic text search.

        Args:
            documents (List[Document]): List of documents

        Returns:
            Optional[SimpleVectorStore]: Simple vector store or None if failed
        """
        try:
            # Create simple text-based vector store
            simple_store = SimpleVectorStore(documents)
            logger.info("Created simple text-based fallback vector store")
            return simple_store
        except Exception as e:
            logger.error(f"Even fallback vector store creation failed: {e}")
            return None
    
    def save_vector_store(self, vectorstore: FAISS, path: str) -> bool:
        """
        Save vector store to disk.
        
        Args:
            vectorstore (FAISS): Vector store to save
            path (str): Path to save the vector store
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
            vectorstore.save_local(path)
            return True
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            return False
    
    def load_vector_store(self, path: str) -> Optional[FAISS]:
        """
        Load vector store from disk.
        
        Args:
            path (str): Path to load the vector store from
            
        Returns:
            Optional[FAISS]: Loaded vector store or None if failed
        """
        try:
            if not os.path.exists(path):
                logger.error(f"Vector store path does not exist: {path}")
                return None
                
            vectorstore = FAISS.load_local(path, self.embeddings)
            return vectorstore
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return None
    
    def create_qa_chain(self, vectorstore, chain_type: str = "stuff") -> Optional[RetrievalQA]:
        """
        Create QA chain from vector store with fallback options.

        Args:
            vectorstore: Vector store (FAISS or SimpleVectorStore)
            chain_type (str): Type of chain to create

        Returns:
            Optional[RetrievalQA]: QA chain or None if failed
        """
        try:
            # Check if it's a simple vector store (fallback mode)
            if isinstance(vectorstore, SimpleVectorStore):
                logger.info("Using simple fallback QA system")
                return FallbackQAChain(vectorstore)

            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )

            # Try with OpenAI LLM first
            try:
                qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type=chain_type,
                    retriever=retriever,
                    return_source_documents=True
                )
                return qa_chain
            except Exception as openai_error:
                logger.warning(f"OpenAI LLM failed: {openai_error}")

                # Fallback to a simple text-based QA system
                logger.info("Creating fallback QA system")
                return FallbackQAChain(vectorstore)

        except Exception as e:
            logger.error(f"Error creating QA chain: {e}")
            return None

    def _create_fallback_qa_chain(self, vectorstore: FAISS):
        """
        Create a fallback QA chain that works without OpenAI API.

        Args:
            vectorstore (FAISS): Vector store

        Returns:
            FallbackQAChain: Simple QA chain
        """
        return FallbackQAChain(vectorstore)
    
    def process_transcript(self, transcript_text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process transcript text and create QA chain.
        
        Args:
            transcript_text (str): Transcript text
            metadata (Dict[str, Any]): Video metadata
            
        Returns:
            Dict[str, Any]: Processing result with QA chain and vector store
        """
        result = {
            'success': False,
            'qa_chain': None,
            'vectorstore': None,
            'documents': None,
            'error': None
        }
        
        try:
            # Create documents from transcript
            documents = self.create_documents_from_text(transcript_text, metadata)
            if not documents:
                result['error'] = "Failed to create documents from transcript"
                return result
            
            # Create vector store
            vectorstore = self.create_vector_store(documents)
            if not vectorstore:
                result['error'] = "Failed to create vector store"
                return result
            
            # Create QA chain
            qa_chain = self.create_qa_chain(vectorstore)
            if not qa_chain:
                result['error'] = "Failed to create QA chain"
                return result
            
            result['success'] = True
            result['qa_chain'] = qa_chain
            result['vectorstore'] = vectorstore
            result['documents'] = documents
            
        except Exception as e:
            result['error'] = f"Error processing transcript: {str(e)}"
            logger.error(f"Error processing transcript: {e}")
        
        return result
    
    def ask_question(self, qa_chain: RetrievalQA, question: str) -> Dict[str, Any]:
        """
        Ask a question using the QA chain.
        
        Args:
            qa_chain (RetrievalQA): QA chain
            question (str): Question to ask
            
        Returns:
            Dict[str, Any]: Answer and source documents
        """
        try:
            result = qa_chain({"query": question})
            return {
                'success': True,
                'answer': result['result'],
                'source_documents': result.get('source_documents', []),
                'error': None
            }
        except Exception as e:
            logger.error(f"Error asking question: {e}")
            return {
                'success': False,
                'answer': None,
                'source_documents': [],
                'error': f"Error processing question: {str(e)}"
            }
