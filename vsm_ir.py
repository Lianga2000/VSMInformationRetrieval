# This is a simple Python script.

# -*- coding: utf-8 -*-
"""hw3draft3_good_res_without_shit (3).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LmKI7Y3WtEA9e4ojtmELaF2HjUZwn23j
"""

import sys
import os
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
import xml.etree.ElementTree as ET
import math
import json
from itertools import combinations
from collections import Counter

stopwords = {"aren't", "you'd", 'or', 'those', "won't", "isn't", 'own', 'was', 'hadn', 'while', 'where', 'before',
             'being', 'doesn', 'through', "shouldn't", 'their', 'they', 'most', 'were', 'about', 'so', "hadn't", 'been',
             'shouldn', 'me', 'wouldn', 'and', 'during', 'against', 'of', 'them', 'down', 'until', 'when', 'should',
             'myself', 'haven', 'does', 'nor', "you're", 'it', 'what', 'have', 'am', 'a', 'wasn', 'not', 'to',
             "couldn't", 'didn', 'same', 'as', "wouldn't", 'with', 'that', 'weren', 'some', 'now', 'once', 'we', 'is',
             'other', 'who', "she's", 'under', 'his', 'more', 'ain', 'shan', "didn't", 'm', 'won', "mustn't", 'on',
             'hers', 'by', "weren't", 'here', 'in', 'i', 'if', 'mightn', 'having', 'an', "haven't", 'y', 'your', 'than',
             'her', 'there', 're', "you'll", 'isn', 'the', 'too', 'couldn', 'don', 'had', 'just', 'our', "mightn't",
             'you', 'my', "it's", 'few', 'between', "needn't", 'up', 'further', 'do', 'needn', "you've", 'because',
             'all', 'theirs', 'll', 'she', 'these', 'above', 't', "wasn't", 'such', 'very', 'after', 'mustn',
             'themselves', 'off', 'yourself', 'yours', 'will', 'ourselves', 'only', 'aren', 'this', 'yourselves', 'ma',
             'for', 'out', 'from', "should've", 'again', 'no', 'its', 's', "don't", 'why', 'over', 'then', 'are',
             "doesn't", 'into', 'any', 'be', 'whom', 'at', 'can', "hasn't", 'herself', 'both', 've', 'd', 'how', 'ours',
             'o', 'below', 'which', 'he', 'did', 'has', 'him', "that'll", 'hasn', 'itself', 'doing', 'each', 'himself',
             'but', "shan't"}


