# Ideal Prompt

## Description

Ideal Prompt is a desktop application built with Python and Tkinter that helps users create structured text prompts based on customizable templates. It loads templates from JSON files, allowing users to enable/disable sections, fill in placeholder values, and generate a final prompt text that can be easily copied to the clipboard.

## Features

*   **Graphical User Interface (GUI):** Built with Tkinter for ease of use.
*   **Template-Based:** Uses JSON files to define prompt structures (sections, content, placeholders).
*   **Customizable Sections:** Users can enable or disable predefined sections using checkboxes.
*   **Placeholder Editing:** Input fields (single-line or multi-line text boxes) are provided for editing placeholder values within each section.
*   **Dynamic Output Generation:** The output text area updates in real-time as users modify inputs or toggle sections.
*   **Copy to Clipboard:** A button allows users to copy the generated prompt text directly to the clipboard.
*   **Load Custom Templates:** Users can load different prompt templates (`.json` files) via the File menu.
*   **Clear Fields:** An option to clear all input fields is available.
*   **Multi-language Support:** Supports different languages through separate JSON template files (e.g., `example_eng.json`, `example_ita.json`).

## Files

*   **`prompts/example-eng.json`**: An example English prompt template file in JSON format.
*   **`prompts/example-ita.json`**: An example Italian prompt template file in JSON format.
*   **`ideal-prompt.py`**: The main Python script containing the application logic and GUI code.
*   **`ideal-prompt.json`**: The default English prompt template file in JSON format.
*   **`ideal-prompt.ico`**: The icon file used for the application window.
*   **`README.md`**: This file.

## How to Use

1.  **Prerequisites:** Ensure you have Python installed. Install the `pyperclip` library:
    ```bash
    pip install pyperclip
    ```
2.  **Run the Application:** Navigate to the project directory in your terminal and run the script:
    ```bash
    python ideal-prompt.py
    ```
3.  **Interact with the GUI:**
    *   The application will launch, loading the `ideal-prompt.json` template by default.
    *   The left pane shows the available sections from the template. Use the checkboxes to enable or disable sections for the final output.
    *   Fill in or modify the default text in the input fields associated with placeholders for each enabled section.
    *   The right pane displays the generated prompt text, updating automatically as you make changes.
    *   Click the "Copy to Clipboard" button to copy the generated text.
    *   Use the "File" > "Open Prompt Template" menu to load a different `.json` template file.
    *   Use the "Options" > "Clear All" menu to clear all input fields.

## Template Structure (`.json`)

Each JSON template file defines the structure of the prompt:

*   It contains a root object with a `sections` key, which is an array of section objects.
*   Each section object has:
    *   `name`: The display name of the section (string).
    *   `enabled`: Whether the section is enabled by default (boolean).
    *   `content`: The template string for the section, potentially containing placeholders like `{placeholder_name}` (string).
    *   `placeholders` (optional): An object defining the placeholders used in the `content`.
        *   Each key is the placeholder name (string).
        *   The value is an object with:
            *   `default`: The default text for the placeholder's input field (string).
            *   `lines`: The number of lines for the input field (1 for a single-line Entry, >1 for a multi-line Text widget) (integer).