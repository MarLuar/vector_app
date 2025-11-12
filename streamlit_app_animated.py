#!/usr/bin/env python3
"""
Streamlit Web App with Plotly Animations
Mobile-friendly with smooth arrow animations
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from vector_addition import add_vectors, ColorTheme, VectorHistory, generate_solution_text

# Page config
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
if 'show_result' not in st.session_state:
    st.session_state.show_result = False

# Custom CSS
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

def create_arc(angle_deg, radius, color, num_points=50):
    """Create arc points for angle annotation"""
    if abs(angle_deg) < 0.01:
        return [], []
    theta = np.linspace(0, np.radians(angle_deg), num_points)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    return x.tolist(), y.tolist()

def create_animated_vector_plot(f1, f2, r, scale, animate=True, unit: str = 'N', quantity: str = 'Force'):
    """Create interactive Plotly plot with animations"""
    
    # Map quantity type to variable symbol
    var_symbols = {
        "Force": "F",
        "Displacement": "d",
        "Velocity": "V",
        "Acceleration": "a"
    }
    var_symbol = var_symbols.get(quantity, "F")
    
    # Calculate display values
    max_val = max(abs(f1.x), abs(f1.y), abs(f2.x), abs(f2.y), abs(r.x), abs(r.y))
    padding = max_val * 0.3
    min_neg = max_val * 0.15
    
    # Animation frames
    if animate:
        num_frames = 30
        arc_start_frame = 20
        frames = []
        
        for i in range(num_frames + 10):  # Extra frames for arc animation
            progress = min(1.0, i / num_frames)
            arc_progress = max(0, (i - arc_start_frame) / 10) if i >= arc_start_frame else 0
            
            # Eased progress
            eased = 1 - (1 - progress) ** 3
            arc_eased = 1 - (1 - arc_progress) ** 3
            
            frame_data = []
            
            # Vector arrows
            for vec, color, name in [(f1, '#5B8DEE', f'{var_symbol}₁'), (f2, '#FF6B6B', f'{var_symbol}₂'), 
                                      (r, '#28A745', f'{var_symbol}R')]:
                width = 6 if name.endswith('R') else 4
                frame_data.append(go.Scatter(
                    x=[0, vec.x * eased],
                    y=[0, vec.y * eased],
                    mode='lines+markers',
                    line=dict(color=color, width=width),
                    marker=dict(size=[8, 12], color=color, symbol=['circle', 'arrow-bar-up']),
                    name=f'{name}: {vec.mag:.1f}{unit} @ {vec.angle:.1f}°',
                    showlegend=True,
                    hovertemplate=f'{name}<br>Magnitude: {vec.mag:.2f}{unit}<br>Angle: {vec.angle:.2f}°<extra></extra>'
                ))
            
            # Construction lines (show after arrows complete)
            if progress >= 0.95:
                frame_data.extend([
                    go.Scatter(x=[f1.x, r.x], y=[f1.y, r.y], mode='lines',
                              line=dict(color='#FF6B6B', dash='dash', width=1.5),
                              showlegend=False, hoverinfo='skip', opacity=0.4),
                    go.Scatter(x=[f2.x, r.x], y=[f2.y, r.y], mode='lines',
                              line=dict(color='#5B8DEE', dash='dash', width=1.5),
                              showlegend=False, hoverinfo='skip', opacity=0.4)
                ])
            
            # Angle arcs (animate after arrows)
            if arc_eased > 0:
                for vec, color, radius_mult, name in [(f1, '#5B8DEE', 0.15, 'θ₁'), 
                                                       (f2, '#FF6B6B', 0.20, 'θ₂'),
                                                       (r, '#28A745', 0.25, 'θR')]:
                    arc_x, arc_y = create_arc(vec.angle * arc_eased, max_val * radius_mult, color)
                    if arc_x:
                        frame_data.append(go.Scatter(
                            x=arc_x, y=arc_y, mode='lines',
                            line=dict(color=color, width=2.5 if name == 'θR' else 2),
                            showlegend=False, hoverinfo='skip'
                        ))
                        # Arc label
                        if arc_eased > 0.5:
                            label_angle = vec.angle * arc_eased * 1.1
                            label_r = max_val * radius_mult * 1.15
                            label_x = label_r * np.cos(np.radians(label_angle))
                            label_y = label_r * np.sin(np.radians(label_angle))
                            frame_data.append(go.Scatter(
                                x=[label_x], y=[label_y], mode='text',
                                text=[f"{vec.angle * arc_eased:.1f}°"],
                                textfont=dict(size=11, color=color, family='Arial Black'),
                                showlegend=False, hoverinfo='skip'
                            ))
            
            frames.append(go.Frame(data=frame_data, name=str(i)))
    
    # Final static frame
    static_data = []
    
    # Vectors
    for vec, color, name in [(f1, '#5B8DEE', f'{var_symbol}₁'), (f2, '#FF6B6B', f'{var_symbol}₂'), (r, '#28A745', f'{var_symbol}R')]:
        width = 6 if name.endswith('R') else 4
        static_data.append(go.Scatter(
            x=[0, vec.x], y=[0, vec.y],
            mode='lines+markers',
            line=dict(color=color, width=width),
            marker=dict(size=[8, 12], color=color, symbol=['circle', 'arrow-bar-up']),
            name=f'{name}: {vec.mag:.1f}{unit} @ {vec.angle:.1f}°',
            hovertemplate=f'{name}<br>Magnitude: {vec.mag:.2f}{unit}<br>Angle: {vec.angle:.2f}°<extra></extra>'
        ))
    
    # Construction lines
    static_data.extend([
        go.Scatter(x=[f1.x, r.x], y=[f1.y, r.y], mode='lines',
                  line=dict(color='#FF6B6B', dash='dash', width=1.5),
                  showlegend=False, hoverinfo='skip', opacity=0.4),
        go.Scatter(x=[f2.x, r.x], y=[f2.y, r.y], mode='lines',
                  line=dict(color='#5B8DEE', dash='dash', width=1.5),
                  showlegend=False, hoverinfo='skip', opacity=0.4)
    ])
    
    # Arcs
    for vec, color, radius_mult in [(f1, '#5B8DEE', 0.15), (f2, '#FF6B6B', 0.20), (r, '#28A745', 0.25)]:
        arc_x, arc_y = create_arc(vec.angle, max_val * radius_mult, color)
        if arc_x:
            static_data.append(go.Scatter(
                x=arc_x, y=arc_y, mode='lines',
                line=dict(color=color, width=2.5 if color == '#28A745' else 2),
                showlegend=False, hoverinfo='skip'
            ))
            # Arc label
            label_angle = vec.angle * 1.1
            label_r = max_val * radius_mult * 1.15
            label_x = label_r * np.cos(np.radians(label_angle))
            label_y = label_r * np.sin(np.radians(label_angle))
            static_data.append(go.Scatter(
                x=[label_x], y=[label_y], mode='text',
                text=[f"{vec.angle:.1f}°"],
                textfont=dict(size=11, color=color, family='Arial Black'),
                showlegend=False, hoverinfo='skip'
            ))
    
    # Create figure
    fig = go.Figure(data=static_data, frames=frames if animate else None)

    # Add emphasized FR label annotation at ~35% along resultant
    fr_label_x = r.x * 0.35
    fr_label_y = r.y * 0.35
    fig.add_annotation(
        x=fr_label_x, y=fr_label_y, xref='x', yref='y', text=f'{var_symbol}R',
        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5,
        ax=0, ay=0,
        font=dict(size=12, color='black', family='Times New Roman, Times, Liberation Serif, Nimbus Roman, DejaVu Serif, serif'),
        align='center',
        bgcolor='rgba(0,0,0,0)',  # transparent background
        bordercolor='#28A745', borderwidth=1
    )
    
    # Layout
    x_min = min(0, f1.x, f2.x, r.x)
    x_max = max(0, f1.x, f2.x, r.x)
    y_min = min(0, f1.y, f2.y, r.y)
    y_max = max(0, f1.y, f2.y, r.y)

    # Emphasize resultant angle label
    ra_label_angle = r.angle * 1.1
    ra_label_radius = max_val * 0.25 * 1.2
    ra_label_x = ra_label_radius * np.cos(np.radians(ra_label_angle))
    ra_label_y = ra_label_radius * np.sin(np.radians(ra_label_angle))

    fig.add_annotation(
        x=ra_label_x, y=ra_label_y, xref='x', yref='y',
        text=f"θR = {r.angle:.1f}°",
        showarrow=False,
        font=dict(size=12, color='black', family='Times New Roman, Times, Liberation Serif, Nimbus Roman, DejaVu Serif, serif'),
        align='center',
        bgcolor='rgba(0,0,0,0)',
        bordercolor='#28A745', borderwidth=1
    )
    
    fig.update_layout(
        title="Vector Addition Visualization",
        xaxis=dict(
            range=[min(x_min - padding, -min_neg), x_max + padding],
            zeroline=True, zerolinewidth=2, zerolinecolor='gray',
            gridcolor='lightgray', title=f'{var_symbol}ₓ ({unit})'
        ),
        yaxis=dict(
            range=[min(y_min - padding, -min_neg), y_max + padding],
            zeroline=True, zerolinewidth=2, zerolinecolor='gray',
            gridcolor='lightgray', title=f'{var_symbol}ᵧ ({unit})',
            scaleanchor="x", scaleratio=1
        ),
font=dict(family='Times New Roman, Times, Liberation Serif, Nimbus Roman, DejaVu Serif, serif'),
        plot_bgcolor='#F0F8FF',
        hovermode='closest',
        showlegend=True,
        legend=dict(x=1, y=1, bgcolor='rgba(255,255,255,0.8)'),
        height=600,
    )
    
    # Animation settings
    if animate:
        fig.update_layout(
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [{
                    'label': '▶ Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 40, 'redraw': True},
                        'fromcurrent': True,
                        'mode': 'immediate'
                    }]
                }]
            }]
        )
        # Auto-play on load
        fig.layout.updatemenus[0].buttons[0].args[1]['transition'] = {'duration': 0}
    
    # Add scale annotation (top-left)
    fig.add_annotation(
        xref='paper', yref='paper', x=0.01, y=0.99, text=f'Scale: 1 cm = {scale} {unit}',
        showarrow=False, align='left', bgcolor='rgba(255,255,255,0.8)',
        bordercolor='lightgray', borderwidth=1, font=dict(size=12)
    )
    return fig

# Header
st.title("Vector Addition Calculator")
st.markdown("Visualize and analyze force vectors with **smooth animations**")

# Start Guide — Classic Manual
with st.expander("Start Guide — User Manual", expanded=True):
    st.markdown(
        """
