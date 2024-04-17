import tkinter as tk
from typing import Callable, Optional


class OverlayFrame(tk.Frame):
    def __init__(self,
                 parent: tk.Widget,
                 text: str, callback: Callable[[], None],
                 background_color: str = 'darkgrey',
                 text_color: str = 'white',
                 dismissal_shortcut: Optional[str] = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.callback = callback

        # Create a label within the overlay
        self.label = tk.Label(self, text=text, bg=background_color, fg=text_color)
        self.label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Bind clicking on the label to dismiss the overlay
        self.bind("<Button-1>", self.dismiss)
        self.label.bind("<Button-1>", self.dismiss)
        self._dismissal_button = dismissal_shortcut
        if dismissal_shortcut is not None:
            self.bind_all(dismissal_shortcut, self.dismiss)
        # parent.bind("<Button-1>", self.dismiss, add="+")  # '+' ensures additional bindings don't get overwritten
        self.keep_on_top()

    def show(self):
        """Show the overlay, dynamically centered in the parent frame."""
        self.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.update_idletasks()  # Update internal state to get accurate dimensions
        # self.recenter()
        self.lift()

    def keep_on_top(self):
        """Keep the overlay on top by lifting it periodically."""
        self.lift()
        self.after(200, self.keep_on_top)  # Adjust the timing as necessary

    def recenter(self):
        """Re-center the overlay based on its actual size."""
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        self_width = self.winfo_reqwidth()
        self_height = self.winfo_reqheight()
        x = (parent_width - self_width) // 2
        y = (parent_height - self_height) // 2
        self.place(x=x, y=y)

    def dismiss(self, event=None):
        """Hide the overlay and call the callback."""
        self.unbind_all(self._dismissal_button)
        # self.pack_forget()
        try:
            self.place_forget()
        except:
            pass
        self.destroy()
        self.callback()
        # Unbind the click event from parent to prevent unintended dismissals after destruction
        # self.master.unbind("<Button-1>", self.d ismiss)

def demo_overlay_widget():
    def on_dismiss():
        print("The overlay was dismissed!")

    root = tk.Tk()
    root.geometry("400x300")

    # Main frame that the overlay will cover
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Function to open a new overlay
    def open_floating():
        # Ensure old overlays are destroyed and cleaned up
        for widget in main_frame.winfo_children():
            if isinstance(widget, OverlayFrame):
                widget.dismiss()

        # Create a new instance of the OverlayFrame each time
        overlay = OverlayFrame(main_frame, "Click anywhere to dismiss", on_dismiss,
                               background_color='lightgray', text_color='black')
        overlay.show()

    # Button to show the overlay
    open_btn = tk.Button(root, text="Show Overlay", command=open_floating)
    open_btn.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    demo_overlay_widget()
