# Written by jonathan kjellen 

import requests
import json
from bs4 import BeautifulSoup
import re


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
        if data['dokumentlista']["@traffar"] != "0":
            dokument = data['dokumentlista']['dokument']
            next_page = data['dokumentlista']['@sida'] 
            total_pages = data['dokumentlista']['@sidor'] 
            tmp = int(next_page) + 1
            next_page = str(tmp)
            params['p'] = next_page

            return dokument, next_page, total_pages
        else:
            return [], data['dokumentlista']['@sida'] ,data['dokumentlista']['@sidor']
    else:
        return [], None,None


# Gets all data from riksdagen.se
def fetch_all_data(params):
    base_url = "https://data.riksdagen.se/dokumentlista/"
    all_data = []
    total_pages = 2
    page = 1

    while page < total_pages :
        data, page, total_pages = fetch_data(base_url, params) # None/False if there is no more next page
        page = int(page)
        total_pages = int(total_pages)
        all_data.extend(data)
    return all_data



# Uses beautiful soup to parse html page,
def text_from_url(document_html_url):

    response = requests.get(document_html_url)
    if response.status_code == 200:

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the <p> elements and extract their text
        paragraphs = soup.find_all('p')
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
                besvaradav_partibet,
                debattdag,
                ip_id):

    return {
        'id_': id_,
        'question': question,
        'question_date': question_date,
        'answer': answer,
        'undertecknare_name': undertecknare_name,
        'undertecknare_partibet': undertecknare_partibet,
        'besvaradav_name': besvaradav_name,
        'besvaradav_partibet': besvaradav_partibet,
        'debattdag':debattdag,
        'ip_id':ip_id
    }


def get_answer_from_html_using_id(id_):
    url = "https://data.riksdagen.se/dokument/"+ id_ + ".html"
    answer = text_from_url(url)
    return answer

# Get Questions
def get_data_questions(doc_type, start_date, end_date):

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
        debattdag = doc["debattdag"]
        # Get answer
        answer = ""
        ip_id = doc["rm"] +":"+ doc["nummer"]
        d = create_dict(id_que,
                    question,
                    question_date,
                    answer,
                    undertecknare_name,
                    undertecknare_partibet,
                    besvaradav_name,
                    besvaradav_partibet,
                    debattdag,
                    ip_id)

        database.append(d)
    return database



def remove_duplicates(database):
    i = 0
    while i < len(database):
        entry = database[i]
        ans = entry['answer']
        id_ = entry['id_']
        

        j = i + 1
        while j < len(database):
            entry_2nd = database[j]
            id_2nd = entry_2nd['id_']
                    
            if id_ == id_2nd and ans != "":
                database.pop(j)
                
            elif (id_ == id_2nd):
                database.pop(i)
                break
                
            else:
                j += 1

        i += 1
    return database

# Returns all the text related to the interpellation by matching the title with the target word
def text_from_url_debate_answers(document_html_url, target_word):

    response = requests.get(document_html_url)
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the sentence that contains the target word
        ans = ""
        parts = re.split(r'[/\s:]+', target_word)

        # Convert each part to an integer
        target = [int(part) for part in parts if part.isdigit()]

        # find all the titles
        h1_tags = soup.find_all('h1')
        
        # Find the title that contains the correct interpelation id and the start of the next section
        start_h1 = h1_tags[0]
        end_h1 = h1_tags[1]
        for i in range(len(h1_tags)):
            tag = [int(match.group()) for match in re.finditer(r'\b\d+\b', h1_tags[i].get_text())]
            condition1 = target[:2] == tag[1:3]
            condition2 = target[-1] in tag[3:]
            # Combine conditions
            is_match = condition1 and condition2
            if is_match:
                start_h1 = h1_tags[i]
                end_h1 = h1_tags[i+1]
                break

        current_tag = start_h1.find_next()
        # Extract all text between the title and the next title
        extracted_text = []
        while current_tag and current_tag != end_h1:
            
            if current_tag.name and current_tag.name.lower() != 'h1':
                if current_tag.name == "p" or current_tag.name == "h2":
                    extracted_text.append(current_tag.get_text())
                    ans = ans + current_tag.get_text()
                    

            current_tag = current_tag.find_next()

        return extracted_text
    else:
        return ""
    

def create_dict_debate_answer(answer,
                besvaradav_name,
                besvaradav_partibet):

    return {
        'answer': answer,
        'besvaradav_name': besvaradav_name,
        'besvaradav_partibet': besvaradav_partibet,
    }

# Filter the text from the debate to split the answers from different people 
def add_answers_from_debate(debate):
    answers = []
    paragraphs = []

    for part in debate:
        paragraph = re.split(r'\n\s*\d+\s+', part.strip())
        paragraphs.append(paragraph)

    end = len(paragraphs) - 1
    indices = [index for index, element in enumerate(paragraphs) if element[0].startswith("Anf.")]

    for i in range(len(indices)):
        header = paragraphs[indices[i]]
        words = header[0].split()
        besvaradav_name = " ".join(words[2:-1])
        besvaradav_partibet = words[-1][1:-2]
        # Check that the answer is not from a talman or the ålderspresident
        # These answers look like the following and are more information:
        # Jag vill påminna de ledamöter som vill delta i interpellationsdebatter om att man måste anmäla sig under den första omgången. Det finns information om debattregler i kammaren men också på Intranätet.
        if besvaradav_partibet != "ALMANNE" and besvaradav_partibet != "LDERSPRESIDENTE":
            answer = ""

            if i == len(indices) - 1:
                for j in range(indices[i],end):
                    answer = answer + paragraphs[j][0]
            else:
                for j in range(indices[i],indices[i+1]):
                    answer = answer + paragraphs[j][0]
            d = create_dict_debate_answer(answer, besvaradav_name, besvaradav_partibet)
            answers.append(d)
    return answers



def main():
    doc_type = "ip" # Get documents from "interpellations"
    start_date = "2018-09-09"
    end_date = "2022-09-11"

    # Get all question data
    response_questions = get_data_questions(doc_type, start_date, end_date)

    # Parse the data
    database = parse_question_data(response_questions)

    # save the interpellations 
    # with open('data_interpellation.txt', 'w') as file:
    #     # Serialize the data as JSON and write it to the file
    #     json.dump(database, file)


    doc_type = "prot" # Get documents from "kammarens protokoll"
    count = 0
    tot_len = len(database)

    for interpelation in database:
        count +=1
        if (count%10 == 0):
            print("interpellation: ", count, "/", tot_len)

        date = interpelation["debattdag"]
        if date != "":
            start_date = date
            end_date = date
            # Get all question data
            response_questions = get_data_questions(doc_type, start_date, end_date)
            if len(response_questions) > 0:
                url = "http:" + response_questions[0]["dokument_url_html"]
                target = "Svar på interpellation " + interpelation["ip_id"]
                debate = text_from_url_debate_answers(url, target)
                answers = add_answers_from_debate(debate)         
                interpelation["answer"] = answers
            else:
                interpelation["answer"] = []
        else:
            interpelation["answer"] = []


    # Save file in .txt format
    with open('data/data_debates_2018-09-09_to_2022-09-11.txt', 'w') as file:
        # Serialize the data as JSON and write it to the file
        json.dump(database, file)

if __name__ == '__main__':
    main()