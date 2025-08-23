from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import numpy as np
from sentence_transformers import SentenceTransformer
from utils.database import getDBConnection
import json

class StoreMemoryInput(BaseModel):
    """Input for store_memory tool"""
    content: str = Field(description="The important information to store in long-term memory")
    user_id: str = Field(description="User identifier for this memory")
    importance: str = Field(description="Importance level: 'high', 'medium', or 'low'", default="medium")

class RetrieveMemoryInput(BaseModel):
    """Input for retrieve_memory tool"""
    query: str = Field(description="What to search for in long-term memory")
    user_id: str = Field(description="User identifier to search memories for")
    top_k: int = Field(description="Number of similar memories to retrieve", default=3)
    similarity_threshold: float = Field(description="Minimum similarity score (0-1)", default=0.7)

class UpdateMemoryInput(BaseModel):
    """Input for update_memory tool"""
    memory_id: int = Field(description="ID of the memory to update")
    new_content: str = Field(description="Updated content for the memory")
    user_id: str = Field(description="User identifier for verification")

class SemanticMemoryTools:
    def __init__(self):
        """
        Initialize semantic memory tools with Nomic embedding model
        
        Args:
            db_connection: PostgreSQL connection with pgvector
        """
        self.db_connection = getDBConnection()
        
        # Load Nomic embedding model (768 dimensions, high quality)
        print("Loading Nomic embedding model...")
        self.embedding_model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
        print("Nomic model loaded successfully!")
        
        # Ensure database schema is correct for 768D embeddings
        self._setup_schema()
        
    def _setup_schema(self):
        """Setup database schema for 768D embeddings"""
        try:
            with self.db_connection.cursor() as cursor:
                # Create table with correct dimension (768 for Nomic)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS semantic_memories (
                        id SERIAL PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        content TEXT NOT NULL,
                        embedding vector(768),
                        importance TEXT DEFAULT 'medium',
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Create index for fast similarity search
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_semantic_memories_embedding
                    ON semantic_memories
                    USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100);
                """)
                
                print("Database schema ready for semantic memories")
                
        except Exception as e:
            print(f"Warning: Could not setup schema: {e}")
        
    def get_embedding(self, text: str, is_query: bool = False) -> List[float]:
        """
        Get embedding using Nomic model with appropriate prefixes
        
        Args:
            text: Text to embed
            is_query: If True, adds search_query prefix; else search_document prefix
        """
        try:
            # Add Nomic-specific prefixes for better performance
            if is_query:
                text = f"search_query: {text}"
            else:
                text = f"search_document: {text}"
            
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return [0.0] * 768  # Nomic is 768 dimensions
    
    def create_store_memory_tool(self) -> BaseTool:
        """Create tool for storing memories"""
        
        class StoreMemoryTool(BaseTool):
            name = "store_memory"
            description = """Store important information in long-term semantic memory. 
            Use this when you encounter information that should be remembered for future conversations, such as:
            - User preferences and personal details
            - Important facts or decisions
            - Recurring topics or patterns
            - Context that will be valuable later
            
            Only store information that is genuinely important for future interactions."""
            args_schema = StoreMemoryInput
            
            def _run(self, content: str, user_id: str, importance: str = "medium") -> str:
                try:
                    embedding = self.get_embedding(content, is_query=False)
                    
                    with self.db_connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO semantic_memories (user_id, content, embedding, importance)
                            VALUES (%s, %s, %s, %s)
                            RETURNING id
                        """, (user_id, content, embedding, importance))
                        
                        memory_id = cursor.fetchone()['id']
                        
                    return f"Memory stored successfully with ID {memory_id}. Content: '{content[:100]}...'"
                    
                except Exception as e:
                    return f"Error storing memory: {str(e)}"
        
        tool = StoreMemoryTool()
        tool.get_embedding = self.get_embedding
        tool.db_connection = self.db_connection
        return tool
    
    def create_retrieve_memory_tool(self) -> BaseTool:
        """Create tool for retrieving similar memories"""
        
        class RetrieveMemoryTool(BaseTool):
            name = "retrieve_memory"
            description = """Search and retrieve relevant information from long-term semantic memory.
            Use this when:
            - You need context about the user's preferences or history
            - The conversation touches on topics discussed before
            - You want to check if you have relevant stored information
            - Building upon previous conversations or decisions
            
            This performs semantic similarity search to find the most relevant stored memories."""
            args_schema = RetrieveMemoryInput
            
            def _run(self, query: str, user_id: str, top_k: int = 3, similarity_threshold: float = 0.7) -> str:
                try:
                    query_embedding = self.get_embedding(query, is_query=True)
                    
                    with self.db_connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT 
                                id,
                                content,
                                importance,
                                created_at,
                                1 - (embedding <=> %s) as similarity
                            FROM semantic_memories
                            WHERE user_id = %s
                              AND 1 - (embedding <=> %s) > %s
                            ORDER BY similarity DESC
                            LIMIT %s
                        """, (query_embedding, user_id, query_embedding, similarity_threshold, top_k))
                        
                        results = cursor.fetchall()
                    
                    if not results:
                        return f"No relevant memories found for query: '{query}'"
                    
                    formatted_results = "Retrieved memories:\n"
                    for i, row in enumerate(results, 1):
                        formatted_results += f"{i}. [ID: {row['id']}, Similarity: {round(row['similarity'], 3)}, {row['importance']} importance]\n"
                        formatted_results += f"   Content: {row['content']}\n"
                        formatted_results += f"   Stored: {row['created_at'].strftime('%Y-%m-%d %H:%M')}\n\n"
                    
                    return formatted_results
                    
                except Exception as e:
                    return f"Error retrieving memories: {str(e)}"
        
        tool = RetrieveMemoryTool()
        tool.get_embedding = self.get_embedding
        tool.db_connection = self.db_connection
        return tool
    
    def create_update_memory_tool(self) -> BaseTool:
        """Create tool for updating existing memories"""
        
        class UpdateMemoryTool(BaseTool):
            name = "update_memory"
            description = """Update an existing memory with new information.
            Use this when you need to modify or correct previously stored information.
            You need the memory ID from a previous retrieve_memory call."""
            args_schema = UpdateMemoryInput
            
            def _run(self, memory_id: int, new_content: str, user_id: str) -> str:
                try:
                    new_embedding = self.get_embedding(new_content, is_query=False)
                    
                    with self.db_connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE semantic_memories 
                            SET content = %s, embedding = %s, created_at = NOW()
                            WHERE id = %s AND user_id = %s
                            RETURNING id
                        """, (new_content, new_embedding, memory_id, user_id))
                        
                        result = cursor.fetchone()
                        
                        if result:
                            return f"Memory {memory_id} updated successfully with new content: '{new_content[:100]}...'"
                        else:
                            return f"Memory {memory_id} not found or access denied"
                    
                except Exception as e:
                    return f"Error updating memory: {str(e)}"
        
        tool = UpdateMemoryTool()
        tool.get_embedding = self.get_embedding
        tool.db_connection = self.db_connection
        return tool

def create_memory_tools() -> List[BaseTool]:
    """
    Create all memory tools for the agent using Nomic embeddings
    
    Args:
        db_connection: PostgreSQL connection with pgvector
        
    Returns:
        List of memory tools: [store_memory, retrieve_memory, update_memory]
    """
    memory_tools = SemanticMemoryTools(getDBConnection())
    
    return [
        memory_tools.create_store_memory_tool(),
        memory_tools.create_retrieve_memory_tool(),
        memory_tools.create_update_memory_tool()
    ]

# Simple integration:
"""
# In your agent setup:
db_conn = initialize_database()
memory_tools = create_memory_tools(db_conn)

# Add to your existing tools
all_tools = your_existing_tools + memory_tools
"""