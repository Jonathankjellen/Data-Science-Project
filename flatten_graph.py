from igraph import *
import json

graph = Graph.Read_GraphML("graph_topic_sentiment.graphml")


if graph.is_bipartite():

    graph.vs["is_person"] = [True if v["type"] == "person" else False for v in graph.vs]
    
    g1_questions, g2_persons = graph.bipartite_projection(graph.vs["is_person"])

    g2_persons.write_graphml("graph_flatten_persons.graphml")
    g1_questions.write_graphml("graph_flatten_questions.graphml")
