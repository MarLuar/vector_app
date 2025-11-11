#!/usr/bin/env python3
"""
Gradio Web App for Vector Addition Calculator
Supports matplotlib plots with animations
"""

import gradio as gr
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
from vector_addition import (
    add_vectors, ColorTheme, draw_vector_with_labels, draw_angle_arc,
    generate_solution_text, PADDING_RATIO, MIN_NEGATIVE_SPACE_RATIO,
    ARC_F1_RADIUS_RATIO, ARC_F2_RADIUS_RATIO, ARC_FR_RADIUS_RATIO
)

def create_vector_plot(scale, f1_mag, f1_angle, f2_mag, f2_angle, show_solution):
    """Create matplotlib plot and optional solution text"""
    try:
        # Calculate vectors
        f1, f2, r = add_vectors(f1_mag, f1_angle, f2_mag, f2_angle)
        theme = ColorTheme.ocean_theme()
        
        # Create figure
        fig = Figure(figsize=(10, 8), dpi=100, facecolor=theme.background_color)
        ax = fig.add_subplot(111, facecolor=theme.background_color)
        
        # Calculate max value
        max_val = max(abs(f1.x), abs(f1.y), abs(f2.x), abs(f2.y), abs(r.x), abs(r.y))
        
        # Draw vectors
        f1_cm = f1.mag / scale
        f2_cm = f2.mag / scale
        r_cm = r.mag / scale
        
        draw_vector_with_labels(ax, 0, 0, f1.x, f1.y, '#5B8DEE', 'F₁',
                               f1.mag, f1.angle, f1_cm, max_val, theme=theme)
        draw_vector_with_labels(ax, 0, 0, f2.x, f2.y, '#FF6B6B', 'F₂',
                               f2.mag, f2.angle, f2_cm, max_val, theme=theme)
        draw_vector_with_labels(ax, 0, 0, r.x, r.y, '#28A745', 'FR',
                               r.mag, r.angle, r_cm, max_val, width=0.004,
                               highlight=True, theme=theme)
        
        # Construction lines
        ax.plot([f1.x, f1.x + f2.x], [f1.y, f1.y + f2.y],
                color='#FF6B6B', linestyle='--', linewidth=1.5, alpha=0.4)
        ax.plot([f2.x, f2.x + f1.x], [f2.y, f2.y + f1.y],
                color='#5B8DEE', linestyle='--', linewidth=1.5, alpha=0.4)
        
        # Angle arcs
        draw_angle_arc(ax, f1.angle, '#5B8DEE', max_val, ARC_F1_RADIUS_RATIO, theme=theme)
        draw_angle_arc(ax, f2.angle, '#FF6B6B', max_val, ARC_F2_RADIUS_RATIO, theme=theme)
        draw_angle_arc(ax, r.angle, '#28A745', max_val, ARC_FR_RADIUS_RATIO,
                      linewidth=2.5, highlight=True, theme=theme)
        
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
        ax.set_facecolor(theme.background_color)
        ax.grid(True, alpha=0.3, color=theme.grid_color, linestyle='-', linewidth=0.5)
        ax.axhline(y=0, color=theme.grid_color, linewidth=1.5, zorder=2)
        ax.axvline(x=0, color=theme.grid_color, linewidth=1.5, zorder=2)
        
        ax.set_xlabel('Fₓ (N)', fontsize=11, color=theme.text_color, fontweight='600')
        ax.set_ylabel('Fᵧ (N)', fontsize=11, color=theme.text_color, fontweight='600')
        ax.set_title('Vector Addition Visualization', fontsize=13, fontweight='bold',
                    color=theme.text_color, pad=15)
        ax.tick_params(colors=theme.text_color)
        
        ax.legend(loc='upper right', fontsize=10, framealpha=0.95,
                 edgecolor=theme.text_color)
        
        fig.tight_layout()
        
        # Result text
        result_text = f"""**Resultant Force (FR)**
Magnitude: {r.mag:.2f} N
Length: {r.mag/scale:.2f} cm
Angle: {r.angle:.2f}°

**Components:**
X: {r.x:.2f} N
Y: {r.y:.2f} N"""
        
        # Solution text
        solution_text = ""
        if show_solution:
            solution_text = generate_solution_text(f1, f2, r, scale)
        
        return fig, result_text, solution_text
    
    except Exception as e:
        fig = Figure(figsize=(10, 8))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, f"Error: {str(e)}", ha='center', va='center')
        return fig, f"Error: {str(e)}", ""

# Create Gradio interface
with gr.Blocks(title="Vector Addition Calculator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Vector Addition Calculator")
    gr.Markdown("Visualize and analyze force vectors")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Settings")
            scale = gr.Number(label="Scale: 1 cm equals (N)", value=10.0, minimum=0.1)
            
            gr.Markdown("### Force 1 (F₁)")
            f1_mag = gr.Number(label="Magnitude (N)", value=50.0, minimum=0.0)
            f1_angle = gr.Slider(label="Angle (°)", minimum=0, maximum=360, value=30, step=1)
            
            gr.Markdown("### Force 2 (F₂)")
            f2_mag = gr.Number(label="Magnitude (N)", value=40.0, minimum=0.0)
            f2_angle = gr.Slider(label="Angle (°)", minimum=0, maximum=360, value=120, step=1)
            
            show_solution = gr.Checkbox(label="Show analytical solution", value=False)
            
            calculate_btn = gr.Button("Calculate", variant="primary", size="lg")
        
        with gr.Column(scale=2):
            plot_output = gr.Plot(label="Vector Visualization")
            result_output = gr.Markdown("Click Calculate to see results")
    
    with gr.Accordion("Analytical Solution", open=False):
        solution_output = gr.Code(language=None, label="")
    
    # Connect button to function
    calculate_btn.click(
        fn=create_vector_plot,
        inputs=[scale, f1_mag, f1_angle, f2_mag, f2_angle, show_solution],
        outputs=[plot_output, result_output, solution_output]
    )
    
    gr.Markdown("""
    ## Quick Guide
    - Enter force magnitudes and angles
    - Click Calculate to visualize
    - Results show the resultant force
    - Enable checkbox for step-by-step solution
    
    **Mobile-friendly** - Works on all devices!
    """)

if __name__ == "__main__":
    demo.launch(share=False)  # Set share=True for public URL
