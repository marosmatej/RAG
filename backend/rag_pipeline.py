from typing import List, Dict, Optional, Any
import requests
from config import settings


class RAGPipeline:
    """Handles retrieval-augmented generation pipeline"""
    
    def __init__(self, vector_store):
        """
        Initialize RAG pipeline
        
        Args:
            vector_store: VectorStore instance for retrieval
        """
        self.vector_store = vector_store
        self.llm_provider = settings.llm_provider
    
    def generate_answer(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Generate answer using RAG pipeline
        
        Args:
            question: User's question
            top_k: Number of document chunks to retrieve
            
        Returns:
            Dictionary with answer and sources
        """
        # Step 1: Retrieve relevant documents
        retrieved_docs = self.vector_store.search(question, top_k=top_k)
        
        if not retrieved_docs:
            return {
                'answer': "I don't have any documents to answer this question. Please upload some documents first.",
                'sources': []
            }
        
        # Step 2: Prepare context from retrieved documents
        context = self._prepare_context(retrieved_docs)
        
        # Step 3: Generate answer using LLM
        answer = self._generate_with_llm(question, context)
        
        # Step 4: Format sources
        sources = [
            {
                'text': doc['text'][:200] + '...' if len(doc['text']) > 200 else doc['text'],
                'filename': doc['metadata']['filename'],
                'chunk_id': doc['metadata']['chunk_id']
            }
            for doc in retrieved_docs
        ]
        
        return {
            'answer': answer,
            'sources': sources
        }
    
    def _prepare_context(self, retrieved_docs: List[Dict]) -> str:
        """
        Prepare context string from retrieved documents
        
        Args:
            retrieved_docs: List of retrieved document chunks
            
        Returns:
            Formatted context string
        """
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"[Source {i} from {doc['metadata']['filename']}]:\n{doc['text']}")
        
        return "\n\n".join(context_parts)
    
    def _generate_with_llm(self, question: str, context: str) -> str:
        """
        Generate answer using configured LLM
        
        Args:
            question: User's question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        # Create prompt
        prompt = self._create_prompt(question, context)
        
        if self.llm_provider == "ollama":
            return self._generate_with_ollama(prompt)
        elif self.llm_provider == "openai":
            return self._generate_with_openai(question, context)
        elif self.llm_provider == "groq":
            return self._generate_with_groq(question, context)
        else:
            return "LLM provider not configured correctly."
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create prompt for LLM"""
        return f"""You are a helpful assistant. Answer the question based on the provided context.

Context:
{context}

Question: {question}

Answer: Provide a clear and concise answer based solely on the context provided. If the context doesn't contain relevant information, say so."""
    
    def _generate_with_ollama(self, prompt: str) -> str:
        """
        Generate answer using Ollama
        
        Args:
            prompt: Complete prompt with context and question
            
        Returns:
            Generated answer
        """
        try:
            response = requests.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()['response']
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {str(e)}. Make sure Ollama is running."
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def _generate_with_openai(self, question: str, context: str) -> str:
        """
        Generate answer using OpenAI
        
        Args:
            question: User's question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=settings.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Answer questions based on the provided context."
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {question}"
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating answer with OpenAI: {str(e)}"
    
    def _generate_with_groq(self, question: str, context: str) -> str:
        """
        Generate answer using Groq (fast and free!)
        
        Args:
            question: User's question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        try:
            from openai import OpenAI
            
            # Groq uses OpenAI-compatible API
            client = OpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            
            response = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Answer questions based on the provided context. Be concise and accurate."
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {question}"
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating answer with Groq: {str(e)}"
