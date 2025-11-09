#!/usr/bin/env python3
"""
Streamlit Web App for Vector Addition Calculator
Mobile-friendly and deployable to Streamlit Cloud
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
import numpy as np

from vector_addition import (
    add_vectors, ColorTheme, VectorHistory,
    draw_vector_with_labels, draw_angle_arc,
    generate_solution_text, generate_direct_solution,
    PADDING_RATIO, MIN_NEGATIVE_SPACE_RATIO,
    ARC_F1_RADIUS_RATIO, ARC_F2_RADIUS_RATIO, ARC_FR_RADIUS_RATIO
)

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="Vector Addition Calculator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = VectorHistory()
if 'theme' not in st.session_state:
    st.session_state.theme = ColorTheme.ocean_theme()

# Custom CSS for better mobile experience
st.markdown("""
<style>
    .stSlider > div > div > div > div {
        background-color: #5B8DEE;
    }
    .main > div {
        padding-top: 2rem;
    }
    h1 {
        color: #2C3E50;
        font-size: 2rem;
    }
    @media (max-width: 768px) {
        h1 {
            font-size: 1.5rem;
        }
        .stButton button {
            width: 100%;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("Vector Addition Calculator")
st.markdown("Visualize and analyze force vectors")

# Sidebar for inputs
with st.sidebar:
    st.header("Settings")
    
    # Method selection
    st.subheader("Visualization Method")
    method = st.radio(
        "Choose method:",
        ["Parallelogram", "Polygon (Tip-to-Tail)"],
        help="Parallelogram: Both vectors start at origin\nPolygon: Second vector starts at tip of first"
    )
    
    st.divider()
    
    # Scale settings
    st.subheader("Scale")
    scale = st.number_input("1 cm equals (N):", min_value=0.1, value=10.0, step=0.5)
    
    st.divider()
    
    # Force 1
    st.subheader("Force 1 (F₁)")
    f1_mag = st.number_input("Magnitude (N):", min_value=0.0, value=50.0, step=1.0, key="f1_mag")
    f1_angle = st.number_input("Angle (°):", min_value=0.0, max_value=360.0, value=30.0, step=1.0, key="f1_angle")
    
    st.divider()
    
    # Force 2
    st.subheader("Force 2 (F₂)")
    f2_mag = st.number_input("Magnitude (N):", min_value=0.0, value=40.0, step=1.0, key="f2_mag")
    f2_angle = st.number_input("Angle (°):", min_value=0.0, max_value=360.0, value=120.0, step=1.0, key="f2_angle")
    
    st.divider()
    
    # Controls
    col1, col2 = st.columns(2)
    with col1:
        calculate_btn = st.button("Calculate", use_container_width=True, type="primary")
    with col2:
        show_solution = st.checkbox("Show Steps", value=False)

# Main content area
if calculate_btn or 'last_result' in st.session_state:
    try:
        # Calculate vectors
        f1, f2, r = add_vectors(f1_mag, f1_angle, f2_mag, f2_angle)
        
        # Add to history
        st.session_state.history.add(f1_mag, f1_angle, f2_mag, f2_angle, scale, r)
        st.session_state.last_result = (f1, f2, r, scale)
        
        # Results section - Plot on top
        st.subheader("Vector Visualization")
        st.info(f"🔹 **Method:** {method}")
        
        # Create plot
        fig = Figure(figsize=(12, 7), dpi=100, facecolor=st.session_state.theme.background_color)
        ax = fig.add_subplot(111, facecolor=st.session_state.theme.background_color)
        
        # Calculate max value for scaling
        max_val = max(abs(f1.x), abs(f1.y), abs(f2.x), abs(f2.y), abs(r.x), abs(r.y))
        
        # Draw vectors
        f1_cm = f1.mag / scale
        f2_cm = f2.mag / scale
        r_cm = r.mag / scale
        
        if method == "Parallelogram":
            # Parallelogram method: both vectors start at origin
            draw_vector_with_labels(ax, 0, 0, f1.x, f1.y, '#5B8DEE', 'F₁',
                                   f1.mag, f1.angle, f1_cm, max_val, theme=st.session_state.theme)
            draw_vector_with_labels(ax, 0, 0, f2.x, f2.y, '#FF6B6B', 'F₂',
                                   f2.mag, f2.angle, f2_cm, max_val, theme=st.session_state.theme)
            draw_vector_with_labels(ax, 0, 0, r.x, r.y, '#28A745', 'FR',
                                   r.mag, r.angle, r_cm, max_val, width=0.004,
                                   highlight=True, theme=st.session_state.theme)
            
            # Construction lines for parallelogram
            ax.plot([f1.x, f1.x + f2.x], [f1.y, f1.y + f2.y],
                    color='#FF6B6B', linestyle='--', linewidth=1.5, alpha=0.4)
            ax.plot([f2.x, f2.x + f1.x], [f2.y, f2.y + f1.y],
                    color='#5B8DEE', linestyle='--', linewidth=1.5, alpha=0.4)
        
        else:  # Polygon (Tip-to-Tail) method
            # First vector starts at origin
            draw_vector_with_labels(ax, 0, 0, f1.x, f1.y, '#5B8DEE', 'F₁',
                                   f1.mag, f1.angle, f1_cm, max_val, theme=st.session_state.theme)
            # Second vector starts at tip of first
            draw_vector_with_labels(ax, f1.x, f1.y, f2.x, f2.y, '#FF6B6B', 'F₂',
                                   f2.mag, f2.angle, f2_cm, max_val, theme=st.session_state.theme)
            # Resultant from origin to final tip
            draw_vector_with_labels(ax, 0, 0, r.x, r.y, '#28A745', 'FR',
                                   r.mag, r.angle, r_cm, max_val, width=0.004,
                                   highlight=True, theme=st.session_state.theme)
        
        # Angle arcs
        if method == "Parallelogram":
            # In parallelogram, show all angles from origin
            draw_angle_arc(ax, f1.angle, '#5B8DEE', max_val, ARC_F1_RADIUS_RATIO, theme=st.session_state.theme)
            draw_angle_arc(ax, f2.angle, '#FF6B6B', max_val, ARC_F2_RADIUS_RATIO, theme=st.session_state.theme)
        else:
            # In polygon, only show F1 angle from origin (F2 is tip-to-tail)
            draw_angle_arc(ax, f1.angle, '#5B8DEE', max_val, ARC_F1_RADIUS_RATIO, theme=st.session_state.theme)
        
        # Always show resultant angle
        draw_angle_arc(ax, r.angle, '#28A745', max_val, ARC_FR_RADIUS_RATIO,
                      linewidth=2.5, highlight=True, theme=st.session_state.theme)
        
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
        ax.set_facecolor(st.session_state.theme.background_color)
        ax.grid(True, alpha=0.3, color=st.session_state.theme.grid_color, linestyle='-', linewidth=0.5)
        ax.axhline(y=0, color=st.session_state.theme.grid_color, linewidth=1.5, zorder=2)
        ax.axvline(x=0, color=st.session_state.theme.grid_color, linewidth=1.5, zorder=2)
        
        ax.set_xlabel('X (N)', fontsize=11, color=st.session_state.theme.text_color, fontweight='600')
        ax.set_ylabel('Y (N)', fontsize=11, color=st.session_state.theme.text_color, fontweight='600')
        title = f'Vector Addition - {method} Method'
        ax.set_title(title, fontsize=13, fontweight='bold',
                    color=st.session_state.theme.text_color, pad=15)
        ax.tick_params(colors=st.session_state.theme.text_color)
        
        legend = ax.legend(loc='upper right', fontsize=10, framealpha=0.95,
                          edgecolor=st.session_state.theme.text_color)
        
        fig.tight_layout()
        st.pyplot(fig)
        
        # Export button
        if st.button("Download Plot (PNG)", use_container_width=True):
            from io import BytesIO
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            buf.seek(0)
            st.download_button(
                label="Click to Download",
                data=buf,
                file_name="vector_plot.png",
                mime="image/png",
                use_container_width=True
            )
        
        st.divider()
        
        # Two columns below for analytical and direct solution
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Resultant & Components")
            
            # Result metrics
            st.metric("Magnitude", f"{r.mag:.2f} N")
            st.metric("Length", f"{r.mag/scale:.2f} cm")
            st.metric("Angle", f"{r.angle:.2f}°")
            
            st.divider()
            
            st.subheader("Components")
            st.write(f"**X:** {r.x:.2f} N")
            st.write(f"**Y:** {r.y:.2f} N")
        
        with col_right:
            st.subheader("Direct Solution")
            solution_text = generate_direct_solution(f1, f2, r, scale)
            st.code(solution_text, language=None)
        
        # Detailed solution panel
        if show_solution:
            st.divider()
            st.subheader("Detailed Analytical Solution")
            detailed_solution_text = generate_solution_text(f1, f2, r, scale)
            st.code(detailed_solution_text, language=None)
        
        # History
        if len(st.session_state.history) > 1:
            with st.expander("Calculation History"):
                history = st.session_state.history.get_all()
                for i, entry in enumerate(reversed(history[-10:])):  # Show last 10
                    st.text(
                        f"{len(history)-i}. F₁={entry['f1_mag']}N@{entry['f1_angle']}° | "
                        f"F₂={entry['f2_mag']}N@{entry['f2_angle']}° → "
                        f"FR={entry['result']['mag']:.2f}N@{entry['result']['angle']:.2f}°"
                    )
    
    except ValueError as e:
        st.error(f"Error: {e}")
else:
    # Welcome message
    st.info("Enter force values in the sidebar and click Calculate to visualize vectors!")
    
    # Quick start guide
    with st.expander("Quick Start Guide"):
        st.markdown("""
        **How to use:**
        1. Choose visualization method:
           - **Parallelogram**: Both vectors start at the origin (classic)
           - **Polygon (Tip-to-Tail)**: Second vector starts at tip of first
        2. Set the scale (how many Newtons = 1 cm)
        3. Enter Force 1 magnitude and angle
        4. Enter Force 2 magnitude and angle
        5. Click **Calculate** to see the resultant vector
        
        **Features:**
        - Two visualization methods
        - Works on mobile devices
        - Step-by-step solution
        - Download plots as PNG
        - View calculation history
        
        **Angle Convention:**
        - 0° = Right (+X axis)
        - 90° = Up (+Y axis)
        - 180° = Left (-X axis)
        - 270° = Down (-Y axis)
        
        **Methods Explained:**
        - **Parallelogram**: Shows how vectors combine when both applied at same point
        - **Polygon**: Shows sequential application of forces (tip-to-tail)
        """)

# Footer
st.divider()
st.markdown("Developed by [Mar Luar](https://www.tiktok.com/@k00gs)")
