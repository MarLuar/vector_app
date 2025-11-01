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

# Custom CSS
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

def create_arc(angle_deg, radius, color, num_points=50):
    """Create arc points for angle annotation"""
    if abs(angle_deg) < 0.01:
        return [], []
    theta = np.linspace(0, np.radians(angle_deg), num_points)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    return x.tolist(), y.tolist()

def create_animated_vector_plot(f1, f2, r, scale, animate=True):
    """Create interactive Plotly plot with animations"""
    
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
            for vec, color, name in [(f1, '#5B8DEE', 'F₁'), (f2, '#FF6B6B', 'F₂'), 
                                      (r, '#28A745', 'FR')]:
                width = 6 if name == 'FR' else 4
                frame_data.append(go.Scatter(
                    x=[0, vec.x * eased],
                    y=[0, vec.y * eased],
                    mode='lines+markers',
                    line=dict(color=color, width=width),
                    marker=dict(size=[8, 12], color=color, symbol=['circle', 'arrow-bar-up']),
                    name=f'{name}: {vec.mag:.1f}N @ {vec.angle:.1f}°',
                    showlegend=True,
                    hovertemplate=f'{name}<br>Magnitude: {vec.mag:.2f}N<br>Angle: {vec.angle:.2f}°<extra></extra>'
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
    for vec, color, name in [(f1, '#5B8DEE', 'F₁'), (f2, '#FF6B6B', 'F₂'), (r, '#28A745', 'FR')]:
        width = 6 if name == 'FR' else 4
        static_data.append(go.Scatter(
            x=[0, vec.x], y=[0, vec.y],
            mode='lines+markers',
            line=dict(color=color, width=width),
            marker=dict(size=[8, 12], color=color, symbol=['circle', 'arrow-bar-up']),
            name=f'{name}: {vec.mag:.1f}N @ {vec.angle:.1f}°',
            hovertemplate=f'{name}<br>Magnitude: {vec.mag:.2f}N<br>Angle: {vec.angle:.2f}°<extra></extra>'
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
    
    # Layout
    x_min = min(0, f1.x, f2.x, r.x)
    x_max = max(0, f1.x, f2.x, r.x)
    y_min = min(0, f1.y, f2.y, r.y)
    y_max = max(0, f1.y, f2.y, r.y)
    
    fig.update_layout(
        title="Vector Addition Visualization",
        xaxis=dict(
            range=[min(x_min - padding, -min_neg), x_max + padding],
            zeroline=True, zerolinewidth=2, zerolinecolor='gray',
            gridcolor='lightgray', title='X (N)'
        ),
        yaxis=dict(
            range=[min(y_min - padding, -min_neg), y_max + padding],
            zeroline=True, zerolinewidth=2, zerolinecolor='gray',
            gridcolor='lightgray', title='Y (N)',
            scaleanchor="x", scaleratio=1
        ),
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
    
    return fig

# Header
st.title("Vector Addition Calculator")
st.markdown("Visualize and analyze force vectors with **smooth animations**")

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    scale = st.number_input("1 cm equals (N):", min_value=0.1, value=10.0, step=0.5)
    st.divider()
    
    st.subheader("Force 1 (F₁)")
    f1_mag = st.number_input("Magnitude (N):", min_value=0.0, value=50.0, step=1.0, key="f1_mag")
    f1_angle = st.slider("Angle (°):", 0, 360, 30, key="f1_angle")
    st.divider()
    
    st.subheader("Force 2 (F₂)")
    f2_mag = st.number_input("Magnitude (N):", min_value=0.0, value=40.0, step=1.0, key="f2_mag")
    f2_angle = st.slider("Angle (°):", 0, 360, 120, key="f2_angle")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        calculate_btn = st.button("Calculate", use_container_width=True, type="primary")
    with col2:
        animate = st.checkbox("Animate", value=True)
    
    show_solution = st.checkbox("Show Steps", value=False)

# Main content
if calculate_btn or 'last_result' in st.session_state:
    try:
        f1, f2, r = add_vectors(f1_mag, f1_angle, f2_mag, f2_angle)
        st.session_state.history.add(f1_mag, f1_angle, f2_mag, f2_angle, scale, r)
        st.session_state.last_result = (f1, f2, r, scale)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Vector Visualization")
            fig = create_animated_vector_plot(f1, f2, r, scale, animate)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Resultant (FR)")
            st.metric("Magnitude", f"{r.mag:.2f} N")
            st.metric("Length", f"{r.mag/scale:.2f} cm")
            st.metric("Angle", f"{r.angle:.2f}°")
            st.divider()
            st.subheader("Components")
            st.write(f"**X:** {r.x:.2f} N")
            st.write(f"**Y:** {r.y:.2f} N")
        
        if show_solution:
            st.divider()
            st.subheader("Analytical Solution")
            solution_text = generate_solution_text(f1, f2, r, scale)
            st.code(solution_text, language=None)
        
        if len(st.session_state.history) > 1:
            with st.expander("Calculation History"):
                history = st.session_state.history.get_all()
                for i, entry in enumerate(reversed(history[-10:])):
                    st.text(
                        f"{len(history)-i}. F₁={entry['f1_mag']}N@{entry['f1_angle']}° | "
                        f"F₂={entry['f2_mag']}N@{entry['f2_angle']}° → "
                        f"FR={entry['result']['mag']:.2f}N@{entry['result']['angle']:.2f}°"
                    )
    
    except ValueError as e:
        st.error(f"Error: {e}")
else:
    st.info("Enter force values in the sidebar and click **Calculate** to see animated vectors!")
    
    with st.expander("Quick Start Guide"):
        st.markdown("""
        **Features:**
        - **Smooth animations** for arrows and arcs
        - **Touch-friendly** - works perfectly on mobile
        - **Interactive** - hover over vectors for details
        - Toggle animation on/off with checkbox
        
        **How to use:**
        1. Enter force magnitudes and angles
        2. Check "Animate" for smooth animation
        3. Click Calculate to visualize
        4. Click "Play" button on plot to replay animation
        """)

st.divider()
st.caption("Built with Streamlit + Plotly • Vector Calculator v2.1 (Animated)")
