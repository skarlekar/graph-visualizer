from langchain.prompts.prompt import PromptTemplate


TEMPLATE = """
I am providing two RDF graphs. Please combine the two RDF graphs into one RDF graph.
Only provide the final graph in the output, no description needed.

Graph 1:

{graph1}

Graph 2:

{graph2}
"""

def construct_prompt(graph1, graph2):
	prompt = PromptTemplate(
		input_variables=["graph1", "graph2"],
		template=TEMPLATE
	)
	return prompt.format(graph1=graph1, graph2=graph2)

def join_graphs(graph1, graph2, llm):
	prompt = construct_prompt(graph1, graph2)
	response = llm.invoke(prompt)
	return response.content