"""OnboardingAgent implementation using LangChain."""

import os
from typing import Any, Dict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from onboarding_agent.tools import (
    EntryPointTool,
    LearningPathTool,
    CoreModulesTool,
    ComplexityMapTool,
)


class OnboardingAgent:
    """The Mentor - Helps new developers navigate the codebase."""

    def __init__(self, repo_path: str, llm: Any):
        """Initialize the OnboardingAgent.

        Args:
            repo_path: Path to the repository to analyze
            llm: Language model instance (from LangChain)
        """
        self.repo_path = repo_path
        self.llm = llm

        # Initialize tools
        self.tools = {
            "suggest_entry_points": EntryPointTool(repo_path=repo_path),
            "generate_learning_path": LearningPathTool(repo_path=repo_path),
            "identify_core_modules": CoreModulesTool(repo_path=repo_path),
            "create_complexity_map": ComplexityMapTool(repo_path=repo_path),
        }

        # System prompt
        self.system_prompt = """You are the OnboardingAgent, a friendly and knowledgeable mentor who helps new developers understand and navigate codebases.

Your role:
- Help developers find the right starting points for their tasks
- Create progressive learning paths from simple to complex
- Identify core modules that are critical to understand
- Show complexity maps to guide learning journey

Your personality:
- Friendly and encouraging
- Patient and clear in explanations
- Practical and actionable in advice
- Supportive of learning at any pace

When a developer asks you a question:
1. Understand what they're trying to accomplish
2. Use your tools to analyze the codebase
3. Provide clear, structured guidance
4. Include specific file paths and reasons
5. Encourage them with helpful tips

Available tools:
- suggest_entry_points(task_description): Find where to start for a specific task
- generate_learning_path(area): Create a learning path for an area (simple → complex)
- identify_core_modules(): Find the most important modules to understand
- create_complexity_map(): Show which parts are simple vs complex

Always provide actionable advice with specific file paths and clear reasoning."""

    def _use_tool(self, tool_name: str, query: str = "") -> str:
        """Use a specific tool.

        Args:
            tool_name: Name of the tool to use
            query: Query/input for the tool

        Returns:
            Tool output
        """
        if tool_name not in self.tools:
            return f"Tool {tool_name} not found"

        try:
            return self.tools[tool_name]._run(query)
        except Exception as e:
            return f"Error using tool {tool_name}: {str(e)}"

    def chat(self, message: str, chat_history: List[tuple] = None) -> Dict[str, Any]:
        """Send a message to the agent and get a response.

        Args:
            message: User message
            chat_history: Optional chat history as list of (human, ai) tuples

        Returns:
            Dictionary with response and metadata
        """
        # Check if user is asking for a specific analysis
        message_lower = message.lower()

        try:
            # Determine which tool to use based on the message
            tool_output = None

            if any(word in message_lower for word in ["entry point", "where", "start", "begin"]):
                tool_output = self._use_tool("suggest_entry_points", message)
            elif any(word in message_lower for word in ["learning path", "learn", "understand"]):
                # Extract the area from the message
                area = message.replace("learning path", "").replace("learn", "").strip()
                tool_output = self._use_tool("generate_learning_path", area)
            elif any(word in message_lower for word in ["core module", "important", "critical"]):
                tool_output = self._use_tool("identify_core_modules", "")
            elif any(word in message_lower for word in ["complexity", "simple", "complex", "difficult"]):
                tool_output = self._use_tool("create_complexity_map", "")

            # If we have tool output, return it
            if tool_output:
                return {
                    "output": tool_output,
                    "success": True,
                    "error": None,
                }

            # Otherwise, use the LLM to respond
            messages = [SystemMessage(content=self.system_prompt)]

            # Add chat history
            if chat_history:
                for human_msg, ai_msg in chat_history:
                    messages.append(HumanMessage(content=human_msg))
                    messages.append(AIMessage(content=ai_msg))

            # Add current message
            messages.append(HumanMessage(content=message))

            # Get LLM response
            response = self.llm.invoke(messages)

            return {
                "output": response.content,
                "success": True,
                "error": None,
            }

        except Exception as e:
            return {
                "output": f"I encountered an error: {str(e)}",
                "success": False,
                "error": str(e),
            }

    def quick_analysis(self) -> Dict[str, str]:
        """Perform a quick analysis of the codebase.

        Returns:
            Dictionary with analysis results
        """
        results = {}

        # Get core modules
        core_tool = CoreModulesTool(repo_path=self.repo_path)
        results["core_modules"] = core_tool._run("")

        # Get complexity map
        complexity_tool = ComplexityMapTool(repo_path=self.repo_path)
        results["complexity_map"] = complexity_tool._run("")

        return results
