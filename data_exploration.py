from collections import defaultdict
from datetime import datetime

def process_party_mapping(graph, mapping_function, label):
    # Initi dict to store which party answer/questions which party
    person_to_party_mapping = {}

    # Iterate through person nodes
    for person_node in graph.vs.select(type="person"):
        party = person_node["partibet"]

        # Find the questions directed from this person
        questions_indices = graph.successors(person_node)

        for question_index in questions_indices:
            question = graph.vs[question_index]
            
            # Find the person directed from this question
            person_index = graph.successors(question)

            if len(person_index) > 0:
                person_index = person_index[0]
                person_ans = graph.vs[person_index]

                if person_ans:
                    mapping_function(person_to_party_mapping, party, person_ans)

    data_ = person_to_party_mapping

    # Dictionary for all counts for each key
    string_counts = {}

    # loop through the dictionary
    for key, values in data_.items():
        key_counts = {}  # Create a dictionary for counts specific to this key
        for value in values:
            if value in key_counts:
                key_counts[value] += 1
            else:
                key_counts[value] = 1
        string_counts[key] = key_counts

    # Print the counts for each key
    for key, key_counts in string_counts.items():
        print(f"\n{key} {label}:")
        for value, count in key_counts.items():
            print(f"{value} {count} times.")


def party_asked_which_party(graph):
    def asked_mapping(mapping_dict, party, person_ans):
        if party in mapping_dict:
            mapping_dict[party].append(person_ans["partibet"])
        else:
            mapping_dict[party] = [person_ans["partibet"]]
        


    process_party_mapping(graph, asked_mapping, "asked")


def party_answered_which_party(graph):
    def answered_mapping(mapping_dict, party, person_ans):
        person_of_ans_party = person_ans["partibet"]
        if person_of_ans_party in mapping_dict:
            mapping_dict[person_of_ans_party].append(party)
        else:
            mapping_dict[person_of_ans_party] = [party]

    process_party_mapping(graph, answered_mapping, "answered")


def questions_per_month(database):

    # Init dicts to store the counts
    total_counts = defaultdict(int)
    monthly_counts = defaultdict(int)
    yearly_counts = defaultdict(lambda: defaultdict(int))

    # Iterate through database
    for entry in database:

        # Parse date to a datetime object
        date_object = datetime.strptime(entry["question_date"], "%Y-%m-%d")
        
        # Update total counts
        total_counts[date_object.month] += 1
        
        # Update monthly counts
        monthly_counts[date_object.strftime("%B")] += 1
        
        # Update yearly counts
        yearly_counts[date_object.year][date_object.strftime("%B")] += 1

    # Average for all months and years
    # TODO: Now hardcoded for exactly 4 years
    total_months = 12*4
    average_count = sum(total_counts.values()) / total_months

    # Print all results
    print("\nAverage Questions Per Month", average_count)

    print("\nAverage Questions For Each Month")
    for month, count in monthly_counts.items():
        print(f"{month}: {count/4}")

    print("\nQuestions Per Month")
    for year, counts in yearly_counts.items():
        print(f"Year {year}:")
        for month, count in counts.items():
            print(f"    {month}: {count}")