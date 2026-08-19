
BASE_SYSTEM_PROMPT = """You are R.I.A.N., an intelligent, sharp, and adaptive AI collaborator.
- Voice & Tone: Highly conversational, grounded, witty, and concise. Avoid robotic fluff or generic filler phrases.
- Language: Naturally match the user's language. Use smooth, authentic Hinglish (blend of Hindi and English) if the user speaks Hindi/Hinglish, or crisp English if spoken to in English.
- Output Format: Keep verbal answers clean, natural to speak out loud, and free of unnecessary markdown symbols, code blocks, or robotic templates."""

import logging
import operator
import json
import re
import ast
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage, AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

from agents.verifier_node import code_verifier

logger = logging.getLogger(__name__)

class GraphState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

def build_agent_graph(llm: ChatGroq, tools: list[BaseTool], system_prompt: str = BASE_SYSTEM_PROMPT) -> StateGraph:
    llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)
    
    def agent_node(state: GraphState) -> GraphState:
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        
        if len(state["messages"]) > 0 and isinstance(state["messages"][-1], ToolMessage):
            logger.debug("Tool result received, forcing AI to speak answer...")
            try:
                response = llm.invoke(messages)
                return {"messages": [response]}
            except Exception as e:
                logger.error(f"Error synthesizing final response: {e}")
                return {"messages": [AIMessage(content="Task complete, but I had trouble formatting the response.")]}
        
        try:
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}
        except Exception as e:
            error_str = str(e)
            if "failed_generation" in error_str and "<function=" in error_str:
                logger.warning("Caught Groq API 400 error. Hijacking the failed generation string...")
                match = re.search(r'(<function=[^>]*>.*?</function>|<function=[^>]*>)', error_str)
                if match:
                    raw_call = match.group(1)
                    mock_msg = AIMessage(content=raw_call)
                    return {"messages": [mock_msg]}
            
            return {"messages": [AIMessage(content=f"API Error: {error_str}")]}
    
    def action_node(state: GraphState) -> GraphState:
        last_message = state["messages"][-1]
        tool_calls = getattr(last_message, "tool_calls", [])
        
        tool_map = {tool.name: tool for tool in tools}
        tool_results = []
        
        # 🚨 THE BULLETPROOF RECOVERY PARSER 🚨
        content_str = str(getattr(last_message, "content", ""))
        if not tool_calls and "<function=" in content_str:
            logger.warning(f"Extracting tools from raw text: {content_str}")
            
            name_match = re.search(r'<function=([a-zA-Z0-9_]+)', content_str)
            t_name = name_match.group(1) if name_match else "unknown_tool"
            
            start_idx = content_str.find('{')
            end_idx = content_str.rfind('}')
            
            t_args = {}
            if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                json_str = content_str[start_idx:end_idx+1]
                json_str = re.sub(r'\}\}+$', '}', json_str)
                
                try:
                    t_args = json.loads(json_str, strict=False)
                except Exception as parse_err:
                    logger.warning("JSON parsing failed. Engaging BRUTE FORCE Parser...")
                    # 🚨 BRUTE FORCE EXTRACTION 🚨
                    try:
                        tn = re.search(r'"tool_name"\s*:\s*"([^"]+)"', content_str).group(1)
                        desc = re.search(r'"description"\s*:\s*"([^"]+)"', content_str).group(1)
                        
                        code_marker = '"python_code":'
                        c_idx = content_str.find(code_marker)
                        if c_idx != -1:
                            raw_code = content_str[c_idx + len(code_marker):].strip()
                            if raw_code.startswith('"'):
                                raw_code = raw_code[1:]
                            # Strip the trailing closing tags and braces
                            raw_code = re.sub(r'"\s*\}\}?\s*(?:</function>)?\s*$', '', raw_code)
                            t_args = {"tool_name": tn, "description": desc, "python_code": raw_code}
                    except Exception as brute_err:
                        logger.error(f"Brute force failed: {brute_err}")
                        t_args = {}
            
            if isinstance(t_args, dict) and t_args:
                tool_calls = [{"name": t_name, "args": t_args, "id": "groq_hijack_id"}]
            else:
                logger.error("Failed to build valid tool arguments structure.")

        if not tool_calls:
            return {"messages": [ToolMessage(content="Tool execution skipped due to parsing error.", tool_call_id="failed_id", name="parser")]}
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool_call_id = tool_call.get("id", "tool_id")
            
            try:
                if tool_name in tool_map:
                    tool = tool_map[tool_name]
                    result = tool.invoke(tool_args)
                    logger.info(f"Tool {tool_name} executed successfully.")
                    tool_message = ToolMessage(content=str(result), tool_call_id=tool_call_id, name=tool_name)
                    tool_results.append(tool_message)
                else:
                    raise KeyError(f"Tool '{tool_name}' not configured in R.I.A.N.")
            except Exception as e:
                logger.error(f"Tool {tool_name} failed: {e}")
                error_message = ToolMessage(content=f"Tool execution failed: {str(e)}", tool_call_id=tool_call_id, name=tool_name)
                tool_results.append(error_message)
                
        return {"messages": tool_results}
    
    def route_after_agent(state: GraphState) -> str:
        last_state_msg = state["messages"][-1]
        if isinstance(last_state_msg, AIMessage):
            if (hasattr(last_state_msg, "tool_calls") and last_state_msg.tool_calls) or ("<function=" in str(last_state_msg.content)):
                return "action"
            elif "```python" in str(last_state_msg.content):
                return "verifier"
        return END

    def route_after_verifier(state: GraphState) -> str:
        last_state_msg = state["messages"][-1]
        if isinstance(last_state_msg, HumanMessage) and "VERIFICATION FAILED" in str(last_state_msg.content):
            logger.warning("Code check failed! Sending back to RIAN to fix...")
            return "agent"
        return END
    
    # --- Graph Architecture ---
    workflow = StateGraph(GraphState)
    
    workflow.add_node("agent", agent_node)
    workflow.add_node("action", action_node)
    workflow.add_node("verifier", code_verifier)
    
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges("agent", route_after_agent)
    workflow.add_conditional_edges("verifier", route_after_verifier)
    workflow.add_edge("action", "agent")
    
    app = workflow.compile()
    logger.info("Agent graph compiled with Multi-Agent Verifier & Groq Error Hijacker.")
    return app