"""
Agent prompt templates for the Customer Support Agent.
Handles prompt formatting, templates, and prompt management.
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain import hub
from typing import Dict, Any, List
from langchain_core.messages import BaseMessage


class AgentPrompts:
    """Manages all agent prompts and templates."""
    
    def __init__(self):
        """Initialize the prompt manager."""
        self._prompts = {}
        self._load_default_prompts()
    
    def _load_default_prompts(self):
        """Load default prompt templates."""
        # Load the ReAct prompt from LangChain Hub
        try:
            self._prompts['react_chat'] = self.create_react_prompt()
        except Exception as e:
            print(f"Warning: Could not load ReAct prompt from hub: {e}")
            self._prompts['react_chat'] = self._create_fallback_react_prompt()
        
        # Custom customer support prompt
        self._prompts['customer_support'] = self._create_customer_support_prompt()
        
        # System message prompt
        self._prompts['system'] = self._create_system_prompt()
    
    def _create_fallback_react_prompt(self) -> ChatPromptTemplate:
        """Create a fallback ReAct prompt if hub loading fails."""
        template = """You are a helpful customer support agent. Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Available tools:
{tools}

Previous conversation:
{chat_history}

Begin!

Question: {input}
Thought: {agent_scratchpad}"""
        
        return ChatPromptTemplate.from_messages([
            ("system", template)
        ])
    
    def create_react_prompt(self) -> PromptTemplate:
        """Create a fallback ReAct prompt if hub loading fails. from https://smith.langchain.com/hub/hwchase17/react-chat"""
        template = """Assistant is a large language model trained by OpenAI.

Assistant can help with many kinds of tasks — from answering quick questions to giving detailed explanations. It generates human-like text, so conversations feel natural and relevant.

It keeps improving over time, learning from more data to give better answers. You can use it to get clear explanations, useful insights, or just have a conversation.

TOOLS:
------

Assistant has access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}"""
        
        return PromptTemplate(
            input_variables=["tools", "tool_names", "chat_history", "input", "agent_scratchpad"],
            template=template
        )
    
    def _create_customer_support_prompt(self) -> ChatPromptTemplate:
        """Create a custom customer support prompt."""
        system_template = """You are a friendly and helpful customer support agent for an electronics retail company. 

Your goals:
- Provide excellent customer service
- Answer questions about products, policies, and services
- Help customers find what they need
- Use web search when you need current information
- Be professional but warm and approachable

Company Information:
- Store hours: Monday-Saturday 9 AM - 7 PM, Closed Sundays
- Return policy: 30 days for unused items in original packaging
- Warranty: 1-year limited warranty on all products
- Free shipping on orders over $50
- Customer support: (555) 123-4567, support@company.com

Available tools: {tool_names}
Tools: {tools}

Previous conversation:
{chat_history}

Current question: {input}

If you need to search for information, use the web_search tool.
Always be helpful and try to fully answer the customer's question.

{agent_scratchpad}"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_template)
        ])
    
    def _create_system_prompt(self) -> ChatPromptTemplate:
        """Create a system message prompt."""
        system_message = """You are a customer support agent. You are helpful, professional, and knowledgeable about products and services.

Key guidelines:
1. Always be polite and professional
2. Use tools when you need current information
3. Provide complete and accurate answers
4. If you don't know something, use web search or admit you don't know
5. Help customers resolve their issues effectively"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="messages")
        ])
    
    def get_prompt(self, prompt_name: str) -> ChatPromptTemplate:
        """
        Get a specific prompt template by name.
        
        Args:
            prompt_name: Name of the prompt to retrieve
            
        Returns:
            The requested prompt template
        """
        return self._prompts.get(prompt_name)
    
    def get_available_prompts(self) -> List[str]:
        """Get list of available prompt names."""
        return list(self._prompts.keys())
    
    def register_prompt(self, name: str, prompt: ChatPromptTemplate):
        """
        Register a new prompt template.
        
        Args:
            name: Name for the prompt
            prompt: The prompt template to register
        """
        self._prompts[name] = prompt
    
    def format_prompt_variables(self, 
                              messages: List[BaseMessage],
                              tools: List[Any],
                              tool_names: List[str]) -> Dict[str, Any]:
        """
        Format variables needed for prompt templates.
        
        Args:
            messages: Conversation messages
            tools: Available tools
            tool_names: Names of available tools
            
        Returns:
            Dictionary of formatted prompt variables
        """
        from agent.runnable import get_current_input, get_chat_history, get_agent_scratchpad
        
        return {
            'messages': messages,
            'tools': tools,
            'tool_names': tool_names,
            'input': get_current_input(messages),
            'chat_history': get_chat_history(messages),
            'agent_scratchpad': get_agent_scratchpad(messages)
        }


