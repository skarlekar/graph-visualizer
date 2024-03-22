from langchain.prompts.prompt import PromptTemplate


def construct_prompt(ontology, text):
    prompt = PromptTemplate(
        input_variables=["ontology", "input_text"],
        template=PROMPT_TEMPLATE
    )
    return prompt.format(ontology=ontology, input_text=text)


PROMPT_TEMPLATE = """Using this provided ontology, between <ontology> tags, exclusively, please create specific instances and data about the property appraisal from the following input text, between <input_text> tags. Also, create a full and complete RDF graph without leaving any statements from the graph. Only output the graph, do not include any descriptions.

<ontology>
{ontology}
</ontology>

<input_text>
{input_text}
</input_text>"""