# agent.py
# EcoLens Audit Agent — Plan-and-execute pattern
# IBM Bob recommended: extract each audit step as a named function
# so the orchestrator loop stays readable and each step is independently testable.

import json
from groq import Groq
from benchmarks import (
    CO2_PER_KWH_KG, ENERGY_PER_STUDENT_KWH_YEAR,
    WATER_PER_STUDENT_LITRES_DAY, WASTE_PER_STUDENT_KG_DAY,
    CO2_PER_KG_WASTE, CO2_PER_VEHICLE_KM_KG, AVG_DAILY_COMMUTE_KM,
    WORKING_DAYS, CO2_ABSORBED_PER_TREE_KG_YEAR, RECOMMENDED_TREES_PER_SQFT,
    CO2_PER_MEAL_MIXED_KG, CO2_PER_MEAL_VEG_KG, MEALS_PER_STUDENT_PER_DAY,
    ENERGY_BENCHMARK_KWH_PER_SQFT_PER_YEAR, SDG_SCORES
)

MODEL = "openai/gpt-oss-120b"
MAX_TOKENS = 1500


def _llm(client: Groq, system: str, user: str) -> str:
    """Single LLM call — centralised so model/params change in one place."""
    resp = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content.strip()


# ── STEP 1: Calculate domain footprints ─────────────────────────────────────

def calculate_footprints(data: dict) -> dict:
    """
    Pure Python calculations using real BEE/MoEFCC benchmark factors.
    Returns actual vs benchmark for each domain.
    """
    students = data["students"]
    staff = data["staff"]
    total_people = students + staff
    campus_sqft = data["campus_sqft"]
    working_days = data.get("working_days", WORKING_DAYS)

    # Energy
    actual_energy_kwh_year = data["electricity_kwh_month"] * 12
    benchmark_energy_kwh_year = ENERGY_PER_STUDENT_KWH_YEAR * total_people
    energy_co2_kg_year = actual_energy_kwh_year * CO2_PER_KWH_KG
    solar_offset_kwh = data.get("solar_kw", 0) * 4.5 * working_days
    net_energy_kwh = max(actual_energy_kwh_year - solar_offset_kwh, 0)
    net_energy_co2 = net_energy_kwh * CO2_PER_KWH_KG

    # Water
    actual_water_litres_day = data["water_litres_day"]
    benchmark_water_litres_day = WATER_PER_STUDENT_LITRES_DAY * total_people

    # Waste
    actual_waste_kg_day = data["waste_kg_day"]
    benchmark_waste_kg_day = WASTE_PER_STUDENT_KG_DAY * total_people
    waste_co2_kg_year = actual_waste_kg_day * 365 * CO2_PER_KG_WASTE

    # Transport
    vehicles = data["vehicles"]
    transport_co2_kg_year = (
        vehicles * AVG_DAILY_COMMUTE_KM * working_days * CO2_PER_VEHICLE_KM_KG
    )

    # Green cover
    actual_trees = data.get("trees", 0)
    recommended_trees = int(campus_sqft * RECOMMENDED_TREES_PER_SQFT)
    trees_co2_offset_kg_year = actual_trees * CO2_ABSORBED_PER_TREE_KG_YEAR

    # Canteen
    canteen = data.get("canteen_type", "mixed")
    co2_per_meal = CO2_PER_MEAL_VEG_KG if canteen == "veg" else CO2_PER_MEAL_MIXED_KG
    canteen_co2_kg_year = (
        co2_per_meal * MEALS_PER_STUDENT_PER_DAY * students * working_days
    )

    # Total footprint
    total_co2 = (
        net_energy_co2 + waste_co2_kg_year +
        transport_co2_kg_year + canteen_co2_kg_year - trees_co2_offset_kg_year
    )
    total_co2 = max(total_co2, 0)

    return {
        "energy": {
            "actual_kwh_year": round(actual_energy_kwh_year),
            "benchmark_kwh_year": round(benchmark_energy_kwh_year),
            "solar_offset_kwh": round(solar_offset_kwh),
            "co2_kg_year": round(net_energy_co2),
            "ratio": round(actual_energy_kwh_year / max(benchmark_energy_kwh_year, 1), 2),
        },
        "water": {
            "actual_litres_day": actual_water_litres_day,
            "benchmark_litres_day": round(benchmark_water_litres_day),
            "ratio": round(actual_water_litres_day / max(benchmark_water_litres_day, 1), 2),
        },
        "waste": {
            "actual_kg_day": actual_waste_kg_day,
            "benchmark_kg_day": round(benchmark_waste_kg_day, 1),
            "co2_kg_year": round(waste_co2_kg_year),
            "ratio": round(actual_waste_kg_day / max(benchmark_waste_kg_day, 1), 2),
        },
        "transport": {
            "vehicles": vehicles,
            "co2_kg_year": round(transport_co2_kg_year),
        },
        "green": {
            "actual_trees": actual_trees,
            "recommended_trees": recommended_trees,
            "co2_offset_kg_year": round(trees_co2_offset_kg_year),
            "ratio": round(actual_trees / max(recommended_trees, 1), 2),
        },
        "canteen": {
            "type": canteen,
            "co2_kg_year": round(canteen_co2_kg_year),
        },
        "total_co2_kg_year": round(total_co2),
        "total_co2_tonnes_year": round(total_co2 / 1000, 2),
    }


# ── STEP 2: Score each domain ────────────────────────────────────────────────

