#!/usr/bin/env python3
"""
Streamlit Web App for Vector Addition Calculator
Mobile-friendly and deployable to Streamlit Cloud
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
# Set default font for Matplotlib (with fallbacks)
matplotlib.rcParams['font.family'] = ['Times New Roman', 'Times', 'Liberation Serif', 'Nimbus Roman', 'DejaVu Serif', 'serif']
matplotlib.rcParams['font.serif'] = ['Times New Roman', 'Times', 'Liberation Serif', 'Nimbus Roman', 'DejaVu Serif']
matplotlib.rcParams['mathtext.fontset'] = 'dejavuserif'
from matplotlib.figure import Figure
import matplotlib.patheffects as pe
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
if 'show_result' not in st.session_state:
    st.session_state.show_result = False

# Custom CSS for better mobile experience
st.markdown("""
<style>
    /* Global font */
html, body, [class*="css"], .stMarkdown, .stText, .stButton button, .stSelectbox, .stSlider, .stNumberInput, .stRadio {
        font-family: 'Times New Roman', Times, 'Liberation Serif', 'Nimbus Roman', 'DejaVu Serif', serif !important;
    }
    code, pre, .stCode {
        font-family: 'Times New Roman', Times, 'Liberation Serif', 'Nimbus Roman', 'DejaVu Serif', serif !important;
    }
    .stSlider > div > div > div > div {
        background-color: #5B8DEE;
    }
    .main > div {
        padding-top: 2rem;
    }
