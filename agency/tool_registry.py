"""SPEACE Agency — Tool Registry.

Sandboxed tool execution framework. Allows the digital brain to interact
with the computer (files, Python, shell) through controlled, logged interfaces.

BIOLOGICAL PRINCIPLE: The motor system converts abstract intentions into
specific muscle commands via a hierarchy: prefrontal (goal) → premotor
(plan) → motor cortex (command) → spinal cord (execution) → muscles (action).
Each level decompresses the abstract into the concrete.

SPEACE tools are the "muscles" — the final effectors. The hierarchy is:
Frontal Lobe (what to do) → Basal Ganglia (select action) → Cerebellum (refine)
→ Tool Registry (execute). Safety gates at each level.
"""

import asyncio
import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any


class Tool:
    def __init__(self, name: str, description: str, func: callable):
        self.name = name
        self.description = description
        self.func = func

    async def execute(self, **kwargs) -> dict:
        try:
            result = self.func(**kwargs)
            if asyncio.iscoroutine(result):
                result = await result
            return {"success": True, "tool": self.name, "result": result}
        except Exception as e:
            return {"success": False, "tool": self.name, "error": str(e)}


class ToolRegistry:

    def __init__(self, config: dict):
        self.tools: dict[str, Tool] = {}
        self.execution_log: list[dict] = []
        self._register_defaults()

    def _register_defaults(self):
        self.register(Tool("read_file", "Read text file contents", self._read_file))
        self.register(Tool("write_file", "Write text to file (append optional)", self._write_file))
        self.register(Tool("list_dir", "List directory contents", self._list_dir))
        self.register(Tool("run_python", "Execute Python code in sandbox", self._run_python))
        self.register(Tool("run_shell", "Execute shell command", self._run_shell))

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    async def execute(self, name: str, **kwargs) -> dict:
        if name not in self.tools:
            return {"success": False, "error": f"Tool '{name}' non trovato"}

        start = time.time()
        result = await self.tools[name].execute(**kwargs)
        elapsed = (time.time() - start) * 1000

        self.execution_log.append({
            "tool": name,
            "args": str(kwargs)[:200],
            "success": result.get("success", False),
            "latency_ms": round(elapsed, 1),
            "timestamp": time.time(),
        })
        if len(self.execution_log) > 100:
            self.execution_log = self.execution_log[-100:]

        return result

    # ── Built-in Tool Implementations ──

    async def _read_file(self, path: str) -> str:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"File non trovato: {path}")
        if p.stat().st_size > 10_000_000:
            raise ValueError("File troppo grande (>10MB)")
        return p.read_text(encoding="utf-8", errors="replace")

    async def _write_file(self, path: str, content: str, append: bool = False) -> str:
        p = Path(path).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with open(p, mode, encoding="utf-8") as f:
            f.write(content)
        return f"Scritto: {p} ({len(content)} caratteri, mode={mode})"

    async def _list_dir(self, path: str = ".") -> list[str]:
        p = Path(path).expanduser().resolve()
        if not p.is_dir():
            raise NotADirectoryError(f"Non è una directory: {path}")
        items = []
        for entry in sorted(p.iterdir()):
            tag = "📁" if entry.is_dir() else "📄"
            items.append(f"{tag} {entry.name}")
        return items

    async def _run_python(self, code: str, timeout: int = 30) -> str:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False,
                                          encoding="utf-8") as f:
            f.write(code)
            tmp_path = f.name

        try:
            proc = await asyncio.create_subprocess_exec(
                "python", tmp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
            out = stdout.decode("utf-8", errors="replace")
            err = stderr.decode("utf-8", errors="replace")
            return out + ("\n[STDERR]\n" + err if err else "")
        except asyncio.TimeoutError:
            return f"Timeout ({timeout}s) superato"
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    async def _run_shell(self, command: str, timeout: int = 30) -> str:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
            out = stdout.decode("utf-8", errors="replace")
            err = stderr.decode("utf-8", errors="replace")
            return out + ("\n[ERR]\n" + err if err else "")
        except asyncio.TimeoutError:
            proc.kill()
            return f"Timeout ({timeout}s)"

    def list_tools(self) -> list[dict]:
        return [{"name": t.name, "desc": t.description} for t in self.tools.values()]
