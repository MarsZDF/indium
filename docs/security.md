# Unicode Security

`indium` implements security mechanisms defined by the Unicode Consortium.

## Visual Normalization (Skeleton)

The `skeleton()` function implements the **TR39** recommendation for detecting visual confusables. It uses:

1.  **NFKC Normalization**: Converts characters to their "canonical confusable" form (e.g., Mathematical Bold $\rightarrow$ Standard).
2.  **Prototype Mapping**: Uses a database of thousands of character mappings to reduce look-alike characters to a single prototype (e.g., Cyrillic 'а', Greek 'ο' $\rightarrow$ Latin equivalents).

Comparing the skeletons of two strings tells you if they **look the same** to a human, even if they use completely different code points.

## Mixed Script Detection

Phishing attacks often mix characters from different scripts (e.g., Latin and Cyrillic) in a single word. `is_mixed_script()` detects these anomalies.

Standard domains and identifiers usually use only one script. `indium` provides script boundaries to help analyze where the script changes occur.

## Invisible Characters

Characters in categories like `Cf` (Format), `Cc` (Control), and `Co` (Private Use) are often invisible but can be used to bypass filters or mislead users.

- **reveal()**: Makes these characters visible for debugging.
- **sanitize()**: Safely removes them while preserving legitimate whitespace.
- **detect_invisibles()**: Locates them for security auditing.
