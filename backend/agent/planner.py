import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List
from backend.mcp.dispatcher import dispatch_tool_call
from backend.agent.reducer import SafeReducer

class AgentPlanner:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers

    def plan_and_execute(
        self,
        supplier_id: str,
        question: str,
        jwt_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determines tools needed for supplier risk inquiry and executes them concurrently.
        """
        # For exposure/risk analysis, dispatch all 4 tools
        tool_tasks = [
            ("get_supplier_balance", {"supplier_id": supplier_id}, "v1"),
            ("get_alternate_sources", {"supplier_id": supplier_id}, "v1"),
            ("get_payment_history", {"supplier_id": supplier_id}, "v1"),
            (
                "search_contract_corpus",
                {"query": f"insolvency liability termination supplier {supplier_id}", "k": 3, "supplier_id": supplier_id},
                "v1"
            )
        ]

        reducer = SafeReducer()
        execution_trace = []
        start_time = time.time()

        def worker(tool_name, inputs, version):
            t_start = time.time()
            res = dispatch_tool_call(
                tool_name=tool_name,
                inputs=inputs,
                jwt_payload=jwt_payload,
                version=version,
                actor="agent-planner"
            )
            t_duration = round((time.time() - t_start) * 1000, 2)
            return tool_name, res, t_duration

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(worker, tool_name, inputs, version)
                for tool_name, inputs, version in tool_tasks
            ]

            for future in as_completed(futures):
                tool_name, res, duration_ms = future.result()
                reducer.add_result(tool_name, res["result"])
                execution_trace.append({
                    "tool": tool_name,
                    "version": res["version"],
                    "status": "SUCCESS" if res["success"] else "FAILED",
                    "execution_ms": duration_ms,
                    "audit_seq": res["audit_seq"]
                })

        total_time_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "supplier_id": supplier_id,
            "question": question,
            "tool_results": reducer.get_aggregated_results(),
            "execution_trace": execution_trace,
            "total_execution_ms": total_time_ms
        }
