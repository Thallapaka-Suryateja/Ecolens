# report.py
# EcoLens PDF Report Generator
# Uses fpdf2 with DejaVu Sans TTF for full Unicode support
# (handles –  —  " "  ' '  CO₂  and other AI-generated Unicode)

from fpdf import FPDF
from datetime import datetime
import os

# Path to bundled fonts (relative to this file)
_FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_FONT_REGULAR = os.path.join(_FONT_DIR, "DejaVuSans.ttf")
_FONT_BOLD    = os.path.join(_FONT_DIR, "DejaVuSans-Bold.ttf")

DARK_GREEN = (30, 80, 50)
MID_GREEN  = (60, 140, 90)
LIGHT_GREEN= (220, 240, 225)
GOLD       = (180, 140, 60)
DARK       = (30, 35, 30)
MUTED      = (90, 100, 90)
WHITE      = (255, 255, 255)
WARN_RED   = (180, 50, 50)
WARN_AMBER = (180, 120, 30)


def _safe(text: str) -> str:
    """
    Replace characters that DejaVu Sans does not cover (emoji / combining marks)
    with plain-ASCII equivalents so fpdf2 never raises a character range error.
    Typographic punctuation and subscripts (–, —, CO₂, curly quotes) are fully
    supported by DejaVu Sans and are left untouched.
    """
    replacements = {
        "\u2705": "[OK]",   # ✅
        "\u274c": "[X]",    # ❌
        "\u26a0": "[!]",    # ⚠
        "\ufe0f": "",       # variation selector (emoji modifier)
        "\u2b50": "*",      # ⭐
        "\U0001f331": "",   # 🌱
    }
    for char, sub in replacements.items():
        text = text.replace(char, sub)
    return text


class EcoLensReport(FPDF):

    def __init__(self, campus_name: str):
        super().__init__()
        self.campus_name = campus_name
        # Register DejaVu Sans (regular + bold) for Unicode support
        self.add_font("DejaVu", "",  _FONT_REGULAR)
        self.add_font("DejaVu", "B", _FONT_BOLD)
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(18, 18, 18)

    def header(self):
        # Green top bar
        self.set_fill_color(*DARK_GREEN)
        self.rect(0, 0, 210, 14, "F")
        self.set_font("DejaVu", "B", 9)
        self.set_text_color(0, 0, 0)
        self.set_xy(0, 3)
        self.cell(0, 8, "ECOLENS  \u00b7  Campus Sustainability Audit Report", align="C")
        self.ln(16)

    def footer(self):
        self.set_y(-14)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 8,
            f"EcoLens  \u00b7  Benchmarks: BEE, MoEFCC, CPCB, Jal Shakti  \u00b7  Page {self.page_no()}",
            align="C"
        )

    def _section_title(self, title: str):
        self.ln(4)
        self.set_fill_color(*LIGHT_GREEN)
        self.set_text_color(*DARK_GREEN)
        self.set_font("DejaVu", "B", 11)
        self.cell(0, 9, f"  {_safe(title)}", ln=True, fill=True)
        self.ln(2)

    def _body(self, text: str):
        self.set_font("DejaVu", "", 10)
        self.set_text_color(*DARK)
        self.multi_cell(0, 6, _safe(text))
        self.ln(1)

    def _score_bar(self, label: str, score: int, sdg: str, status: str):
        """Horizontal score bar for each domain."""
        if "Compliant" in status and "Non" not in status:
            bar_color = MID_GREEN
        elif "Improvement" in status:
            bar_color = WARN_AMBER
        else:
            bar_color = WARN_RED

        self.set_font("DejaVu", "B", 9)
        self.set_text_color(*DARK)
        self.cell(40, 7, label.upper(), ln=False)

        # Bar background
        x, y = self.get_x(), self.get_y()
        self.set_fill_color(220, 220, 220)
        self.rect(x, y + 1, 80, 5, "F")
        # Bar fill
        self.set_fill_color(*bar_color)
        self.rect(x, y + 1, 80 * score / 100, 5, "F")
        # Score label
        self.set_xy(x + 83, y)
        self.set_font("DejaVu", "B", 9)
        self.set_text_color(*bar_color)
        self.cell(14, 7, f"{score}/100", ln=False)
        # SDG label — em-dash replaced with hyphen for safety, but DejaVu handles it
        self.set_font("DejaVu", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 7, _safe(sdg), ln=True)

    def _metric_row(self, label: str, actual, benchmark, unit: str):
        self.set_font("DejaVu", "", 9)
        self.set_text_color(*DARK)
        self.cell(70, 6, label, ln=False)
        self.set_font("DejaVu", "B", 9)
        self.cell(40, 6, f"{actual:,} {unit}", ln=False)
        self.set_font("DejaVu", "", 9)
        self.set_text_color(*MUTED)
        self.cell(0, 6, f"Benchmark: {benchmark:,} {unit}", ln=True)
        self.set_text_color(*DARK)


