from typing import List, TypedDict
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from app.services.summarization import generate_summary, collapse_summaries, generate_final_summary
from app.services.image_generation import generate_image_prompt

# Define the overall state of the graph
class OverallState(TypedDict):
    contents: List[str]
    summaries: List[str]
    collapsed_summaries: List[str]
    final_summary: str
    image_prompt: str
    image_url: str

# Define the graph structure for summarization and image generation
graph = StateGraph(OverallState)
graph.add_node("generate_summary", generate_summary)
graph.add_node("collapse_summaries", collapse_summaries)
graph.add_node("generate_final_summary", generate_final_summary)
graph.add_node("generate_image_prompt", generate_image_prompt)

# Connect the nodes
graph.add_edge(START, "generate_summary")
graph.add_edge("generate_summary", "collapse_summaries")
graph.add_edge("collapse_summaries", "generate_final_summary")
graph.add_edge("generate_final_summary", "generate_image_prompt")
graph.add_edge("generate_image_prompt", END)

# Compile the graph
app_graph = graph.compile()