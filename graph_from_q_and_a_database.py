from igraph import *
import matplotlib.pyplot as plt

def remove_duplicates(database):
    """
    Removes duplicates from a list of dictionaries based on a specified key.
    """
    for i, entry in enumerate(database):
        id_ = entry['id_']
        for j, entry_2nd in enumerate(database[i+1:]):
            id_2nd, ans_2nd = entry_2nd['id_'], entry_2nd['answer']
            if id_ == id_2nd and ans_2nd == "":
                database.pop(i + 1 + j)
            elif id_ == id_2nd:
                database.pop(i)
    return database

def create_graph(data, output):
    """
    Creates an igraph Graph object and populates it with nodes and edges based on data from a list of dictionaries.
    """
    # Function to check if a vertex with the same name already exists
    def vertex_exists(graph, name):
        for vertex in graph.vs:
            if vertex["name"] == name:
                return True
        return False
    
    # Create an igraph Graph object
    graph = Graph(directed=True)
    
    for entry in data:
        id_ = entry['id_']
        question = entry["question"]
        answer = entry["answer"]
        undertecknare_name = entry["undertecknare_name"]
        undertecknare_partibet = entry["undertecknare_partibet"]
        besvaradav_name = entry["besvaradav_name"]
        besvaradav_partibet = entry["besvaradav_partibet"]
        
        # Add a node for the person in the igraph
        if not vertex_exists(graph, undertecknare_name):
            vertex = graph.add_vertex(undertecknare_name, type="person")
            vertex["partibet"] = undertecknare_partibet
            
        vertex_que = graph.add_vertex(id_, type="question")
        vertex_que['answer'] = answer
        vertex_que['question'] = question
        vertex_que['partibet'] = "?"
        
        graph.add_edge(undertecknare_name, id_)
        
        if (answer != ""): #Checks if there is an answer
            # Add a node for the person in the igraph
            if not vertex_exists(graph, besvaradav_name):
                vertex = graph.add_vertex(besvaradav_name, type="person")
                vertex["partibet"] = besvaradav_partibet
            graph.add_edge(id_, besvaradav_name)

    graph.write_graphml(output + ".graphml")