# going through the elements in the xml file and choosing from specified elements specific data
def get_primary_data(file, DocumentReference, inverted_index, document_similarities):
    ps = PorterStemmer()
    tokenizer = RegexpTokenizer(r'\w+')
    file_xml_tree = ET.parse(file)
    file_xml_root = file_xml_tree.getroot()
    record_num = 0
    for doc in file_xml_root.findall("./RECORD"):
        flag = 0
        for obj in doc:
            if obj.tag == "RECORDNUM":
                record_num = int(obj.text)
                if record_num not in DocumentReference:
                    DocumentReference.update(
                        {record_num: [0, 0, {"REFERENCES": [], "CITATIONS": [], "MAJORSUBJ": [], "MINORSUBJ": []}, 0,
                                      ""]})
                    document_similarities.update(
                        {record_num: {"REFERENCES": set(), "CITATIONS": set(), "MAJORSUBJ": set(), "MINORSUBJ": set()}})
            if obj.tag == "REFERENCES":
                flag += 1
        file_txt = ""
        file_txt_MAJORSUBJ = ""
        file_txt_MINORSUBJ = ""
        for obj in doc:
            if obj.tag in {"TITLE", "EXTRACT", "ABSTRACT"}:
                file_txt += str(obj.text).lower() + " "
            if obj.tag == "SOURCE":
                DocumentReference[record_num][4] = str(obj.text).lower().split(".", 1)[0]

            if obj.tag == "MAJORSUBJ":
                for topic in obj:
                    document_similarities[record_num]["MAJORSUBJ"].add(
                        str(topic.text.split(":", 1)[0]).lower().replace("-", " "))
                    file_txt_MAJORSUBJ += str(topic.text.split(":", 1)[0]).lower().replace("-", " ") + " "
            if obj.tag == "MINORSUBJ":
                for topic in obj:
                    document_similarities[record_num]["MINORSUBJ"].add(
                        str(topic.text.split(":", 1)[0]).lower().replace("-", " "))
                    file_txt_MINORSUBJ += str(topic.text.split(":", 1)[0]).lower().replace("-", " ") + " "
            if obj.tag == "REFERENCES":
                if flag == 1:
                    for cite in obj:
                        document_similarities[record_num]["REFERENCES"].add(
                            (' '.join(cite.attrib["author"].split()).lower(),
                             ' '.join(cite.attrib["publication"].split()).lower()))
                elif flag == 2:
                    flag = 1
                    for cite in obj:
                        document_similarities[record_num]["CITATIONS"].add(
                            (' '.join(cite.attrib["author"].split()).lower(),
                             ' '.join(cite.attrib["publication"].split()).lower()))
            if obj.tag == "CITATIONS":
                for cite in obj:
                    document_similarities[record_num]["CITATIONS"].add(
                        (' '.join(cite.attrib["author"].split()).lower(),
                         ' '.join(cite.attrib["publication"].split()).lower()))
        file_txt = tokenizer.tokenize(file_txt)
        file_txt_MAJORSUBJ = tokenizer.tokenize(file_txt_MAJORSUBJ)
        file_txt_MINORSUBJ = tokenizer.tokenize(file_txt_MINORSUBJ)
        d_file_txt = {"file_txt": [file_txt, 1], "file_txt_MAJORSUBJ": [file_txt_MAJORSUBJ, 1.5],
                      "file_txt_MINORSUBJ": [file_txt_MINORSUBJ,
                                             1.1]}  # minor 1.2 for tfidf.. 1.1 for bm25, major 1.7 for tfidf. tho for bm25 1.5 or 1.3... 2 for tfidf tho f1 is smaller

        lis = []

        for txt_type in d_file_txt:
            for word in d_file_txt[txt_type][0]:
                adder = d_file_txt[txt_type][1]
                if word not in stopwords:
                    word = ps.stem(word)
                    lis.append(word)
                    if word in inverted_index:
                        if record_num in inverted_index[word]["records"]:
                            inverted_index[word]["records"][record_num] += adder
                        else:
                            inverted_index[word]["records"][record_num] = adder
                            inverted_index[word]["df"] += 1
                    else:
                        inverted_index[word] = {"df": 1, "records": {record_num: adder}}

        freq = Counter(lis)
        max_f = 0
        for i in freq:
            if freq[i] > max_f:
                max_f = freq[i]
        DocumentReference[record_num][1] = len(file_txt)
        DocumentReference[record_num][3] = max_f


