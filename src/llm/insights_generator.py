import requests
import json

def generate_insights(df):
    """Generate insights using Ollama LLM. Falls back to basic stats if unavailable."""
    
    if df.empty:
        return "No data available for insights"
    
    try:
        summary = df.describe().to_string()
        
        prompt = f"""
Analyze this supply chain data and give short, actionable insights:

{summary}

Focus on:
- demand trends (increasing/decreasing)
- inventory risks (too high/too low)
- anomalies detected
- recommendations

Keep response under 200 words."""

        # Try to connect to Ollama
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama2",
                "prompt": prompt,
                "stream": False
            },
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json().get("response", "No insights generated")
        else:
            raise Exception(f"Ollama returned status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Ollama not running - using fallback insights")
        return generate_fallback_insights(df)
    except requests.exceptions.Timeout:
        print("⚠️  Ollama timeout - using fallback insights")
        return generate_fallback_insights(df)
    except Exception as e:
        print(f"⚠️  Insights error: {e}")
        return generate_fallback_insights(df)


def generate_fallback_insights(df):
    """Generate basic insights without LLM."""
    
    demand_mean = df['demand'].mean()
    demand_std = df['demand'].std()
    inventory_mean = df['inventory'].mean()
    
    insights = f"""
📊 Supply Chain Analysis

Demand Metrics:
  • Average: {demand_mean:.0f} units
  • Variability (Std Dev): {demand_std:.0f}
  • Status: {"Stable" if demand_std < demand_mean * 0.3 else "Volatile"}

Inventory Metrics:
  • Average Level: {inventory_mean:.0f} units
  • Coverage: {(inventory_mean / demand_mean if demand_mean > 0 else 0):.1f} days

Recommendations:
  • Monitor for demand spikes
  • Maintain safety stock buffer
  • Review lead time implications
"""
    
    return insights
