from langchain.chains.combine_documents.reduce import acollapse_docs, split_list_of_docs
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Initialize the language model for summarization
llm_summarization = ChatOpenAI(model="gpt-4", temperature=0)

# Define the prompt templates for summarization
map_template = "Write a concise summary of the following: {context}."
reduce_template = """
The following is a set of summaries:
{docs}
Take these and distill it into a final, consolidated summary of the main themes.
"""

map_prompt = ChatPromptTemplate([("human", map_template)])
reduce_prompt = ChatPromptTemplate([("human", reduce_template)])

# Create chains for mapping and reducing
map_chain = map_prompt | llm_summarization | StrOutputParser()
reduce_chain = reduce_prompt | llm_summarization | StrOutputParser()

async def generate_summary(contents):
    summaries = await map_chain.ainvoke(contents)
    return summaries

async def collapse_summaries(summaries):
    token_max = 1000  # Set your token limit
    doc_lists = split_list_of_docs(summaries, lambda docs: sum(len(doc) for doc in docs), token_max)
    results = []
    for doc_list in doc_lists:
        results.append(await acollapse_docs(doc_list, reduce_chain.ainvoke))
    return results

async def generate_final_summary(collapsed_summaries):
    response = await reduce_chain.ainvoke(collapsed_summaries)
    return response