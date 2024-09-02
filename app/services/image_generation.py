from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper

# Initialize the language model for image generation
llm_image_generation = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Define the prompt template for image generation
image_prompt_template = """
    Generate a short prompt (must be length 1000 or less) to generate an image based on the following description:
    {text}
    Note: DO NOT PRINT/ADD ANY TEXT ON IMAGE.
"""

image_prompt = ChatPromptTemplate.from_template(image_prompt_template)

async def generate_image_prompt(final_summary):
    image_chain = image_prompt | llm_image_generation | StrOutputParser()
    image_prompt_result = await image_chain.ainvoke({"text": final_summary})
    return image_prompt_result

async def generate_image(image_prompt):
    # Generate a thumbnail image using DallEAPIWrapper
    image_url = DallEAPIWrapper(model="dall-e-3").run(f"""
    DO NOT print any text on image, just use it AS-IS:
    {image_prompt}

    Guidelines:
    ------------
      - Do not include any text.
      - Generate image without map of india.
    """)
    
    return image_url