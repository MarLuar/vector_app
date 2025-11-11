from typing import Tuple, Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patheffects as pe

# Visual constants
LABEL_POSITION_RATIO = 0.65  # Position along vector for measurement label
PERPENDICULAR_OFFSET_RATIO = 0.04  # Offset for labels perpendicular to vector
TIP_OFFSET_RATIO = 0.05  # Offset for tip labels
ARC_LABEL_OFFSET_RATIO = 1.15  # Position for angle arc labels
ARC_LABEL_RADIUS_RATIO = 1.08  # Radius offset for angle arc labels
PADDING_RATIO = 0.3  # Padding around plot
MIN_NEGATIVE_SPACE_RATIO = 0.15  # Minimum negative space on axes

# Arc radii ratios
ARC_BASE_RADIUS_RATIO = 0.15
ARC_F1_RADIUS_RATIO = 0.7
ARC_F2_RADIUS_RATIO = 1.0
ARC_FR_RADIUS_RATIO = 1.35

# Angle thresholds
PERPENDICULAR_THRESHOLD = 5  # degrees
RIGHT_ANGLE = 90

# Precision thresholds
ZERO_THRESHOLD = 1e-6


@dataclass
class VectorData:
    """Data class to hold vector component information."""
    x: float
    y: float
    mag: float
    angle: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ColorTheme:
    """Color theme for vector visualization."""
    name: str
    vector1_color: str
    vector2_color: str
    resultant_color: str
    background_color: str
    grid_color: str
    text_color: str
    highlight_color: str
    info_box_color: str
    solution_box_color: str
    
    @staticmethod
    def light_theme() -> 'ColorTheme':
        """Default light theme."""
        return ColorTheme(
            name="light",
            vector1_color="blue",
            vector2_color="red",
            resultant_color="black",
            background_color="white",
            grid_color="gray",
            text_color="black",
            highlight_color="yellow",
            info_box_color="lightblue",
            solution_box_color="white"
        )
    
    @staticmethod
    def dark_theme() -> 'ColorTheme':
        """Dark theme for better visibility in low light."""
        return ColorTheme(
            name="dark",
            vector1_color="#00D4FF",  # Cyan
            vector2_color="#FF6B6B",  # Coral red
            resultant_color="#FFD93D",  # Yellow
            background_color="#1E1E1E",
            grid_color="#3A3A3A",
            text_color="white",
            highlight_color="#FF6B6B",
            info_box_color="#2D2D2D",
            solution_box_color="#252525"
        )
    
    @staticmethod
    def ocean_theme() -> 'ColorTheme':
        """Ocean color theme."""
        return ColorTheme(
            name="ocean",
            vector1_color="#0077BE",
            vector2_color="#00A896",
            resultant_color="#FF6B35",
            background_color="#F0F8FF",
            grid_color="#B0C4DE",
            text_color="#003366",
            highlight_color="#FFD700",
            info_box_color="#E0F2FF",
            solution_box_color="#FAFAFA"
        )


