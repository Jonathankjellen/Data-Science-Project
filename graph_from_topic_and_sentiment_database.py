import ast
from igraph import *
import matplotlib.pyplot as plt

# Function to check if a vertex with the same name already exists
def vertex_exists(graph, name):
    for vertex in graph.vs:
        if vertex["name"] == name:
            return True
    return False


def add_person_respondent(graph, entry):
    undertecknare_name = entry["undertecknare_name"]
    undertecknare_partibet = entry["undertecknare_partibet"]
    
    bert_probs = ast.literal_eval(entry['question_BERT_probs'])
    if not vertex_exists(graph, undertecknare_name):
        vertex = graph.add_vertex(undertecknare_name, type="person")
        vertex["partibet"] = undertecknare_partibet
        vertex["question_BERT"] = [bert_probs]
    else:
        vertex = graph.vs.find(undertecknare_name)
        vertex["question_BERT"].append(bert_probs)
        
def add_person_answerer(graph, entry, answer):
    if (answer != ""): #Checks if there is an answer
        # Add a node for the person in the igraph
        
        besvaradav_name = entry["besvaradav_name"]
        besvaradav_partibet = entry["besvaradav_partibet"]
        
        bert_probs = ast.literal_eval(entry['answer_BERT_probs'])
      
        if not vertex_exists(graph, besvaradav_name):
            vertex = graph.add_vertex(besvaradav_name, type="person")
            vertex["partibet"] = besvaradav_partibet
            vertex["answer_BERT"] = [bert_probs]
        
        else:
            vertex = graph.vs.find(besvaradav_name)
            vertex["answer_BERT"].append(bert_probs)
        
        graph.add_edge(id_, besvaradav_name)

def add_question_answer(graph, entry, id_):
    vertex = graph.add_vertex(id_, type="question")
    
    # Time
    vertex['question_date'] = entry['question_date']
    
    # Party
    vertex['partibet'] = "?"
    
    # Topics
    vertex['name_topic_combined'] = entry['name_topic_combined']
    vertex['name_topic_question'] = entry['name_topic_question']
    vertex['name_topic_answer'] = entry['name_topic_answer']
    
    # Probabilities
    bert_probs_a = ast.literal_eval(entry['answer_BERT_probs'])
    
    vertex['answer_BERT_label'] = entry['answer_BERT_label']
    vertex['answer_BERT_label_prob'] = entry['answer_BERT_label_prob']
    vertex['answer_by_party'] = entry["besvaradav_partibet"]
    
    
    vertex['question_BERT_label'] = entry['question_BERT_label']
    vertex['question_BERT_label_prob'] = entry['question_BERT_label_prob']
    vertex['question_by_party'] = entry["undertecknare_partibet"]

    
    # Q and A
    vertex['question'] = entry['question']
    vertex['answer'] = entry['answer']


# Create an igraph Graph object
graph = Graph(directed=True)

data_part = data_sentiment
for entry in data_part:
    id_ = entry['id_']
    answer = entry["answer"]
    undertecknare_name = entry['undertecknare_name']

    # Adds a node for the person in the igraph (The one who asked the question)
    add_person_respondent(graph, entry)
    
    # Adds a node for the question-answer into the graph
    add_question_answer(graph, entry, id_)    
    
    # Creates edge between respondent and the question-answer node
    graph.add_edge(undertecknare_name, id_)

    # Adds a node for the person in the igraph (The one who answered the question)
    # Note that this also ands an edge depending on if there in an answer or not
    add_person_answerer(graph, entry, answer)


def average_person_sentiment(graph):
    for vertex in graph.vs.select(type="person"):
        if vertex['question_BERT'] is not None or vertex['answer_BERT'] is not None:
            if vertex['question_BERT'] is not None:
                zipped_lists = zip(*vertex['question_BERT'])
            else:
                zipped_lists = zip(*vertex['answer_BERT'])

            bert_probs = [(sum(group) / len(group)) for group in zipped_lists]

            vertex['bert_negative'] = bert_probs[0]
            vertex['bert_neutral'] = bert_probs[1]
            vertex['bert_positive'] = bert_probs[2]

    del graph.vs['question_BERT']
    del graph.vs['answer_BERT']
    return graph