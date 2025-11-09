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
if 'num_forces' not in st.session_state:
    st.session_state.num_forces = 2

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
    
    # Number of forces (only for polygon method)
    if method == "Polygon (Tip-to-Tail)":
        st.subheader("Number of Forces")
        num_forces = st.number_input("How many forces?", min_value=2, max_value=10, value=st.session_state.num_forces, step=1, key="num_forces_input")
        st.session_state.num_forces = num_forces
        st.divider()
    else:
        num_forces = 2
    
    # Dynamic force inputs
    forces = []
    for i in range(num_forces):
        st.subheader(f"Force {i+1} (F�{i+1})")
        mag = st.number_input(f"Magnitude (N):", min_value=0.0, value=50.0 if i == 0 else 40.0, step=1.0, key=f"f{i+1}_mag")
        angle = st.number_input(f"Angle (°):", min_value=0.0, max_value=360.0, value=30.0 if i == 0 else 120.0 if i == 1 else 0.0, step=1.0, key=f"f{i+1}_angle")
        forces.append((mag, angle))
        st.divider()
    
    # Remove last divider
    st.markdown("")
    
    # Controls
    col1, col2 = st.columns(2)
    with col1:
        calculate_btn = st.button("Calculate", use_container_width=True, type="primary")
    with col2:
        show_solution = st.checkbox("Show Steps", value=False)

# Main content area
if calculate_btn or 'last_result' in st.session_state:
    try:
        # Calculate vectors for all forces
        from vector_addition import VectorData
        
        vector_list = []
        resultant_x, resultant_y = 0.0, 0.0
        
        for i, (mag, angle) in enumerate(forces):
            angle_rad = np.radians(angle)
            vx = mag * np.cos(angle_rad)
            vy = mag * np.sin(angle_rad)
            vector_list.append(VectorData(vx, vy, mag, angle))
            resultant_x += vx
            resultant_y += vy
        
        # Calculate resultant magnitude and angle
        r_mag = np.sqrt(resultant_x**2 + resultant_y**2)
        r_angle = np.degrees(np.arctan2(resultant_y, resultant_x))
        r = VectorData(resultant_x, resultant_y, r_mag, r_angle)
        
        # For history (only store first two forces for compatibility)
        if len(forces) >= 2:
            st.session_state.history.add(forces[0][0], forces[0][1], forces[1][0], forces[1][1], scale, r)
        
        st.session_state.last_result = (vector_list, r, scale, method)
        
        # Results section - Plot on top
        st.subheader("Vector Visualization")
        st.info(f"🔹 **Method:** {method}")
        
        # Create plot
        fig = Figure(figsize=(12, 7), dpi=100, facecolor=st.session_state.theme.background_color)
        ax = fig.add_subplot(111, facecolor=st.session_state.theme.background_color)
        
        # Calculate max value for scaling
        all_vals = [0]
        for v in vector_list:
            all_vals.extend([abs(v.x), abs(v.y)])
        all_vals.extend([abs(r.x), abs(r.y)])
        max_val = max(all_vals)
        
        # Color palette for multiple vectors
        colors = ['#5B8DEE', '#FF6B6B', '#9B59B6', '#F39C12', '#1ABC9C', '#E74C3C', '#3498DB', '#2ECC71', '#E67E22', '#95A5A6']
        
        if method == "Parallelogram":
            # Parallelogram method: only works for 2 vectors
            if len(vector_list) == 2:
                f1, f2 = vector_list[0], vector_list[1]
                f1_cm = f1.mag / scale
                f2_cm = f2.mag / scale
                r_cm = r.mag / scale
                
                draw_vector_with_labels(ax, 0, 0, f1.x, f1.y, colors[0], 'F₁',
                                       f1.mag, f1.angle, f1_cm, max_val, theme=st.session_state.theme)
                draw_vector_with_labels(ax, 0, 0, f2.x, f2.y, colors[1], 'F₂',
                                       f2.mag, f2.angle, f2_cm, max_val, theme=st.session_state.theme)
                draw_vector_with_labels(ax, 0, 0, r.x, r.y, '#28A745', 'FR',
                                       r.mag, r.angle, r_cm, max_val, width=0.004,
                                       highlight=True, theme=st.session_state.theme)
                
                # Construction lines for parallelogram
                ax.plot([f1.x, f1.x + f2.x], [f1.y, f1.y + f2.y],
                        color=colors[1], linestyle='--', linewidth=1.5, alpha=0.4)
                ax.plot([f2.x, f2.x + f1.x], [f2.y, f2.y + f1.y],
                        color=colors[0], linestyle='--', linewidth=1.5, alpha=0.4)
                
                # Angle arcs for parallelogram
                draw_angle_arc(ax, f1.angle, colors[0], max_val, ARC_F1_RADIUS_RATIO, theme=st.session_state.theme)
                draw_angle_arc(ax, f2.angle, colors[1], max_val, ARC_F2_RADIUS_RATIO, theme=st.session_state.theme)
        
        else:  # Polygon (Tip-to-Tail) method
            # Draw vectors tip-to-tail
            cumulative_x, cumulative_y = 0.0, 0.0
            
            for i, v in enumerate(vector_list):
                v_cm = v.mag / scale
                subscript = chr(0x2080 + i + 1) if i < 10 else str(i + 1)
                color = colors[i % len(colors)]
                
                draw_vector_with_labels(ax, cumulative_x, cumulative_y, v.x, v.y, color, f'F{subscript}',
                                       v.mag, v.angle, v_cm, max_val, theme=st.session_state.theme)
                
                # Draw angle arc only for first vector
                if i == 0:
                    draw_angle_arc(ax, v.angle, color, max_val, ARC_F1_RADIUS_RATIO, theme=st.session_state.theme)
                
                cumulative_x += v.x
                cumulative_y += v.y
            
            # Draw resultant
            r_cm = r.mag / scale
            draw_vector_with_labels(ax, 0, 0, r.x, r.y, '#28A745', 'FR',
                                   r.mag, r.angle, r_cm, max_val, width=0.004,
                                   highlight=True, theme=st.session_state.theme)
        
        # Always show resultant angle
        draw_angle_arc(ax, r.angle, '#28A745', max_val, ARC_FR_RADIUS_RATIO,
                      linewidth=2.5, highlight=True, theme=st.session_state.theme)
        
        # Styling
        x_vals = [0, r.x]
        y_vals = [0, r.y]
        cumulative_x, cumulative_y = 0.0, 0.0
        for v in vector_list:
            x_vals.extend([v.x, cumulative_x])
            y_vals.extend([v.y, cumulative_y])
            cumulative_x += v.x
            cumulative_y += v.y
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
            if len(vector_list) >= 2:
                solution_text = generate_direct_solution(vector_list[0], vector_list[1], r, scale)
                st.code(solution_text, language=None)
            else:
                st.write("Solution text available for 2+ forces")
        
        # Detailed solution panel
        if show_solution:
            st.divider()
            st.subheader("Detailed Analytical Solution")
            if len(vector_list) >= 2:
                detailed_solution_text = generate_solution_text(vector_list[0], vector_list[1], r, scale)
                st.code(detailed_solution_text, language=None)
            else:
                st.write("Detailed solution available for 2+ forces")
        
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
