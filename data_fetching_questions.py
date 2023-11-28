import requests
import json
from bs4 import BeautifulSoup
import argparse


# Get parameters for the search using riksdagen.se RUST API
def define_params(doc_type, from_date, tom_date):

    # Define variables for the parameters
    param = {

        "sok": "",
        "doktyp": doc_type,
        "rm": "",
        "from": from_date,
        "tom": tom_date,
        "ts": "",
        "bet": "",
        "tempbet": "",
        "nr": "",
        "org": "",
        "iid": "",
        "avd": "",
        "webbtv": "",
        "talare": "",
        "exakt": "",
        "planering": "",
        "facets": "",
        "sort": "rel",
        "sortorder": "desc",
        "rapport": "",
        "utformat": "json",
        "a": "s",
        "parti": ""

    }

    return param

# Function for looping through all documents from riksdagen.se
def fetch_data(url, params):

    response = requests.get(url, params)
    if response.status_code == 200:

        data = response.json()

        if data['dokumentlista']['@traffar'] != '0':
            dokument = data['dokumentlista']['dokument']
            next_page = data['dokumentlista']['@sida'] 
            total_pages = data['dokumentlista']['@sidor'] 
            tmp = int(next_page) + 1
            next_page = str(tmp)
            params['p'] = next_page

            return dokument, next_page, total_pages
        
        else:
            return [], None, None
    else:
        return [], None, None


# Gets all data from riksdagen.se
def fetch_all_data(params):
    base_url = "https://data.riksdagen.se/dokumentlista/"
    all_data = []
    total_pages = 2
    page = 1

    while page < total_pages :
        data, page, total_pages = fetch_data(base_url, params) # None/False if there is no more next page

        if page == None:
            return all_data
        
        page = int(page)
        total_pages = int(total_pages)
        all_data.extend(data)
    return all_data



# help function for text_from_url.
# Checks if there is a <p> or div
def is_paragraph_or_div(tag):
    return tag.name == 'p' or tag.name == 'div'

# Uses beautiful soup to parte html page,

def text_from_url(document_html_url):

    response = requests.get(document_html_url)
    if response.status_code == 200:

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the <p> elements and extract their text
        paragraphs = soup.find_all(is_paragraph_or_div)
        all_text = '\n'.join(paragraph.get_text() for paragraph in paragraphs)

        return all_text
    else:
        return ""
    

def create_dict(id_,
                question,
                question_date,
                answer,
                undertecknare_name,
                undertecknare_partibet,
                besvaradav_name,
                besvaradav_partibet):

    return {
        'id_': id_,
        'question': question,
        'question_date': question_date,
        'answer': answer,
        'undertecknare_name': undertecknare_name,
        'undertecknare_partibet': undertecknare_partibet,
        'besvaradav_name': besvaradav_name,
        'besvaradav_partibet': besvaradav_partibet
    }


def get_answer_from_html_using_id(id_):
    url = "https://data.riksdagen.se/dokument/"+ id_ + ".html"
    answer = text_from_url(url)
    return answer

# Get Questions
def get_data_questions(doc_type, start_date, end_date):
# Construct the API request URL with the variables
    base_url = "https://data.riksdagen.se/dokumentlista/"

    # Change params to only include fr (skriftlig fråga)
    params = define_params(doc_type, start_date, end_date)

    # Make the GET request
    response_questions = fetch_all_data(params)
    return response_questions




def parse_question_data(response_questions):

    database = []

    count = 0
    tot_len = len(response_questions)
    for doc in response_questions:
        count +=1

        if (count%10 == 0):
            print("Parsing entry: ", count, "/", tot_len)

        # Gets question and ID
        url = "http:" + doc['dokument_url_html']
        question = text_from_url(url)
        id_que = doc['id']
        id_ans = id_que[:3] + "2" + id_que[3 + 1:]
        question_date = doc['publicerad']

        
        # Gets persons/party who asked/answered the question
        intressent_list = doc['dokintressent']['intressent']
        for item in intressent_list:
            roll = item.get('roll')
            namn = item.get('namn')
            partibet = item.get('partibet')

            if roll == 'undertecknare':
                undertecknare_name = namn
                undertecknare_partibet = partibet

            elif roll == 'besvaradav':
                besvaradav_name = namn
                besvaradav_partibet = partibet

        # Get answer
        answer = get_answer_from_html_using_id(id_ans)

        d = create_dict(id_que,
                    question,
                    question_date,
                    answer,
                    undertecknare_name,
                    undertecknare_partibet,
                    besvaradav_name,
                    besvaradav_partibet)

        database.append(d)
    return database



def remove_duplicates(database):
    for i, entry in enumerate(database):
        id_ = entry['id_']

        for j, entry_2nd in enumerate(database[i+1:]):
            id_2nd, ans_2nd = entry_2nd['id_'], entry_2nd['answer']

            if id_ == id_2nd and ans_2nd == "":
                database.pop(i + 1 + j)
            elif id_ == id_2nd:
                database.pop(i)
    return database


def main(start_date, end_date):

    doc_type = "fr" # Get documents from "Skriftlig fråga"

    # Get all question data
    response_questions = get_data_questions(doc_type, start_date, end_date)

    # Parse the data
    database = parse_question_data(response_questions)
    database = remove_duplicates(database)

    # Save file in .txt format
    with open('data.txt', 'w') as file:
        # Serialize the data as JSON and write it to the file
        json.dump(database, file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetches questions, answers and other information from riksdagen.se API, for the category \"Skriftlig fråga\" and \"Svar på skriftlig fråga\"")
    parser.add_argument("--start_date", type=str, help="Start date in YYYY-MM-DD format", required=True)
    parser.add_argument("--end_date", type=str, help="End date in YYYY-MM-DD format", required=True)
    args = parser.parse_args()
    
    main(args.start_date, args.end_date)