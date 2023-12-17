# Detecting Opinion Change and Cleavage in Parliamentary Data

Welcome to the repository for the Riksdagen Detecting Opinion Change and Cleavage in Parliamentary Data. This project aims to analyze parliamentary data retrieved from the REST API provided by riksdagen.se. The methodology involves data exploration, performing sentiment analysis, applying topic modeling algorithms, creating networks, detecting controversy, exploring hot topics, and tracking sentiment changes over time. This is for a project conducted at Uppsala University, in a course called "Project in Data Science" 15 credits.

## Methodology

### 3.1 Preprocessing

Data was collected from the riksdagen.se REST API, specifically focusing on "Skriftlig fråga" and "Svar på skriftlig fråga." Information such as ID, timestamp, answering party, questioning party, questioner's name, and respondent's name was stored. Text for questions and answers was retrieved using the respective ID. Data cleanup involved removing duplicates and resolving missing text issues.

### 3.2 Sentiment Analysis

Sentiment analysis were performed using the BERTSentiment model, based on BERT architecture, and VADER. BERTSentiment, released by the national library of Sweden, demonstrated superior performance. VADER, while effective for social media texts, struggled with formal language used by politicians.

### 3.3 Topic Modelling Algorithm

Topic modeling employed the BERTopic algorithm, a TF-IDF-based method that leverages the BERT embeddings. The decision to use BERTopic was based on its performance to create accurate understandable topics, in parts in comparison to LDA. BERTopic also offers flexibility in its components to incorporate new state-of-the-art components. The topics models model files were to big to include in the directory.

### 3.4 Network

Network analysis utilized igraph and NetworkX to represent bipartite networks with nodes for people and topics. Community detection, attribute assortativity coefficient, and degree distributions were explored. Gephi was employed for visualization, providing insights into relationships and clusters within the network.

### 3.5 Controversy Detection

Controversy detection followed a 2-dimensional definition considering importance and contention, based on voter surveys and sentiment differences between questions and answers. The contoversy was then calculated as the multiplication of contention and importance.

### 3.6 Hot Topics

To identify hot topics, the project analyzed the frequency of topic discussions among different political parties over time.

### 3.7 Sentiment Change

Sentiment change over time was explored for each party and topic, plotting sentiments from 2006 to 2022 and correlating with party support data.

## How to Use

1. Install the repository using

    ```bash
    git clone https://github.com/your-username/your-repo.git
    cd your-repo
    ```
    
2. Fetch all parlamentary data, given start date, end data, and output name:

    ```bash
    cd data_fetching
    python data_fetching_questions.py --start_date 2023-01-01 --end_date 2023-12-31 --output_name output_data
    ```
    
3. Install the required dependencies:

    ```bash
    pip install notebook pandas shapely
    ```

4. Run the Jupyter Notebooks related to each Methodology, how each notebook is used can be found in each respective notebook
