from rdf_extractor_experiment import extract
import importlib
import argparse

rdf_to_cypher_neptune = importlib.import_module('rdf-to-cypher-neptune')


def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-d", "--doc_name", help="Document filename")
    parser.add_argument("-o", "--ontology_name", help="Ontology name")

    args = parser.parse_args()
    
    doc_key = args.doc_name if args.doc_name != None else 'MFRUnderwritingTemplate-Example.pdf'
    ontology_key = args.ontology_name if args.ontology_name != None else 'underwriting-narrative.ttl'
    
    graph = extract(doc_link=doc_key, ontology_link=ontology_key)
    rdf_to_cypher_neptune.main(graph)


if __name__ == '__main__':
    main()
    