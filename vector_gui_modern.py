#!/usr/bin/env python3
"""
Modern Vector Addition Calculator GUI
Inspired by modern dashboard design with clean, card-based interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime

from vector_addition import (
    add_vectors, plot_vectors, ColorTheme, VectorHistory,
    VectorData, format_measurement
)


class ModernVectorGUI:
    """Modern GUI application for vector addition calculator."""
    
    # Modern color palette
    COLORS = {
        'bg': '#F5F7FA',
        'card_bg': '#FFFFFF',
        'primary': '#5B8DEE',
        'primary_hover': '#4A7BD9',
        'secondary': '#6C757D',
        'success': '#28A745',
        'danger': '#DC3545',
        'warning': '#FFC107',
        'text_dark': '#2C3E50',
        'text_light': '#6C757D',
        'border': '#E1E8ED',
        'shadow': '#E0E0E0'
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("Vector Addition Calculator")
        # Make window responsive
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = min(1600, int(screen_width * 0.9))
        window_height = min(950, int(screen_height * 0.9))
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.configure(bg=self.COLORS['bg'])
        
        # Bind keyboard shortcuts
        self.root.bind('<Return>', lambda e: self.calculate_and_plot())
        self.root.bind('<Control-e>', lambda e: self.export_plot('png'))
        self.root.bind('<Control-z>', lambda e: self.history_undo())
        self.root.bind('<Control-y>', lambda e: self.history_redo())
        
        # Initialize components
        self.history = VectorHistory()
        self.current_theme = ColorTheme.ocean_theme()
        self.solution_visible = False
        
        # Animation variables
        self.animation_progress = 0
        self.animation_running = False
        self.animation_id = None
        self.stored_vectors = None
        self.animation_enabled = True
        self.animation_speed = 0.04  # Default speed
        
        # History navigation
        self.history_index = -1
        
        # Custom styles
        self.setup_modern_styles()
        self.create_modern_widgets()
        
    def setup_modern_styles(self):
        """Setup modern ttk styles."""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure modern card style
        self.style.configure('Card.TFrame', 
                           background=self.COLORS['card_bg'],
                           relief='flat')
        
        # Modern button styles
        self.style.configure('Primary.TButton',
                           background=self.COLORS['primary'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           padding=10,
                           font=('Segoe UI', 10, 'bold'))
        
        self.style.map('Primary.TButton',
                      background=[('active', self.COLORS['primary_hover'])])
        
        # Modern entry style
        self.style.configure('Modern.TEntry',
                           fieldbackground='white',
                           borderwidth=1,
                           relief='solid')
        
        # Modern label style
        self.style.configure('Title.TLabel',
                           background=self.COLORS['card_bg'],
                           foreground=self.COLORS['text_dark'],
                           font=('Segoe UI', 14, 'bold'))
        
        self.style.configure('Subtitle.TLabel',
                           background=self.COLORS['card_bg'],
                           foreground=self.COLORS['text_light'],
                           font=('Segoe UI', 10))
        
    def create_modern_widgets(self):
        """Create modern card-based layout."""
        # Header
        self.create_header()
        
        # Main content area
        content = tk.Frame(self.root, bg=self.COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Left sidebar (wider cards)
        left_sidebar = tk.Frame(content, bg=self.COLORS['bg'], width=420)
        left_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_sidebar.pack_propagate(False)
        
        self.create_input_cards(left_sidebar)
        
        # Right main area
        right_area = tk.Frame(content, bg=self.COLORS['bg'])
        right_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_plot_area(right_area)
        
    def create_header(self):
        """Create modern header with app title and controls."""
        header = tk.Frame(self.root, bg=self.COLORS['card_bg'], height=70)
        header.pack(fill=tk.X, padx=20, pady=(20, 20))
        header.pack_propagate(False)
        
        # Add subtle shadow effect
        shadow = tk.Frame(self.root, bg=self.COLORS['shadow'], height=2)
        shadow.place(x=20, y=88, relwidth=1, width=-40)
        
        # App title and subtitle
        title_frame = tk.Frame(header, bg=self.COLORS['card_bg'])
        title_frame.pack(side=tk.LEFT, padx=20)
        
        title = tk.Label(title_frame, text="Vector Addition Calculator",
                        font=('Segoe UI', 18, 'bold'),
                        fg=self.COLORS['text_dark'],
                        bg=self.COLORS['card_bg'])
        title.pack(anchor=tk.W)
        
        subtitle = tk.Label(title_frame, text="Visualize and analyze force vectors",
                           font=('Segoe UI', 10),
                           fg=self.COLORS['text_light'],
                           bg=self.COLORS['card_bg'])
        subtitle.pack(anchor=tk.W)
        
        # Right side controls
        controls = tk.Frame(header, bg=self.COLORS['card_bg'])
        controls.pack(side=tk.RIGHT, padx=20)
        
        # Theme selector
        theme_label = tk.Label(controls, text="Theme:",
                              font=('Segoe UI', 9),
                              fg=self.COLORS['text_light'],
                              bg=self.COLORS['card_bg'])
        theme_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.theme_var = tk.StringVar(value="Ocean")
        theme_menu = ttk.Combobox(controls, textvariable=self.theme_var,
                                  values=["Ocean"],
                                  state='disabled', width=12)
        theme_menu.pack(side=tk.LEFT, padx=5)
        
    def create_input_cards(self, parent):
        """Create modern input cards."""
        # Scale card
        scale_card = self.create_card(parent, "Scale Settings")
        self.create_input_field(scale_card, "1 cm equals (N):", "10", 'scale')
        
        # Force 1 card
        f1_card = self.create_card(parent, "Force 1 (F₁)", color='#5B8DEE')
        self.create_input_field(f1_card, "Magnitude (N):", "50", 'f1_mag')
        self.create_input_field(f1_card, "Angle (°):", "30", 'f1_angle')
        self.f1_slider = self.create_slider(f1_card, 'f1_angle')
        
        # Force 2 card
        f2_card = self.create_card(parent, "Force 2 (F₂)", color='#FF6B6B')
        self.create_input_field(f2_card, "Magnitude (N):", "40", 'f2_mag')
        self.create_input_field(f2_card, "Angle (°):", "120", 'f2_angle')
        self.f2_slider = self.create_slider(f2_card, 'f2_angle')
        
        # Result card
        result_card = self.create_card(parent, "Resultant (FR)", color='#28A745')
        self.result_text = tk.Text(result_card, height=6, width=25,
                                   font=('Segoe UI', 9),
                                   bg='#F8F9FA', fg=self.COLORS['text_dark'],
                                   relief='flat', padx=10, pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        self.result_text.config(state=tk.DISABLED)
        
        # Action buttons
        btn_frame = tk.Frame(parent, bg=self.COLORS['bg'])
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        calc_btn = tk.Button(btn_frame, text="Calculate & Plot (Enter)",
                            command=self.calculate_and_plot,
                            bg=self.COLORS['primary'],
                            fg='white',
                            font=('Segoe UI', 11, 'bold'),
                            relief='flat',
                            cursor='hand2',
                            padx=20, pady=12)
        calc_btn.pack(fill=tk.X, pady=(0, 8))
        calc_btn.bind('<Enter>', lambda e: calc_btn.config(bg=self.COLORS['primary_hover']))
        calc_btn.bind('<Leave>', lambda e: calc_btn.config(bg=self.COLORS['primary']))
        
        # History navigation buttons
        history_frame = tk.Frame(btn_frame, bg=self.COLORS['bg'])
        history_frame.pack(fill=tk.X, pady=(0, 8))
        
        undo_btn = tk.Button(history_frame, text="⟲ Undo (Ctrl+Z)",
                            command=self.history_undo,
                            bg='white', fg=self.COLORS['text_dark'],
                            font=('Segoe UI', 9), relief='solid', bd=1,
                            cursor='hand2', pady=6)
        undo_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        undo_btn.bind('<Enter>', lambda e: undo_btn.config(bg=self.COLORS['border']))
        undo_btn.bind('<Leave>', lambda e: undo_btn.config(bg='white'))
        
        redo_btn = tk.Button(history_frame, text="⟳ Redo (Ctrl+Y)",
                            command=self.history_redo,
                            bg='white', fg=self.COLORS['text_dark'],
                            font=('Segoe UI', 9), relief='solid', bd=1,
                            cursor='hand2', pady=6)
        redo_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))
        redo_btn.bind('<Enter>', lambda e: redo_btn.config(bg=self.COLORS['border']))
        redo_btn.bind('<Leave>', lambda e: redo_btn.config(bg='white'))
        
        # Animation control
        anim_frame = tk.Frame(btn_frame, bg=self.COLORS['bg'])
        anim_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.anim_toggle_btn = tk.Button(anim_frame, text="⏸ Disable Animation",
                                        command=self.toggle_animation,
                                        bg='white', fg=self.COLORS['text_dark'],
                                        font=('Segoe UI', 9), relief='solid', bd=1,
                                        cursor='hand2', pady=6)
        self.anim_toggle_btn.pack(fill=tk.X)
        self.anim_toggle_btn.bind('<Enter>', lambda e: self.anim_toggle_btn.config(bg=self.COLORS['border']))
        self.anim_toggle_btn.bind('<Leave>', lambda e: self.anim_toggle_btn.config(bg='white'))
        
        # Export buttons row
        export_frame = tk.Frame(btn_frame, bg=self.COLORS['bg'])
        export_frame.pack(fill=tk.X)
        
        export_label = tk.Label(export_frame, text="Export:",
                               font=('Segoe UI', 8),
                               fg=self.COLORS['text_light'],
                               bg=self.COLORS['bg'])
        export_label.pack(side=tk.LEFT, padx=(0, 5))
        
        for fmt in ['PNG', 'SVG', 'PDF']:
            btn = self.create_small_button(export_frame, fmt,
                                          lambda f=fmt.lower(): self.export_plot(f))
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
    def create_card(self, parent, title, color=None):
        """Create a modern card with shadow."""
        card = tk.Frame(parent, bg=self.COLORS['card_bg'],
                       highlightbackground=self.COLORS['border'],
                       highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 12))
        
        # Color accent bar if provided
        if color:
            accent = tk.Frame(card, bg=color, height=4)
            accent.pack(fill=tk.X)
        
        # Title
        title_label = tk.Label(card, text=title,
                              font=('Segoe UI', 12, 'bold'),
                              fg=self.COLORS['text_dark'],
                              bg=self.COLORS['card_bg'])
        title_label.pack(anchor=tk.W, padx=15, pady=(12, 10))
        
        return card
    
    def create_input_field(self, parent, label, default, var_name):
        """Create modern input field with validation."""
        frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        lbl = tk.Label(frame, text=label,
                      font=('Segoe UI', 9),
                      fg=self.COLORS['text_light'],
                      bg=self.COLORS['card_bg'])
        lbl.pack(anchor=tk.W)
        
        var = tk.StringVar(value=default)
        setattr(self, f'{var_name}_var', var)
        
        entry = tk.Entry(frame, textvariable=var,
                        font=('Segoe UI', 10),
                        relief='solid', bd=1,
                        highlightthickness=1,
                        highlightcolor=self.COLORS['primary'])
        entry.pack(fill=tk.X, pady=(3, 0))
        
        # Add validation feedback
        error_label = tk.Label(frame, text="",
                              font=('Segoe UI', 8),
                              fg=self.COLORS['danger'],
                              bg=self.COLORS['card_bg'])
        error_label.pack(anchor=tk.W)
        setattr(self, f'{var_name}_error', error_label)
        
        # Bind validation
        var.trace_add('write', lambda *args: self.validate_input(var_name))
        
        return var
    
    def create_slider(self, parent, var_name):
        """Create modern slider."""
        frame = tk.Frame(parent, bg=self.COLORS['card_bg'])
        frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        slider = ttk.Scale(frame, from_=0, to=360, orient=tk.HORIZONTAL,
                          command=lambda v: self.update_angle_from_slider(var_name, v))
        slider.pack(fill=tk.X)
        
        # Set initial value
        initial = float(getattr(self, f'{var_name}_var').get())
        slider.set(initial)
        
        return slider
    
    def create_small_button(self, parent, text, command):
        """Create small modern button."""
        btn = tk.Button(parent, text=text,
                       command=command,
                       bg='white',
                       fg=self.COLORS['text_dark'],
                       font=('Segoe UI', 9),
                       relief='solid',
                       bd=1,
                       cursor='hand2',
                       pady=6)
        btn.bind('<Enter>', lambda e: btn.config(bg=self.COLORS['border']))
        btn.bind('<Leave>', lambda e: btn.config(bg='white'))
        return btn
    
    def create_plot_area(self, parent):
        """Create modern plot area with toggle."""
        # Top bar with solution toggle
        top_bar = tk.Frame(parent, bg=self.COLORS['card_bg'], height=50)
        top_bar.pack(fill=tk.X, pady=(0, 12))
        top_bar.pack_propagate(False)
        
        self.toggle_btn = tk.Button(top_bar, text="📊 Show Solution",
                                    command=self.toggle_solution_panel,
                                    bg=self.COLORS['primary'],
                                    fg='white',
                                    font=('Segoe UI', 10, 'bold'),
                                    relief='flat',
                                    cursor='hand2',
                                    padx=15, pady=8)
        self.toggle_btn.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Main container for plot and solution
        self.plot_container = tk.PanedWindow(parent, orient=tk.HORIZONTAL,
                                            bg=self.COLORS['bg'],
                                            sashwidth=5,
                                            sashrelief='flat')
        self.plot_container.pack(fill=tk.BOTH, expand=True)
        
        # Plot card
        plot_card = tk.Frame(self.plot_container, bg=self.COLORS['card_bg'])
        self.plot_container.add(plot_card, stretch='always')
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 8), dpi=100,
                            facecolor=self.current_theme.background_color)
        self.figure.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.08)
        
        self.canvas = FigureCanvasTkAgg(self.figure, plot_card)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, plot_card)
        toolbar.update()
        
        # Solution panel (initially hidden)
        self.solution_panel = tk.Frame(self.plot_container, bg=self.COLORS['card_bg'])
        self.solution_panel.pack_propagate(False)  # Prevent panel from shrinking
        self.create_solution_panel()
        
    def create_solution_panel(self):
        """Create modern solution panel."""
        # Title
        title = tk.Label(self.solution_panel, text="Analytical Solution",
                        font=('Segoe UI', 14, 'bold'),
                        fg=self.COLORS['text_dark'],
                        bg=self.COLORS['card_bg'])
        title.pack(anchor=tk.W, padx=20, pady=(15, 10))
        
        # Solution text
        self.solution_text = scrolledtext.ScrolledText(
            self.solution_panel,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#F8F9FA',
            fg=self.COLORS['text_dark'],
            relief='flat',
            padx=15,
            pady=15
        )
        self.solution_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        self.solution_text.config(state=tk.DISABLED)
        
    def toggle_solution_panel(self):
        """Toggle solution panel visibility."""
        if self.solution_visible:
            self.plot_container.forget(self.solution_panel)
            self.toggle_btn.config(text="📊 Show Solution")
            self.solution_visible = False
        else:
            # Set minimum width for solution panel
            self.solution_panel.config(width=520)
            self.plot_container.add(self.solution_panel, minsize=520)
            
            # Force update and set sash position
            self.root.update_idletasks()
            
            # Give it a moment to render, then set position
            self.root.after(10, self._position_solution_sash)
            
            self.toggle_btn.config(text="❌ Hide Solution")
            self.solution_visible = True
    
    def _position_solution_sash(self):
        """Position the solution panel sash after it's added."""
        try:
            container_width = self.plot_container.winfo_width()
            sash_pos = max(100, container_width - 540)  # Leave 540px for solution panel
            
            if hasattr(self.plot_container, 'sashpos'):
                self.plot_container.sashpos(0, sash_pos)
            elif hasattr(self.plot_container, 'sash_place'):
                self.plot_container.sash_place(0, sash_pos, 0)
        except Exception:
            pass
    
    def validate_input(self, var_name):
        """Validate input field in real-time."""
        var = getattr(self, f'{var_name}_var')
        error_label = getattr(self, f'{var_name}_error')
        
        try:
            value = var.get().strip()
            if value == "":
                error_label.config(text="")
                return
            
            num = float(value)
            
            # Check for negative magnitudes
            if 'mag' in var_name and num < 0:
                error_label.config(text="⚠ Must be non-negative")
                return
            
            error_label.config(text="")
        except ValueError:
            error_label.config(text="⚠ Invalid number")
    
    def update_angle_from_slider(self, var_name, value):
        """Update angle entry from slider."""
        var = getattr(self, f'{var_name}_var')
        var.set(f"{float(value):.1f}")
    
    def calculate_and_plot(self):
        """Calculate and display results."""
        try:
            # Get inputs
            scale = float(self.scale_var.get())
            f1_mag = float(self.f1_mag_var.get())
            f1_angle = float(self.f1_angle_var.get())
            f2_mag = float(self.f2_mag_var.get())
            f2_angle = float(self.f2_angle_var.get())
            
            # Calculate
            f1, f2, r = add_vectors(f1_mag, f1_angle, f2_mag, f2_angle)
            
            # Add to history (only if it's a new calculation)
            if self.history_index == -1 or len(self.history.history) == 0:
                self.history.add(f1_mag, f1_angle, f2_mag, f2_angle, scale, r)
                self.history_index = len(self.history.history) - 1
            else:
                # If we're not at the end, truncate future history
                self.history.history = self.history.history[:self.history_index + 1]
                self.history.add(f1_mag, f1_angle, f2_mag, f2_angle, scale, r)
                self.history_index = len(self.history.history) - 1
            
            # Update result display
            self.display_result(r, scale)
            
            # Update solution
            self.update_solution_text(f1, f2, r, scale)
            
            # Store vectors and start animation
            self.stored_vectors = (f1, f2, r, scale)
            self.start_animation()
            
        except ValueError as e:
            # Show inline error instead of modal dialog
            self.show_inline_error(str(e))
    
    def draw_vectors_on_ax(self, ax, f1, f2, r, scale, progress=1.0, arc_progress=None):
        """Draw vectors on axes with optional animation progress."""
        if arc_progress is None:
            arc_progress = progress
        from vector_addition import (
            draw_vector_with_labels, draw_angle_arc,
            PADDING_RATIO, MIN_NEGATIVE_SPACE_RATIO,
            ARC_F1_RADIUS_RATIO, ARC_F2_RADIUS_RATIO, ARC_FR_RADIUS_RATIO
        )
        
        f1_cm = f1.mag / scale
        f2_cm = f2.mag / scale
        r_cm = r.mag / scale
        
        max_val = max(abs(f1.x), abs(f1.y), abs(f2.x), abs(f2.y), abs(r.x), abs(r.y))
        
        # Draw vectors with animation progress
        draw_vector_with_labels(ax, 0, 0, f1.x * progress, f1.y * progress, '#5B8DEE', 'F₁',
                               f1.mag, f1.angle, f1_cm, max_val, theme=self.current_theme)
        draw_vector_with_labels(ax, 0, 0, f2.x * progress, f2.y * progress, '#FF6B6B', 'F₂',
                               f2.mag, f2.angle, f2_cm, max_val, theme=self.current_theme)
        draw_vector_with_labels(ax, 0, 0, r.x * progress, r.y * progress, '#28A745', 'FR',
                               r.mag, r.angle, r_cm, max_val, width=0.004,
                               highlight=True, theme=self.current_theme)
        
        # Construction lines (only show when animation complete - consistent threshold)
        if progress >= 1.0:
            ax.plot([f1.x, f1.x + f2.x], [f1.y, f1.y + f2.y],
                    color='#FF6B6B', linestyle='--', linewidth=1.5, alpha=0.4)
            ax.plot([f2.x, f2.x + f1.x], [f2.y, f2.y + f1.y],
                    color='#5B8DEE', linestyle='--', linewidth=1.5, alpha=0.4)
        
        # Angle arcs (only show after arrows complete, with gradual growth)
        if arc_progress >= 1.0:
            # Calculate arc angle progress (grows after arrows are complete)
            arc_angle_progress = min(1.0, (arc_progress - 1.0) * 3)  # Grows 3x faster than arrows
            draw_angle_arc(ax, f1.angle * arc_angle_progress, '#5B8DEE', max_val, ARC_F1_RADIUS_RATIO, theme=self.current_theme)
            draw_angle_arc(ax, f2.angle * arc_angle_progress, '#FF6B6B', max_val, ARC_F2_RADIUS_RATIO, theme=self.current_theme)
            draw_angle_arc(ax, r.angle * arc_angle_progress, '#28A745', max_val, ARC_FR_RADIUS_RATIO,
                          linewidth=2.5, highlight=True, theme=self.current_theme)
        
        # Styling
        x_vals = [0, f1.x, f2.x, r.x]
        y_vals = [0, f1.y, f2.y, r.y]
        x_min, x_max = min(x_vals), max(x_vals)
        y_min, y_max = min(y_vals), max(y_vals)
        
        padding = max_val * PADDING_RATIO
        min_neg_space = max_val * MIN_NEGATIVE_SPACE_RATIO
        
        ax.set_xlim(min(x_min - padding, -min_neg_space), x_max + padding)
        ax.set_ylim(min(y_min - padding, -min_neg_space), y_max + padding)
        ax.set_aspect('equal')
        ax.set_facecolor(self.current_theme.background_color)
        ax.grid(True, alpha=0.3, color=self.current_theme.grid_color, linestyle='-', linewidth=0.5)
        ax.axhline(y=0, color=self.current_theme.grid_color, linewidth=1.5, zorder=2)
        ax.axvline(x=0, color=self.current_theme.grid_color, linewidth=1.5, zorder=2)
        
        ax.set_xlabel('Fₓ (N)', fontsize=11, color=self.current_theme.text_color, fontweight='600')
        ax.set_ylabel('Fᵧ (N)', fontsize=11, color=self.current_theme.text_color, fontweight='600')
        ax.set_title('Vector Addition Visualization', fontsize=13, fontweight='bold',
                    color=self.current_theme.text_color, pad=15)
        ax.tick_params(colors=self.current_theme.text_color)
        
        legend = ax.legend(loc='upper right', fontsize=10, framealpha=0.95,
                          edgecolor=self.current_theme.text_color)
    
    def start_animation(self):
        """Start the arrow animation."""
        if not self.animation_enabled:
            # Skip animation, draw final state
            if self.stored_vectors:
                f1, f2, r, scale = self.stored_vectors
                self.figure.clear()
                self.figure.set_facecolor(self.current_theme.background_color)
                ax = self.figure.add_subplot(111, facecolor=self.current_theme.background_color)
                self.draw_vectors_on_ax(ax, f1, f2, r, scale, progress=1.0, arc_progress=1.33)
                self.canvas.draw()
            return
        
        if self.animation_running and self.animation_id:
            self.root.after_cancel(self.animation_id)
        
        self.animation_progress = 0
        self.animation_running = True
        self.animate_step()
    
    def animate_step(self):
        """Perform one step of the animation."""
        if not self.stored_vectors:
            self.animation_running = False
            return
        
        # Ease-out cubic easing for smoother animation
        t = min(1.0, self.animation_progress)
        arrow_progress = 1 - pow(1 - t, 3)
        
        # Calculate arc progress (starts after arrows complete)
        arc_progress = 0
        if self.animation_progress >= 1.0:
            arc_t = min(1.0, (self.animation_progress - 1.0) / 0.33)  # Arc animation duration
            arc_progress = 1.0 + (1 - pow(1 - arc_t, 3)) * 0.33  # Ease-out for arcs
        else:
            arc_progress = arrow_progress
        
        f1, f2, r, scale = self.stored_vectors
        
        # Clear and redraw with current progress
        self.figure.clear()
        self.figure.set_facecolor(self.current_theme.background_color)
        ax = self.figure.add_subplot(111, facecolor=self.current_theme.background_color)
        # Use arrow_progress capped at 1.0 for arrows, arc_progress for arcs
        self.draw_vectors_on_ax(ax, f1, f2, r, scale, progress=min(1.0, arrow_progress), arc_progress=arc_progress)
        self.canvas.draw()
        
        # Update progress using instance variable
        self.animation_progress += self.animation_speed
        
        # Continue animation until both arrows and arcs are complete
        if self.animation_progress < 1.33:  # 1.0 for arrows + 0.33 for arcs
            self.animation_id = self.root.after(16, self.animate_step)  # ~60 FPS
        else:
            self.animation_running = False
            # Draw final frame with full vectors and arcs
            self.figure.clear()
            self.figure.set_facecolor(self.current_theme.background_color)
            ax = self.figure.add_subplot(111, facecolor=self.current_theme.background_color)
            self.draw_vectors_on_ax(ax, f1, f2, r, scale, progress=1.0, arc_progress=1.33)
            self.canvas.draw()
        
    def display_result(self, r, scale):
        """Display calculation results."""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        result = f"Magnitude: {r.mag:.2f} N\n"
        result += f"Length: {r.mag/scale:.2f} cm\n"
        result += f"Angle: {r.angle:.2f}°\n\n"
        result += f"Components:\n"
        result += f"  X: {r.x:.2f} N\n"
        result += f"  Y: {r.y:.2f} N"
        
        self.result_text.insert(1.0, result)
        self.result_text.config(state=tk.DISABLED)
    
    def update_solution_text(self, f1, f2, r, scale):
        """Update solution panel."""
        from vector_addition import generate_solution_text
        
        solution = generate_solution_text(f1, f2, r, scale)
        
        self.solution_text.config(state=tk.NORMAL)
        self.solution_text.delete(1.0, tk.END)
        self.solution_text.insert(1.0, solution)
        self.solution_text.config(state=tk.DISABLED)
    
    def toggle_animation(self):
        """Toggle animation on/off."""
        self.animation_enabled = not self.animation_enabled
        if self.animation_enabled:
            self.anim_toggle_btn.config(text="⏸ Disable Animation")
        else:
            self.anim_toggle_btn.config(text="▶ Enable Animation")
    
    def history_undo(self):
        """Undo to previous calculation."""
        if self.history_index > 0:
            self.history_index -= 1
            self.load_from_history(self.history_index)
    
    def history_redo(self):
        """Redo to next calculation."""
        if self.history_index < len(self.history.history) - 1:
            self.history_index += 1
            self.load_from_history(self.history_index)
    
    def load_from_history(self, index):
        """Load calculation from history."""
        if 0 <= index < len(self.history.history):
            entry = self.history.history[index]
            
            # Update input fields
            self.scale_var.set(str(entry['scale']))
            self.f1_mag_var.set(str(entry['f1_mag']))
            self.f1_angle_var.set(str(entry['f1_angle']))
            self.f2_mag_var.set(str(entry['f2_mag']))
            self.f2_angle_var.set(str(entry['f2_angle']))
            
            # Update sliders
            self.f1_slider.set(entry['f1_angle'])
            self.f2_slider.set(entry['f2_angle'])
            
            # Recalculate and display
            f1, f2, r = add_vectors(entry['f1_mag'], entry['f1_angle'], 
                                   entry['f2_mag'], entry['f2_angle'])
            
            self.display_result(r, entry['scale'])
            self.update_solution_text(f1, f2, r, entry['scale'])
            
            self.stored_vectors = (f1, f2, r, entry['scale'])
            self.start_animation()
    
    def show_inline_error(self, message):
        """Show error inline instead of modal dialog."""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, f"❌ Error:\n{message}")
        self.result_text.config(state=tk.DISABLED, fg=self.COLORS['danger'])
        
        # Reset color after 3 seconds
        self.root.after(3000, lambda: self.result_text.config(fg=self.COLORS['text_dark']))
    
    def export_plot(self, fmt):
        """Export plot with better filename suggestion."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"vector_plot_{timestamp}.{fmt}"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=f".{fmt}",
            initialfile=default_name,
            filetypes=[(f"{fmt.upper()} files", f"*.{fmt}"), ("All files", "*.*")]
        )
        if filepath:
            try:
                self.figure.savefig(filepath, format=fmt, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Exported to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def change_theme(self, event=None):
        """Change color theme and apply it across the UI and plot."""
        theme_name = self.theme_var.get().lower()
        if theme_name == "light":
            self.current_theme = ColorTheme.light_theme()
        elif theme_name == "dark":
            self.current_theme = ColorTheme.dark_theme()
        else:
            self.current_theme = ColorTheme.ocean_theme()
        self.apply_theme()

    def apply_theme(self):
        """Apply the current theme to widgets and re-render the plot."""
        # Update text areas to match theme
        try:
            self.solution_text.config(bg=self.current_theme.solution_box_color,
                                      fg=self.current_theme.text_color)
        except Exception:
            pass
        try:
            self.result_text.config(bg=self.current_theme.solution_box_color,
                                    fg=self.current_theme.text_color)
        except Exception:
            pass
        
        # Redraw plot with the latest values if available
        last = self.history.get_last(1)
        if last:
            entry = last[0]
            try:
                from vector_addition import add_vectors
                f1, f2, r = add_vectors(entry['f1_mag'], entry['f1_angle'], entry['f2_mag'], entry['f2_angle'])
                scale = entry['scale']
                self.figure.clear()
                self.figure.set_facecolor(self.current_theme.background_color)
                ax = self.figure.add_subplot(111, facecolor=self.current_theme.background_color)
                self.draw_vectors_on_ax(ax, f1, f2, r, scale)
            except Exception:
                pass
        self.canvas.draw_idle()


def main():
    """Run the modern GUI application."""
    root = tk.Tk()
    app = ModernVectorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
