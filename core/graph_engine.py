"""SPEACE Core — Typed Adaptive Computational Graph on NetworkX."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable

import networkx as nx

from core.contracts import ExecutionContract, NodeContract


@dataclass
class SPEACENode:
    """A typed computational node in the adaptive graph."""
    name: str
    func: Callable
    contract: NodeContract = field(default_factory=NodeContract)
    execution_contract: ExecutionContract = field(default_factory=ExecutionContract)
    metadata: dict[str, Any] = field(default_factory=dict)
    state: str = "idle"
    last_execution_time: float = 0.0
    performance_score: float = 0.5
    failure_count: int = 0
    total_executions: int = 0

    async def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Execute the node's function with input validation and performance tracking."""
        start = time.time()

        # Type validation
        for key, typ in self.contract.input_types.items():
            if key in inputs and not isinstance(inputs[key], typ):
                raise TypeError(
                    f"Node '{self.name}': input '{key}' expected {typ.__name__}, "
                    f"got {type(inputs[key]).__name__}"
                )

        # Pre-conditions
        ok, failures = self.execution_contract.validate_pre(inputs)
        if not ok:
            raise ValueError(f"Node '{self.name}' pre-conditions failed: {failures}")

        self.state = "running"
        try:
            result = self.func(inputs)
            if asyncio.iscoroutine(result):
                result = await asyncio.wait_for(
                    result, timeout=self.execution_contract.timeout_seconds
                )
            # Post-conditions
            ok, failures = self.execution_contract.validate_post(result)
            if not ok:
                raise ValueError(f"Node '{self.name}' post-conditions failed: {failures}")
            self.state = "success"
            self.total_executions += 1
            self.performance_score = min(1.0, self.performance_score + 0.01)
        except Exception:
            self.state = "failed"
            self.failure_count += 1
            self.performance_score = max(0.0, self.performance_score - 0.05)
            raise

        self.last_execution_time = time.time() - start
        return result


class SPEACEAdaptiveGraph:
    """Adaptive typed computational graph with Hebbian plasticity."""

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self._nodes: dict[str, SPEACENode] = {}

    def register_node(
        self,
        name: str,
        func: Callable,
        input_types: dict[str, type] | None = None,
        output_types: dict[str, type] | None = None,
        metadata: dict[str, Any] | None = None,
        execution_contract: ExecutionContract | None = None,
    ) -> SPEACENode:
        contract = NodeContract(
            input_types=input_types or {},
            output_types=output_types or {},
            metadata=metadata or {},
        )
        node = SPEACENode(
            name=name,
            func=func,
            contract=contract,
            execution_contract=execution_contract or ExecutionContract(),
            metadata=metadata or {},
        )
        self._nodes[name] = node
        self.graph.add_node(name, spence_node=node)
        return node

    def connect(self, source: str, target: str, output_to_input_map: dict[str, str] | None = None):
        """Add a directed edge with optional field renaming."""
        self.graph.add_edge(
            source, target,
            output_map=output_to_input_map or {},
            plasticity=0.5,
            coactivation_count=0,
        )
        self._nodes[source].state = "connected"

    def strengthen_edge(self, source: str, target: str, amount: float = 0.05):
        """Hebbian strengthening — neurons that fire together wire together."""
        if self.graph.has_edge(source, target):
            for key in self.graph[source][target]:
                edge = self.graph[source][target][key]
                edge["plasticity"] = min(1.0, edge.get("plasticity", 0.5) + amount)
                edge["coactivation_count"] = edge.get("coactivation_count", 0) + 1

    def weaken_edge(self, source: str, target: str, amount: float = 0.02):
        """Reduce plasticity of unused connections."""
        if self.graph.has_edge(source, target):
            for key in self.graph[source][target]:
                edge = self.graph[source][target][key]
                edge["plasticity"] = max(0.0, edge.get("plasticity", 0.5) - amount)

    def prune_weak_edges(self, threshold: float = 0.1):
        """Remove connections below plasticity threshold to save resources."""
        to_remove = []
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            if data.get("plasticity", 0.5) < threshold:
                to_remove.append((u, v, key))
        for u, v, key in to_remove:
            self.graph.remove_edge(u, v, key)

    async def propagate(
        self, start_node: str, inputs: dict[str, Any], max_hops: int = 10
    ) -> list[dict[str, Any]]:
        """Breadth-first propagation through the graph, passing mapped outputs downstream."""
        results: list[dict[str, Any]] = []
        visited = set()
        queue = [(start_node, inputs, 0)]

        while queue and len(visited) < max_hops:
            node_name, node_inputs, hop = queue.pop(0)
            if node_name in visited or hop >= max_hops:
                continue
            visited.add(node_name)

            if node_name not in self._nodes:
                continue

            try:
                output = await self._nodes[node_name].execute(node_inputs)
                results.append({"node": node_name, "output": output, "hop": hop})
            except Exception as e:
                results.append({"node": node_name, "error": str(e), "hop": hop})
                continue

            # Fan out to successors
            for succ in self.graph.successors(node_name):
                if succ in visited:
                    continue
                succ_inputs: dict[str, Any] = {}
                for edge_key in self.graph[node_name][succ]:
                    edge = self.graph[node_name][succ][edge_key]
                    mapping = edge.get("output_map", {})
                    for out_key, in_key in mapping.items():
                        if out_key in output:
                            succ_inputs[in_key] = output[out_key]
                    # Strengthen edges that were used
                    self.strengthen_edge(node_name, succ)
                if not succ_inputs:
                    succ_inputs = dict(output)
                queue.append((succ, succ_inputs, hop + 1))

        return results

    def get_introspection(self) -> dict:
        """Full diagnostic snapshot of the graph."""
        nodes_info = {}
        for name, node in self._nodes.items():
            nodes_info[name] = {
                "state": node.state,
                "performance": round(node.performance_score, 3),
                "failures": node.failure_count,
                "executions": node.total_executions,
                "last_execution_ms": round(node.last_execution_time * 1000, 1),
                "metadata": node.metadata,
            }
        return {
            "node_count": len(self._nodes),
            "edge_count": self.graph.number_of_edges(),
            "nodes": nodes_info,
            "density": round(nx.density(self.graph), 4),
        }

    def save_state(self, filepath: str):
        data = {
            "nodes": {
                name: {
                    "state": n.state,
                    "performance": n.performance_score,
                    "failures": n.failure_count,
                    "executions": n.total_executions,
                    "metadata": n.metadata,
                }
                for name, n in self._nodes.items()
            },
            "edges": [
                {"source": u, "target": v, "key": k, "data": d}
                for u, v, k, d in self.graph.edges(keys=True, data=True)
            ],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
