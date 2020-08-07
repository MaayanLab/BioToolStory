import os
import json
import shutil
import connexion
from whoosh import index, qparser, query
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from flask_cors import CORS
from flask import jsonify
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import warnings
from bert_serving.server.helper import get_args_parser
from bert_serving.server import BertServer
from bert_serving.client import BertClient
from bert_serving.server.helper import get_shutdown_parser
#import subprocess
from os import listdir
from os.path import isfile, join
import re
#import scipy.stats as ss
#from scipy.spatial import distance
#import scipy.spatial.distance

load_dotenv(verbose=True)

PTH = os.environ.get('PTH_A')

# load BERT vectors for tools
pth = os.path.join(PTH,'vectors/')
files = [f for f in listdir(pth) if isfile(join(pth, f))]
tools_mat = np.load(os.path.join(PTH,'vectors/'+str(files[0])))
# group vectors to a matrix
print('loading vectors...')
tools_ids = [files[0].replace('.npy','')]
for file in files[1:]:
  vec2 = np.load(os.path.join(PTH,'vectors/'+str(file)))
  tools_mat = np.concatenate((tools_mat,vec2), axis=0)
  tools_ids.append(file.replace('.npy',''))

# start BERT server
# def start_server():
#   os.system("bert-serving-terminate -port 5555")
#   args = get_args_parser().parse_args([ '-model_dir', os.path.join(PTH,'biobert'),
#                                       '-tuned_model_dir', os.path.join(PTH,'biobert'),
#                                       '-port', '5555',
#                                       '-port_out', '5556',
#                                       '-max_seq_len', 'NONE',
#                                       '-mask_cls_sep',
#                                       '-ckpt_name', 'model.ckpt-1000000',
#                                       '-max_batch_size', '16',
#                                       '-cpu'])
#   server = BertServer(args)
#   server.start()
#   print("server online")


# Compute cosine distances between each row of matrix and a given vector
def most_similar_tools(vector,mat):
  sim = [cosine_similarity(vector, v.reshape(1,-1), 'cosine')[0][0] for v in mat ] 
  sim_dic = dict(zip(tools_ids, sim)) # create dictionary
  sim_dic = {k: str(v) for k, v in sorted(sim_dic.items(), key=lambda item: item[1],reverse=True)} # sort ASC
  return sim_dic


def print_dictionary(dic):
  for x in list(dic)[0:5]:
    print ("Top 5 similar tools key {}, value {} ".format(x,  dic[x]))


def get_sim(tool_text):
  bc = BertClient(port=5555)
  vector = bc.encode([str(tool_text)])
  print(vector)
  bc.close() 	# close client server
  # Enable code below to rank the vector...
  # t = ss.rankdata(t)
  res = most_similar_tools(vector, tools_mat) # get tools (pubmed ids) ordered by similarity ASC
  print_dictionary(res) # validation: print the 5 most similar tools
  return (json.dumps(res))
  

# web server
#start_server()
app = connexion.App(__name__)
CORS(app.app)
app.add_api(os.path.join(PTH,'swagger.yaml'))
application = app.app


if __name__ == '__main__':
  print('server is up')
  app.run(port=8080, server='gevent')
  # delfolders()
  

