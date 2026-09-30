import json
import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from storage.db import get_db_connection

app = Server("sovereign-intel-mesh-production")

# Configuration flag: True keeps everything free/waived for testing & hardening
FREE_TIER_WAIVER = os.getenv("SIP_FREE_TIER_WAIVER", "true").lower() == "true"

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="query_intelligence_cell",
            description="Query verified intelligence objects. Metered dynamically by compute complexity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "client_id": {
                        "type": "string",
                        "description": "The bot or client identifier for compute tracking."
                    },
                    "min_confidence": {
                        "type": "number",
                        "description": "Minimum confidence filter threshold (0.0 to 1.0)."
                    },
                    "jurisdiction": {
                        "type": "string",
                        "description": "Optional jurisdiction filter tag."
                    }
                },
                "required": ["client_id", "min_confidence"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "query_intelligence_cell":
        raise ValueError(f"Unknown tool requested: {name}")

    client_id = arguments.get("client_id", "anonymous_bot")
    
    try:
        min_confidence = float(arguments.get("min_confidence", 0.8))
        if not (0.0 <= min_confidence <= 1.0):
            raise ValueError("min_confidence must be between 0.0 and 1.0.")
    except (TypeError, ValueError) as e:
        return [TextContent(type="text", text=json.dumps({"error": f"Invalid argument format: {e}"}))]

    jurisdiction = arguments.get("jurisdiction")

    # --- Dynamic Compute & Pricing Calculation ---
    # Base cost: 1 Compute Unit (CU). 
    # Dynamic Upcharge: If querying across global scopes without a strict jurisdiction index filter, 
    # or if the bot pulls high-volume data, upcharge appropriately.
    base_compute_units = 1
    if not jurisdiction:
        base_compute_units += 2  # Global sweeps require heavier index scanning
    
    cost_per_unit = 0.001  # USD equivalent in SOL/credits per CU
    total_charge = base_compute_units * cost_per_unit

    try:
        with get_db_connection() as conn:
            # Check client balance if not in free waiver mode
            if not FREE_TIER_WAIVER:
                cursor = conn.execute("SELECT credit_balance FROM bot_accounts WHERE client_id = ?", (client_id,))
                row = cursor.fetchone()
                if not row or row[0] < total_charge:
                    return [TextContent(type="text", text=json.dumps({
                        "error": "Insufficient compute credits. Please top up your on-chain escrow balance.",
                        "required_credits": total_charge
                    }))]
                
                # Deduct balance
                conn.execute("UPDATE bot_accounts SET credit_balance = credit_balance - ? WHERE client_id = ?", (total_charge, client_id))

            # Log compute telemetry
            conn.execute("""
                INSERT INTO compute_ledger_log (client_id, compute_units, query_type, charged_amount, waived)
                VALUES (?, ?, ?, ?, ?)
            """, (client_id, base_compute_units, "intelligence_query", total_charge if not FREE_TIER_WAIVER else 0.0, FREE_TIER_WAIVER))

            # Execute actual query
            if jurisdiction:
                cursor = conn.execute(
                    "SELECT claim, sources, confidence, jurisdiction, lineage_hash, signature FROM intelligence_objects WHERE confidence >= ? AND jurisdiction = ? ORDER BY confidence DESC LIMIT 50",
                    (min_confidence, jurisdiction)
                )
            else:
                cursor = conn.execute(
                    "SELECT claim, sources, confidence, jurisdiction, lineage_hash, signature FROM intelligence_objects WHERE confidence >= ? ORDER BY confidence DESC LIMIT 50",
                    (min_confidence,)
                )
            rows = cursor.fetchall()
            
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": f"Execution failed: {e}"}))]

    results = []
    for row in rows:
        results.append({
            "claim": row[0],
            "sources": json.loads(row[1]),
            "confidence": row[2],
            "jurisdiction": row[3],
            "lineage_hash": row[4],
            "signature": row[5]
        })

    response_payload = {
        "meta": {
            "client_id": client_id,
            "compute_units_consumed": base_compute_units,
            "charged_amount": 0.0 if FREE_TIER_WAIVER else total_charge,
            "waiver_active": FREE_TIER_WAIVER
        },
        "data": results
    }

    return [TextContent(type="text", text=json.dumps(response_payload, indent=2))]

if __name__ == "__main__":
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    asyncio.run(main())
