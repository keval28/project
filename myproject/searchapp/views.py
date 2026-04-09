from django.shortcuts import render


SOURCE_HINTS = [
    "Bloomberg",
    "Reuters",
    "Economic Times",
    "Moneycontrol",
]

# Lightweight internal baseline metrics used for demo-quality decision support.
# In a production system these values should be pulled from live market data APIs.
STOCK_BASELINES = {
    "reliance": {
        "display_name": "Reliance Industries",
        "sector": "Energy + Retail + Telecom",
        "price_to_earnings": 24.8,
        "roe": 9.8,
        "roce": 8.4,
        "debt_to_equity": 0.38,
        "quarter_summary": "Consolidated revenue remained resilient, telecom ARPU improved, and retail expansion stayed intact while upstream margins remained mixed.",
        "management_commentary": "Management continues to prioritize digital monetization and disciplined capex while balancing growth in retail and new energy initiatives.",
        "promoter_change": "Promoter holding stable in recent disclosures; no major dilution signal.",
        "bull_points": [
            "Consumer + telecom scale creates multiple growth engines.",
            "Retail footprint and digital ecosystem support long-term operating leverage.",
            "Strong access to capital for strategic investments.",
        ],
        "bear_points": [
            "Large capex cycles can delay free-cash-flow conversion.",
            "Commodity-linked businesses add earnings volatility.",
            "Execution risk in new energy projects.",
        ],
        "red_flags": [
            "Watch consolidated leverage if capex intensity rises sharply.",
            "Track segment-level margin compression in retail and O2C.",
        ],
    },
    "hdfc bank": {
        "display_name": "HDFC Bank",
        "sector": "Private Banking",
        "price_to_earnings": 18.1,
        "roe": 15.6,
        "roce": 7.1,
        "debt_to_equity": 0.00,
        "quarter_summary": "Loan book growth remained healthy with focus on deposit mobilization and post-merger integration efficiency.",
        "management_commentary": "Management focus is on balancing growth and margins while improving CASA mix and sustaining asset quality discipline.",
        "promoter_change": "No material promoter holding disruption indicated in recent filings.",
        "bull_points": [
            "Strong liability franchise with broad retail reach.",
            "Consistent underwriting and superior asset quality history.",
            "Scale benefits support long-term profitability.",
        ],
        "bear_points": [
            "Deposit competition can pressure funding costs.",
            "Integration periods can temporarily impact cost ratios.",
            "Regulatory changes may affect growth pace in key products.",
        ],
        "red_flags": [
            "Monitor net interest margin trend over multiple quarters.",
            "Watch unsecured retail credit mix for stress signals.",
        ],
    },
}


def _normalize_stock_name(value: str) -> str:
    return (value or "").strip().lower()


def _default_profile(stock_name: str) -> dict:
    title = stock_name.strip().title() if stock_name else "Selected Stock"
    return {
        "display_name": title,
        "sector": "General",
        "price_to_earnings": 22.0,
        "roe": 12.0,
        "roce": 10.0,
        "debt_to_equity": 0.45,
        "quarter_summary": "Latest quarter indicates stable topline trajectory with selective margin pressure across business lines.",
        "management_commentary": "Management commentary suggests a cautious growth stance, prioritizing efficiency and capital discipline.",
        "promoter_change": "No large promoter holding shift flagged in baseline screening.",
        "bull_points": [
            "Potential upside from sector tailwinds and operating efficiency.",
            "Scope for margin recovery if input costs normalize.",
            "Balanced strategy between growth and capital allocation.",
        ],
        "bear_points": [
            "Execution uncertainty in near-term demand environment.",
            "Valuation rerating risk if earnings disappoint.",
            "Competitive intensity may cap margin expansion.",
        ],
        "red_flags": [
            "Sustained decline in return metrics would weaken thesis.",
            "Rising debt without proportional cash-flow growth.",
        ],
    }


def _calculate_ai_score(metrics: dict) -> tuple[int, list[str]]:
    score = 50
    reasons = []

    roe = metrics["roe"]
    roce = metrics["roce"]
    pe = metrics["price_to_earnings"]
    debt = metrics["debt_to_equity"]

    if roe >= 15:
        score += 12
        reasons.append("ROE is strong, supporting capital efficiency.")
    elif roe >= 10:
        score += 6
        reasons.append("ROE is healthy but not exceptional.")
    else:
        score -= 5
        reasons.append("ROE is modest, limiting quality conviction.")

    if roce >= 12:
        score += 10
        reasons.append("ROCE indicates productive operating capital usage.")
    elif roce >= 8:
        score += 4
        reasons.append("ROCE is acceptable with room for improvement.")
    else:
        score -= 4
        reasons.append("ROCE is soft versus premium-quality benchmarks.")

    if pe <= 18:
        score += 8
        reasons.append("Valuation appears reasonable relative to earnings.")
    elif pe <= 26:
        score += 3
        reasons.append("Valuation is fair, with moderate rerating risk.")
    else:
        score -= 6
        reasons.append("Elevated valuation increases downside sensitivity.")

    if debt <= 0.3:
        score += 8
        reasons.append("Leverage profile is conservative.")
    elif debt <= 0.7:
        score += 3
        reasons.append("Leverage appears manageable for current profile.")
    else:
        score -= 10
        reasons.append("Leverage is high and can pressure resilience.")

    score = max(0, min(100, score))
    return score, reasons


def _portfolio_context(holdings_text: str, stock_display_name: str, ai_score: int) -> dict:
    holdings = [item.strip() for item in holdings_text.split(",") if item.strip()]
    normalized_holdings = {item.lower() for item in holdings}
    held = stock_display_name.lower() in normalized_holdings

    if held:
        impact = (
            "Already held. Treat this output as conviction calibration: increase only if thesis quality remains intact."
        )
    else:
        impact = "Not currently held. Consider adding if it improves sector balance and quality profile."

    if ai_score >= 75:
        sizing = "High conviction: 6%–8% starter allocation (staggered entries)."
    elif ai_score >= 60:
        sizing = "Moderate conviction: 3%–5% allocation and review after next quarter."
    else:
        sizing = "Low conviction: keep on watchlist or sub-3% tracking position."

    add_decision = "Add" if (not held and ai_score >= 65) else "Hold / Watch"

    return {
        "raw_holdings": holdings,
        "is_held": held,
        "impact": impact,
        "add_decision": add_decision,
        "sizing": sizing,
    }


def search(request):
    stock_query = (request.GET.get("stock") or "").strip()
    holdings_query = (request.GET.get("holdings") or "").strip()

    analysis = None
    if stock_query:
        key = _normalize_stock_name(stock_query)
        profile = STOCK_BASELINES.get(key, _default_profile(stock_query))
        ai_score, score_reasons = _calculate_ai_score(profile)
        portfolio = _portfolio_context(holdings_query, profile["display_name"], ai_score)

        analysis = {
            "profile": profile,
            "ai_score": ai_score,
            "score_reasons": score_reasons,
            "portfolio": portfolio,
            "source_hints": SOURCE_HINTS,
        }

    return render(
        request,
        "searchapp/search.html",
        {
            "stock_query": stock_query,
            "holdings_query": holdings_query,
            "analysis": analysis,
        },
    )
