import pandas as pd

df_results = pd.read_csv("/content/drive/My Drive/BERTTOOLS/bert_output/test_results.tsv",sep="\t",header=None)
df_results

df_results_csv = pd.DataFrame({'index_col':df_test['index_col'].tolist(),
                               'Is_Response':df_results.idxmax(axis=1)})
df_results_csv

x = pd.merge(df_test, df_results_csv, on='index_col')
x

"""**Precision Recall**"""

# https://stackabuse.com/text-classification-with-python-and-scikit-learn/
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
y_test = x['label'].tolist()
y_pred = x['Is_Response'].tolist()
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))
print(accuracy_score(y_test, y_pred))