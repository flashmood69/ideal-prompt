import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import pyperclip

class ideal_prompt_app:
    """Main application class for the Ideal Prompt generator.
    
    Handles UI creation, template loading, and prompt generation functionality.
    Uses a JSON schema to define prompt sections and placeholders.
    """

    def __init__(self, root):
        """Initialize the application window and widgets.
        
        Args:
            root: The Tk root window instance
        """
        self.root = root
        self.root.title('Ideal Prompt')
        self.root.minsize(800, 600)

        # Configure grid layout for responsive resizing
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Open Prompt Template', command=self.load_json_template)
        menubar.add_cascade(label='File', menu=filemenu)
        root.config(menu=menubar)
        optionmenu = tk.Menu(menubar, tearoff=0)
        optionmenu.add_command(label='Clear All', command=self.clear_all_textboxes)
        menubar.add_cascade(label='Options', menu=optionmenu)

        # --- Create PanedWindow ---
        paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned_window.grid(row=0, column=0, sticky="nsew")
        paned_window.configure(width=800)

        # --- Left Frame Setup (add to PanedWindow) ---
        # Use ttk.Frame and add minimal padding for both panels
        self.left_frame_container = ttk.Frame(paned_window, padding="5 5 5 5") # Parent is now paned_window
        # self.left_frame_container.grid(row=0, column=0, sticky="nsew") # REMOVED grid call
        self.left_frame_container.rowconfigure(0, weight=1)
        self.left_frame_container.columnconfigure(0, weight=1)
        self.left_frame_container.rowconfigure(1, weight=0)  # For horizontal scrollbar

        # --- Scrollable Left Frame Setup ---
        self.canvas = tk.Canvas(self.left_frame_container)
        self.v_scrollbar = ttk.Scrollbar(self.left_frame_container, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.left_frame_container, orient="horizontal", command=self.canvas.xview)
        # Use ttk.Frame for the scrollable content area
        self.left_frame = ttk.Frame(self.canvas)

        self.left_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.left_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Store the ID of the window created on the canvas
        self.canvas_window_id = self.canvas.create_window((0, 0), window=self.left_frame, anchor="nw")

        # Bind canvas resizing to adjust the inner frame's width
        self.canvas.bind("<Configure>", self.on_canvas_configure)


        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        # --- End Scrollable Left Frame Setup ---

        # --- Right Frame Setup (add to PanedWindow) ---
        self.right_frame = ttk.Frame(paned_window, padding="5 5 5 5") # Parent is now paned_window
        # self.right_frame.grid(row=0, column=1, sticky="nsew") # REMOVED grid call
        self.right_frame.rowconfigure(0, weight=1) # Allow text widget to expand
        self.right_frame.columnconfigure(0, weight=1) # Allow text widget to expand
        # --- End Right Frame Setup ---

        # --- Add frames to PanedWindow with weights ---
        paned_window.add(self.left_frame_container, weight=1) # Set equal weight for left frame
        paned_window.add(self.right_frame, weight=1)          # Set equal weight for right frame

        self.input_fields = {}
        self.section_contents = {}
        self.checkboxes = {}
        self.schema_path = 'ideal-prompt.json'
        # Load default schema on initialization
        if not self.load_schema(self.schema_path):
             # Handle case where default schema fails to load (e.g., show error and exit)
             messagebox.showerror("Initialization Error", f"Failed to load default schema:\n{self.schema_path}\nApplication cannot start.")
             root.destroy() # Close the app if default schema fails
             return # Stop further initialization
        self.create_widgets()

    # Add this new method to handle canvas resizing
    def on_canvas_configure(self, event):
        """Adjust inner frame width when canvas is resized."""
        self.canvas.itemconfig(self.canvas_window_id, width=event.width)

    def load_json_template(self):
        """Load a new JSON template file via file dialog and update UI."""
        file_path = filedialog.askopenfilename(filetypes=[('JSON files', '*.json')])
        if file_path and self.load_schema(file_path):
            self.create_widgets()

    def load_schema(self, file_path):
        """Load and validate JSON schema from file.
        
        Args:
            file_path: Path to JSON schema file
            
        Returns:
            bool: True if schema loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                new_schema = json.load(file)
                
            if 'sections' not in new_schema or not isinstance(new_schema['sections'], list):
                raise ValueError("Invalid template format: 'sections' key missing or not a list.")
                
            self.schema = new_schema
            self.schema_path = file_path
            return True
            
        except FileNotFoundError:
            messagebox.showerror("Error", f"Template file not found:\n{file_path}")
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Failed to parse JSON template:\n{file_path}\nPlease ensure it's valid JSON.")
        except ValueError as ve:
             messagebox.showerror("Error", f"Invalid template structure:\n{str(ve)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading the template:\n{str(e)}")
        return False # Indicate failure

    def variable_changed(self, *args):
        self.update_output()

    def clear_all_textboxes(self):
        # Clear textboxes in the scrollable left frame
        self._find_and_clear_textboxes(self.left_frame)
        # Clear textboxes in the right frame (output area)
        self._find_and_clear_textboxes(self.right_frame)

    # Renamed find_textboxes to be more specific and internal
    def _find_and_clear_textboxes(self, parent_widget):
        """Recursively clear all Entry and Text widgets within a parent widget.
        
        Args:
            parent_widget: The container widget to search through
        """
        for widget in parent_widget.winfo_children():
            if isinstance(widget, (ttk.Entry, tk.Text)):
                if isinstance(widget, ttk.Entry):
                    widget.delete(0, tk.END)
                elif isinstance(widget, tk.Text): # tk.Text
                    widget.delete('1.0', tk.END)
            # Recurse through children container widgets (like Frames)
            # Exclude widgets that don't typically contain other input widgets (like Scrollbar)
            elif isinstance(widget, (ttk.Frame, tk.Frame)):
                 self._find_and_clear_textboxes(widget)


    def _clear_widgets(self):
        """Clears widgets from the main frames and resets state."""
        for widget in self.left_frame.winfo_children():
            widget.destroy()
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        self.input_fields.clear()
        self.section_contents.clear()
        self.checkboxes.clear()

    def _create_section_widgets(self, section, row_index):
        """Creates widgets for a single section in the left frame."""
        section_name = section['name']
        self.checkboxes[section_name] = tk.BooleanVar(value=section.get('enabled', True)) # Default to True if missing
        self.checkboxes[section_name].trace_add('write', self.variable_changed)

        section_checkbox = ttk.Checkbutton(self.left_frame, text=section_name, variable=self.checkboxes[section_name], style='Bold.TCheckbutton')
        section_checkbox.grid(row=row_index, column=0, sticky=tk.W, pady=(10, 2), padx=5)
        row_index += 1
        self.section_contents[section_name] = section['content']

        if 'placeholders' in section:
            placeholder_frame = ttk.Frame(self.left_frame)
            placeholder_frame.grid(row=row_index, column=0, sticky='ew', pady=2, padx=20)
            placeholder_frame.columnconfigure(0, weight=1)
            row_index += 1
            self._create_placeholder_widgets(section, placeholder_frame)

        return row_index # Return the next available row index

    def _create_placeholder_widgets(self, section, parent_frame):
        """Creates label and entry widgets for placeholders within a section."""
        inner_row_index = 0
        section_name = section['name']
        for placeholder, attributes in section['placeholders'].items():
            container = ttk.Frame(parent_frame)
            container.grid(row=inner_row_index, column=0, sticky='ew', pady=2)
            container.columnconfigure(1, weight=1) # Make entry expand
            inner_row_index += 1

            placeholder_label = ttk.Label(container, text=f'{placeholder.capitalize()}:')
            placeholder_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))

            lines = attributes.get('lines', 1) # Default to 1 line if missing
            default_value = attributes.get('default', '') # Default to empty string

            if lines > 1:
                text_frame = ttk.Frame(container, borderwidth=1, relief="sunken")
                text_frame.grid(row=0, column=1, sticky="ew")
                text_frame.columnconfigure(0, weight=1)
                text_frame.rowconfigure(0, weight=1)
                entry = tk.Text(text_frame, height=lines, font=('Arial', 9), wrap=tk.WORD)
                entry.grid(row=0, column=0, sticky="nsew")
                entry.insert('1.0', default_value)
                entry.bind('<KeyRelease>', self.update_output)
            else:
                entry = ttk.Entry(container, font=('Arial', 9))
                entry.grid(row=0, column=1, sticky="ew")
                entry.insert(0, default_value)
                entry.bind('<KeyRelease>', self.update_output)

            self.input_fields[section_name, placeholder] = entry

    def _create_output_widgets(self):
        """Creates the output text area and copy button in the right frame."""
        output_frame = ttk.Frame(self.right_frame)
        output_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)

        self.output_text = tk.Text(output_frame, wrap=tk.WORD, borderwidth=1, relief="sunken")
        self.output_text.grid(row=0, column=0, sticky="nsew")
        self.output_text.configure(width=40)  # Set a fixed width for the output text area

        output_scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        output_scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_text.configure(yscrollcommand=output_scrollbar.set)

        self.copy_button = ttk.Button(self.right_frame, text='Copy to Clipboard', command=self.copy_to_clipboard)
        self.copy_button.grid(row=1, column=0, pady=5)

    def create_widgets(self):
        """Clears and recreates all dynamic widgets based on the current schema."""
        self._clear_widgets()

        # Configure the main column in the left_frame to expand
        self.left_frame.columnconfigure(0, weight=1)
        row_index = 0 # Keep track of grid rows in left_frame

        # Create widgets for each section in the left frame
        if hasattr(self, 'schema') and 'sections' in self.schema:
             for section in self.schema['sections']:
                 row_index = self._create_section_widgets(section, row_index)
        else:
             # Handle case where schema is missing or invalid after initialization attempt
             ttk.Label(self.left_frame, text="Error: Schema not loaded correctly.").grid(row=0, column=0, padx=10, pady=10)
             ttk.Label(self.right_frame, text="Error: Schema not loaded correctly.").grid(row=0, column=0, padx=10, pady=10)
             return # Stop widget creation if schema is bad


        # Create output widgets in the right frame
        self._create_output_widgets()

        # Configure style for bold checkbutton text (ensure style exists)
        style = ttk.Style()
        try:
            style.configure('Bold.TCheckbutton', font=('Arial', 10, 'bold'))
        except tk.TclError:
             print("Warning: Could not configure Bold.TCheckbutton style (maybe style element doesn't exist?).")


        # Update canvas scroll region after adding widgets
        self.left_frame.update_idletasks() # Ensure layout is calculated
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Trigger the canvas configure event once manually to set initial width
        self.left_frame.update_idletasks() # Ensure frame size is updated
        self.canvas.event_generate("<Configure>")

        self.update_output() # Initial output generation

    def _build_section_output(self, section):
        """Builds the output string for a single section, applying placeholders."""
        section_name = section['name']
        # Check if checkbox exists and is checked
        if section_name not in self.checkboxes or not self.checkboxes[section_name].get():
            return None # Return None if section is disabled

        section_content = self.section_contents.get(section_name, "")
        has_content = False # Flag to track if any placeholder has a value

        if 'placeholders' in section:
            for placeholder in section['placeholders']:
                value = self.get_placeholder_value(section_name, placeholder)
                section_content = section_content.replace(f'{{{placeholder}}}', value)
                if value: # Check if the retrieved value is non-empty
                    has_content = True
        else:
             # If no placeholders, the section itself is considered content
             has_content = True


        # Return content only if it's meant to be included (no placeholders or has content)
        if has_content:
            return section_content
        else:
            return None # Return None if section has placeholders but all are empty


    def update_output(self, event=None):
        """Updates the output text area based on enabled sections and placeholder values."""
        output_parts = []
        try:
            if not hasattr(self, 'schema') or 'sections' not in self.schema:
                 self.output_text.delete('1.0', tk.END)
                 self.output_text.insert(tk.END, "Error: Schema not loaded.")
                 return

            for section in self.schema['sections']:
                section_output = self._build_section_output(section)
                if section_output is not None: # Only add if section is enabled and has content
                    output_parts.append(section_output)

            final_output = '\n\n'.join(output_parts).strip()
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert(tk.END, final_output)
        except Exception as e:
            print(f"Error during update_output: {e}")
            # Optionally update the text area itself with an error message
            try:
                self.output_text.delete('1.0', tk.END)
                self.output_text.insert(tk.END, f"Error generating output: {e}")
            except tk.TclError: # Handle cases where output_text might not exist yet
                 pass


    def get_placeholder_value(self, section_name, placeholder):
        # Check if input field exists
        if (section_name, placeholder) not in self.input_fields:
            return ""
        entry = self.input_fields[section_name, placeholder]
        # Check instance type
        if isinstance(entry, ttk.Entry):
            return entry.get().strip()
        elif isinstance(entry, tk.Text):
            return entry.get('1.0', tk.END).strip()
        return "" # Should not happen if types are correct

    def copy_to_clipboard(self):
        output = self.output_text.get('1.0', tk.END).strip()
        pyperclip.copy(output)
        messagebox.showinfo('Copied', 'Prompt copied to clipboard')
if __name__ == '__main__':
    root = tk.Tk()
    # Apply theme if available (e.g., 'clam', 'alt', 'default', 'vista')
    style = ttk.Style(root)
    try:
        # Try setting a theme that might look better on Windows
        style.theme_use('vista')
    except tk.TclError:
        print("Vista theme not available, using default.") # Fallback
    app = ideal_prompt_app(root)
    # Ensure icon path is correct or handle FileNotFoundError
    try:
        root.iconbitmap('ideal-prompt.ico')
    except tk.TclError:
        print("Could not load icon 'ideal-prompt.ico'. Make sure it's in the same directory.")
    root.mainloop()
