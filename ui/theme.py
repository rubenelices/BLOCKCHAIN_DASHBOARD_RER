"""Theme helpers for cryptocurrency-specific visual identity."""

from config.crypto_config import CryptoConfig


THEME_BACKGROUNDS = {
    "bitcoin": {
        "top": "#201006",
        "mid": "#120B06",
        "bottom": "#05070C",
        "primary_alpha": "66",
        "secondary_alpha": "30",
    },
    "ethereum": {
        "top": "#0A1233",
        "mid": "#111A45",
        "bottom": "#050815",
        "primary_alpha": "5c",
        "secondary_alpha": "34",
    },
    "litecoin": {
        "top": "#04170F",
        "mid": "#07120E",
        "bottom": "#040807",
        "primary_alpha": "60",
        "secondary_alpha": "38",
    },
}


def crypto_theme_css(crypto: CryptoConfig) -> str:
    """Return CSS overrides derived from the active cryptocurrency."""
    primary = crypto.primary_color
    secondary = crypto.secondary_color
    bg = THEME_BACKGROUNDS.get(crypto.id, THEME_BACKGROUNDS["bitcoin"])
    return f"""
<style>
:root {{
    --crypto-primary: {primary};
    --crypto-secondary: {secondary};
    --accent-blue: {secondary};
    --accent-gold: {primary};
    --text-mono: {secondary};
}}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {{
    background:
        radial-gradient(circle at 50% -22%, {primary}{bg["primary_alpha"]} 0%, transparent 42%),
        radial-gradient(circle at 8% 18%, {primary}3f 0%, transparent 32%),
        radial-gradient(circle at 92% 24%, {secondary}{bg["secondary_alpha"]} 0%, transparent 38%),
        linear-gradient(180deg, {bg["top"]} 0%, {bg["mid"]} 48%, {bg["bottom"]} 100%) !important;
}}

.ph-btc-sym {{
    color: {primary} !important;
    text-shadow:
        0 0 30px {primary}cc,
        0 0 80px {primary}55,
        0 0 130px {primary}22 !important;
}}
.ph-wordmark {{
    background: linear-gradient(100deg, #FFFFFF 0%, {secondary} 32%, {primary} 72%, #FFFFFF 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}}
.ph-sep,
.card-title,
code {{
    color: {primary} !important;
}}
.ph-t2 {{ color: color-mix(in srgb, {secondary} 74%, #E8EDF5) !important; }}
.ph-time-text {{ color: color-mix(in srgb, {secondary} 78%, #6B7DA0) !important; }}
.ph-glow-c {{ background: radial-gradient(ellipse, {primary}30 0%, transparent 64%) !important; }}
.ph-glow-l {{ background: radial-gradient(ellipse at left center, {primary}25 0%, transparent 65%) !important; }}
.ph-glow-r {{ background: radial-gradient(ellipse at right center, {secondary}22 0%, transparent 65%) !important; }}
.ph-bg {{
    background: transparent !important;
    background-image: none !important;
    display: none !important;
}}
.ph-wrap {{
    overflow: visible !important;
}}
#ph-canvas {{
    display: none !important;
}}
.ph-glow-c,
.ph-glow-l,
.ph-glow-r {{
    display: none !important;
}}
.ph-ghost {{
    display: none !important;
}}
h1, h2, h3, h4 {{
    color: color-mix(in srgb, {primary} 42%, #E8EDF5) !important;
}}
.ph-divider,
.module-divider,
.glow-sep {{
    background: linear-gradient(90deg, transparent 0%, {secondary}26 18%, {primary}aa 50%, {secondary}26 82%, transparent 100%) !important;
}}
.field-val {{
    color: {secondary} !important;
    background: color-mix(in srgb, {secondary} 8%, transparent) !important;
    border-color: color-mix(in srgb, {secondary} 20%, transparent) !important;
}}
[data-testid="stMetric"],
.card {{
    border-color: color-mix(in srgb, {secondary} 26%, #1E2D5A) !important;
}}
[data-testid="stMetric"] {{
    border-left-color: {primary} !important;
}}
div[data-testid="stButton"] > button {{
    background:
        linear-gradient(180deg,
            color-mix(in srgb, {primary} 20%, #101827) 0%,
            color-mix(in srgb, {secondary} 10%, #070B15) 100%) !important;
    border-color: color-mix(in srgb, {primary} 48%, {secondary}) !important;
    color: color-mix(in srgb, {secondary} 38%, #F4F7FF) !important;
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.05),
        0 10px 26px color-mix(in srgb, {primary} 12%, transparent) !important;
}}
div[data-testid="stButton"] > button::before {{
    background:
        radial-gradient(circle at 18% 0%, {secondary}24, transparent 38%),
        linear-gradient(90deg, {primary}00, {primary}14, {secondary}00) !important;
}}
div[data-testid="stButton"] > button:hover {{
    background:
        linear-gradient(180deg,
            color-mix(in srgb, {primary} 34%, #101827) 0%,
            color-mix(in srgb, {secondary} 16%, #070B15) 100%) !important;
    border-color: {primary} !important;
    color: #E8F7FF !important;
    box-shadow:
        0 12px 32px color-mix(in srgb, {primary} 22%, transparent),
        inset 0 1px 0 rgba(255,255,255,0.06) !important;
}}
div[data-testid="stButton"] > button[kind="primary"] {{
    background:
        linear-gradient(180deg,
            color-mix(in srgb, {primary} 46%, #121826) 0%,
            color-mix(in srgb, {secondary} 24%, #070B15) 100%) !important;
    border-color: {primary} !important;
    color: #FFFFFF !important;
    box-shadow:
        0 0 0 1px color-mix(in srgb, {primary} 38%, transparent),
        0 0 34px color-mix(in srgb, {primary} 32%, transparent),
        inset 0 -2px 0 {secondary} !important;
}}
.crypto-context {{
    max-width: 1240px;
    margin: 0 auto 12px auto;
    border: 1px solid color-mix(in srgb, {secondary} 24%, #1E2D5A);
    border-left: 3px solid {primary};
    border-radius: 10px;
    background: rgba(15,22,41,0.72);
    padding: 13px 16px;
}}
.crypto-context-title {{
    font-family: Rajdhani, sans-serif;
    color: #E8EDF5;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0 0 4px 0;
}}
.crypto-context-copy {{
    font-family: Inter, sans-serif;
    color: #6B7DA0;
    font-size: 0.82rem;
    line-height: 1.55;
    margin: 0;
}}
.crypto-context-title {{
    color: color-mix(in srgb, {primary} 54%, #E8EDF5) !important;
}}
.card {{
    background:
        linear-gradient(180deg, color-mix(in srgb, {primary} 7%, #0F1629) 0%, #0A1020 100%) !important;
}}
</style>
"""


def chart_colors(crypto: CryptoConfig) -> dict[str, str]:
    """Return semantic chart colors for Plotly figures."""
    return {
        "primary": crypto.primary_color,
        "secondary": crypto.secondary_color,
        "success": "#1CE87A",
        "danger": "#FF4560",
        "muted": "#6B7DA0",
        "text": "#E8EDF5",
        "paper": "#0A0E1A",
        "plot": "#0F1629",
        "grid": "#1E2D5A",
    }
