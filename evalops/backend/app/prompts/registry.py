"""Prompt registry for versioning and baseline management."""

import json
from pathlib import Path
from typing import Optional, Dict, Any

import yaml
from jinja2 import Template


class Prompt:
    """Represents a versioned prompt template."""

    def __init__(self, name: str, version: str, config: Dict[str, Any]):
        self.name = name
        self.version = version
        self.config = config
        self.system_prompt = config.get("system_prompt", "")
        self.user_template_str = config.get("user_template", "")
        self.parameters = config.get("parameters", {})

    def render(self, **kwargs) -> str:
        """Render the user prompt template with given variables."""
        template = Template(self.user_template_str)
        return template.render(**kwargs)

    def get_system_prompt(self) -> str:
        """Get the system prompt."""
        return self.system_prompt


class PromptRegistry:
    """Registry for managing versioned prompts and their baselines."""

    def __init__(self, prompts_dir: Optional[Path] = None, baselines_dir: Optional[Path] = None):
        """Initialize the registry.

        Args:
            prompts_dir: Directory containing prompt YAML files (default: this directory)
            baselines_dir: Directory containing baseline JSON files (default: tests/fixtures/prompt_baselines)
        """
        self.prompts_dir = prompts_dir or Path(__file__).parent
        # Navigate from app/prompts/ to tests/fixtures/prompt_baselines/
        # Path: evalops/backend/app/prompts/registry.py -> evalops/backend/tests/fixtures/prompt_baselines
        self.baselines_dir = baselines_dir or Path(__file__).parent.parent.parent / "tests" / "fixtures" / "prompt_baselines"
        self._cache: Dict[str, Prompt] = {}

    def load_prompt(self, name: str, version: str = "latest") -> Prompt:
        """Load a prompt by name and version.

        Args:
            name: Prompt name (e.g., "rag_prompt")
            version: Version string (default: "latest" resolves to highest version)

        Returns:
            Prompt object

        Raises:
            FileNotFoundError: If prompt file not found
            ValueError: If version not found
        """
        cache_key = f"{name}:{version}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        prompt_file = self.prompts_dir / f"{name}.yaml"
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt '{name}' not found at {prompt_file}")

        with open(prompt_file) as f:
            config = yaml.safe_load(f)

        prompt = Prompt(name=name, version=config.get("version", "1.0"), config=config)
        self._cache[cache_key] = prompt
        return prompt

    def get_baseline(self, name: str, version: str, model: str) -> Dict[str, Any]:
        """Load the golden baseline output for a prompt.

        Args:
            name: Prompt name
            version: Version string
            model: Model name (e.g., "llama3", "gpt-4")

        Returns:
            Baseline output dictionary

        Raises:
            FileNotFoundError: If baseline not found
        """
        baseline_file = self.baselines_dir / f"{name}_{version}_{model}.json"
        if not baseline_file.exists():
            raise FileNotFoundError(
                f"Baseline for '{name}' v{version} on {model} not found at {baseline_file}"
            )

        with open(baseline_file) as f:
            return json.load(f)

    def save_baseline(self, name: str, version: str, model: str, baseline: Dict[str, Any]) -> None:
        """Save a baseline output.

        Args:
            name: Prompt name
            version: Version string
            model: Model name
            baseline: Baseline data to save
        """
        self.baselines_dir.mkdir(parents=True, exist_ok=True)
        baseline_file = self.baselines_dir / f"{name}_{version}_{model}.json"
        with open(baseline_file, "w") as f:
            json.dump(baseline, f, indent=2)

    def list_prompts(self) -> list:
        """List all available prompts."""
        return [f.stem for f in self.prompts_dir.glob("*.yaml") if f.name != "__init__.py"]

    def list_baselines(self, name: str) -> list:
        """List all baselines for a given prompt."""
        baselines = []
        for f in self.baselines_dir.glob(f"{name}_*.json"):
            # filename: {name}_{version}_{model}.json
            parts = f.stem.split("_")
            if len(parts) >= 3:
                version = parts[1]
                model = "_".join(parts[2:])
                baselines.append({"version": version, "model": model, "file": f.name})
        return baselines


# Global registry instance
_registry: Optional[PromptRegistry] = None


def get_registry() -> PromptRegistry:
    """Get or create the global prompt registry."""
    global _registry
    if _registry is None:
        _registry = PromptRegistry()
    return _registry