class VectorHistory:
    """Track history of vector calculations."""
    
    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.history: List[Dict[str, Any]] = []
    
    def add(self, f1_mag: float, f1_angle: float, f2_mag: float, f2_angle: float,
            scale: float, result: VectorData) -> None:
        """Add a calculation to history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "f1_mag": f1_mag,
            "f1_angle": f1_angle,
            "f2_mag": f2_mag,
            "f2_angle": f2_angle,
            "scale": scale,
            "result": result.to_dict()
        }
        self.history.append(entry)
        
        # Keep only max_size entries
        if len(self.history) > self.max_size:
            self.history = self.history[-self.max_size:]
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all history entries."""
        return self.history.copy()
    
    def get_last(self, n: int = 1) -> List[Dict[str, Any]]:
        """Get last n entries."""
        return self.history[-n:] if self.history else []
    
    def clear(self) -> None:
        """Clear all history."""
        self.history.clear()
    
    def save_to_file(self, filepath: str) -> None:
        """Save history to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def load_from_file(self, filepath: str) -> None:
        """Load history from JSON file."""
        with open(filepath, 'r') as f:
            self.history = json.load(f)
    
    def __len__(self) -> int:
        return len(self.history)


def validate_input(magnitude: float, angle: float, name: str) -> None:
    """
    Validate vector input parameters.
    
    Args:
        magnitude: Vector magnitude (must be non-negative)
        angle: Vector angle in degrees
        name: Name of the vector for error messages
        
    Raises:
        ValueError: If magnitude is negative
    """
    if magnitude < 0:
        raise ValueError(f"{name} magnitude must be non-negative, got {magnitude}")


def add_vectors(f1_mag: float, f1_angle: float, f2_mag: float, f2_angle: float) -> Tuple[VectorData, VectorData, VectorData]:
    """
    Add two force vectors given magnitude and angle.
    
    Args:
        f1_mag: Magnitude of force 1 (N)
        f1_angle: Angle of force 1 (degrees, measured from positive x-axis)
        f2_mag: Magnitude of force 2 (N)
        f2_angle: Angle of force 2 (degrees)
    
    Returns:
        Tuple of (force1_data, force2_data, resultant_data)
        
    Raises:
        ValueError: If magnitudes are negative
    """
    validate_input(f1_mag, f1_angle, "Force 1")
    validate_input(f2_mag, f2_angle, "Force 2")
    
    # Convert angles to radians
    f1_rad = np.radians(f1_angle)
    f2_rad = np.radians(f2_angle)
    
    # Calculate components
    f1_x = f1_mag * np.cos(f1_rad)
    f1_y = f1_mag * np.sin(f1_rad)
    
    f2_x = f2_mag * np.cos(f2_rad)
    f2_y = f2_mag * np.sin(f2_rad)
    
    # Resultant
    r_x = f1_x + f2_x
    r_y = f1_y + f2_y
    r_mag = np.sqrt(r_x**2 + r_y**2)
    r_angle = np.degrees(np.arctan2(r_y, r_x))
    
    return (VectorData(f1_x, f1_y, f1_mag, f1_angle),
            VectorData(f2_x, f2_y, f2_mag, f2_angle),
            VectorData(r_x, r_y, r_mag, r_angle))

def format_measurement(value: float) -> str:
    """
    Format a measurement value by removing trailing zeros and decimal point.
    
    Args:
        value: The numeric value to format
        
    Returns:
        Formatted string
    """
    return f'{value:.3f}'.rstrip('0').rstrip('.')


def draw_vector_with_labels(ax, origin_x: float, origin_y: float, vx: float, vy: float,
                            color: str, label: str, mag: float, angle: float, 
                            cm_value: float, max_val: float, width: float = 0.003,
                            highlight: bool = False, theme: Optional[ColorTheme] = None) -> None:
    """
    Draw a vector arrow with measurement and label annotations.
    
    Args:
        ax: Matplotlib axes object
        origin_x, origin_y: Starting point of vector
        vx, vy: Vector components
        color: Arrow color
        label: Vector label (e.g., 'F₁', 'F₂', 'FR')
        mag: Magnitude in Newtons
        angle: Angle in degrees
        cm_value: Length in centimeters
        max_val: Maximum value for offset calculations
        width: Arrow width
        highlight: Whether to highlight with yellow background
    """
    # Draw arrow with 2 decimal places for magnitude and angle
    ax.quiver(origin_x, origin_y, vx, vy, angles='xy', scale_units='xy', scale=1,
              color=color, width=width, label=f'{label} = {mag:.2f}N, θ = {angle:.2f}°')
    
    # Calculate positions and offsets
    mid_x = origin_x + vx * LABEL_POSITION_RATIO
    mid_y = origin_y + vy * LABEL_POSITION_RATIO
    perp_angle = np.radians(angle - 90)
    offset_dist = max_val * PERPENDICULAR_OFFSET_RATIO
    
    # Add measurement label
    if theme is None:
        theme = ColorTheme.ocean_theme()
    
    bbox_style = dict(boxstyle='round,pad=0.4', facecolor=theme.highlight_color, 
                     edgecolor=color, linewidth=2, alpha=0.9) if highlight else None
    
    ax.text(mid_x + offset_dist * np.cos(perp_angle),
            mid_y + offset_dist * np.sin(perp_angle),
            f'{format_measurement(cm_value)} cm',
            fontsize=14, color=color, fontweight='bold', ha='center', va='center',
            rotation=angle, rotation_mode='anchor', zorder=10, bbox=bbox_style)
    
    # Add vector label at tip
    tip_offset = max_val * TIP_OFFSET_RATIO
    tip_x = origin_x + vx + tip_offset * np.cos(perp_angle)
    tip_y = origin_y + vy + tip_offset * np.sin(perp_angle)
    
    label_bbox = dict(boxstyle='round,pad=0.3', facecolor=theme.background_color, edgecolor=color)
    if highlight:
        label_bbox = dict(boxstyle='round,pad=0.3', facecolor=theme.background_color, 
                         edgecolor=theme.resultant_color)
    
    ax.text(tip_x, tip_y, label, fontsize=13, color=color if not highlight else 'black',
            fontweight='bold', bbox=label_bbox, zorder=10)


def draw_angle_arc(ax, angle: float, color: str, max_val: float, 
                   radius_ratio: float, linewidth: float = 2,
                   highlight: bool = False, theme: Optional[ColorTheme] = None) -> None:
    """
    Draw an angle arc from the positive x-axis.
    
    Args:
        ax: Matplotlib axes object
        angle: Angle in degrees
        color: Arc color
        max_val: Maximum value for radius calculation
        radius_ratio: Ratio for arc radius
        linewidth: Line width for arc
        highlight: Whether to highlight with yellow background
    """
    if abs(angle) < ZERO_THRESHOLD:
        return
    
    arc_radius = max_val * ARC_BASE_RADIUS_RATIO * radius_ratio
    theta = np.linspace(0, np.radians(angle), 50)
    arc_x = arc_radius * np.cos(theta)
    arc_y = arc_radius * np.sin(theta)
    ax.plot(arc_x, arc_y, color=color, linewidth=linewidth)
    
    # Add label at arc tip
    tip_angle_rad = np.radians(angle * ARC_LABEL_OFFSET_RATIO)
    tip_radius = arc_radius * ARC_LABEL_RADIUS_RATIO
    tip_x = tip_radius * np.cos(tip_angle_rad)
    tip_y = tip_radius * np.sin(tip_angle_rad)
    
    if theme is None:
        theme = ColorTheme.ocean_theme()
    
    bbox_style = dict(boxstyle='round,pad=0.4', facecolor=theme.highlight_color,
                     edgecolor=color, linewidth=2, alpha=0.9) if highlight else None
    
    precision = 1 if highlight else 0
    angle_text = f'{angle:.{precision}f}°'
    
    ax.text(tip_x, tip_y, angle_text, fontsize=14, color=color if not highlight else 'black',
            fontweight='bold', ha='center', va='center',
            rotation=angle - 90, rotation_mode='anchor', zorder=10, bbox=bbox_style)


def quadrant(angle_deg: float) -> str:
    """Determine which quadrant or axis an angle points to."""
    a = angle_deg % 360
    if np.isclose(a, 0) or np.isclose(a, 360):
        return '+x axis'
    if np.isclose(a, 90):
        return '+y axis'
    if np.isclose(a, 180):
        return '-x axis'
    if np.isclose(a, 270):
        return '-y axis'
    if 0 < a < 90:
        return 'Q1'
    if 90 < a < 180:
        return 'Q2'
    if 180 < a < 270:
        return 'Q3'
    return 'Q4'


def relative_angle(a: float, b: float) -> float:
    """Calculate the relative angle between two angles."""
    d = (b - a) % 360
    return d if d <= 180 else 360 - d


def contribution_note(a: float, b: float, axis: str) -> str:
    """Determine which force dominates on a given axis."""
    sa, sb = abs(a), abs(b)
    if sa + sb == 0:
        return f'No net {axis} component'
    lead = 'F₁' if sa > sb else ('F₂' if sb > sa else 'F₁ and F₂ equally')
    return f'{lead} dominates {axis}'


def generate_solution_text(f1: VectorData, f2: VectorData, r: VectorData, 
                          scale: float) -> str:
    """
    Generate detailed analytical solution text.
    
    Args:
        f1, f2: Input force vector data
        r: Resultant vector data
        scale: Scale factor (N per cm)
        
    Returns:
        Formatted solution text
    """
    f1_cm = f1.mag / scale
    f2_cm = f2.mag / scale
    r_cm = r.mag / scale
    
    angle_between = relative_angle(f1.angle, f2.angle)
    relation = 'reinforce each other' if angle_between < 90 else (
        'are nearly perpendicular' if abs(angle_between - 90) <= PERPENDICULAR_THRESHOLD 
        else 'partly cancel each other')
    
    q1 = quadrant(f1.angle)
    q2 = quadrant(f2.angle)
    qr = quadrant(r.angle)
    
    x_note = contribution_note(f1.x, f2.x, 'horizontal')
    y_note = contribution_note(f1.y, f2.y, 'vertical')
    
    near_vertical = abs(r.x) < ZERO_THRESHOLD
    near_horizontal = abs(r.y) < ZERO_THRESHOLD
    
    text = 'ANALYTICAL SOLUTION\n'
    text += '=' * 70 + '\n\n'
    
    text += 'UNDERSTANDING THE PROBLEM\n'
    text += f'  • F₁ points to {q1}, F₂ points to {q2}\n'
    text += f'  • Angle between them: {angle_between:.1f}° → they {relation}\n'
    if angle_between < 90:
        text += f'    (< 90° means forces pull in similar directions)\n'
    elif abs(angle_between - 90) <= PERPENDICULAR_THRESHOLD:
        text += f'    (≈ 90° means forces are perpendicular)\n'
    else:
        text += f'    (> 90° means forces pull in opposite directions)\n'
    text += f'  • {x_note}; {y_note}\n\n'
    
    text += 'STEP 1: Break forces into x and y parts\n'
    text += '  WHY? Angled forces are hard to add. We split them into\n'
    text += '  horizontal (x) and vertical (y) parts first.\n\n'
    text += f'  F₁: {f1.mag}N at {f1.angle}°\n'
    text += f'    x-part: {f1.mag}×cos({f1.angle}°) = {f1.x:.2f}N (how much pushes right)\n'
    text += f'    y-part: {f1.mag}×sin({f1.angle}°) = {f1.y:.2f}N (how much pushes up)\n\n'
    text += f'  F₂: {f2.mag}N at {f2.angle}°\n'
    text += f'    x-part: {f2.mag}×cos({f2.angle}°) = {f2.x:.2f}N\n'
    text += f'    y-part: {f2.mag}×sin({f2.angle}°) = {f2.y:.2f}N\n\n'
    
    text += 'STEP 2: Add all x\'s together, add all y\'s together\n'
    text += '  WHY? Now that forces are split, we can add same directions.\n'
    text += '  All horizontal forces combine to make total horizontal.\n'
    text += '  All vertical forces combine to make total vertical.\n\n'
    text += f'  Total x: {f1.x:.2f} + {f2.x:.2f} = {r.x:.2f}N\n'
    if r.x > 0:
        text += f'           (positive = net push to the right)\n'
    elif r.x < 0:
        text += f'           (negative = net push to the left)\n'
    text += f'  Total y: {f1.y:.2f} + {f2.y:.2f} = {r.y:.2f}N\n'
    if r.y > 0:
        text += f'           (positive = net push upward)\n'
    elif r.y < 0:
        text += f'           (negative = net push downward)\n'
    text += '\n'
    
    text += 'STEP 3: Find the total strength (magnitude)\n'
    text += '  WHY? We have x and y parts, but need the actual force size.\n'
    text += '  Use Pythagorean theorem: diagonal of a right triangle.\n\n'
    text += f'  |FR| = √(x² + y²) = √({r.x:.2f}² + {r.y:.2f}²)\n'
    text += f'       = {r.mag:.2f}N\n'
    text += f'       = {format_measurement(r_cm)} cm (using scale: 1cm = {scale}N)\n\n'
    
    text += 'STEP 4: Find which direction it points\n'
    text += '  WHY? We know the strength, but need to know where it points.\n'
    text += '  Use atan2(y,x) which gives angle from +x axis.\n'
    if near_vertical:
        text += '  NOTE: x≈0, so force is nearly vertical (90° or 270°)\n'
    elif near_horizontal:
        text += '  NOTE: y≈0, so force is nearly horizontal (0° or 180°)\n'
    text += f'\n  θ = atan2({r.y:.2f}, {r.x:.2f}) = {r.angle:.2f}°\n'
    text += f'  Result: FR points to {qr}\n'
    if 0 <= r.angle < 90:
        text += '         (up and to the right)\n'
    elif 90 <= r.angle < 180:
        text += '         (up and to the left)\n'
    elif -180 <= r.angle < -90:
        text += '         (down and to the left)\n'
    else:
        text += '         (down and to the right)\n'
    
    return text


def plot_vectors(f1_mag: float, f1_angle: float, f2_mag: float, f2_angle: float, 
                scale: float = 10, theme: Optional[ColorTheme] = None,
                save_path: Optional[str] = None, save_format: str = 'png',
                history: Optional[VectorHistory] = None) -> None:
    """
    Plot the two force vectors and their resultant with detailed annotations.
    
    Args:
        f1_mag: Magnitude of force 1 (N)
        f1_angle: Angle of force 1 (degrees)
        f2_mag: Magnitude of force 2 (N)
        f2_angle: Angle of force 2 (degrees)
        scale: N per cm (e.g., 10 means 1 cm = 10 N)
        theme: Color theme for visualization
        save_path: Path to save the plot (if None, displays interactively)
        save_format: Format for saving ('png', 'svg', 'pdf')
        history: VectorHistory object to track calculations
    """
    f1, f2, r = add_vectors(f1_mag, f1_angle, f2_mag, f2_angle)
    
    # Add to history if provided
    if history is not None:
        history.add(f1_mag, f1_angle, f2_mag, f2_angle, scale, r)
    
    # Use default theme if not provided
    if theme is None:
        theme = ColorTheme.ocean_theme()
    
    # Convert to cm based on scale
    f1_cm = f1.mag / scale
    f2_cm = f2.mag / scale
    r_cm = r.mag / scale
    
    fig, ax = plt.subplots(figsize=(20, 10), facecolor=theme.background_color)
    ax.set_facecolor(theme.background_color)
    
    # Calculate max value for scaling (needed for offsets)
    max_val = max(abs(f1.x), abs(f1.y), abs(f2.x), abs(f2.y), abs(r.x), abs(r.y))
    
    # Draw vectors with labels
    draw_vector_with_labels(ax, 0, 0, f1.x, f1.y, theme.vector1_color, 'F₁', f1.mag, f1.angle, 
                           f1_cm, max_val, theme=theme)
    draw_vector_with_labels(ax, 0, 0, f2.x, f2.y, theme.vector2_color, 'F₂', f2.mag, f2.angle, 
                           f2_cm, max_val, theme=theme)
    draw_vector_with_labels(ax, 0, 0, r.x, r.y, theme.resultant_color, 'FR', r.mag, r.angle, 
                           r_cm, max_val, width=0.004, highlight=True, theme=theme)
    
    # Draw parallelogram construction lines
    ax.plot([f1.x, f1.x + f2.x], [f1.y, f1.y + f2.y], color=theme.vector2_color, 
            linestyle='--', linewidth=1.5, alpha=0.6, zorder=1)
    ax.plot([f2.x, f2.x + f1.x], [f2.y, f2.y + f1.y], color=theme.vector1_color, 
            linestyle='--', linewidth=1.5, alpha=0.6, zorder=1)
    
    # Draw angle arcs
    draw_angle_arc(ax, f1.angle, theme.vector1_color, max_val, ARC_F1_RADIUS_RATIO, theme=theme)
    draw_angle_arc(ax, f2.angle, theme.vector2_color, max_val, ARC_F2_RADIUS_RATIO, theme=theme)
    draw_angle_arc(ax, r.angle, theme.resultant_color, max_val, ARC_FR_RADIUS_RATIO, 
                  linewidth=2.5, highlight=True, theme=theme)
    
    # Set equal aspect ratio and grid
    x_vals = [0, f1.x, f2.x, r.x]
    y_vals = [0, f1.y, f2.y, r.y]
    x_min, x_max = min(x_vals), max(x_vals)
    y_min, y_max = min(y_vals), max(y_vals)
    
    # Add padding and ensure some negative space is visible
    padding = max_val * PADDING_RATIO
    min_neg_space = max_val * MIN_NEGATIVE_SPACE_RATIO
    
    ax.set_xlim(min(x_min - padding, -min_neg_space), x_max + padding)
    ax.set_ylim(min(y_min - padding, -min_neg_space), y_max + padding)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, color=theme.grid_color)
    ax.axhline(y=0, color=theme.grid_color, linewidth=0.5)
    ax.axvline(x=0, color=theme.grid_color, linewidth=0.5)
    
    # Labels and title
    ax.set_xlabel('Fₓ (N)', fontsize=12, color=theme.text_color)
    ax.set_ylabel('Fᵧ (N)', fontsize=12, color=theme.text_color)
    ax.set_title('Vector Addition of Forces', fontsize=14, fontweight='bold', color=theme.text_color)
    ax.tick_params(colors=theme.text_color)
    
    # Create legend with emphasis on FR
    legend = ax.legend(loc='upper right', fontsize=13, framealpha=0.95)
    legend.get_texts()[2].set_fontweight('bold')
    legend.get_texts()[2].set_fontsize(15)
    
    # Add scale below legend
    ax.text(0.98, 0.88, f'Scale: 1 cm = {scale} N', transform=ax.transAxes,
            fontsize=12, ha='right', va='top', color=theme.text_color,
            bbox=dict(boxstyle='round,pad=0.5', facecolor=theme.highlight_color, 
                     edgecolor=theme.text_color, linewidth=1.5))
    
    # Display given information
    info_text = f'Given:\n'
    info_text += f'F₁ = {f1.mag} N, θ = {f1.angle}°\n'
    info_text += f'F₂ = {f2.mag} N, θ = {f2.angle}°\n'
    info_text += f'\nScale: 1 cm = {scale} N'
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
            fontsize=13, verticalalignment='top', fontweight='bold', color=theme.text_color,
            bbox=dict(boxstyle='round,pad=0.7', facecolor=theme.info_box_color, 
                     edgecolor=theme.text_color, linewidth=2, alpha=0.9))
    
    # Add analytical solution text
    solution_text = generate_solution_text(f1, f2, r, scale)
    ax.text(1.03, 0.5, solution_text, transform=ax.transAxes,
            fontsize=13, verticalalignment='center', horizontalalignment='left',
            family='monospace', color=theme.text_color,
            bbox=dict(boxstyle='round,pad=0.8', facecolor=theme.solution_box_color, 
                     edgecolor=theme.text_color, linewidth=2))
    
    plt.tight_layout()
    
    # Save or show
    if save_path:
        plt.savefig(save_path, format=save_format, dpi=300, bbox_inches='tight',
                   facecolor=theme.background_color)
        print(f"Plot saved to: {save_path}")
    else:
        plt.show()

if __name__ == "__main__":
    print("Vector Addition Calculator")
    print("=" * 40)
    
    # Get user input
    try:
        scale = float(input("Enter scale (1 cm = ? N): "))
        f1_mag = float(input("Enter magnitude of Force 1 (N): "))
        f1_angle = float(input("Enter angle of Force 1 (degrees): "))
        f2_mag = float(input("Enter magnitude of Force 2 (N): "))
        f2_angle = float(input("Enter angle of Force 2 (degrees): "))
    except ValueError:
        print("\nUsing default values...")
        scale = 10
        f1_mag, f1_angle = 50, 30
        f2_mag, f2_angle = 40, 120
    
    print(f"\nF₁ = {f1_mag} N at {f1_angle}°")
    print(f"F₂ = {f2_mag} N at {f2_angle}°")
    
    # Calculate
    try:
        f1, f2, r = add_vectors(f1_mag, f1_angle, f2_mag, f2_angle)
        
        print(f"\nScale: 1 cm = {scale} N")
        print(f"Resultant: {r.mag:.2f} N ({r.mag/scale:.2f} cm) at {r.angle:.2f}°")
        print(f"Components: ({r.x:.2f}, {r.y:.2f}) N")
        
        # Plot
        plot_vectors(f1_mag, f1_angle, f2_mag, f2_angle, scale)
    except ValueError as e:
        print(f"\nError: {e}")
