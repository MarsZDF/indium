# User Guide

This guide covers common scenarios and best practices for using `indium`.

## Handling Usernames and IDs

When accepting user input for IDs, it is recommended to store both the raw input and the "skeleton" form.

```python
import indium

def register_user(username: str):
    # 1. Sanitize (remove invisibles)
    clean_name = indium.sanitize(username)
    
    # 2. Generate skeleton for collision detection
    skel = indium.skeleton(clean_name)
    
    if db.find_by_skeleton(skel):
        raise ValueError("Username is too similar to an existing account")
        
    db.save(username=clean_name, skeleton=skel)
```

## LLM / RAG Context Sanitization

Frontier AI labs can use `indium` to prevent "invisible prompt injection" where attackers embed instructions in invisible characters.

```python
import indium

def safe_llm_input(prompt: str) -> str:
    # Reveal any hidden characters for logging/auditing
    revealed = indium.reveal(prompt)
    if "<U+" in revealed:
        logger.warning(f"Invisible chars detected: {revealed}")
        
    # Strictly sanitize before passing to tokenization
    return indium.sanitize(prompt, schema="strict")
```

## Safe UI Display

Avoid truncating text in the middle of a complex emoji or multi-codepoint character.

```python
import indium

long_comment = "The family was 👨‍👩‍👧‍👦 and they loved it!"
# Naive slicing might leave a broken Man or Woman emoji
safe_preview = indium.safe_truncate(long_comment, 20)
```
