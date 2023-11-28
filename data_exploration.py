from collections import defaultdict
from datetime import datetime


def party_asked_which_party(database):
    dict_ans = defaultdict(lambda: defaultdict(int))
    
    for entry in database:
        asked_by_party = entry["undertecknare_partibet"]
        answe_by_party = entry["besvaradav_partibet"]

        dict_ans[asked_by_party][answe_by_party] += 1

    # Print the counts for each key
    for key, key_counts in dict_ans.items():
        print(f"\n{key} questioned:")
        for value, count in key_counts.items():
            print(f"{value} {count} times.")




def party_answered_which_party(database):
    dict_ans = defaultdict(lambda: defaultdict(int))
    
    for entry in database:
        asked_by_party = entry["undertecknare_partibet"]
        answe_by_party = entry["besvaradav_partibet"]

        dict_ans[answe_by_party][asked_by_party] += 1

    # Print the counts for each key
    for key, key_counts in dict_ans.items():
        print(f"\n{key} answered:")
        for value, count in key_counts.items():
            print(f"{value} {count} times.")


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