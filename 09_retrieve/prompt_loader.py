# D:\AI Project\financial_agent_V1\09_retrieve\prompt_loader.py
"""
Prompt Template Loader - Load and manage Prompt templates from YAML files
"""
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class PromptLoader:
    """Prompt template loader"""

    def __init__(self, prompts_dir: str = None):
        """
        Initialize Prompt loader

        Args:
            prompts_dir: Prompts directory path, defaults to prompts subdirectory of current file's directory
        """
        if prompts_dir is None:
            # Default path: 09_retrieve/prompts
            self.prompts_dir = Path(__file__).parent / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)

        # Cache loaded templates
        self._templates_cache: Dict[str, Dict[str, Any]] = {}

        # Verify directory exists
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Prompts directory not found: {self.prompts_dir}")

    def load_template(self, template_name: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load specified Prompt template

        Args:
            template_name: Template name (without .yaml extension)
            force_reload: Whether to force reload (ignore cache)

        Returns:
            Dictionary containing template and config
        """
        # Check cache
        if not force_reload and template_name in self._templates_cache:
            return self._templates_cache[template_name].copy()

        # Build file path
        yaml_file = self.prompts_dir / f"{template_name}.yaml"

        if not yaml_file.exists():
            raise FileNotFoundError(f"Prompt template not found: {yaml_file}")

        # Load YAML file
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)

            # Validate required fields
            if 'template' not in template_data:
                raise ValueError(f"Template '{template_name}' missing 'template' field")

            # Set default config
            if 'config' not in template_data:
                template_data['config'] = {}

            # Cache
            self._templates_cache[template_name] = template_data

            return template_data.copy()

        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML template '{template_name}': {e}")

    def render_template(self, template_name: str, **kwargs) -> str:
        """
        Load and render Prompt template

        Args:
            template_name: Template name
            **kwargs: Parameters for replacing placeholders in template

        Returns:
            Rendered Prompt string
        """
        template_data = self.load_template(template_name)
        template_str = template_data['template']

        # Use Python's format method to replace placeholders
        try:
            rendered = template_str.format(**kwargs)
            return rendered
        except KeyError as e:
            missing_key = str(e).strip("'")
            raise KeyError(f"Missing required parameter for template '{template_name}': {missing_key}")

    def get_config(self, template_name: str) -> Dict[str, Any]:
        """
        Get template configuration

        Args:
            template_name: Template name

        Returns:
            Configuration dictionary
        """
        template_data = self.load_template(template_name)
        return template_data.get('config', {})

    def list_templates(self) -> list:
        """
        List all available templates

        Returns:
            List of template names
        """
        templates = []
        for yaml_file in self.prompts_dir.glob("*.yaml"):
            templates.append(yaml_file.stem)
        return sorted(templates)

    def clear_cache(self):
        """Clear template cache"""
        self._templates_cache.clear()


# Global singleton
_prompt_loader_instance: Optional[PromptLoader] = None


def get_prompt_loader(prompts_dir: str = None) -> PromptLoader:
    """
    Get global PromptLoader instance (singleton pattern)

    Args:
        prompts_dir: Prompts directory path

    Returns:
        PromptLoader instance
    """
    global _prompt_loader_instance
    if _prompt_loader_instance is None:
        _prompt_loader_instance = PromptLoader(prompts_dir)
    return _prompt_loader_instance
