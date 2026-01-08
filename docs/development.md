# Development

`indium` is a data-driven library. To ensure performance and stability, we pre-generate lookup tables from official Unicode Consortium data.

## Updating Unicode Data

To update the library with the latest Unicode version:

1.  **Download and Generate**:
    ```bash
    python3 tools/generate_confusables.py
    python3 tools/generate_scripts.py
    python3 tools/generate_grapheme_data.py
    ```

2.  **Verify Compliance**:
    Run the full UAX #29 compliance suite:
    ```bash
    pytest tests/test_full_compliance.py
    ```

## Standards Reference

- **UAX #29**: Unicode Text Segmentation (Grapheme Clusters).
- **UTS #39**: Unicode Security Mechanisms (Confusables, Scripts).
- **Unicode Version**: `indium` behavior depends on the host Python's `unicodedata` version.