h1, h2, h3, h4, h5, h6 {
        color: #2C3E50;
        font-family: 'Times New Roman', Times, 'Liberation Serif', 'Nimbus Roman', 'DejaVu Serif', serif !important;
    }
    h1 { font-size: 2rem; }
    @media (max-width: 768px) {
        h1 { font-size: 1.5rem; }
        .stButton button { width: 100%; }
    }
    /* Classic manual styling */
    .manual-card {
        background: #FDFBF5;
        border: 1px solid #C9B99A;
        border-radius: 6px;
        padding: 18px 22px;
        box-shadow: 0 1px 0 rgba(0,0,0,0.04);
        color: #2C3E50;
        line-height: 1.6;
    }
    .manual-card h2, .manual-card h3 { color: #2C3E50; }
    .manual-card p, .manual-card li, .manual-card ul, .manual-card ol, .manual-card span { color: #2C3E50 !important; }
    .manual-card a { color: #2C3E50; text-decoration: underline; }
    .manual-card hr { border: none; border-top: 1px solid #C9B99A; margin: 10px 0 14px; }
    .manual-callout { font-style: italic; color: #5B4636; }
</style>
""", unsafe_allow_html=True)

# Header
st.title("Vector Addition Calculator")
st.markdown("Visualize and analyze force vectors")

# Start Guide — Classic Manual
with st.expander("Start Guide — User Manual", expanded=True):
    st.markdown(
        """
<div class="manual-card">
<h2>1. Introduction</h2>
<p>This application lets you visualize vector addition for different physical quantities (force, displacement, velocity, acceleration). The math is the same; only the units change.</p>
<hr/>

<h2>2. Page Layout</h2>
<h3>2.1 Sidebar — Settings</h3>
<ul>
  <li><b>Quantity Type</b>: Choose the vector type. Units update everywhere automatically.</li>
  <li><b>Visualization Method</b>: 
    <ul>
      <li><b>Parallelogram</b> — Both vectors start at the origin. Best for two vectors.</li>
      <li><b>Polygon (Tip-to-Tail)</b> — Vectors connect head-to-tail. Works for many vectors.</li>
    </ul>
  </li>
  <li><b>Scale</b>: Sets the drawing scale (e.g., 1 cm = 10 N). This affects labels like cm-length and the top-left scale badge only — not the math.</li>
  <li><b>Forces/Vectors</b>: Enter each vector’s <i>Magnitude</i> and <i>Angle</i> (degrees from +X, counterclockwise).</li>
  <li><b>Controls</b>: 
    <ul>
      <li><b>Calculate</b> — Computes and shows the resultant FR and steps.</li>
      <li><b>Show Steps</b> — Shows a detailed analytical solution.</li>
    </ul>
  </li>
</ul>

<h3>2.2 Main Area — Visualization</h3>
<ul>
  <li><b>Live Preview</b>: As you type, individual vectors are drawn <i>without</i> FR for guidance.</li>
  <li><b>Result View</b>: After clicking <b>Calculate</b>, the resultant <b>FR</b>, its components, and angle are displayed.</li>
  <li><b>Angle Convention</b>: 0°=+X, 90°=+Y, 180°=-X, 270°=-Y.</li>
  <li><b>Resultant Angle (θR)</b>: Emphasized near the arc. Negative angles are clockwise from +X and occur when FRᵧ &lt; 0.</li>
  <li><b>Scale Badge</b>: Top-left label shows the current scale (e.g., 1 cm = 10 N).</li>
</ul>
<hr/>

<h2>3. Result Details</h2>
<ul>
  <li><b>Magnitude / Components / Angle</b>: Numerical results after Calculate.</li>
  <li><b>Direct Solution</b>: A concise calculation transcript (no pedagogy).</li>
  <li><b>Detailed Analytical Solution</b>: Step-by-step reasoning. If any component is negative, the text explains <i>why</i> (signs from cos/sin and which side dominates).</li>
</ul>
<hr/>

<h2>4. Methods</h2>
<ul>
  <li><b>Parallelogram</b>: Draws both vectors from origin and FR as the diagonal; also shows construction lines.</li>
  <li><b>Polygon</b>: Draws vectors tip-to-tail and highlights the final FR from origin to the last tip.</li>
</ul>
<hr/>

<h2>5. Extras</h2>
<ul>
  <li><b>Download Plot</b>: Export the figure as PNG.</li>
  <li><b>Calculation History</b>: View recent runs (last 10 shown).</li>
  <li><b>Units</b>: Switch Quantity Type to use N, m, m/s, or m/s².</li>
</ul>
<hr/>

<h2>6. Tips & Notes</h2>
<ul>
  <li>FR only appears after clicking <b>Calculate</b>. Before that, you’ll see a live preview of your vectors.</li>
  <li>Angles near 90°/270° make cos≈0 (x≈0). Angles near 0°/180° make sin≈0 (y≈0).</li>
  <li>If the plot seems cramped, adjust the <b>Scale</b> or vector magnitudes to improve spacing.</li>
</ul>
</div>
""",
        unsafe_allow_html=True,
    )

# Helper to hide result when inputs change
def _hide_result():
    st.session_state.show_result = False

# Apply inline quick input changes to main inputs
def _apply_inline_changes():
    try:
        n = st.session_state.get('num_forces', 2)
        for i in range(1, n + 1):
            mag_key = f'inline_f{i}_mag'
            ang_key = f'inline_f{i}_angle'
            if mag_key in st.session_state:
                st.session_state[f'f{i}_mag'] = st.session_state[mag_key]
            if ang_key in st.session_state:
                st.session_state[f'f{i}_angle'] = st.session_state[ang_key]
        st.session_state.show_result = False
    except Exception:
        st.session_state.show_result = False

# Sidebar for inputs
with st.sidebar:
    st.header("Settings")

    # Quantity type selection (affects units only)
    st.subheader("Quantity Type")
    quantity = st.selectbox(
        "Choose vector type:",
        ["Force", "Displacement", "Velocity", "Acceleration"],
        index=0,
        help="Only the units change; calculations remain the same",
        on_change=_hide_result
    )
    units_map = {
        "Force": "N",
        "Displacement": "m",
        "Velocity": "m/s",
        "Acceleration": "m/s²",
    }
    unit_label = units_map.get(quantity, "N")
    
    # Method selection
    st.subheader("Visualization Method")
    method = st.radio(
        "Choose method:",
        ["Parallelogram", "Polygon (Tip-to-Tail)"],
        help="Parallelogram: Both vectors start at origin\nPolygon: Second vector starts at tip of first",
        on_change=_hide_result
    )
    
    st.divider()
    
    # Scale settings
    st.subheader("Scale")
    scale = st.number_input(f"1 cm equals ({unit_label}):", min_value=0.1, value=10.0, step=0.5, on_change=_hide_result)
    
    st.divider()
    
    # Number of forces (only for polygon method)
    if method == "Polygon (Tip-to-Tail)":
        st.subheader("Number of Forces")
        num_forces = st.number_input("How many forces?", min_value=2, max_value=10, value=st.session_state.num_forces, step=1, key="num_forces_input", on_change=_hide_result)
        st.session_state.num_forces = num_forces
        st.divider()
    else:
        num_forces = 2
    
    # Dynamic force inputs
    forces = []
    for i in range(num_forces):
        st.subheader(f"Force {i+1} (F{i+1})")
        mag = st.number_input(f"Magnitude ({unit_label}):", min_value=0.0, value=0.0, step=1.0, key=f"f{i+1}_mag", on_change=_hide_result)
        angle = st.number_input(f"Angle (°):", min_value=0.0, max_value=360.0, value=0.0, step=1.0, key=f"f{i+1}_angle", on_change=_hide_result)
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
if calculate_btn:
    try:
        # Calculate vectors and resultant only on Calculate
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
        st.session_state.show_result = True
        
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
                                       f1.mag, f1.angle, f1_cm, max_val, theme=st.session_state.theme, unit=unit_label)
                draw_vector_with_labels(ax, 0, 0, f2.x, f2.y, colors[1], 'F₂',
                                       f2.mag, f2.angle, f2_cm, max_val, theme=st.session_state.theme, unit=unit_label)
                draw_vector_with_labels(ax, 0, 0, r.x, r.y, '#28A745', 'FR',
                                       r.mag, r.angle, r_cm, max_val, width=0.004,
                                       highlight=True, theme=st.session_state.theme, unit=unit_label)
                
                # Construction lines for parallelogram
                ax.plot([f1.x, f1.x + f2.x], [f1.y, f1.y + f2.y],
                        color=colors[1], linestyle='--', linewidth=1.5, alpha=0.4)
                ax.plot([f2.x, f2.x + f1.x], [f2.y, f2.y + f1.y],
                        color=colors[0], linestyle='--', linewidth=1.5, alpha=0.4)
                
                # Angle arcs for parallelogram
                draw_angle_arc(ax, f1.angle, colors[0], max_val, ARC_F1_RADIUS_RATIO, theme=st.session_state.theme)
                draw_angle_arc(ax, f2.angle, colors[1], max_val, ARC_F2_RADIUS_RATIO, theme=st.session_state.theme)
        
        else:  # Polygon (Tip-to-Tail) method
            # Draw vectors tip-to-tail with labels and angle arcs
            cumulative_x, cumulative_y = 0.0, 0.0
            
            for i, v in enumerate(vector_list):
                v_cm = v.mag / scale
                subscript = chr(0x2080 + i + 1) if i < 10 else str(i + 1)
                color = colors[i % len(colors)]
                
                # Draw arrow (no label in quiver since we have title legend)
                ax.quiver(cumulative_x, cumulative_y, v.x, v.y, angles='xy', scale_units='xy', scale=1,
                          color=color, width=0.003, zorder=3)
                
                # Add force label near the middle of the vector
                mid_x = cumulative_x + v.x * 0.5
                mid_y = cumulative_y + v.y * 0.5
                # Rotate 180° for left-pointing vectors to keep readable
                label_rotation = 180 if (v.angle > 90 and v.angle < 270) else 0
                ax.text(mid_x, mid_y, f'F{subscript}', 
                        fontsize=10, color=color, fontweight='bold',
                        ha='center', va='center', zorder=10, rotation=label_rotation)
                
                # Add angle arc from starting point of each vector
                if abs(v.angle) > 0.1:  # Only draw if angle is significant
                    arc_radius = max_val * 0.1 * (0.8 + i * 0.2)  # Increasing radius for each vector
                    theta = np.linspace(0, np.radians(v.angle), 50)
                    arc_x = cumulative_x + arc_radius * np.cos(theta)
                    arc_y = cumulative_y + arc_radius * np.sin(theta)
                    ax.plot(arc_x, arc_y, color=color, linewidth=1.5, zorder=2, alpha=0.7)
                    
                    # Add angle label (always upright, positioned smartly)
                    label_angle_rad = np.radians(v.angle * 0.5)
                    label_radius = arc_radius * 1.3
                    label_x = cumulative_x + label_radius * np.cos(label_angle_rad)
                    label_y = cumulative_y + label_radius * np.sin(label_angle_rad)
                    ax.text(label_x, label_y, f'{v.angle:.0f}°', 
                            fontsize=8, color=color, fontweight='bold',
                            ha='center', va='center', zorder=10, rotation=0)
                
                # Add dot at tip
                tip_x = cumulative_x + v.x
                tip_y = cumulative_y + v.y
                ax.plot(tip_x, tip_y, 'o', color=color, markersize=5, zorder=4)
                
                cumulative_x += v.x
                cumulative_y += v.y
            
            # Draw resultant with highlight
            r_cm = r.mag / scale
            ax.quiver(0, 0, r.x, r.y, angles='xy', scale_units='xy', scale=1,
                      color='#28A745', width=0.004, 
                      label=f'FR = {r.mag:.2f}{unit_label}, θ = {r.angle:.2f}°', zorder=5)
            
            # Add FR label near the vector (no background)
            r_label_x = r.x * 0.35
            r_label_y = r.y * 0.35
            fr_bbox = dict(boxstyle='round,pad=0.25', facecolor='none',
                            edgecolor='#28A745', linewidth=1.5)
            fr_text = ax.text(r_label_x, r_label_y, 'FR', 
                    fontsize=12, color='black', fontweight='bold',
                    ha='center', va='center', zorder=12, bbox=fr_bbox)
            fr_text.set_path_effects([pe.withStroke(linewidth=2, foreground='white')])
            
            # Add magnitude label for resultant (no background)
            r_mid_x = r.x * 0.65
            r_mid_y = r.y * 0.65
            ax.text(r_mid_x, r_mid_y, f'{r_cm:.2f} cm', 
                    fontsize=10, color='#28A745', fontweight='bold',
                    ha='center', va='center', zorder=10)
        
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
        
        ax.set_xlabel(f'X ({unit_label})', fontsize=11, color=st.session_state.theme.text_color, fontweight='600')
        ax.set_ylabel(f'Y ({unit_label})', fontsize=11, color=st.session_state.theme.text_color, fontweight='600')
        
        # Create title with legend info inline
        if method == "Polygon (Tip-to-Tail)":
            # Build horizontal legend text
            legend_parts = []
            for i, v in enumerate(vector_list):
                subscript = chr(0x2080 + i + 1) if i < 10 else str(i + 1)
                legend_parts.append(f'F{subscript}={v.mag:.1f}{unit_label}@{v.angle:.0f}°')
            legend_parts.append(f'FR={r.mag:.1f}{unit_label}@{r.angle:.1f}°')
            title = f'Vector Addition - {method}\n' + ' | '.join(legend_parts)
            ax.set_title(title, fontsize=11, fontweight='bold',
                        color=st.session_state.theme.text_color, pad=10)
        else:
            title = f'Vector Addition - {method} Method'
            ax.set_title(title, fontsize=13, fontweight='bold',
                        color=st.session_state.theme.text_color, pad=15)
            # Keep legend for parallelogram
            legend = ax.legend(loc='upper right', fontsize=8, framealpha=0.95,
                              edgecolor=st.session_state.theme.text_color,
                              borderpad=0.4, labelspacing=0.3, handlelength=1.5, handletextpad=0.5)
        
        ax.tick_params(colors=st.session_state.theme.text_color)
        
        # Show scale in top-left corner
        ax.text(0.02, 0.98, f'Scale: 1 cm = {scale} {unit_label}', transform=ax.transAxes,
                fontsize=11, color=st.session_state.theme.text_color,
                ha='left', va='top', zorder=10,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor=st.session_state.theme.grid_color))
        
        fig.tight_layout()
        st.pyplot(fig, width='stretch')
        
        # Quick Inputs below plot
        st.divider()
        st.subheader("Quick Inputs")
        n_q = st.session_state.get('num_forces', len(vector_list))
        for i in range(1, n_q + 1):
            st.session_state.setdefault(f'inline_f{i}_mag', st.session_state.get(f'f{i}_mag', 0.0))
            st.session_state.setdefault(f'inline_f{i}_angle', st.session_state.get(f'f{i}_angle', 0.0))
            c1, c2 = st.columns(2)
            with c1:
                st.number_input(f"F{i} Magnitude ({unit_label})", min_value=0.0, step=1.0,
                                key=f'inline_f{i}_mag', on_change=_hide_result)
            with c2:
                st.number_input(f"F{i} Angle (°)", min_value=0.0, max_value=360.0, step=1.0,
                                key=f'inline_f{i}_angle', on_change=_hide_result)
        st.button("Apply Inline Changes", type="primary", use_container_width=True, on_click=_apply_inline_changes)
        
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
            st.metric("Magnitude", f"{r.mag:.2f} {unit_label}")
            st.metric("Length", f"{r.mag/scale:.2f} cm")
            st.metric("Angle", f"{r.angle:.2f}°")
            
            st.divider()
            
            st.subheader("Components")
            st.write(f"**X:** {r.x:.2f} {unit_label}")
            st.write(f"**Y:** {r.y:.2f} {unit_label}")
        
        with col_right:
            st.subheader("Direct Solution")
            if len(vector_list) >= 2:
                solution_text = generate_direct_solution(vector_list[0], vector_list[1], r, scale, unit=unit_label)
                st.code(solution_text, language=None)
            else:
                st.write("Solution text available for 2+ forces")
        
        # Detailed solution panel
        if show_solution:
            st.divider()
            st.subheader("Detailed Analytical Solution")
            if len(vector_list) >= 2:
                detailed_solution_text = generate_solution_text(vector_list[0], vector_list[1], r, scale, unit=unit_label)
                st.code(detailed_solution_text, language=None)
            else:
                st.write("Detailed solution available for 2+ forces")
        
        # History
        if len(st.session_state.history) > 1:
            with st.expander("Calculation History"):
                history = st.session_state.history.get_all()
                for i, entry in enumerate(reversed(history[-10:])):  # Show last 10
                    st.text(
                        f"{len(history)-i}. F₁={entry['f1_mag']}{unit_label}@{entry['f1_angle']}° | "
                        f"F₂={entry['f2_mag']}{unit_label}@{entry['f2_angle']}° → "
                        f"FR={entry['result']['mag']:.2f}{unit_label}@{entry['result']['angle']:.2f}°"
                    )
    
    except ValueError as e:
        st.error(f"Error: {e}")
elif st.session_state.get('show_result') and 'last_result' in st.session_state:
    # Re-display last calculated result without recalculation
    vector_list, r, scale_saved, method_saved = st.session_state.last_result
    method_to_use = method_saved
    scale_to_use = scale_saved
    
    st.subheader("Vector Visualization")
    st.info(f"🔹 **Method:** {method_to_use}")
    
    fig = Figure(figsize=(12, 7), dpi=100, facecolor=st.session_state.theme.background_color)
    ax = fig.add_subplot(111, facecolor=st.session_state.theme.background_color)
    
    # Compute max_val from saved vectors and r
    all_vals = [0]
    for v in vector_list:
        all_vals.extend([abs(v.x), abs(v.y)])
    all_vals.extend([abs(r.x), abs(r.y)])
    max_val = max(all_vals) if all_vals else 1.0
    
    colors = ['#5B8DEE', '#FF6B6B', '#9B59B6', '#F39C12', '#1ABC9C', '#E74C3C', '#3498DB', '#2ECC71', '#E67E22', '#95A5A6']
    
    if method_to_use == "Parallelogram" and len(vector_list) >= 2:
        f1, f2 = vector_list[0], vector_list[1]
        f1_cm = f1.mag / scale_to_use
        f2_cm = f2.mag / scale_to_use
        r_cm = r.mag / scale_to_use
        draw_vector_with_labels(ax, 0, 0, f1.x, f1.y, colors[0], 'F₁', f1.mag, f1.angle, f1_cm, max_val, theme=st.session_state.theme, unit=unit_label)
        draw_vector_with_labels(ax, 0, 0, f2.x, f2.y, colors[1], 'F₂', f2.mag, f2.angle, f2_cm, max_val, theme=st.session_state.theme, unit=unit_label)
        draw_vector_with_labels(ax, 0, 0, r.x, r.y, '#28A745', 'FR', r.mag, r.angle, r_cm, max_val, width=0.004, highlight=True, theme=st.session_state.theme, unit=unit_label)
        draw_angle_arc(ax, f1.angle, colors[0], max_val, ARC_F1_RADIUS_RATIO, theme=st.session_state.theme)
        draw_angle_arc(ax, f2.angle, colors[1], max_val, ARC_F2_RADIUS_RATIO, theme=st.session_state.theme)
    else:
        # Polygon display
        cumulative_x, cumulative_y = 0.0, 0.0
        for i, v in enumerate(vector_list):
            color = colors[i % len(colors)]
            ax.quiver(cumulative_x, cumulative_y, v.x, v.y, angles='xy', scale_units='xy', scale=1, color=color, width=0.003, zorder=3)
            mid_x = cumulative_x + v.x * 0.5
            mid_y = cumulative_y + v.y * 0.5
            label_rotation = 180 if (v.angle > 90 and v.angle < 270) else 0
            ax.text(mid_x, mid_y, f'F{chr(0x2080 + i + 1) if i < 10 else str(i+1)}', fontsize=10, color=color, fontweight='bold', ha='center', va='center', zorder=10, rotation=label_rotation)
            cumulative_x += v.x
            cumulative_y += v.y
        # Draw resultant
        ax.quiver(0, 0, r.x, r.y, angles='xy', scale_units='xy', scale=1, color='#28A745', width=0.004, label=f'FR = {r.mag:.2f}{unit_label}, θ = {r.angle:.2f}°', zorder=5)
        r_label_x = r.x * 0.35
        r_label_y = r.y * 0.35
        fr_bbox = dict(boxstyle='round,pad=0.25', facecolor='none', edgecolor='#28A745', linewidth=1.5)
        fr_text = ax.text(r_label_x, r_label_y, 'FR', fontsize=12, color='black', fontweight='bold', ha='center', va='center', zorder=12, bbox=fr_bbox)
        
    # Add resultant angle arc emphasis
    draw_angle_arc(ax, r.angle, '#28A745', max_val, ARC_FR_RADIUS_RATIO, linewidth=2.5, highlight=True, theme=st.session_state.theme)
    
    # Styling and axes
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
    ax.set_xlabel(f'X ({unit_label})', fontsize=11, color=st.session_state.theme.text_color, fontweight='600')
    ax.set_ylabel(f'Y ({unit_label})', fontsize=11, color=st.session_state.theme.text_color, fontweight='600')
    ax.set_title('Vector Addition Visualization', fontsize=13, fontweight='bold', color=st.session_state.theme.text_color, pad=15)
    ax.tick_params(colors=st.session_state.theme.text_color)

    # Scale annotation
    ax.text(0.02, 0.98, f'Scale: 1 cm = {scale_to_use} {unit_label}', transform=ax.transAxes, fontsize=11, color=st.session_state.theme.text_color, ha='left', va='top', zorder=10, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor=st.session_state.theme.grid_color))

    fig.tight_layout()
    st.pyplot(fig, width='stretch')

    # Quick Inputs below preview
    st.divider()
    st.subheader("Quick Inputs")
    for i in range(1, num_forces + 1):
        # Seed inline defaults from sidebar state
        st.session_state.setdefault(f'inline_f{i}_mag', st.session_state.get(f'f{i}_mag', 0.0))
        st.session_state.setdefault(f'inline_f{i}_angle', st.session_state.get(f'f{i}_angle', 0.0))
        c1, c2 = st.columns(2)
        with c1:
            st.number_input(f"F{i} Magnitude ({unit_label})", min_value=0.0, step=1.0,
                            key=f'inline_f{i}_mag', on_change=_hide_result)
        with c2:
            st.number_input(f"F{i} Angle (°)", min_value=0.0, max_value=360.0, step=1.0,
                            key=f'inline_f{i}_angle', on_change=_hide_result)
    st.button("Apply Inline Changes", type="primary", use_container_width=True, on_click=_apply_inline_changes)

else:
    # Live preview: plot current forces only (no FR) for visualization
    from vector_addition import VectorData
    vector_list = []
    for i, (mag, angle) in enumerate(forces):
        angle_rad = np.radians(angle)
        vx = mag * np.cos(angle_rad)
        vy = mag * np.sin(angle_rad)
        vector_list.append(VectorData(vx, vy, mag, angle))
    
    st.subheader("Live Preview (FR appears after Calculate)")
    fig = Figure(figsize=(12, 7), dpi=100, facecolor=st.session_state.theme.background_color)
    ax = fig.add_subplot(111, facecolor=st.session_state.theme.background_color)

    # Determine scale from forces only
    max_val = max([abs(v.x) for v in vector_list] + [abs(v.y) for v in vector_list] + [1e-6])
    colors = ['#5B8DEE', '#FF6B6B', '#9B59B6', '#F39C12', '#1ABC9C', '#E74C3C', '#3498DB', '#2ECC71', '#E67E22', '#95A5A6']

    if method == "Parallelogram":
        for i, v in enumerate(vector_list[:2]):
            v_cm = v.mag / scale if scale else 0
            draw_vector_with_labels(ax, 0, 0, v.x, v.y, colors[i % len(colors)], f'F{chr(0x2080 + i + 1) if i < 10 else str(i+1)}', v.mag, v.angle, v_cm, max_val, theme=st.session_state.theme, unit=unit_label)
            draw_angle_arc(ax, v.angle, colors[i % len(colors)], max_val, ARC_F1_RADIUS_RATIO if i == 0 else ARC_F2_RADIUS_RATIO, theme=st.session_state.theme)
    else:
        cumulative_x, cumulative_y = 0.0, 0.0
        for i, v in enumerate(vector_list):
            color = colors[i % len(colors)]
            ax.quiver(cumulative_x, cumulative_y, v.x, v.y, angles='xy', scale_units='xy', scale=1, color=color, width=0.003, zorder=3)
            mid_x = cumulative_x + v.x * 0.5
            mid_y = cumulative_y + v.y * 0.5
            label_rotation = 180 if (v.angle > 90 and v.angle < 270) else 0
            ax.text(mid_x, mid_y, f'F{chr(0x2080 + i + 1) if i < 10 else str(i+1)}', fontsize=10, color=color, fontweight='bold', ha='center', va='center', zorder=10, rotation=label_rotation)
            cumulative_x += v.x
            cumulative_y += v.y

    # Axes and styling
    x_vals = [0]
    y_vals = [0]
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
    ax.set_xlabel(f'X ({unit_label})', fontsize=11, color=st.session_state.theme.text_color, fontweight='600')
    ax.set_ylabel(f'Y ({unit_label})', fontsize=11, color=st.session_state.theme.text_color, fontweight='600')
    ax.set_title('Vector Preview', fontsize=13, fontweight='bold', color=st.session_state.theme.text_color, pad=15)
    ax.tick_params(colors=st.session_state.theme.text_color)

    # Scale annotation
    ax.text(0.02, 0.98, f'Scale: 1 cm = {scale} {unit_label}', transform=ax.transAxes, fontsize=11, color=st.session_state.theme.text_color, ha='left', va='top', zorder=10, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor=st.session_state.theme.grid_color))

    fig.tight_layout()
    st.pyplot(fig, width='stretch')

    # Quick Inputs below plot
    st.divider()
    st.subheader("Quick Inputs")
    n_q = st.session_state.get('num_forces', len(vector_list))
    for i in range(1, n_q + 1):
        st.session_state.setdefault(f'inline_f{i}_mag', st.session_state.get(f'f{i}_mag', 0.0))
        st.session_state.setdefault(f'inline_f{i}_angle', st.session_state.get(f'f{i}_angle', 0.0))
        c1, c2 = st.columns(2)
        with c1:
            st.number_input(f"F{i} Magnitude ({unit_label})", min_value=0.0, step=1.0,
                            key=f'inline_f{i}_mag', on_change=_hide_result)
        with c2:
            st.number_input(f"F{i} Angle (°)", min_value=0.0, max_value=360.0, step=1.0,
                            key=f'inline_f{i}_angle', on_change=_hide_result)
    st.button("Apply Inline Changes", type="primary", use_container_width=True, on_click=_apply_inline_changes)

