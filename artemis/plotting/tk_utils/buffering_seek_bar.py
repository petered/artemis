import tkinter as tk
from typing import Callable


class BufferedSeekBar(tk.Canvas):
    def __init__(self,
                 parent: tk.Widget,
                 background_color: str = 'darkgray',
                 head_color: str = 'white',
                 buffer_color: str = 'darkblue',
                 border_color: str = 'black',
                 on_click_callback: Callable[[float], None] = lambda x: None,
                 height: int = 15,
                 **kwargs) -> None:
        super().__init__(parent, height=height, **kwargs)
        self.configure(bg=background_color, bd=1, highlightbackground=border_color)

        self.current_value: float = 0.0
        self.buffered_value: float = 0.0
        self.callback: Callable[[float], None] = on_click_callback

        self.background_color = background_color
        self.head_color = head_color
        self.buffer_color = buffer_color

        self.scale_width: int = self.winfo_reqwidth()
        self.scale_height: int = height

        self.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", self.on_click)

        # self.draw_scale()
        self.update_buffered_area()
        self.update_position_indicator()

    def draw_scale(self) -> None:
        self.scale = self.create_rectangle(5, 5, self.scale_width - 5, self.scale_height - 5, outline='black', fill=self.background_color)

    def reset(self) -> None:
        self.current_value = 0.0
        self.buffered_value = 0.0
        self.update_buffered_area()
        self.update_position_indicator()

    def update_buffered_area(self) -> None:
        self.delete('buffered')
        if self.buffered_value != 0:
            buffered_width = self.buffered_value * (self.scale_width - 10)
            self.create_rectangle(5, 5, buffered_width + 5, self.scale_height - 5, outline='', fill=self.buffer_color, tags='buffered')
            self.update_position_indicator()  # Ensure position indicator is drawn last

    def update_position_indicator(self) -> None:
        self.delete('position')
        position_x = self.current_value * (self.scale_width - 10) + 5
        self.create_rectangle(position_x - 2, 5, position_x + 2, self.scale_height - 5, outline=self.head_color, fill=self.head_color, tags='position')

    def set_buffered_amount(self, value: float, force_redraw: bool = False) -> None:
        redraw = force_redraw or value != self.buffered_value
        self.buffered_value = value
        if redraw:
            self.update_buffered_area()

    def set_current_position(self, value: float) -> None:
        self.current_value = value
        self.update_position_indicator()

    def get_current_position(self) -> float:
        return self.current_value

    def on_resize(self, event: tk.Event) -> None:
        self.scale_width = event.width
        self.scale_height = event.height
        # self.draw_scale()
        self.update_buffered_area()

    def on_click(self, event: tk.Event) -> None:
        click_position = (event.x - 5) / (self.scale_width - 10)
        click_position = max(0, min(click_position, 1))
        self.set_current_position(click_position)
        self.callback(click_position)

    def set_on_click_callback(self, callback: Callable[[float], None]) -> None:
        self.callback = callback

# Usage


def demo_buffering_seek_bar():
    def on_scale_click(position: float) -> None:
        print(f"Clicked at position: {position}")

    def start_buffering_loop(frac_per_sec = 0.05, cycle_time=0.1):
        def buffering_loop():
            buffering_scale.set_buffered_amount(buffering_scale.buffered_value + frac_per_sec*cycle_time)
            if buffering_scale.buffered_value < 1.0:
                root.after(int(1000*cycle_time), buffering_loop)
        buffering_loop()

    root = tk.Tk()
    buffering_scale = BufferedSeekBar(root, width=300, height=30, on_click_callback=on_scale_click)
    buffering_scale.pack(fill='both', expand=True)
    buffering_scale.set_on_click_callback(on_scale_click)
    start_buffering_loop()
    root.mainloop()


if __name__ == '__main__':
    demo_buffering_seek_bar()