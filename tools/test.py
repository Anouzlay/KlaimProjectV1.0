from tavily import TavilyClient
tavily_client = TavilyClient(api_key="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")
response = tavily_client.search("Al Dhaid Hospital CEO")
print(response)