<div class="manual-card">
<p>
  <b>Developer</b>: <a href="https://www.tiktok.com/@k00gs" target="_blank" rel="noopener noreferrer">Mar Luar Igot</a><br/>
  <b>Co-developer</b>: Alexander Miranda
</p>
<hr/>
<h2>1. Introduction</h2>
<p>This animated variant shows vectors and arcs smoothly for clearer understanding. The underlying math is unchanged: only units differ by the selected Quantity Type.</p>
<hr/>

<h2>2. Page Layout</h2>
<h3>2.1 Sidebar — Settings</h3>
<ul>
  <li><b>Quantity Type</b>: Select the vector type. Units update throughout.</li>
  <li><b>Scale</b>: Sets drawing scale (e.g., 1 cm = 10 N) used for labels and the scale badge.</li>
  <li><b>F₁ / F₂</b>: Magnitude and angle for each vector.</li>
  <li><b>Controls</b>: 
    <ul>
      <li><b>Calculate</b> — Computes and displays FR.</li>
      <li><b>Animate</b> — Toggles the animation playback.</li>
      <li><b>Show Steps</b> — Displays the analytical solution.</li>
    </ul>
  </li>
</ul>

<h3>2.2 Main Area — Visualization</h3>
<ul>
  <li><b>Live Preview</b>: While editing inputs, only the entered vectors are drawn. FR is hidden until you click <b>Calculate</b>.</li>
  <li><b>Animation</b>: Press Calculate to animate F₁, F₂, FR, construction lines, and the angle arcs.</li>
  <li><b>Resultant Angle (θR)</b>: Emphasized with a clean label; negative angles indicate clockwise rotation (FRᵧ &lt; 0).</li>
  <li><b>Scale Badge</b>: Top-left label shows the current scale.</li>