# Global prompt manager instance
_prompt_manager = AgentPrompts()


# Convenience functions
def get_agent_prompt(prompt_name: str = 'react_chat') -> ChatPromptTemplate:
    """
    Get the main agent prompt template.
    
    Args:
        prompt_name: Name of the prompt to use ('react_chat', 'customer_support', etc.)
        
    Returns:
        The requested prompt template
    """
    return _prompt_manager.get_prompt(prompt_name)


def get_system_prompt() -> ChatPromptTemplate:
    """Get the system message prompt."""
    return _prompt_manager.get_prompt('system')


def get_customer_support_prompt() -> ChatPromptTemplate:
    """Get the customer support specific prompt."""
    return _prompt_manager.get_prompt('customer_support')


def list_available_prompts() -> List[str]:
    """Get list of available prompt templates."""
    return _prompt_manager.get_available_prompts()


def register_custom_prompt(name: str, prompt: ChatPromptTemplate):
    """Register a new custom prompt template."""
    _prompt_manager.register_prompt(name, prompt)


def format_agent_variables(messages: List[BaseMessage], 
                          tools: List[Any], 
                          tool_names: List[str]) -> Dict[str, Any]:
    """Format variables for agent prompts."""
    return _prompt_manager.format_prompt_variables(messages, tools, tool_names)


# Prompt configuration
class PromptConfig:
    """Configuration for prompt behavior."""
    
    # Default prompt to use
    DEFAULT_PROMPT = 'react_chat'
    
    # Fallback to custom prompt if hub fails
    USE_FALLBACK_ON_HUB_FAILURE = True
    
    # Enable verbose prompt logging
    VERBOSE_PROMPTS = False
    
    # Maximum prompt length (for truncation if needed)
    MAX_PROMPT_LENGTH = 8000
    
    @classmethod
    def get_default_prompt_name(cls) -> str:
        """Get the default prompt name to use."""
        return cls.DEFAULT_PROMPT
    
    @classmethod
    def should_use_fallback(cls) -> bool:
        """Check if fallback should be used on hub failure."""
        return cls.USE_FALLBACK_ON_HUB_FAILURE
    
    @classmethod
    def is_verbose(cls) -> bool:
        """Check if verbose prompt logging is enabled."""
        return cls.VERBOSE_PROMPTS


# Example: How to create and register a custom prompt
def example_custom_prompt():
    """Example of how to create a custom prompt."""
    
    custom_template = """You are a specialized technical support agent for software products.

    Focus on:
    - Technical troubleshooting
    - Software installation help  
    - Bug reporting and analysis
    - Performance optimization tips
    
    Tools available: {tool_names}
    
    Customer question: {input}
    Previous conversation: {chat_history}
    
    {agent_scratchpad}"""
    
    custom_prompt = ChatPromptTemplate.from_messages([
        ("system", custom_template)
    ])
    
    register_custom_prompt("technical_support", custom_prompt)
    return custom_prompt


# For debugging/testing
if __name__ == "__main__":
    print("Agent Prompts Test")
    print("=" * 40)
    print(f"Available prompts: {list_available_prompts()}")
    
    # Test getting a prompt
    react_prompt = get_agent_prompt()
    print(f"Default prompt type: {type(react_prompt)}")
    
    # Test custom prompt registration
    example_custom_prompt()
    print(f"Prompts after adding custom: {list_available_prompts()}")