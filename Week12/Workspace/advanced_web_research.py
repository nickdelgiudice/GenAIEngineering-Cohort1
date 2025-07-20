# agentic_dell_7560_flow.py

from phi.agent import Agent
from phi.tools.serpapi_tools import SerpApiTools
import os
from dotenv import load_dotenv
from typing import List
import re
import pandas as pd

# Load env variables
load_dotenv()
serp_key = os.getenv("SERPAPI_API_KEY")

# --- Step 1: SearchAgent ---
search_agent = Agent(
    name="SearchDellConfigsAgent",
    description="Search for Dell Precision 7560 listings in the used market",
    tools=[SerpApiTools(api_key=serp_key)]
)

query = "Dell Precision 7560 used site:ebay.com OR site:backmarket.com OR site:newegg.com"

# For print_response()
search_agent.print_response(query, stream=True)

# Run the search and collect output
search_response_stream = search_agent.run(query, stream=True)
search_results = "".join([chunk.content if hasattr(chunk, "content") else str(chunk) for chunk in search_response_stream])

# Debug output
print("\n--- RAW SEARCH RESULTS ---\n")
print(search_results[:1000] + "...\n")  # Print first 1000 chars

# --- Step 2: ConfigExtractorAgent ---
def extract_dell_configurations(input_text: str) -> List[dict]:
    """Extract configuration details from listing texts"""
    listings = []
    pattern = re.compile(r"Dell Precision 7560.*?(?P<cpu>i[579]|Xeon)[^,\n]*[,].*?(?P<ram>\d+GB).*?(?P<ssd>\d+TB|\d+GB).*?(?P<gpu>RTX [A-Z0-9]+)?.*?(?P<price>\$\d+[,\.\d]*)", re.IGNORECASE | re.DOTALL)
    for match in pattern.finditer(input_text):
        listings.append(match.groupdict())
    return listings

extractor_agent = Agent(
    name="ConfigExtractorAgent",
    tools=[extract_dell_configurations]
)

extractor_agent.print_response(search_results, stream=True)

extracted_data = extractor_agent.run(search_results, stream=True)

if not extracted_data:
    print("\n❌ No configurations extracted. Regex may need to be updated for current listing format. Skipping analysis.")
else:
    # --- Step 3: MarketInsightAgent ---
    def analyze_configurations(configs: List[dict]) -> str:
        """Analyze configurations and group by popularity and value"""
        df = pd.DataFrame(configs)
        df["price"] = df["price"].str.replace("$", "").str.replace(",", "").astype(float)
        summary = df.groupby(["cpu", "ram", "ssd", "gpu"]).agg(
            avg_price=("price", "mean"),
            count=("price", "count")
        ).sort_values(by=["count", "avg_price"], ascending=[False, True])
        return summary.reset_index().to_markdown()

    analyzer_agent = Agent(
        name="MarketInsightAgent",
        tools=[analyze_configurations]
    )

    analysis_summary = analyzer_agent.run(extracted_data)

    # --- Step 4: PurchaseAdvisorAgent ---
    def advise_purchase(insights: str) -> str:
        """Give suggestions based on budget and best configurations"""
        return f"Based on the analysis below, the best value configurations are:\n\n{insights}\n\nRecommended: Choose any model with RTX A2000+ and 32GB+ RAM under $1500."

    advisor_agent = Agent(
        name="PurchaseAdvisorAgent",
        tools=[advise_purchase]
    )

    recommendation = advisor_agent.chat(analysis_summary)

    print("\n======= RECOMMENDED CONFIGURATIONS =======\n")
    print(recommendation)