# for each document updating the docs that are similar to it
def update_similarities(DocumentReference, document_similarities, alpha=0.8, beta=0.8):
    res = list(combinations([i for i in document_similarities], 2))
    # avg_scores = {"CITATIONS":[0,0,0.4], "REFERENCES":[0,0,0.4], "MAJORSUBJ":[0,0,1], "MINORSUBJ":[0,0,0.2]}
    # for i in res:
    #     for type_str in {"CITATIONS", "REFERENCES", "MAJORSUBJ", "MINORSUBJ"}:
    #         s11 = document_similarities[i[0]][type_str]
    #         s21 = document_similarities[i[1]][type_str]
    #         i1 = set.intersection(s11, s21)
    #
    #         d1 = s11.difference(s21)
    #         d2 = s21.difference(s11)
    #         a = min(len(d1), len(d2))
    #         b = max(len(d1), len(d2))
    #
    #         u1 = set.union(s11, s21)
    #         try:
    #             #j1 = max(len(i1) / len(s11), len(i1) / len(s21))
    #             j1 = (len(i1)/(len(i1) + beta*a + alpha*b))#len(i1)/len(u1)#max(len(i1) / len(s11), len(i1) / len(s21))
    #         except:
    #             j1 = 0
    #
    #         if (j1>=avg_scores[type_str][2]):
    #             avg_scores[type_str][0] += j1
    #             avg_scores[type_str][1] += 1
    #
    # print(avg_scores)
    # for type_str in {"CITATIONS", "REFERENCES", "MAJORSUBJ", "MINORSUBJ"}:
    #     avg_scores[type_str][0] = avg_scores[type_str][0]/avg_scores[type_str][1]
    # print(avg_scores)
    avg_scores = {'CITATIONS': [0.6268095339976784, 99, 0.4], 'REFERENCES': [0.5199150190862325, 93, 0.4],
                  'MAJORSUBJ': [1.0, 8769, 1], 'MINORSUBJ': [0.2874374415078146, 220011, 0.2]}
    for i in res:
        for type_str in {"CITATIONS", "REFERENCES", "MAJORSUBJ", "MINORSUBJ"}:
            s11 = document_similarities[i[0]][type_str]
            s21 = document_similarities[i[1]][type_str]
            i1 = set.intersection(s11, s21)

            d1 = s11.difference(s21)
            d2 = s21.difference(s11)

            try:
                j1 = (len(i1) / (len(i1) + beta * len(d1) + alpha * len(d2)))  # Tversky index
            except:
                j1 = 0

            if j1 >= avg_scores[type_str][0] or (
                    j1 >= 0.8 * avg_scores[type_str][0] and DocumentReference[i[0]][4] == DocumentReference[i[1]][4]):
                DocumentReference[i[0]][2][type_str].append(i[1])
                DocumentReference[i[1]][2][type_str].append(i[0])


# updating tf, idf values, updating each document's vector length
def update_vector_length(N, DocumentReference, inverted_index):
    for word in inverted_index:
        n_word = len(inverted_index[word]["records"])
        idf = math.log2(N / n_word)
        for record_num in inverted_index[word]["records"]:
            tf = inverted_index[word]["records"][record_num]
            ntf = tf / DocumentReference[record_num][
                1]  # raw count of term word in document record_num divided by the length of the document
            DocumentReference[record_num][0] += (ntf * idf) ** 2

    for record_num in DocumentReference:
        DocumentReference[record_num][0] = math.sqrt(DocumentReference[record_num][0])


# document_similarities
# key = record_num, value = {"REFERENCES": set(), "CITATIONS": set(), "MAJORSUBJ": set(), "MINORSUBJ": set()}}
# each key holds a set of values for the element (key) in the paper
# this dict is updated in -get_primary_data-
# while going through the elements in the xml file, for each element from the above keys, we add its values to the value of the respected element (key)

# DocumentReference
# key = record_num, value =  [0, 0, {"REFERENCES": [], "CITATIONS": [], "MAJORSUBJ": [], "MINORSUBJ": []}, 0, ""]
# [0, 0, {"REFERENCES": [], "CITATIONS": [], "MAJORSUBJ": [], "MINORSUBJ": []}, 0, ""] =
# [vector length, paper's length, {“REFERNCES”: [], “CITATIONS”: [], “MAJORSUBJ”: [], “MINORSUBJ”:[]}, paper's maximum frequency of word, publication name]
# the dictionary at index 2 is updated in -update_similarities-, each key holds a list of the most similar docs to the current doc by similary function for the specific element (key).
# It's evalueated using document_similarities.
# index 1: is updated in -get_primary_data-, for each paper we speciffacly choose its text, and update its length.
# index 3: is updated in -get_primary_data-, for each paper we speciffacly choose its text, and update the maximum frequency of word in the text.
# index 0: is updated in -update_vector_length-, for each word in the index we look at all the docs that containing it, evaluate tf-idf, and add the square of it to the length, at the end we aquare root the sum.
# index 4: is updated in -get_primary_data-, the value of "SOURCE" in the xml of the paper.

