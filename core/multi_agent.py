from core.local_llm import local_llm
from core.code_sandbox import sandbox

class AgentRole:
    RESEARCHER = "You are an expert technical researcher. Analyze tasks deeply, identify key constraints, and provide structured solutions."
    CODER = "You are a professional software engineer. Write clean, production-grade, bug-free Python code without conversational filler."
    DEBUGGER = "You are an expert debugger. Analyze execution errors, trace logs, and provide immediate fixes."

class MultiAgentOrchestrator:
    def __init__(self):
        pass

    def run_research(self, query: str) -> str:
        prompt = f"Research and break down the steps to solve this problem:\n{query}"
        return local_llm.generate_response(prompt=prompt, system_prompt=AgentRole.RESEARCHER)

    def run_coding_task(self, requirement: str) -> dict:
        # Step 1: Researcher analyzes
        plan = self.run_research(requirement)
        
        # Step 2: Coder writes code
        code_prompt = f"Requirement: {requirement}\nResearch Plan: {plan}\nWrite ONLY executable Python code:"
        code_generated = local_llm.generate_response(prompt=code_prompt, system_prompt=AgentRole.CODER)
        
        # Strip markdown formatting if any
        clean_code = code_generated.replace("```python", "").replace("```", "").strip()
        
        # Step 3: Sandbox executes code
        execution_result = sandbox.execute_python(clean_code)
        
        # Step 4: Debugger fixes if failed
        if execution_result.get("exit_code") != 0 or execution_result.get("stderr"):
            debug_prompt = f"Code:\n{clean_code}\nError Log:\n{execution_result.get('stderr')}\nFix the code:"
            fixed_code = local_llm.generate_response(prompt=debug_prompt, system_prompt=AgentRole.DEBUGGER)
            clean_fixed = fixed_code.replace("```python", "").replace("```", "").strip()
            execution_result = sandbox.execute_python(clean_fixed)
            return {"plan": plan, "code": clean_fixed, "execution": execution_result, "debugged": True}

        return {"plan": plan, "code": clean_code, "execution": execution_result, "debugged": False}

orchestrator = MultiAgentOrchestrator()
