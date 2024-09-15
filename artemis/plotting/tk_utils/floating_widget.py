import tkinter as tk
from typing import Callable, Optional, Union, Sequence, Tuple

from artemis.general.custom_types import BGRImageArray
from artemis.plotting.tk_utils.ui_utils import bgr_image_to_pil_image
from PIL import ImageTk


def anchor_signs_to_anchor(horizontal_sign: int, vertical_sign: int) -> str:
    horizontal = "e" if horizontal_sign == 1 else "w" if horizontal_sign == -1 else ""
    vertical = "s" if vertical_sign == 1 else "n" if vertical_sign == -1 else ""
    return vertical + horizontal or "center"


def anchor_to_signs(anchor: str) -> Tuple[int, int]:
    if anchor == "center":
        return 0, 0
    horizontal_sign = 1 if "e" in anchor else -1 if "w" in anchor else 0
    vertical_sign = 1 if "s" in anchor else -1 if "n" in anchor else 0
    return horizontal_sign, vertical_sign


class OverlayFrame(tk.Frame):
    def __init__(self,
                 parent: tk.Widget,
                 text: Optional[str] = None,
                 callback: Optional[Callable[[], None]] = None,
                 background_color: str = 'darkgrey',
                 text_color: str = 'white',
                 dismissal_shortcut: Optional[Union[str, Sequence[str]]] = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.callback = callback

        # Create a label within the overlay
        if text is not None:
            self.label = tk.Label(self, text=text, bg=background_color, fg=text_color)
            self.label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
            self.label.bind("<Button-1>", self.dismiss)

        self.image_label = None

        # Bind clicking on the label to dismiss the overlay
        self.bind("<Button-1>", self.dismiss)

        self._dismissal_shortcuts = [dismissal_shortcut] if isinstance(dismissal_shortcut, str) else [] if dismissal_shortcut is None else list(dismissal_shortcut)

        for s in self._dismissal_shortcuts:
            self.bind_all(s, self.dismiss)
        # parent.bind("<Button-1>", self.dismiss, add="+")  # '+' ensures additional bindings don't get overwritten
        self.keep_on_top()

    def show(self):
        """Show the overlay, dynamically centered in the parent frame."""
        self.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.update_idletasks()  # Update internal state to get accurate dimensions
        # self.recenter()
        self.lift()

    def set_image(self, image_array: BGRImageArray):
        """Set the image to display in the overlay."""
        if self.image_label is None:
            self.image_label = tk.Label(self)
            self.image_label.pack(expand=True, fill=tk.BOTH)
        self.image_label.image = ImageTk.PhotoImage(bgr_image_to_pil_image(image_array))
        self.image_label.config(image=self.image_label.image)

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

    def place_within_parent(self, display_xy: tuple, anchor=tk.NW, offset_pix=25, change_anchor_if_outside=True):
        """Place the overlay at a specific location within the parent frame."""

        x, y = display_xy
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        horizontal_anchor_sign, vertical_anchor_sign = anchor_to_signs(anchor)
        if change_anchor_if_outside:
            falls_outside_horizontally = not (0 < x - horizontal_anchor_sign * (offset_pix + w) < self.master.winfo_width())
            if falls_outside_horizontally:
                horizontal_anchor_sign = -horizontal_anchor_sign
            falls_outside_vertically = not (0 < y - vertical_anchor_sign * (offset_pix + h) < self.master.winfo_height())
            if falls_outside_vertically:
                vertical_anchor_sign = -vertical_anchor_sign

        anchor = anchor_signs_to_anchor(horizontal_anchor_sign, vertical_anchor_sign)
        x, y = display_xy
        self.place(x=x, y=y, anchor=anchor)

    def hide(self):
        """Hide the overlay without calling the callback."""
        self.place_forget()

    def dismiss(self, event=None):
        """Hide the overlay and call the callback."""
        for s in self._dismissal_shortcuts:
            self.unbind_all(s)
        # self.pack_forget()
        try:
            self.place_forget()
        except:
            pass
        self.destroy()
        if self.callback:
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