def generate_pdf(result: dict) -> bytes:
    """Generate the audit PDF and return as bytes for Streamlit download."""
    campus_name = result["campus_name"]
    fp = result["footprints"]
    sc = result["scores"]
    domain_scores = sc["domain_scores"]
    sdg_status = sc["sdg_status"]

    pdf = EcoLensReport(campus_name)
    pdf.add_page()

    # ── Cover block ──────────────────────────────────────────────────────────
    pdf.set_fill_color(*DARK_GREEN)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("DejaVu", "B", 22)
    pdf.cell(0, 12, "EcoLens", ln=True, align="C")
    pdf.set_font("DejaVu", "", 11)
    pdf.cell(0, 7, "Campus Sustainability Audit Report", ln=True, align="C")
    pdf.ln(3)
    pdf.set_font("DejaVu", "B", 13)
    pdf.cell(0, 8, campus_name, ln=True, align="C")
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%d %B %Y')}", ln=True, align="C")
    pdf.ln(6)

    # Overall score callout
    overall = domain_scores["overall"]
    if overall >= 75:
        grade, grade_color = "A - Good", MID_GREEN
    elif overall >= 55:
        grade, grade_color = "B - Satisfactory", WARN_AMBER
    elif overall >= 35:
        grade, grade_color = "C - Needs Work", WARN_AMBER
    else:
        grade, grade_color = "D - Critical", WARN_RED

    pdf.set_fill_color(*grade_color)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("DejaVu", "B", 28)
    pdf.cell(0, 18, f"{overall} / 100", ln=True, align="C", fill=True)
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 8, f"Sustainability Grade: {grade}", ln=True, align="C")
    pdf.set_font("DejaVu", "", 9)
    pdf.cell(0, 6, f"Total Carbon Footprint: {fp['total_co2_tonnes_year']} tonnes CO\u2082/year", ln=True, align="C")
    pdf.ln(6)

    # ── Executive Summary ────────────────────────────────────────────────────
    pdf._section_title("Executive Summary")
    pdf._body(result["summary"])

    # ── Domain Scores ────────────────────────────────────────────────────────
    pdf._section_title("Domain Performance vs. National Benchmarks")
    domain_labels = {
        "energy": "Energy", "water": "Water", "waste": "Waste",
        "transport": "Transport", "green": "Green Cover"
    }
    for domain, label in domain_labels.items():
        info = sdg_status[domain]
        pdf._score_bar(label, info["score"], info["sdg"], info["status"])
        pdf.ln(2)

    # ── Detailed Metrics ─────────────────────────────────────────────────────
    pdf._section_title("Detailed Footprint Metrics")
    pdf._metric_row(
        "Annual electricity consumption",
        fp["energy"]["actual_kwh_year"],
        fp["energy"]["benchmark_kwh_year"],
        "kWh"
    )
    pdf._metric_row(
        "Daily water consumption",
        fp["water"]["actual_litres_day"],
        fp["water"]["benchmark_litres_day"],
        "litres"
    )
    pdf._metric_row(
        "Daily waste generated",
        fp["waste"]["actual_kg_day"],
        fp["waste"]["benchmark_kg_day"],
        "kg"
    )
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 6,
        f"Campus vehicles: {fp['transport']['vehicles']} units  \u00b7  "
        f"Transport CO\u2082: {fp['transport']['co2_kg_year']:,} kg/year", ln=True
    )
    pdf.cell(0, 6,
        f"Green cover: {fp['green']['actual_trees']} trees "
        f"(recommended: {fp['green']['recommended_trees']})  \u00b7  "
        f"CO\u2082 offset: {fp['green']['co2_offset_kg_year']:,} kg/year", ln=True
    )
    pdf.ln(2)

    # ── Problem Areas ────────────────────────────────────────────────────────
    pdf._section_title("Critical Problem Areas")
    pdf._body(result["problems"])

    # ── Recommendations ──────────────────────────────────────────────────────
    pdf._section_title("Top 5 Prioritised Recommendations")
    pdf._body(result["recommendations"])

    # ── SDG Compliance Table ─────────────────────────────────────────────────
    pdf._section_title("SDG Compliance Status")
    for domain, info in sdg_status.items():
        status = info["status"]
        if "Compliant" in status and "Non" not in status:
            pdf.set_text_color(*MID_GREEN)
        elif "Improvement" in status:
            pdf.set_text_color(*WARN_AMBER)
        else:
            pdf.set_text_color(*WARN_RED)
        pdf.set_font("DejaVu", "B", 9)
        sdg_label = _safe(info["sdg"])
        status_label = _safe(status)
        pdf.cell(0, 6, f"{status_label}  -  {sdg_label}  (Score: {info['score']}/100)", ln=True)
    pdf.set_text_color(*DARK)

    # ── Disclaimer ───────────────────────────────────────────────────────────
    pdf.ln(6)
    pdf.set_font("DejaVu", "", 8)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(0, 5,
        "Data sources: Bureau of Energy Efficiency (BEE), Ministry of Environment Forest and "
        "Climate Change (MoEFCC) GHG Platform India, Central Pollution Control Board (CPCB) "
        "SWM Guidelines, Ministry of Jal Shakti CPHEEO Manual, ARAI vehicle emissions data. "
        "This report is generated by EcoLens AI and should be reviewed by a certified "
        "sustainability professional before official submission."
    )

    return bytes(pdf.output())