# inverted index
# key = word, value = {"df": #docs with word, "records": {record_num1: tf_word_record_num1_iD, ..., record_numk: tf_word_record_numk_iD}}
# tf_word_record_numi_iD = special-tf of word in doc (from Database) record_numi
# notice that special-tf is not raw count of the word in record_numi, we have a special adder instead of adding 1 for each appearance of word in record_numi
# it's updated in -get_primary_data-, after selecting the paper's text we go through it, word by word, and update the index.
# notice that words appearing in elements MAJORSUBJ/MINORSUBJ add to tf (of the word in the paper) special adders.

def create_index(input_dir):
    DocumentReference = {}
    inverted_index = {}
    corpus = {"inverted_index": inverted_index, "DocumentReference": DocumentReference}
    document_similarities = {}

    for file_name in os.listdir(input_dir):
        if file_name.endswith(".xml"):
            file = input_dir + "/" + file_name
            get_primary_data(file, DocumentReference, inverted_index, document_similarities)

    update_similarities(DocumentReference, document_similarities)

    N = len(DocumentReference)
    update_vector_length(N, DocumentReference, inverted_index)

    corpus_file = open("vsm_inverted_index.json", "w")
    json.dump(corpus, corpus_file)
    corpus_file.close()

# Tokenize and eliminate punctuations, filter stopwords, stemming. Update the index for the query.
def update_query(question, query_index):
    ps = PorterStemmer()
    tokenizer = RegexpTokenizer(r'\w+')
    question = tokenizer.tokenize(question)
    updated_query = []
    for word in question:
        if word not in stopwords:
            word = ps.stem(word)
            updated_query += [word]
            if word in query_index:
                query_index[word] += 1
            else:
                query_index[word] = 1

    return updated_query



# Retrieval Algorithm (RA) using Inverted-Index - as shown in class
def RA(N, query_details, DocumentReference, inverted_index):
    R = {}
    for token in query_details[1]:
        try:
            n_word = (inverted_index[token]["df"])
            I = math.log2(N / n_word)
            K = query_details[1][token] / query_details[0]
            W = K * I
        except:
            W = 0
            I = 0
        if inverted_index.get(token) != None:
            L = inverted_index[token]["records"]
            for O in L:
                if O not in R:
                    R[O] = 0
                C = inverted_index[token]["records"][O] / (DocumentReference[O][1])
                R[O] += W * I * C

    return R


# Retrieval Algorithm cont. (RAC) using Inverted-Index - as shown in class
def RAc(N, query_details, inverted_index, DocumentReference):
    final_docs = {}

    # Calc query vector length
    L = 0
    for word in query_details[1]:
        try:
            n_word = (inverted_index[word]["df"])
            I = math.log2(N / n_word)
            tf_idf = (query_details[1][word] / query_details[0]) * I
            L += tf_idf ** 2
        except:
            L += 0
    L = math.sqrt(L)  # square-root of the sum of the squares of its weights

    R = RA(N, query_details, DocumentReference, inverted_index)
    for d in R:
        S = R[d]
        Y = DocumentReference[str(d)][0]
        score = S / (Y * L)
        final_docs[d] = score
    # Sort list by cosSim
    return sorted(final_docs.items(), key=lambda item: item[1], reverse=True)

