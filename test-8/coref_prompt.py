"""The coreference-resolution prompt from Jang et al. (2025), Table 5 — verbatim.

Jang, Y., Hong, S., Son, J., Park, S., Park, C., & Lim, H. (2025).
"From Ambiguity to Accuracy: The Transformative Effect of Coreference Resolution on
Retrieval-Augmented Generation systems." arXiv:2507.07847.
Korea University + NAVER. Table 5, "Prompt template example for CR task."

Transcribed from the LaTeXML HTML rendering of v3 (arxiv.org/html/2507.07847v3),
Appendix C.2. Character-level fidelity notes:

  * "commentary-output" in the paper uses an EM DASH (U+2014), not a hyphen.
  * "Bob's" in Example 2 uses a RIGHT SINGLE QUOTATION MARK (U+2019), not an ASCII
    apostrophe. Both are preserved below exactly as printed.
  * The paper writes the placeholder as ``{Document}``. We keep that spelling and
    substitute with ``str.replace`` rather than ``str.format`` so that any literal
    braces occurring in a passage are not misread as format fields.

WHAT THE PAPER DOES NOT SPECIFY, AND WHAT WE CHOSE
--------------------------------------------------
Table 5 is a flat template. It shows no system/user role split, no chat markup, and
no decoding parameters. Two choices were therefore ours, and both are recorded here
so the difference between "the paper's prompt" and "our run" stays visible:

  1. Role assignment. We send the entire template as a single ``user`` turn through
     the model's own chat template. We do NOT split the instruction into a system
     message, because the paper shows one contiguous block of text.
  2. Decoding. ``temperature=0`` (greedy, ``do_sample=False``). The paper reports no
     decoding settings; greedy is the only choice that makes the run reproducible.

The paper used ``gpt-4o-mini`` for its main results (Table 1) and
``Qwen2.5-7B-Instruct`` as a cheaper alternative in Appendix B (Tables 3 and 4).
Test 8 uses Qwen2.5-7B-Instruct, so it replicates the Appendix B configuration.
"""

# --- Table 5, verbatim ---------------------------------------------------------
# Do not "clean up" the punctuation in this string. It is a transcription.
COREF_PROMPT_TEMPLATE = (
    "You are an expert in coreference resolution. Your task is to resolve all "
    "ambiguous pronouns and references in the provided document, replacing them "
    "with explicit and contextually accurate entities. Do not add any extra text "
    "or commentary—output only the fully resolved document.\n"
    "\n"
    "Below are some examples:\n"
    "\n"
    "Example 1:\n"
    "Input:\n"
    "Document: Alice, who was late, quickly ran to catch the bus because she "
    "missed her train.\n"
    "Output:\n"
    "Alice, who was late, quickly ran to catch the bus because Alice missed her "
    "train.\n"
    "\n"
    "Example 2:\n"
    "Input:\n"
    "Document: Bob said he would finish his work today because he promised his "
    "manager.\n"
    "Output:\n"
    "Bob said that Bob would finish Bob’s work today because Bob promised his "
    "manager.\n"
    "\n"
    "Example 3:\n"
    "Input:\n"
    "Document: The committee stated that they would review the proposal after they "
    "received feedback.\n"
    "Output:\n"
    "The committee stated that the committee would review the proposal after the "
    "committee received feedback.\n"
    "\n"
    "When you receive the input document (which always starts with \"Document:\"), "
    "please output only the resolved document text.\n"
    "Document: {Document}"
)

# Decoding settings. The paper specifies none; these are ours and are logged by the
# notebook alongside every result.
GENERATION_CONFIG = {
    "do_sample": False,      # temperature 0 / greedy
    "temperature": None,     # explicit: sampling is off, so temperature is unused
    "top_p": None,
    "num_beams": 1,
    "max_new_tokens": 1024,  # sized for NanoBEIR passages (longest is ~2,080 chars)
}

# A short SHA so a findings file can assert it used this exact string.
def prompt_fingerprint() -> str:
    """Stable SHA-256 (first 12 hex chars) of the verbatim template."""
    import hashlib
    return hashlib.sha256(COREF_PROMPT_TEMPLATE.encode("utf-8")).hexdigest()[:12]


def build_prompt(document: str) -> str:
    """Substitute one passage into the paper's template.

    Uses ``str.replace`` rather than ``str.format``: passages containing literal
    ``{`` or ``}`` would raise or be silently mangled by ``format``.
    """
    return COREF_PROMPT_TEMPLATE.replace("{Document}", document)


if __name__ == "__main__":
    print(f"fingerprint: {prompt_fingerprint()}")
    print(f"template chars: {len(COREF_PROMPT_TEMPLATE)}")
    print("-" * 70)
    print(build_prompt("Marie Curie won the Nobel Prize. She later won a second one."))
