"""
Prompt Manager for 7-Step Sanskrit Shloka Analysis.
Loads prompt templates from disk and dynamically formats variables for each step.
"""

from pathlib import Path
from typing import Dict, Any
from src.config import PROMPTS_DIR

# Step definitions: step number -> (file_name, sanskrit_title, english_title)
STEPS_CONFIG = {
    1: {
        "file": "step1_sampradaanam.txt",
        "name_sa": "संप्रदानम्",
        "name_en": "Sampradaanam (Metrical Division)",
        "desc": "Splitting the shloka into metrical padas and chanting units following actual verse structure"
    },
    2: {
        "file": "step2_padavibhaga.txt",
        "name_sa": "पदविभागः",
        "name_en": "Padavibhaga (Word Splitting & Grammatical Tagging)",
        "desc": "Identifying subanta, tinganta, avyaya, sandhivibhajana, samasa preservation"
    },
    3: {
        "file": "step3_anwaya.txt",
        "name_sa": "अन्वयः",
        "name_en": "Anwaya (Syntactic Reordering)",
        "desc": "Rearranging words into standard grammatical sentence flow (Kartru -> Karma -> Kriya)"
    },
    4: {
        "file": "step4_anwayartha.txt",
        "name_sa": "अन्वयार्थः",
        "name_en": "Anwayartha (Direct Literal Meaning)",
        "desc": "Literal word-by-word meaning following the Anwaya order without interpretation"
    },
    5: {
        "file": "step5_bhavartha.txt",
        "name_sa": "भावार्थः",
        "name_en": "Bhavartha (Contextual Meaning & Intended Purport)",
        "desc": "Faithful summary of the author's intended purport in 2-5 sentences"
    },
    6: {
        "file": "step6_padakrutyam.txt",
        "name_sa": "पदकृत्यम्",
        "name_en": "Padakrutyam (Morphological & Lexical Deep Dive)",
        "desc": "Detailed analysis of padas: dhatu, dhatvartha, upasarga, samasa, vigrahavakya, synonyms"
    },
    7: {
        "file": "step7_dhvanitartha.txt",
        "name_sa": "ध्वनितार्थः",
        "name_en": "Dhvanitartha (Implied Deeper Intent)",
        "desc": "Revealing unstated meanings between the lines using Tantrayukti and classical synthesis"
    }
}

class PromptManager:
    """Manages loading and rendering of prompt templates."""

    def __init__(self, prompts_dir: Path = PROMPTS_DIR):
        self.prompts_dir = prompts_dir
        self._cache: Dict[int, str] = {}
        self._load_all_templates()

    def _load_all_templates(self):
        """Preload all 7 prompt templates into memory."""
        for step_num, config in STEPS_CONFIG.items():
            prompt_file = self.prompts_dir / config["file"]
            if prompt_file.exists():
                self._cache[step_num] = prompt_file.read_text(encoding="utf-8")
            else:
                # Fallback template if file not found
                self._cache[step_num] = (
                    f"Perform Step {step_num} ({config['name_sa']} - {config['name_en']}) on the shloka:\n"
                    "Shloka: {shloka_text}\nContext: {retrieved_context}\n"
                )

    def get_template(self, step_number: int) -> str:
        """Get raw prompt template for a specific step."""
        if step_number not in STEPS_CONFIG:
            raise ValueError(f"Invalid step number: {step_number}. Must be 1 to 7.")
        config = STEPS_CONFIG[step_number]
        prompt_file = self.prompts_dir / config["file"]
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        return self._cache.get(step_number, "")

    def render_prompt(
        self,
        step_number: int,
        shloka_text: str,
        retrieved_context: str = "No additional context found.",
        previous_outputs: Dict[int, str] = None
    ) -> str:
        """
        Render a step's prompt template by inserting shloka text, retrieved context,
        and prior step outputs.
        """
        previous_outputs = previous_outputs or {}
        template = self.get_template(step_number)

        # Build replacement mapping
        format_args = {
            "shloka_text": shloka_text.strip(),
            "retrieved_context": retrieved_context.strip() if retrieved_context else "No relevant context found in database.",
            "step1_output": previous_outputs.get(1, "Not yet generated"),
            "step2_output": previous_outputs.get(2, "Not yet generated"),
            "step3_output": previous_outputs.get(3, "Not yet generated"),
            "step4_output": previous_outputs.get(4, "Not yet generated"),
            "step5_output": previous_outputs.get(5, "Not yet generated"),
            "step6_output": previous_outputs.get(6, "Not yet generated"),
        }

        # Safe string formatting
        rendered = template
        for key, val in format_args.items():
            placeholder = "{" + key + "}"
            if placeholder in rendered:
                rendered = rendered.replace(placeholder, val)

        return rendered

    def get_step_info(self, step_number: int) -> Dict[str, str]:
        """Return metadata regarding the given step."""
        return STEPS_CONFIG.get(step_number, {
            "name_sa": f"Step {step_number}",
            "name_en": f"Step {step_number}",
            "desc": ""
        })