def Func_score(N, query_details, inverted_index, DocumentReference, Func="bm25", k1=3, b=0.75):
    potential_docs = set()
    R = {}
    for token in query_details[1]:  # choosing all documents conataining at least one word from the query
        if inverted_index.get(token) is not None:
            for O in inverted_index[token]["records"]:
                potential_docs.add(O)

    avgdl = 0
    for d in DocumentReference:
        avgdl += DocumentReference[d][1]
    avgdl = avgdl / N
    for O in potential_docs:
        score = 0
        for word in query_details[1]:

            try:
                n_word = (inverted_index[word]["df"])
                tf_word_O_iD = inverted_index[word]["records"][O]  # / DocumentReference[O][1]
                if Func == "bm25":  # evaluating scores for potential documents by bim25 scoring
                    idf_word = math.log((N - n_word + 0.5) / (n_word + 0.5) + 1)
                    score += (idf_word) * ((tf_word_O_iD * (k1 + 1)) / (
                            tf_word_O_iD + k1 * (1 - b + b * (DocumentReference[str(O)][1] / avgdl))))
                else:
                    delta = 0.9#0.6
                    k3 = 0.5
                    idf_word = math.log((N + 1) / n_word)
                    tf_word_O_iQ = query_details[1][word]
                    if Func == "bm25+":  # evaluating scores for potential documents by bim25+ scoring
                        a = (((k3 + 1) * tf_word_O_iQ) / (k3 + tf_word_O_iQ))
                        score += (idf_word) * a * ((tf_word_O_iD * (k1 + 1)) / (
                                tf_word_O_iD + k1 * (1 - b + b * (DocumentReference[str(O)][1] / avgdl))) + delta)
                    elif Func == "piv+":  # evaluating scores for potential documents by piv+ scoring
                        s = 0.5
                        delta = 0.7
                        score += (tf_word_O_iQ) * ((1 + math.log(1 + math.log(tf_word_O_iD))) / (
                                1 - s + s * (DocumentReference[str(O)][1] / avgdl)) + delta) * (idf_word)
            except:
                score += 0

        R[O] = score
    return sorted(R.items(), key=lambda item: item[1], reverse=True)


def ranking_by(N, query_details, inverted_index, DocumentReference, ranking="tfidf"):
    if ranking == "tfidf":
        return RAc(N, query_details, inverted_index, DocumentReference)

    return Func_score(N, query_details, inverted_index, DocumentReference, Func=ranking)

# get scoring functions, and retrieve only the docs they agree on, scoring them with normalized summation of the original scores
def mixed_scoring(N, query_details, inverted_index, DocumentReference, scoring_funcs):
    common_docs = set()  # set.intersection(chosen_docs_1_set, chosen_docs_2_set)
    for idx, f in enumerate(scoring_funcs):
        scoring_funcs[f][0] = ranking_by(N, query_details, inverted_index, DocumentReference, ranking=f)
        scoring_funcs[f][1] = set(i[0] for i in scoring_funcs[f][0])
        scoring_funcs[f][2] = dict(scoring_funcs[f][0])
        if idx == 0:
            common_docs = scoring_funcs[f][1]
        else:
            common_docs = set.intersection(common_docs, scoring_funcs[f][1])
    chosen_docs_dict = {}
    for i in common_docs:
        chosen_docs_dict[i] = 0
        for f in scoring_funcs:
            chosen_docs_dict[i] += scoring_funcs[f][2][i] / scoring_funcs[f][0][0][1]
    chosen_docs = (sorted(chosen_docs_dict.items(), key=lambda item: item[1], reverse=True))
    return chosen_docs

def add_similar_docs(DocumentReference, chosen_docs, min_val, ranking="bm25"):
    chosen_docs_dict = dict(chosen_docs)
    for i in chosen_docs:
        s1 = set(DocumentReference[i[0]][2]["REFERENCES"])
        s2 = set(DocumentReference[i[0]][2]["CITATIONS"])
        s3 = set(DocumentReference[i[0]][2]["MAJORSUBJ"])
        s4 = set(DocumentReference[i[0]][2]["MINORSUBJ"])

        i12 = set.intersection(s1, s2)
        i13 = set.intersection(s1, s3)
        i14 = set.intersection(s1, s4)
        i23 = set.intersection(s2, s3)
        i24 = set.intersection(s2, s4)
        i34 = set.intersection(s3, s4)

        if ranking == "bm25":
            u1 = set.union(i12, i13, i14, i23, i24, i34)  # set.union(i123, i124, i134, i234)
        else:
            u1 = s1

        for doc in u1:
            if doc in chosen_docs_dict:
                chosen_docs_dict[doc] = max(min_val, chosen_docs_dict[doc])
            else:
                chosen_docs_dict[doc] = min_val

    return sorted(chosen_docs_dict.items(), key=lambda item: item[1], reverse=True)