</ul>
<hr/>

<h2>3. Results & Steps</h2>
<ul>
  <li><b>Resultant Panel</b>: Magnitude, length in cm (by scale), and angle.</li>
  <li><b>Analytical Solution</b>: Includes sign explanations when components are negative and which contributions dominate.</li>
</ul>
<hr/>

<h2>4. Tips</h2>
<ul>
  <li>Use smaller scales for large magnitudes to keep the drawing readable.</li>
  <li>Angles near 90°/270° make x-components ≈ 0; near 0°/180° make y-components ≈ 0.</li>
</ul>
</div>
""",
        unsafe_allow_html=True,
    )

# Helper to hide result when inputs change
def _hide_result():
    st.session_state.show_result = False

# Sidebar
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
    # Variable symbol by quantity
    var_symbols = {
        "Force": "F",
        "Displacement": "d",
        "Velocity": "V",
        "Acceleration": "a",
    }
    var_symbol = var_symbols.get(quantity, "F")
    
    scale = st.number_input(f"1 cm equals ({unit_label}):", min_value=0.1, value=10.0, step=0.5, on_change=_hide_result)
    st.divider()
    
    st.subheader(f"{quantity} 1 ({var_symbol}₁)")
    f1_mag = st.number_input(f"Magnitude ({unit_label}):", min_value=0.0, value=0.0, step=1.0, key="f1_mag", on_change=_hide_result)
    f1_angle = st.slider("Angle (°):", 0, 360, 0, key="f1_angle", on_change=_hide_result)
    st.divider()
    
    st.subheader(f"{quantity} 2 ({var_symbol}₂)")
    f2_mag = st.number_input(f"Magnitude ({unit_label}):", min_value=0.0, value=0.0, step=1.0, key="f2_mag", on_change=_hide_result)
    f2_angle = st.slider("Angle (°):", 0, 360, 0, key="f2_angle", on_change=_hide_result)
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        calculate_btn = st.button("Calculate", use_container_width=True, type="primary")
    with col2:
        animate = st.checkbox("Animate", value=True)
    
    show_solution = st.checkbox("Show Steps", value=False)

# Main content
if calculate_btn:
    try:
        f1, f2, r = add_vectors(f1_mag, f1_angle, f2_mag, f2_angle)
        st.session_state.history.add(f1_mag, f1_angle, f2_mag, f2_angle, scale, r)
        st.session_state.last_result = (f1, f2, r, scale)
        st.session_state.show_result = True
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Vector Visualization")
            fig = create_animated_vector_plot(f1, f2, r, scale, animate, unit=unit_label, quantity=quantity)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader(f"Resultant ({var_symbol}R)")
            st.metric("Magnitude", f"{r.mag:.2f} {unit_label}")
            st.metric("Length", f"{r.mag/scale:.2f} cm")
            st.metric("Angle", f"{r.angle:.2f}°")
            st.divider()
            st.subheader("Components")
            st.write(f"**X:** {r.x:.2f} {unit_label}")
            st.write(f"**Y:** {r.y:.2f} {unit_label}")
        
        if show_solution:
            st.divider()
            st.subheader("Analytical Solution")
            solution_text = generate_solution_text(f1, f2, r, scale, unit=unit_label)
            for a, b in [
                ('F₁ₓ', f'{var_symbol}₁ₓ'), ('F₁ᵧ', f'{var_symbol}₁ᵧ'), ('F₂ₓ', f'{var_symbol}₂ₓ'), ('F₂ᵧ', f'{var_symbol}₂ᵧ'),
                ('FRₓ', f'{var_symbol}Rₓ'), ('FRᵧ', f'{var_symbol}Rᵧ'),
                ('F₁', f'{var_symbol}₁'), ('F₂', f'{var_symbol}₂'), ('FR', f'{var_symbol}R')
            ]:
                solution_text = solution_text.replace(a, b)
            st.code(solution_text, language=None)
        
        if len(st.session_state.history) > 1:
            with st.expander("Calculation History"):
                history = st.session_state.history.get_all()
                for i, entry in enumerate(reversed(history[-10:])):
                    st.text(
                        f"{len(history)-i}. F₁={entry['f1_mag']}{unit_label}@{entry['f1_angle']}° | "
                        f"F₂={entry['f2_mag']}{unit_label}@{entry['f2_angle']}° → "
                        f"FR={entry['result']['mag']:.2f}{unit_label}@{entry['result']['angle']:.2f}°"
                    )
    
    except ValueError as e:
        st.error(f"Error: {e}")
elif st.session_state.get('show_result') and 'last_result' in st.session_state:
    # Re-display last calculated result
    f1, f2, r, scale_saved = st.session_state.last_result
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Vector Visualization")
        fig = create_animated_vector_plot(f1, f2, r, scale_saved, animate, unit=unit_label, quantity=quantity)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader(f"Resultant ({var_symbol}R)")
        st.metric("Magnitude", f"{r.mag:.2f} {unit_label}")
        st.metric("Length", f"{r.mag/scale_saved:.2f} cm")
        st.metric("Angle", f"{r.angle:.2f}°")
else:
    # Live preview plot without FR
    st.subheader("Live Preview (FR appears after Calculate)")
    import plotly.graph_objects as go
    import numpy as np

    # Compute components
    f1_x = f1_mag * np.cos(np.radians(f1_angle))
    f1_y = f1_mag * np.sin(np.radians(f1_angle))
    f2_x = f2_mag * np.cos(np.radians(f2_angle))
    f2_y = f2_mag * np.sin(np.radians(f2_angle))

    # Determine ranges
    xs = [0, f1_x, f2_x]
    ys = [0, f1_y, f2_y]
    max_val = max([abs(x) for x in xs] + [abs(y) for y in ys] + [1e-6])
    padding = max_val * 0.3
    min_neg = max_val * 0.15

    data = []
    for (x, y, color, name, mag, ang) in [
        (f1_x, f1_y, '#5B8DEE', f'{var_symbol}₁', f1_mag, f1_angle),
        (f2_x, f2_y, '#FF6B6B', f'{var_symbol}₂', f2_mag, f2_angle)
    ]:
        data.append(go.Scatter(
            x=[0, x], y=[0, y], mode='lines+markers',
            line=dict(color=color, width=4),
            marker=dict(size=[8, 10], color=color),
            name=f'{name}: {mag:.1f}{unit_label} @ {ang:.1f}°'
        ))

    # Map quantity type to variable symbol
    var_symbols = {
        "Force": "F",
        "Displacement": "d",
        "Velocity": "V",
        "Acceleration": "a"
    }
    var_symbol = var_symbols.get(quantity, "F")
    
    fig = go.Figure(data=data)
    fig.update_layout(
        title="Vector Preview",
        xaxis=dict(range=[min(min(xs)-padding, -min_neg), max(xs)+padding], zeroline=True, zerolinewidth=2, zerolinecolor='gray', gridcolor='lightgray', title=f'{var_symbol}ₓ ({unit_label})'),
        yaxis=dict(range=[min(min(ys)-padding, -min_neg), max(ys)+padding], zeroline=True, zerolinewidth=2, zerolinecolor='gray', gridcolor='lightgray', title=f'{var_symbol}ᵧ ({unit_label})', scaleanchor='x', scaleratio=1),
        plot_bgcolor='#F0F8FF',
        font=dict(family='Times New Roman, Times, Liberation Serif, Nimbus Roman, DejaVu Serif, serif'),
        showlegend=True,
        height=600,
    )
    fig.add_annotation(xref='paper', yref='paper', x=0.01, y=0.99, text=f'Scale: 1 cm = {scale} {unit_label}', showarrow=False, align='left', bgcolor='rgba(255,255,255,0.8)', bordercolor='lightgray', borderwidth=1, font=dict(size=12))
    st.plotly_chart(fig, use_container_width=True)

    # Quick Inputs below preview (F₁ and F₂)
    st.divider()
    st.subheader("Quick Inputs")
    # Seed inline defaults
    st.session_state.setdefault('inline_f1_mag', st.session_state.get('f1_mag', 0.0))
    st.session_state.setdefault('inline_f1_angle', st.session_state.get('f1_angle', 0))
    st.session_state.setdefault('inline_f2_mag', st.session_state.get('f2_mag', 0.0))
    st.session_state.setdefault('inline_f2_angle', st.session_state.get('f2_angle', 0))
    c1, c2 = st.columns(2)
    with c1:
        st.number_input(f"{var_symbol}1 Magnitude ({unit_label})", min_value=0.0, step=1.0, key='inline_f1_mag', on_change=_hide_result)
        st.number_input(f"{var_symbol}2 Magnitude ({unit_label})", min_value=0.0, step=1.0, key='inline_f2_mag', on_change=_hide_result)
    with c2:
        st.number_input(f"{var_symbol}1 Angle (°)", min_value=0, max_value=360, step=1, key='inline_f1_angle', on_change=_hide_result)
        st.number_input(f"{var_symbol}2 Angle (°)", min_value=0, max_value=360, step=1, key='inline_f2_angle', on_change=_hide_result)

    def _apply_inline_changes_anim():
        try:
            st.session_state['f1_mag'] = st.session_state.get('inline_f1_mag', 0.0)
            st.session_state['f1_angle'] = st.session_state.get('inline_f1_angle', 0)
            st.session_state['f2_mag'] = st.session_state.get('inline_f2_mag', 0.0)
            st.session_state['f2_angle'] = st.session_state.get('inline_f2_angle', 0)
            st.session_state.show_result = False
        except Exception:
            st.session_state.show_result = False

    st.button("Apply Inline Changes", type="primary", use_container_width=True, on_click=_apply_inline_changes_anim)

st.divider()
st.caption("Built with Streamlit + Plotly • Vector Calculator v2.1 (Animated)")
