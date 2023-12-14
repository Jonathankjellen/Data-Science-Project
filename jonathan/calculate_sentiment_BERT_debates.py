# Written by jonathan kjellen



# Load model directly
import matplotlib.pyplot as plt
import json
import requests
import re
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from transformers import pipeline
import timeit
import ast

import string
import nltk
import re
if torch.cuda.is_available():  
    dev = "cuda:0" 
else:  
    dev = "cpu"  
device = torch.device(dev)  

tokenizer = AutoTokenizer.from_pretrained("KBLab/robust-swedish-sentiment-multiclass")
model = AutoModelForSequenceClassification.from_pretrained("KBLab/robust-swedish-sentiment-multiclass").to(device)





# A function that removes the first two rows of the question, that contains the names of people in the question
def remove_names(question):
    ## Split the text by line and exclude the first line
    lines = question.split('\n')[2:]
    
    # Join the remaining lines back into a single string
    new_text = '\n'.join(lines)
    
    return new_text

def chunk_text_to_window_size_and_predict_proba(input_ids, attention_mask, total_len):
    """
    This function splits the given input text into chunks of a specified window length, 
    applies transformer model to each chunk and computes probabilities of each class for each chunk. 
    The computed probabilities are then appended to a list.

    Args:
        input_ids (List[int]): List of token ids representing the input text.
        attention_mask (List[int]): List of attention masks corresponding to input_ids.
        total_len (int): Total length of the input_ids.

    Returns:
        proba_list (List[torch.Tensor]): List of probability tensors for each chunk.
    """
    proba_list = []
    
    start = 0
    window_length = 510
    
    loop = True

    while loop:
        end = start  + window_length
        # If the end index exceeds total length, set the flag to False and adjust the end index
        #print(end)
        if end >= total_len:
            loop = False
            end = total_len

        # 1 => Define the text chunk
        input_ids_chunk = input_ids[start : end]
        attention_mask_chunk = attention_mask[start : end]
        
        # 2 => Append [CLS] and [SEP]
        input_ids_chunk = [101] + input_ids_chunk + [102]
        attention_mask_chunk = [1] + attention_mask_chunk + [1]
        
        #3 Convert regular python list to Pytorch Tensor
        

        input_dict = {
            'input_ids' : torch.Tensor([input_ids_chunk]).long().to(device),
            'attention_mask' : torch.Tensor([attention_mask_chunk]).int().to(device)
        }
        
        outputs = model(**input_dict)
        
        probabilities = torch.nn.functional.softmax(outputs[0], dim = -1)
        proba_list.append(probabilities)
        start = end
    return proba_list

def get_mean_from_proba(proba_list):
    """
    This function computes the mean probabilities of class predictions over all the chunks.

    Args:
        proba_list (List[torch.Tensor]): List of probability tensors for each chunk.

    Returns:
        mean (torch.Tensor): Mean of the probabilities across all chunks.
    """
    
    # Ensures that gradients are not computed, saving memory
    with torch.no_grad():
        # Stack the list of tensors into a single tensor
        stacks = torch.stack(proba_list)

        # Resize the tensor to match the dimensions needed for mean computation
        stacks = stacks.reshape(stacks.shape[0], stacks.shape[2])

        # Compute the mean along the zeroth dimension (i.e., the chunk dimension)
        mean = stacks.mean(dim = 0)
        
    return mean

id2label= {
    0: "NEGATIVE",
    1: "NEUTRAL",
    2: "POSITIVE"
}
def calculateBERT(txt):
    #txt = remove_names(txt)
    
    tokens = tokenizer.encode_plus(txt, add_special_tokens=False)
    input_ids = tokens['input_ids']
    attention_mask = tokens['attention_mask']
    total_len = len(input_ids)
    proba_list = chunk_text_to_window_size_and_predict_proba(input_ids, attention_mask, total_len )
    stacks = torch.stack(proba_list)
    shape = stacks.shape
    torch.reshape(stacks, (shape[0], shape[2] ) )
    mean = get_mean_from_proba(proba_list)

    val = torch.argmax(mean).item()
    label_prob = torch.max(mean).item()
    probabilities = mean.tolist()
    label = id2label[val]
    return label, label_prob, probabilities

def main(file_path,save_path):
    with open(file_path, 'r') as openfile:
        json_object = json.load(openfile)
    df = pd.DataFrame(json_object)



    df["question_len"] = None
    for i in range(len(df)):
        df.at[i,"question_len"] = len(df.iloc[i]["question"].split())
        for j in range(len(df.iloc[i]["answer"])):
            answer_len = len(df.iloc[i]["answer"][j]["answer"].split())
            df.iloc[i]["answer"][j]["answer_len"] = answer_len
            

    

    df["question_BERT_label"] = None
    df["question_BERT_label_prob"] = None
    df["question_BERT_probs"] = None

    for i in range(len(df)):
        if (i%200 == 0):
            print("Question: ", i, "/", len(df))
        question = df.iloc[i]["question"]

        label,label_prob,probs = calculateBERT(question)

        df.at[i,"question_BERT_label"] = label
        df.at[i,"question_BERT_label_prob"] = label_prob
        df.at[i,"question_BERT_probs"] = probs

        for j in range(len(df.iloc[i]["answer"])):
            answer = df.iloc[i]["answer"][j]["answer"]
            
            label,label_prob,probs = calculateBERT(answer)
            df.iloc[i]["answer"][j]["answer_BERT_label"] = label
            df.iloc[i]["answer"][j]["answer_BERT_label_prob"] = label_prob
            df.iloc[i]["answer"][j]["answer_BERT_probs"] = probs

        if i % 100 == 0:
            df.to_csv(save_path, index=False)
            print("saved")
    df.to_csv(save_path, index=False)

if __name__ == '__main__':
    file_path = 'data/data_debates_2018-09-09_to_2022-09-11.txt'
    save_path = "data/data_debates_sentiment_BERT_2018_2022.csv"
    main(file_path,save_path)
    