# Retrieve information given the specific ranking, a question and an inverted index path.
def ev_query(ranking, index_path, question):
    query_index = {}  # word,cnt
    query_details = [0, query_index]  # length, inverted_index for query i.e key=word, value=tf of word in query

    json_file = open(index_path, "r")

    corpus = json.load(json_file)  # Insert the json file to the global dictionary.
    inverted_index = corpus["inverted_index"]
    DocumentReference = corpus["DocumentReference"]
    json_file.close()

    N = len(DocumentReference)  # number of documents in the dataset

    question = update_query(question.lower(),
                            query_index)  # Manipulate the string query to list of words without stopwords and with stemming, as well as updating query_index.
    query_details[0] = len(question)

    chosen_docs = []
    if ranking == "bm25":
        th1 = 6.1
        chosen_docs = ranking_by(N, query_details, inverted_index, DocumentReference, ranking="bm25")
        chosen_docs = [i for i in chosen_docs if (1.6 * i[1] >= chosen_docs[0][1] and i[1] >= th1)]
        if len(chosen_docs) > 10:
            # adding similar docs to the chosen docs to the final array of the chosen docs.
            chosen_docs = add_similar_docs(DocumentReference, chosen_docs, chosen_docs[-1][1])

    elif ranking == "mix":  # choosing the documents that tfidf and bm25 agree on and scoring each doc as mixed scores
        #th1 = 0.0
        chosen_docs = mixed_scoring(N, query_details, inverted_index, DocumentReference,
                                    {"bm25": [None, None, None], "tfidf": [None, None, None]})
        chosen_docs = [i for i in chosen_docs if (1.8 * i[1] >= chosen_docs[0][1])]
        if len(chosen_docs) > 10:
            chosen_docs = add_similar_docs(DocumentReference, chosen_docs, chosen_docs[-1][1])

    elif ranking == "bm25+":
        chosen_docs = ranking_by(N, query_details, inverted_index, DocumentReference, ranking="bm25+")
        chosen_docs = [i for i in chosen_docs if (1.7 * i[1] >= chosen_docs[0][1])]
        if len(chosen_docs):# > 10:
            chosen_docs = add_similar_docs(DocumentReference, chosen_docs, chosen_docs[-1][1])

    elif ranking == "piv+":
        th1 = 0.65
        chosen_docs = ranking_by(N, query_details, inverted_index, DocumentReference, ranking="piv+")
        chosen_docs = [(i[0], i[1] / chosen_docs[0][1]) for i in chosen_docs]
        chosen_docs = [i for i in chosen_docs if (1.7 * i[1] >= chosen_docs[0][1] and i[1] >= th1)]
        if len(chosen_docs) > 10:
            chosen_docs = add_similar_docs(DocumentReference, chosen_docs, chosen_docs[-1][1])

    elif ranking == "tfidf":
        th1 = 0.1
        chosen_docs = ranking_by(N, query_details, inverted_index, DocumentReference, ranking="tfidf")
        chosen_docs = [i for i in chosen_docs if (2 * i[1] >= chosen_docs[0][1] and i[1] >= th1)]
        if chosen_docs:
            chosen_docs = add_similar_docs(DocumentReference, chosen_docs, chosen_docs[-1][1], ranking)

    f = open("ranked_query_docs.txt", "w")
    docs_num = []
    for i in chosen_docs:
        f.write("%s\n" % i[0])
        docs_num.append(int(i[0]))

    f.close()
    #return (docs_num)  # return docs_num for testing

def main():
    if sys.argv[1] == "create_index":
        create_index(sys.argv[2])
    elif sys.argv[1] == "query":
        ev_query(sys.argv[2], sys.argv[3], sys.argv[4])  # query(ranking, index_path, question)
    else:
        print("something is wrong...")


main()
exit()
