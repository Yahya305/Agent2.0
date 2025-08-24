from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import numpy as np
from sentence_transformers import SentenceTransformer
from utils.database import getDBConnection
from utils.logger import logger
import json

class StoreMemoryInput(BaseModel):
    """Input schema for storing memory"""
    input_data: str = Field(description="JSON string containing: content, user_id, and optional importance")


class RetrieveMemoryInput(BaseModel):
    """Input schema for retrieving memory"""
    input_data: str = Field(description="JSON string containing: query, user_id, optional top_k, and optional similarity_threshold")
    # query: str = Field(description="Search query to find relevant memories")
    # user_id: str = Field(description="User ID to search memories for")
    # top_k: int = Field(default=3, description="Number of top results to return")
    # similarity_threshold: float = Field(default=0.7, description="Minimum similarity threshold")


class UpdateMemoryInput(BaseModel):
    """Input schema for updating memory"""
    memory_id: int = Field(description="ID of the memory to update")
    new_content: str = Field(description="New content to replace the existing memory")
    user_id: str = Field(description="User ID who owns this memory")



class SemanticMemoryTools:
    def __init__(self):
        """
        Initialize semantic memory tools with Nomic embedding model
        
        Args:
            db_connection: PostgreSQL connection with pgvector
        """
        self.db_connection = getDBConnection()
        
        # Load Nomic embedding model (768 dimensions, high quality)
        logger.debug("Loading Nomic embedding model...")
        self.embedding_model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
        logger.debug("Nomic model loaded successfully!")
        
        
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
            logger.debug(f"Error getting embedding: {e}")
            return [0.0] * 768  # Nomic is 768 dimensions
        
    def _validate_store_memory_input(self, input_data: str) -> tuple[dict, str]:
        """
        Validate store memory input and return parsed data or error message
        
        Returns:
            tuple: (parsed_data_dict, error_message)
            If error_message is empty, parsed_data_dict contains valid data
        """
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            return {}, "ERROR: Invalid JSON format. Please provide input as: {\"content\": \"your text\", \"user_id\": \"user_id\", \"importance\": \"medium\"}"

        # Validate required fields
        if "content" not in data:
            return {}, "ERROR: Missing required field 'content'. Please provide: {\"content\": \"your text\", \"user_id\": \"user_id\"}"
        
        if "user_id" not in data:
            return {}, "ERROR: Missing required field 'user_id'. Please provide: {\"content\": \"your text\", \"user_id\": \"user_id\"}"
        
        # Extract and validate fields
        content = data["content"]
        user_id = data["user_id"]
        importance = data.get("importance", "medium")
        
        # Validate importance level
        if importance not in ["low", "medium", "high"]:
            return {}, "ERROR: Invalid importance level. Must be 'low', 'medium', or 'high'"
        
        # Validate content is not empty
        if not content.strip():
            return {}, "ERROR: Content cannot be empty"
        
        # Validate user_id is not empty
        if not user_id.strip():
            return {}, "ERROR: User ID cannot be empty"
        
        return {
            "content": content.strip(),
            "user_id": user_id.strip(),
            "importance": importance
        }, ""
    
    def _validate_retrieve_memory_input(self, input_data: str) -> tuple[dict, str]:
        """
        Validate retrieve memory input and return parsed data or error message
        
        Returns:
            tuple: (parsed_data_dict, error_message)
            If error_message is empty, parsed_data_dict contains valid data
        """
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            return {}, "ERROR: Invalid JSON format. Please provide input as: {\"query\": \"search text\", \"user_id\": \"user_id\"}"

        
        # Validate required fields
        if "query" not in data:
            return {}, "ERROR: Missing required field 'query'. Please provide: {\"query\": \"search text\", \"user_id\": \"user_id\"}"
        
        if "user_id" not in data:
            return {}, "ERROR: Missing required field 'user_id'. Please provide: {\"query\": \"search text\", \"user_id\": \"user_id\"}"
        
        # Extract and validate fields
        query = data["query"]
        user_id = data["user_id"]
        top_k = data.get("top_k", 3)
        similarity_threshold = data.get("similarity_threshold", 0.7)
        
        # Validate query is not empty
        if not str(query).strip():
            return {}, "ERROR: Query cannot be empty"
        
        # Validate user_id is not empty
        if not str(user_id).strip():
            return {}, "ERROR: User ID cannot be empty"
        
        # Validate top_k is positive integer
        try:
            top_k = int(top_k)
            if top_k <= 0:
                return {}, "ERROR: top_k must be a positive integer"
        except (ValueError, TypeError):
            return {}, "ERROR: top_k must be a valid integer"
        
        # Validate similarity_threshold is between 0 and 1
        try:
            similarity_threshold = float(similarity_threshold)
            if not 0.0 <= similarity_threshold <= 1.0:
                return {}, "ERROR: similarity_threshold must be between 0.0 and 1.0"
        except (ValueError, TypeError):
            return {}, "ERROR: similarity_threshold must be a valid number"
        
        return {
            "query": str(query).strip(),
            "user_id": str(user_id).strip(),
            "top_k": top_k,
            "similarity_threshold": similarity_threshold
        }, ""

    def _validate_update_memory_input(self, input_data: dict) -> tuple[dict, str]:
        """
        Validate update memory input and return parsed data or error message
        
        Returns:
            tuple: (parsed_data_dict, error_message)
            If error_message is empty, parsed_data_dict contains valid data
        """
        data = input_data
        
        # Validate required fields
        if "memory_id" not in data:
            return {}, "ERROR: Missing required field 'memory_id'. Please provide: {\"memory_id\": 123, \"new_content\": \"text\", \"user_id\": \"user_id\"}"
        
        if "new_content" not in data:
            return {}, "ERROR: Missing required field 'new_content'. Please provide: {\"memory_id\": 123, \"new_content\": \"text\", \"user_id\": \"user_id\"}"
        
        if "user_id" not in data:
            return {}, "ERROR: Missing required field 'user_id'. Please provide: {\"memory_id\": 123, \"new_content\": \"text\", \"user_id\": \"user_id\"}"
        
        # Extract and validate fields
        memory_id = data["memory_id"]
        new_content = data["new_content"]
        user_id = data["user_id"]
        
        # Validate memory_id is positive integer
        try:
            memory_id = int(memory_id)
            if memory_id <= 0:
                return {}, "ERROR: memory_id must be a positive integer"
        except (ValueError, TypeError):
            return {}, "ERROR: memory_id must be a valid integer"
        
        # Validate new_content is not empty
        if not str(new_content).strip():
            return {}, "ERROR: New content cannot be empty"
        
        # Validate user_id is not empty
        if not str(user_id).strip():
            return {}, "ERROR: User ID cannot be empty"
        
        return {
            "memory_id": memory_id,
            "new_content": str(new_content).strip(),
            "user_id": str(user_id).strip()
        }, ""
    
    def create_store_memory_tool(self) -> BaseTool:
        """Create tool for storing memories"""
        
        # Capture self in closure
        memory_tools = self
        
        class StoreMemoryTool(BaseTool):
            name: str = "store_memory"
            description: str = """Store important information in long-term semantic memory. 
            
            Input format: Provide a JSON string with these fields:
            {
                "content": "The important information to store",
                "user_id": "User identifier",
                "importance": "low|medium|high (optional, defaults to medium)"
            }
            
            Example: {"content": "User prefers coffee over tea", "user_id": "john123", "importance": "medium"}
            
            Use for storing:
            - User preferences and personal details
            - Important facts or decisions
            - Recurring topics or patterns
            - Context valuable for future conversations"""
            args_schema: type[BaseModel] = StoreMemoryInput
            
            def _run(self, input_data: str) -> str:

                # Validate input using separate validation function
                parsed_data, error_msg = memory_tools._validate_store_memory_input(input_data)
                if error_msg:
                    return error_msg
                
                try:
                    embedding = memory_tools.get_embedding(parsed_data["content"], is_query=False)
                    
                    with memory_tools.db_connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO semantic_memories (user_id, content, embedding, importance)
                            VALUES (%s, %s, %s, %s)
                            RETURNING id
                        """, (parsed_data["user_id"], parsed_data["content"], embedding, parsed_data["importance"]))
                        
                        memory_id = cursor.fetchone()['id']
                        memory_tools.db_connection.commit()
                        
                    return f"Memory stored successfully with ID {memory_id}. Content: '{parsed_data['content'][:100]}...'"
                    
                except Exception as e:
                    logger.debug(f"Error storing memory: {str(e)}")
                    return f"Error storing memory: {str(e)}"
        
        return StoreMemoryTool()
    
    def create_retrieve_memory_tool(self) -> BaseTool:
        """Create tool for retrieving similar memories"""
        
        # Capture self in closure
        memory_tools = self
        
        class RetrieveMemoryTool(BaseTool):
            name: str = "retrieve_memory"
            description: str = """Search and retrieve relevant information from long-term semantic memory.
            
            Parameters:
            - query (str): Search query to find relevant memories
            - user_id (str): User ID to search memories for
            - top_k (int, optional): Number of top results to return (default: 3)
            - similarity_threshold (float, optional): Minimum similarity threshold 0.0-1.0 (default: 0.7)

            Example: {"query": "search text", "user_id": "user_id", "top_k":"2", "similarity_threshold":"0.8"}
            
            Use when:
            - You need context about the user's preferences or history
            - The conversation touches on topics discussed before
            - You want to check if you have relevant stored information
            - Building upon previous conversations or decisions"""
            args_schema: type[BaseModel] = RetrieveMemoryInput
            
            def _run(self, input_data: str) -> str:

                # Validate input using separate validation function
                parsed_data, error_msg = memory_tools._validate_retrieve_memory_input(input_data)
                if error_msg:
                    return error_msg
                

                try:
                    query_embedding = memory_tools.get_embedding(parsed_data["query"], is_query=True)
                    
                    with memory_tools.db_connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT 
                                id,
                                content,
                                importance,
                                created_at,
                                1 - (embedding <=> %s::vector) as similarity
                            FROM semantic_memories
                            WHERE user_id = %s
                            AND 1 - (embedding <=> %s::vector) > %s
                            ORDER BY similarity DESC
                            LIMIT %s
                        """, (query_embedding, parsed_data["user_id"], query_embedding, parsed_data["similarity_threshold"], parsed_data["top_k"]))
                        
                        results = cursor.fetchall()
                    
                    if not results:
                        logger.debug(f"No relevant memories found for query: {parsed_data['query']}")
                        return f"No relevant memories found for query: {parsed_data['query']}"
                    
                    formatted_results = "Retrieved memories:\n"
                    for i, row in enumerate(results, 1):
                        formatted_results += f"{i}. [ID: {row['id']}, Similarity: {round(row['similarity'], 3)}, {row['importance']} importance]\n"
                        formatted_results += f"   Content: {row['content']}\n"
                        formatted_results += f"   Stored: {row['created_at'].strftime('%Y-%m-%d %H:%M')}\n\n"
                    
                    logger.debug("----------------",formatted_results,"--------------")
                    return formatted_results
                    
                except Exception as e:
                    logger.debug(f"Error retrieving memories: {str(e)}")
                    return f"Error retrieving memories: {str(e)}"
        
        return RetrieveMemoryTool()

    def create_update_memory_tool(self) -> BaseTool:
        """Create tool for updating existing memories"""
        
        # Capture self in closure
        memory_tools = self
        
        class UpdateMemoryTool(BaseTool):
            name: str = "update_memory"
            description: str = """Update an existing memory with new information.
            
            Parameters:
            - memory_id (int): ID of the memory to update (get this from retrieve_memory results)
            - new_content (str): New content to replace the existing memory
            - user_id (str): User ID who owns this memory
            
            Use this when you need to modify or correct previously stored information.
            Always retrieve memories first to get the correct memory_id."""
            args_schema: type[BaseModel] = UpdateMemoryInput
            
            def _run(self, memory_id: int, new_content: str, user_id: str) -> str:
                try:
                    new_embedding = memory_tools.get_embedding(new_content, is_query=False)
                    
                    with memory_tools.db_connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE semantic_memories 
                            SET content = %s, embedding = %s, created_at = NOW()
                            WHERE id = %s AND user_id = %s
                            RETURNING id
                        """, (new_content, new_embedding, memory_id, user_id))
                        
                        result = cursor.fetchone()
                        memory_tools.db_connection.commit()
                        
                        if result:
                            return f"Memory {memory_id} updated successfully with new content: '{new_content[:100]}...'"
                        else:
                            return f"Memory {memory_id} not found or access denied"
                    
                except Exception as e:
                    return f"Error updating memory: {str(e)}"
        
        return UpdateMemoryTool()

def create_memory_tools() -> List[BaseTool]:
    """
    Create all memory tools for the agent using Nomic embeddings
    
    Args:
        db_connection: PostgreSQL connection with pgvector
        
    Returns:
        List of memory tools: [store_memory, retrieve_memory, update_memory]
    """
    memory_tools = SemanticMemoryTools()
    
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