def score_domains(footprints: dict) -> dict:
    """
    Convert ratios to 0-100 scores per domain.
    ratio < 1.0 = better than benchmark (score > 50)
    ratio = 1.0 = exactly at benchmark (score = 50)
    ratio > 2.0 = double the benchmark (score = 0)
    """
    def ratio_to_score(ratio: float) -> int:
        # Lower ratio = better; clamp between 0 and 100
        score = max(0, min(100, int((2.0 - ratio) / 2.0 * 100)))
        return score

    def tree_ratio_to_score(ratio: float) -> int:
        # Higher ratio = better for green cover
        score = max(0, min(100, int(ratio * 100)))
        return score

    scores = {
        "energy":    ratio_to_score(footprints["energy"]["ratio"]),
        "water":     ratio_to_score(footprints["water"]["ratio"]),
        "waste":     ratio_to_score(footprints["waste"]["ratio"]),
        "transport": max(0, 100 - int(footprints["transport"]["co2_kg_year"] / 500)),
        "green":     tree_ratio_to_score(footprints["green"]["ratio"]),
    }

    # Weighted overall score
    weights = {"energy": 0.30, "water": 0.20, "waste": 0.20, "transport": 0.15, "green": 0.15}
    overall = sum(scores[d] * weights[d] for d in scores)
    scores["overall"] = round(overall)

    # SDG compliance status per domain
    sdg_status = {}
    for domain, meta in SDG_SCORES.items():
        s = scores[domain]
        if s >= meta["good"]:
            status = "✅ Compliant"
        elif s >= meta["warning"]:
            status = "⚠️ Needs Improvement"
        else:
            status = "❌ Non-Compliant"
        sdg_status[domain] = {"sdg": meta["sdg"], "score": s, "status": status}

    return {"domain_scores": scores, "sdg_status": sdg_status}


# ── STEP 3: LLM identifies key problem areas ─────────────────────────────────

def identify_problems(client: Groq, campus_name: str, footprints: dict, scores: dict) -> str:
    system = (
        "You are EcoLens, an expert sustainability auditor specialising in Indian educational "
        "institutions. You use data from BEE, MoEFCC, and CPCB. Be specific, factual, and concise. "
        "Never use generic advice — always tie recommendations to the actual numbers provided."
    )
    user = (
        f"Campus: {campus_name}\n"
        f"Domain scores (0-100, higher is better): {json.dumps(scores['domain_scores'])}\n"
        f"Footprint data: {json.dumps(footprints)}\n\n"
        "In 3-4 sentences, identify the 2-3 most critical problem areas for this campus, "
        "referencing the actual numbers. Be direct and specific."
    )
    return _llm(client, system, user)


# ── STEP 4: LLM generates ranked recommendations ─────────────────────────────

def generate_recommendations(client: Groq, campus_name: str, footprints: dict, scores: dict) -> str:
    system = (
        "You are EcoLens, a sustainability consultant for Indian colleges. "
        "Generate exactly 5 numbered recommendations. Each must: "
        "1) name a specific action, "
        "2) reference the actual campus data, "
        "3) estimate CO2 or resource savings using Indian standards, "
        "4) mention which SDG it addresses. "
        "Order by impact — highest first. Be concrete, not generic."
    )
    user = (
        f"Campus: {campus_name}\n"
        f"Total CO2: {footprints['total_co2_tonnes_year']} tonnes/year\n"
        f"Domain scores: {json.dumps(scores['domain_scores'])}\n"
        f"Footprint details: {json.dumps(footprints)}\n\n"
        "Generate the 5 prioritised recommendations."
    )
    return _llm(client, system, user)


# ── STEP 5: LLM writes executive summary ────────────────────────────────────

def generate_summary(client: Groq, campus_name: str, footprints: dict, scores: dict, problems: str) -> str:
    system = (
        "You are EcoLens. Write a professional 3-paragraph executive summary for a campus "
        "sustainability audit report. Paragraph 1: overall performance. "
        "Paragraph 2: key findings. Paragraph 3: urgency and call to action. "
        "Tone: professional, direct, data-backed."
    )
    user = (
        f"Campus: {campus_name}\n"
        f"Overall sustainability score: {scores['domain_scores']['overall']}/100\n"
        f"Total CO2 footprint: {footprints['total_co2_tonnes_year']} tonnes/year\n"
        f"Key problems identified: {problems}\n"
        f"SDG status: {json.dumps({k: v['status'] for k, v in scores['sdg_status'].items()})}\n\n"
        "Write the executive summary."
    )
    return _llm(client, system, user)


# ── ORCHESTRATOR ─────────────────────────────────────────────────────────────

def run_audit(api_key: str, campus_data: dict, progress_callback=None) -> dict:
    """
    Main agent orchestrator — Plan-and-execute pattern.
    Each step is atomic and independently inspectable.
    progress_callback(step: int, message: str) updates the UI.
    """
    client = Groq(api_key=api_key)
    campus_name = campus_data.get("campus_name", "Your Campus")

    def progress(step, msg):
        if progress_callback:
            progress_callback(step, msg)

    # Step 1
    progress(1, "📊 Calculating carbon footprint using BEE & MoEFCC benchmarks...")
    footprints = calculate_footprints(campus_data)

    # Step 2
    progress(2, "🏆 Scoring each domain against national standards...")
    scores = score_domains(footprints)

    # Step 3
    progress(3, "🔍 Identifying critical problem areas...")
    problems = identify_problems(client, campus_name, footprints, scores)

    # Step 4
    progress(4, "💡 Generating prioritised recommendations...")
    recommendations = generate_recommendations(client, campus_name, footprints, scores)

    # Step 5
    progress(5, "📝 Writing executive summary...")
    summary = generate_summary(client, campus_name, footprints, scores, problems)

    progress(6, "✅ Audit complete — generating report...")

    return {
        "campus_name": campus_name,
        "footprints": footprints,
        "scores": scores,
        "problems": problems,
        "recommendations": recommendations,
        "summary": summary,
    }
