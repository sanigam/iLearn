import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import io

from flask import Flask, request, jsonify

from transformers import BertForQuestionAnswering, BertTokenizer
#from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering

import torch
import numpy as np

import pandas_gbq
from google.cloud import bigquery
from oauthlib.oauth2 import WebApplicationClient
from google.oauth2 import service_account

import tensorflow_hub as hub

project_id='learn-339101'
gcp_service_account_file = 'learn-339101-747e8f5ac33b.json'
credentials = service_account.Credentials.from_service_account_file(gcp_service_account_file)

def retreiveData():
    queryString = """ SELECT paragraph FROM botdata.paragraph; """
    df = pandas_gbq.read_gbq(queryString, project_id = project_id, credentials=credentials)
    p_array = df['paragraph'].tolist()
    return (p_array)




model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
tokenizer_for_bert = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

# tokenizer_for_bert = BertTokenizer.from_pretrained('bert-base-uncased')
# model = BertForQuestionAnswering.from_pretrained('bert-base-uncased')

embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4" )



# tokenizer_for_bert = DistilBertTokenizer.from_pretrained('distilbert-base-uncased',return_token_type_ids = True)
# model = DistilBertForQuestionAnswering.from_pretrained('distilbert-base-uncased-distilled-squad')



def get_similar_passges (q, p_list, embeddings_p, n = 3):
    embeddings_q = embed( [q] ).numpy()
    #embeddings_p = embed( p_list ).numpy()
    embeddings_q = embeddings_q / np.linalg.norm(embeddings_q, ord=2, axis=1, keepdims=True)
    #embeddings_p = embeddings_p / np.linalg.norm(embeddings_p, ord=2, axis=1, keepdims=True)
    sim_array = np.matmul(embeddings_p, embeddings_q.T).flatten()
    ind =  (-sim_array).argsort()[:n]
    return [p_list[i] for i in ind]

def bert_answering_machine ( question, passage, max_len =  512):
    ''' Function to provide answer from passage for question asked.
        This function takes question as well as the passage 
        It retuns answer from the passage, along with start/end token index for the answer and start/end token scores
        The scores can be used to rank answers if we are searching answers for same question in multiple passages
        Value of max_len can not exceed 512. If length of question + passage + special tokens is bigger than max_len, function will truncate extra portion.
        
    '''
  
    #Tokenize input question and passage. Keeping maximum number of tokens as specified by max_len parameter. This will also add special tokens - [CLS] and [SEP]
    input_ids = tokenizer_for_bert.encode ( question, passage,  max_length= max_len, truncation=True)  
    
    
    #Getting number of tokens in 1st sentence (question) and 2nd sentence (passage)
    cls_index = input_ids.index(102) #Getting index of first SEP token
    len_question = cls_index + 1       # length of question (1st sentence)
    len_answer = len(input_ids)- len_question  # length of answer (2nd sentence)
    
    
    #BERT need Segment Ids to understand which tokens belong to sentence 1 and which to sentence 2
    segment_ids =  [0]*len_question + [1]*(len_answer)  #Segment ids will be 0 for question and 1 for answer
    
    #Converting token ids to tokens
    tokens = tokenizer_for_bert.convert_ids_to_tokens(input_ids) 
    
    
    # getting start and end scores for answer. Converting input arrays to torch tensors before passing to the model
    start_token_scores = model(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]) )[0]
    end_token_scores = model(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]) )[1]

    #Converting scores tensors to numpy arrays so that we can use numpy functions
    start_token_scores = start_token_scores.detach().numpy().flatten()
    end_token_scores = end_token_scores.detach().numpy().flatten()
    
    #Picking start index and end index of answer based on start/end indices with highest scores
    answer_start_index = np.argmax(start_token_scores)
    answer_end_index = np.argmax(end_token_scores)

    #Getting scores for start token and end token of the answer. Also rounding it to 2 decimal digits
    start_token_score = np.round(start_token_scores[answer_start_index], 2)
    end_token_score = np.round(end_token_scores[answer_end_index], 2)
    
   
    #Combining subwords starting with ## so that we can see full words in output. Note tokenizer breaks words which are not in its vocab.
    answer = tokens[answer_start_index] #Answer starts with start index, we got based on highest score
    for i in range(answer_start_index + 1, answer_end_index + 1):
        if tokens[i][0:2] == '##':  # Token for a splitted word starts with ##
            answer += tokens[i][2:] # If token start with ## we remove ## and combine it with previous word so as to restore the unsplitted word
        else:
            answer += ' ' + tokens[i]  # If token does not start with ## we just put a space in between while combining tokens
            
    # Few patterns indicating that BERT does not get answer from the passage for question asked
    if ( answer_start_index == 0) or (start_token_score < 0 ) or  (answer == '[SEP]') or ( answer_end_index <  answer_start_index):
        answer = "Sorry!, I could not find  an answer in the passage."
    
    return ( answer_start_index, answer_end_index, start_token_score, end_token_score,  answer)


#  to get answer from an array of passages
def get_answer(q, p_array):
    score_list = []
    ans_list = []
    j_list = []
    for j in range (len(p_array)):  
        #p = preprocess(p_array[j] )
        p = p_array[j] 

        start, end , start_score, end_score,  ans = bert_answering_machine (q, p)
        #print( '\nText num:', j, 'Score:', start_score, end_score, '\nBERT Answer:', ans)
        
        if (start != 0) and (start_score > 0.25)  and (ans != '[SEP]')  :
            score_list.append(str(start_score) + ' and ' + str(end_score))
            ans_list.append(ans)
            j_list.append(j)
        else:
            text_num = None
            token_scores = None
            answer = "No Answer From BERT"

            
    if len(score_list) > 0 :
        ind = np.argmax(score_list)
        #print( 'Text number:', j_list[ind], ',  Token Scores:', score_list[ind], '\nBERT Answer:', ans_list[ind])
        text_num = j_list[ind]
        token_scores = score_list[ind]
        answer = ans_list[ind]
    else:
        text_num = None
        token_scores = None
        answer = "No Answer From BERT"
    return text_num, token_scores, answer


# passages_array=["I am a student , I study in UC Davis. I like to play Tennis",
#     "John is a 10 year old boy. He is the son of Robert Smith.  Elizabeth Davis is Robert's wife. She teaches at UC Berkeley. Sophia Smith is Elizabeth's daughter. She studies at UC Davis", 
#  "My name is John. I live in San Jose, California. Rob is my friend. He lives in Seattle, Washington, My sister is Kelly. " ]
#q = "Waht is bert"


bq_data = retreiveData() 
all_passages = [ p['paragraph'] for p in bq_data]
embeddings_p = embed( all_passages ).numpy()
embeddings_p = embeddings_p / np.linalg.norm(embeddings_p, ord=2, axis=1, keepdims=True)




app = Flask(__name__)

@app.route('/')
def hello_world():
   target = os.environ.get('TARGET', 'World')
   return 'Hello {}!\n'.format(target)

@app.route('/', methods=['POST'])
def index():
   q = request.get_json()['question']
   #print("main.py", q)
   passages_array = get_similar_passges (q, all_passages, embeddings_p, n = 1)
   #print(passages_array)
   passage_num, scores, answer = get_answer(q, passages_array)
   data = { "passge_num": passage_num, "scores":scores, "answer": answer}
   return jsonify(data)
  

if __name__ == "__main__":
    app.run(debug=True)