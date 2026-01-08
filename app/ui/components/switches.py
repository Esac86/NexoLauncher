import customtkinter as ctk

PRIMARIO = "#FF55FF"
SECUNDARIO = "#55FFFF"


class DualToggleSwitch(ctk.CTkFrame):    
    def __init__(self, parent, command=None, width=320, height=46, **kwargs):
        super().__init__(parent, fg_color="transparent", width=width, height=height)
        self.command = command
        self.current_position = 0  
        self.is_locked = False
        self._width_total = width
        
        self.bg_color = "#0b1220"
        self.border_color = PRIMARIO
        self.slider_color = PRIMARIO
        self.text_active = "#FFFFFF"
        self.text_inactive = "#64748b"
        
        self.canvas = ctk.CTkCanvas(
            self, width=width, height=height, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack()
        
        self.slider_width = (width // 2) - 8
        self.slider_height = height - 10
        self.slider_x = 5
        self.slider_y = 5
        
        self._create_rounded_rect(
            0, 0, width, height, radius=23, fill="", outline=self.border_color, width=2)
        self._create_rounded_rect(
            3, 3, width-3, height-3, radius=20, fill=self.bg_color, outline="")
        
        self.slider = self.canvas.create_polygon(
            self._get_rect_coords(self.slider_x), 
            fill=self.slider_color, outline="", smooth=True
        )
        
        self.text_basic = self.canvas.create_text(
            width * 0.25, height // 2, text="Vanilla", 
            font=("Segoe UI Semibold", 13), fill=self.text_active)
        self.text_optimized = self.canvas.create_text(
            width * 0.75, height // 2, text="Optifine / Mods", 
            font=("Segoe UI Semibold", 13), fill=self.text_inactive)
        
        self.canvas.tag_raise(self.text_basic)
        self.canvas.tag_raise(self.text_optimized)
        
        self.canvas.bind("<Button-1>", self._on_click)
        
        self.animation_steps = 12
        self.animation_speed = 8

    def _get_rect_coords(self, x):
        radius = 18
        y1, x2 = self.slider_y, x + self.slider_width
        y2, x1 = y1 + self.slider_height, x
        return [
            x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, 
            x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, 
            x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, 
            x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, 
            x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1
        ]

    def _create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, 
            x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, 
            x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, 
            x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, 
            x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1
        ]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def _on_click(self, event):
        if self.is_locked:
            return
        
        click_x = event.x
        section_width = self._width_total / 2
        
        new_position = 0 if click_x < section_width else 1
        
        if new_position != self.current_position:
            self.current_position = new_position
            self._update_colors()
            self._animate_slider()
            if self.command:
                self.command()

    def set_position(self, position):
        if position in [0, 1]:
            self.current_position = position
            target_positions = [5, (self._width_total // 2) + 1]
            self.slider_x = target_positions[position]
            self.canvas.coords(self.slider, *self._get_rect_coords(self.slider_x))
            self._update_colors()

    def _animate_slider(self):
        target_positions = [5, (self._width_total // 2) + 1]
        end_x = target_positions[self.current_position]
        step_size = (end_x - self.slider_x) / self.animation_steps

        def animate_step(step=0):
            if step < self.animation_steps:
                self.slider_x += step_size
                self.canvas.coords(self.slider, *self._get_rect_coords(self.slider_x))
                self.after(self.animation_speed, lambda: animate_step(step + 1))
            else:
                self.slider_x = end_x
                self.canvas.coords(self.slider, *self._get_rect_coords(self.slider_x))

        animate_step()

    def _update_colors(self):
        if self.current_position == 0:
            self.canvas.itemconfig(self.text_basic, fill=self.text_active)
            self.canvas.itemconfig(self.text_optimized, fill=self.text_inactive)
        else:
            self.canvas.itemconfig(self.text_basic, fill=self.text_inactive)
            self.canvas.itemconfig(self.text_optimized, fill=self.text_active)

    def get(self):
        return 'modded' if self.current_position == 1 else 'vanilla'

    def set_lock(self, state):
        self.is_locked = state


class ToggleSwitch(ctk.CTkFrame):    
    def __init__(self, parent, command=None, text_left="Sencillo", text_right="Avanzado", 
                 width=280, height=46, **kwargs):
        super().__init__(parent, fg_color="transparent", width=width, height=height)
        self.command = command
        self.is_right = False
        self.is_locked = False
        self._width_total = width
        
        self.bg_color = "#0b1220"
        self.border_color = PRIMARIO
        self.slider_color = PRIMARIO
        self.text_active = "#FFFFFF"
        self.text_inactive = "#64748b"
        
        self.canvas = ctk.CTkCanvas(
            self, width=width, height=height, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack()
        
        self.slider_width = width // 2 - 6
        self.slider_height = height - 10
        self.slider_x = 5
        self.slider_y = 5
        
        self._create_rounded_rect(
            0, 0, width, height, radius=23, fill="", outline=self.border_color, width=2)
        self._create_rounded_rect(
            3, 3, width-3, height-3, radius=20, fill=self.bg_color, outline="")
        
        self.slider = self.canvas.create_polygon(
            self._get_rect_coords(self.slider_x), 
            fill=self.slider_color, outline="", smooth=True
        )
        
        self.text_left_id = self.canvas.create_text(
            width * 0.25, height // 2, text=text_left, 
            font=("Segoe UI Semibold", 13), fill=self.text_active)
        self.text_right_id = self.canvas.create_text(
            width * 0.75, height // 2, text=text_right, 
            font=("Segoe UI Semibold", 13), fill=self.text_inactive)
        
        self.canvas.tag_raise(self.text_left_id)
        self.canvas.tag_raise(self.text_right_id)
        
        self.canvas.bind("<Button-1>", lambda e: self.toggle())
        
        self.animation_steps = 12
        self.animation_speed = 8

    def _get_rect_coords(self, x):
        radius = 18
        y1, x2 = self.slider_y, x + self.slider_width
        y2, x1 = y1 + self.slider_height, x
        return [
            x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, 
            x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, 
            x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, 
            x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, 
            x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1
        ]

    def _create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, 
            x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, 
            x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, 
            x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, 
            x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1
        ]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def set_state(self, is_right):
        self.is_right = is_right
        self.slider_x = (self._width_total - self.slider_width - 5) if self.is_right else 5
        self.canvas.coords(self.slider, *self._get_rect_coords(self.slider_x))
        self._update_colors()

    def toggle(self):
        if self.is_locked:
            return
        self.is_right = not self.is_right
        self._update_colors()
        self._animate_slider()
        if self.command:
            self.command()

    def _animate_slider(self):
        end_x = (self._width_total - self.slider_width - 5) if self.is_right else 5
        step_size = (end_x - self.slider_x) / self.animation_steps

        def animate_step(step=0):
            if step < self.animation_steps:
                self.slider_x += step_size
                self.canvas.coords(self.slider, *self._get_rect_coords(self.slider_x))
                self.after(self.animation_speed, lambda: animate_step(step + 1))
            else:
                self.slider_x = end_x
                self.canvas.coords(self.slider, *self._get_rect_coords(self.slider_x))

        animate_step()

    def _update_colors(self):
        if self.is_right:
            self.canvas.itemconfig(self.text_left_id, fill=self.text_inactive)
            self.canvas.itemconfig(self.text_right_id, fill=self.text_active)
        else:
            self.canvas.itemconfig(self.text_left_id, fill=self.text_active)
            self.canvas.itemconfig(self.text_right_id, fill=self.text_inactive)

    def get(self):
        return self.is_right

    def set_lock(self, state):
        self.is_locked = state
        

class ToggleSwitch(ctk.CTkFrame):    
    def __init__(self, parent, command=None, text_left="Sencillo", text_right="Avanzado", 
                 width=280, height=46, **kwargs):
        super().__init__(parent, fg_color="transparent", width=width, height=height)
        self.command = command
        self.is_right = False
        self.is_locked = False
        self._width_total = width
        
        self.bg_color = "#0b1220"
        self.border_color = PRIMARIO
        self.slider_color = PRIMARIO
        self.text_active = "#FFFFFF"
        self.text_inactive = "#64748b"
        
        self.canvas = ctk.CTkCanvas(
            self, width=width, height=height, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack()
        
        self.slider_width = width // 2 - 6
        self.slider_height = height - 10
        self.slider_x = 5
        self.slider_y = 5
        
        self._create_rounded_rect(
            0, 0, width, height, radius=23, fill="", outline=self.border_color, width=2)
        self._create_rounded_rect(
            3, 3, width-3, height-3, radius=20, fill=self.bg_color, outline="")
        
        self.slider = self.canvas.create_polygon(
            self._get_rect_coords(self.slider_x), 
            fill=self.slider_color, outline="", smooth=True
        )
        
        self.text_left_id = self.canvas.create_text(
            width * 0.25, height // 2, text=text_left, 
            font=("Segoe UI Semibold", 13), fill=self.text_active)
        self.text_right_id = self.canvas.create_text(
            width * 0.75, height // 2, text=text_right, 
            font=("Segoe UI Semibold", 13), fill=self.text_inactive)
        
        self.canvas.tag_raise(self.text_left_id)
        self.canvas.tag_raise(self.text_right_id)
        
        self.canvas.bind("<Button-1>", lambda e: self.toggle())
        
        self.animation_steps = 12
        self.animation_speed = 8

    def _get_rect_coords(self, x):
        radius = 18
        y1, x2 = self.slider_y, x + self.slider_width
        y2, x1 = y1 + self.slider_height, x
        return [
            x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, 
            x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, 
            x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, 
            x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, 
            x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1
        ]

    def _create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, 
            x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, 
            x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, 
            x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, 
            x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1
        ]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def set_state(self, is_right):
        self.is_right = is_right
        self.slider_x = (self._width_total - self.slider_width - 5) if self.is_right else 5
        self.canvas.coords(self.slider, *self._get_rect_coords(self.slider_x))
        self._update_colors()

    def toggle(self):
        if self.is_locked:
            return
        self.is_right = not self.is_right
        self._update_colors()
        self._animate_slider()
        if self.command:
            self.command()

    def _animate_slider(self):
        end_x = (self._width_total - self.slider_width - 5) if self.is_right else 5
        step_size = (end_x - self.slider_x) / self.animation_steps

        def animate_step(step=0):
            if step < self.animation_steps:
                self.slider_x += step_size
                self.canvas.coords(self.slider, *self._get_rect_coords(self.slider_x))
                self.after(self.animation_speed, lambda: animate_step(step + 1))
            else:
                self.slider_x = end_x
                self.canvas.coords(self.slider, *self._get_rect_coords(self.slider_x))

        animate_step()

    def _update_colors(self):
        if self.is_right:
            self.canvas.itemconfig(self.text_left_id, fill=self.text_inactive)
            self.canvas.itemconfig(self.text_right_id, fill=self.text_active)
        else:
            self.canvas.itemconfig(self.text_left_id, fill=self.text_active)
            self.canvas.itemconfig(self.text_right_id, fill=self.text_inactive)

    def get(self):
        return self.is_right

    def set_lock(self, state):
        self.is_locked = state