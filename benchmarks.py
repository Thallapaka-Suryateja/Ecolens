# benchmarks.py
# Real Indian government benchmark data sources:
# - BEE (Bureau of Energy Efficiency) - Energy benchmarks for educational institutions
# - MoEFCC (Ministry of Environment) - India CO2 emissions factors
# - CPCB (Central Pollution Control Board) - Waste generation norms
# - Ministry of Jal Shakti - Water consumption norms
# - MoRTH (Ministry of Road Transport) - Vehicle emissions factors

# ── ENERGY ──────────────────────────────────────────────────────────────────
# BEE benchmark: educational institutions ~15 kWh/sq.m/year (good practice)
# Source: BEE Energy Performance Index for Educational Buildings
ENERGY_BENCHMARK_KWH_PER_SQFT_PER_YEAR = 1.39  # 15 kWh/sq.m/yr → 1.39 kWh/sq.ft/yr

# MoEFCC India average grid emissions factor (kg CO2 per kWh)
# Source: MoEFCC GHG Platform India, CEA CO2 Baseline Database v18
CO2_PER_KWH_KG = 0.716

# BEE benchmark: energy consumption per student per year (kWh)
ENERGY_PER_STUDENT_KWH_YEAR = 800  # BEE good-practice benchmark for colleges

# ── WATER ───────────────────────────────────────────────────────────────────
# Source: Manual on Water Supply and Treatment, CPHEEO, Ministry of Jal Shakti
# Educational institutions: 45 litres per student per day
WATER_PER_STUDENT_LITRES_DAY = 45

# ── WASTE ───────────────────────────────────────────────────────────────────
# Source: CPCB (Central Pollution Control Board) SWM Guidelines
# Educational institutions: 0.1 kg per student per day
WASTE_PER_STUDENT_KG_DAY = 0.1

# Waste-to-CO2 factor (kg CO2 per kg waste to landfill)
# Source: IPCC Waste Sector Guidelines, used by MoEFCC
CO2_PER_KG_WASTE = 0.5

# ── TRANSPORT ───────────────────────────────────────────────────────────────
# Source: MoRTH / ARAI (Automotive Research Association of India)
# Average CO2 per km per vehicle (mixed fleet: 2W + 4W average)
CO2_PER_VEHICLE_KM_KG = 0.12

# Assumed average daily commute per campus vehicle (km)
AVG_DAILY_COMMUTE_KM = 20

# Working days per year
WORKING_DAYS = 220

# ── GREEN COVER ─────────────────────────────────────────────────────────────
# Source: MoEFCC Green Rating for Integrated Habitat Assessment (GRIHA)
# 1 mature tree absorbs ~22 kg CO2/year (Indian context, tropical trees)
CO2_ABSORBED_PER_TREE_KG_YEAR = 22

# Recommended: 1 tree per 50 sq.ft of campus area (GRIHA guideline)
RECOMMENDED_TREES_PER_SQFT = 0.02

# ── SOLAR ───────────────────────────────────────────────────────────────────
# Average solar irradiation in India: ~5.5 kWh/sq.m/day
# 1 kW solar panel generates ~4.5 kWh/day in Indian conditions
KWH_PER_KW_SOLAR_PER_DAY = 4.5

# ── CANTEEN ─────────────────────────────────────────────────────────────────
# Source: Indian Council of Agricultural Research (ICAR) lifecycle emissions
# Mixed diet (meat included): ~2.5 kg CO2/meal
# Vegetarian diet: ~0.8 kg CO2/meal
CO2_PER_MEAL_MIXED_KG = 2.5
CO2_PER_MEAL_VEG_KG = 0.8
MEALS_PER_STUDENT_PER_DAY = 1  # canteen meals (not all meals)

# ── SDG THRESHOLDS ──────────────────────────────────────────────────────────
# Domain score thresholds for SDG compliance
SDG_SCORES = {
    "energy":    {"sdg": "SDG 7 — Affordable and Clean Energy",    "good": 80, "warning": 50},
    "water":     {"sdg": "SDG 6 — Clean Water and Sanitation",     "good": 80, "warning": 50},
    "waste":     {"sdg": "SDG 12 — Responsible Consumption",       "good": 80, "warning": 50},
    "transport": {"sdg": "SDG 13 — Climate Action",                "good": 80, "warning": 50},
    "green":     {"sdg": "SDG 15 — Life on Land",                  "good": 80, "warning": 50},
}
