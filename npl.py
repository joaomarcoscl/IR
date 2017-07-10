######################################################
###### Base: NPL - National Physical Laboratory ######
######################################################
# 11429 - Documentos
# 93 - Querys
# 13 - Termos - Query 81
# 84 - Documentos - Query 41
# Termos - 7878

################
# Observacoes  #
################
# BM25 - Deixou mais lento

# Importações
import nltk
import string
import numpy as np
import pickle
import operator
import matplotlib.pyplot as pl
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
import sys 
from time import time

stemmer       = PorterStemmer()
querys        = []
querysOri     = []
text_trans    = []
text_trans1   = [] # Texto completo
termos_trans  = []
termos_trans1 = [] # Termo completo
grPrecision   = []
grPrecision1  = []
grPrecision2  = []
grPrecision3  = []
grPrecision4  = [] # BM25
grRecall      = []
grRecall1     = []
grRecall2     = []
grRecall3     = []
grRecall4     = [] # BM25
expansion     = 5      # Retornam os N documentos mais relevantes por cada termo
pc1           = 0      # Parametro de configuração 1 ("Quantidade de Documentos por Termo") - Retrieval (Padrão: 0 - Todos)
pc2           = 1      # Parametro de configuração 2 ("Peso")                               - Retrieval (Padrão: 1 - Todos) | (Padrão: 0.50 - Mais relevantes)
pc3           = 100000 # Parametro de configuração 3 ("N maiores documentos retornados")    - Retrieval (Padrão: 100000 - Todos)
#---------------------------------------------------------------------------------------#
def retrieval(terms, matrix_dt):
    result_docs = []
    for term in terms:
        sum_vector = np.sum(matrix_dt[:,term]) # Quantos documentos para cada termo
        norm = dict()
        for i in (np.where(matrix_dt[:,term]>pc1)[0]+1).tolist():   # documentos do termo
            norm[i] = float(matrix_dt[i-1, term])/float(sum_vector) # frequencia do termos no documento
        norm_sort = sorted(norm.items(), key=operator.itemgetter(1),reverse=True)[:pc3] # os pc3 primeiros (documentos)
        sum_norm_sort = 0
        for i in norm_sort:
            sum_norm_sort = sum_norm_sort + i[1]
            result_docs.append(i[0])
            if sum_norm_sort >= pc2: # Relevancia (1 - Todos, 0.5 os 50% mais importantes)
                break
            pass
    return set(result_docs)

#---------------------------------------------------------------------------------------#
# Com dicionários de sinônimos
def tokenize_stopwords_stemmer(text, stemmer, query):
    no_punctuation = text.translate(None, string.punctuation)
    tokens = nltk.word_tokenize(no_punctuation)
    text_filter = [w for w in tokens if not w in stopwords.words('english')]
    text_final = ''
    if query == True: # Se for query
        for k in range(0, len(text_filter)):
            for i in wn.synsets(text_filter[k]):
                for s in i.lemma_names():
                    text_filter.append(s)

    for k in range(0, len(text_filter)):
        text_final +=str(stemmer.stem(text_filter[k]))
        if k != len(text_filter)-1:
            text_final+=" "
            pass
    return text_final

def tokenize_stopwords_stemmer1(text, stemmer):
    no_punctuation = text.translate(None, string.punctuation)
    tokens = nltk.word_tokenize(no_punctuation)
    text_filter = [w for w in tokens if not w in stopwords.words('english')]
    text_final = ''
    for k in range(0, len(text_filter)):
        text_final +=str(stemmer.stem(text_filter[k]))
        if k != len(text_filter)-1:
            text_final+=" "
            pass
    return text_final

#---------------------------------------------------------------------------------------#
def organizes_documents():
    files = open('npl/doc-text', 'r').read().split('/')
    for i in range(0,len(files)):
        text = files[i].strip()
        text = text.replace(str(i+1), '')
        text = text.strip()
        text_trans.append(tokenize_stopwords_stemmer(text.lower(), stemmer, False))
    generate_matrix()

#---------------------------------------------------------------------------------------#
def organizes_querys():
    files = open('npl/query-text', 'r').read().split('/')
    for i in range(0,len(files)):
        textq = files[i].strip()
        textq = textq.replace(str(i+1), '')
        textq = textq.strip()
        querys.append(textq.lower())

#---------------------------------------------------------------------------------------#
def save_object(obj, filename):
    with open('objects/'+filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def load_object(filename):
    with open(filename, 'rb') as input:
        return pickle.load(input)

def generate_matrix():
    document_term = CountVectorizer()
    # Salvando em arquivo
    matrix_document_term = document_term.fit_transform(text_trans)
    save_object(document_term.get_feature_names(), 'terms_npl.dt')
    matrix_dt = np.matrix(matrix_document_term.toarray())
    save_object(matrix_dt, 'matrix_npl.dt')
    matrix_tt = np.dot(np.transpose(matrix_dt), matrix_dt)
    save_object(matrix_tt, 'matrix_npl.tt')
    pass

#---------------------------------------------------------------------------------------#
# Consulta normal
def search (query, terms_dt, matrix_tt):
    termss = []
    for i in query:
        if i in terms_dt:
            key = terms_dt.index(i)
            termsO = np.matrix(matrix_tt[key,key])
            for j in termsO.tolist()[0]:
                termss.append(matrix_tt[key, :].tolist()[0].index(j))
            pass
        pass
    pass
    return termss

# Consulta expandida
def search_expanded(query, terms_dt, matrix_tt):
    terms = []
    for i in query:
        if i in terms_dt:
            key = terms_dt.index(i) # Pega a posicao que o termo se encontra
            terms_recommended = np.sort(matrix_tt[key])[:, len(matrix_tt)-expansion:len(matrix_tt)] # Final da Linha os 5 ultimos colunas (maiores)
            for j in terms_recommended.tolist()[0]:
                terms
                terms.append(matrix_tt[key, :].tolist()[0].index(j)) # Retorna o indice da frequencia j
            pass
            if key in terms == False or expansion == 0:
                terms.append(key)
        pass
    pass
    return set(terms)

#---------------------------------------------------------------------------------------#
# Documentos relevantes
def relevants_documents():
    relevants_resume = dict() # Vetor chave valor
    files = open('npl/rlv-ass', 'r').read().split('/')
    for i in range(0,len(files)):
        textr = files[i].strip()
        textr = textr.strip()
        textr = textr.replace('\n', ' ')
        textr = textr.replace('  ', ' ')
        textr = textr.replace('  ', ' ')

        line = np.array(textr.split(' ')).tolist()
        key = int(line[0]) # Indice das consultas
        for j in range(len(line)-1):
            if key in relevants_resume:
                relevants_resume[key].append(int(line[j+1]))
            else:
                relevants_resume[key] = [int(line[j+1])]
            pass
    pass
    return relevants_resume

#---------------------------------------------------------------------------------------#
# Ranqueamento (BM25)
def avg_documents(matrix_dt):
    soma = 0
    for i in range(0, len(matrix_dt)):
        soma += np.sum(matrix_dt[i, :])
    return float(soma)/float(len(matrix_dt))

def ranqueamento(matrix_dt, terms_dt, documents_retrieval, query, avg):
        qs = QuerySearch(matrix_dt, avg)
        query_result = dict()
        for docid in documents_retrieval:
            for q in query:
                if q in terms_dt:
                    score = qs.BM25(docid,terms_dt.index(q))
                    if(not docid in query_result):
                        query_result[docid] = score
                    else:
                        query_result[docid]=query_result[docid] + score

        query_result = dict(sorted(query_result.items(), key=operator.itemgetter(1),reverse=True)).keys()[0:int(len(documents_retrieval)*0.3)]
        return query_result

class QuerySearch(object):
    def __init__(self,matrix, avg):
        self.k = 2.0
        self.b = 0.75
        self.matrix = matrix
        self.avg = avg

    def BM25(self,docid,qid):
        df = self.calc_df(qid)
        tf = self.calc_tf(docid,qid)
        dsize = np.sum(self.matrix[docid,:])
        N = len(self.matrix)
        result = self.idf(N,df)*(tf*(self.k+1))/(tf+self.k*(1-self.b+self.b*(dsize/self.avg)))
        return result

    def idf(self,N,df):
        return np.log((N-df+0.5)/(df+0.5))

    def calc_df(self, qid):
        return len(np.where(self.matrix[:,qid]>0)[0])

    def calc_tf(self, docid,qid):
        return len(np.where(self.matrix[docid,qid]>0)[0])

#---------------------------------------------------------------------------------------#
def main():
    t0 = time()

    amount_documents = len(matrix_dt)
    mean_precision   = 0
    mean_recall      = 0
    mean_acuracy     = 0
    mean_precision1  = 0
    mean_recall1     = 0
    mean_acuracy1    = 0
    mean_precision2  = 0
    mean_recall2     = 0
    mean_acuracy2    = 0
    mean_precision3  = 0
    mean_recall3     = 0
    mean_acuracy3    = 0
    mean_precision4  = 0
    mean_recall4     = 0
    mean_acuracy4    = 0

    print "############################################"
    for i in xrange(0,len(querys)-1):
        query_token2         = tokenize_stopwords_stemmer1(querys[i], stemmer)
        query_token          = tokenize_stopwords_stemmer(querys[i], stemmer, True) # Sinonimos
        query                = querys[i] # Original

        #############
        # retrieval #
        #############
        # terms_dt
        terms                = search         (set(query_token2.split(' ')), terms_dt, matrix_tt)  # Sem expansao
        terms1               = search_expanded(set(query_token2.split(' ')), terms_dt, matrix_tt)  # Com expansao
        terms2               = search         (set(query_token.split(' ')) , terms_dt, matrix_tt)  # Sem expansao + Sinonimos
        terms3               = search_expanded(set(query_token.split(' ')) , terms_dt, matrix_tt)  # Com expansao + Sinonimos
        terms4               = search_expanded(set(query_token.split(' ')) , terms_dt, matrix_tt)  # Com expansao + Sinonimos (para BM25)

        # Sem expansao
        documents_retrieval  = retrieval(terms, matrix_dt)
        documents_relevants  = relevants_documents()[i+1]
        TP                   = len(documents_retrieval.intersection(documents_relevants))
        FP                   = len(documents_retrieval) - TP
        FN                   = len(documents_relevants) - TP
        TN                   = len(matrix_dt) - len(documents_retrieval)
        SOMA                 = TP+FP+FN+TN
        Acuracia2            = float(len(documents_retrieval.intersection(documents_relevants)) + amount_documents - len(documents_retrieval))/float(amount_documents)
        doc_rel_rec          = sorted(list(documents_retrieval.intersection(documents_relevants)))

        mean_precision       = mean_precision + (float(TP)/float(TP+FP))
        mean_recall          = mean_recall    + (float(TP)/float(TP+FN))
        mean_acuracy         = mean_acuracy   + (float(TP+TN)/float(TP+TN+FP+FN))

        # Com expansao
        documents_retrieval1 = retrieval(terms1, matrix_dt)
        documents_relevants1 = relevants_documents()[i+1]
        TP1                  = len(documents_retrieval1.intersection(documents_relevants1))
        FP1                  = len(documents_retrieval1) - TP1
        FN1                  = len(documents_relevants1) - TP1
        TN1                  = len(matrix_dt) - len(documents_retrieval1)
        SOMA1                = TP1+FP1+FN1+TN1
        Acuracia21           = float(len(documents_retrieval1.intersection(documents_relevants1)) + amount_documents - len(documents_retrieval1))/float(amount_documents)
        doc_rel_rec1         = sorted(list(documents_retrieval1.intersection(documents_relevants1)))

        mean_precision1 = mean_precision1 + (float(TP1)/float(TP1+FP1))
        mean_recall1    = mean_recall1    + (float(TP1)/float(TP1+FN1))
        mean_acuracy1   = mean_acuracy1   + (float(TP1+TN1)/float(TP1+TN1+FP1+FN1))

        # Sem expansao + Sinonimos
        documents_retrieval2  = retrieval(terms2, matrix_dt)
        documents_relevants2  = relevants_documents()[i+1]
        TP2                   = len(documents_retrieval2.intersection(documents_relevants2))
        FP2                   = len(documents_retrieval2) - TP2
        FN2                   = len(documents_relevants2) - TP2
        TN2                   = len(matrix_dt) - len(documents_retrieval2)
        SOMA2                 = TP2+FP2+FN2+TN2
        Acuracia22            = float(len(documents_retrieval2.intersection(documents_relevants2)) + amount_documents - len(documents_retrieval2))/float(amount_documents)
        doc_rel_rec2          = sorted(list(documents_retrieval2.intersection(documents_relevants2)))

        mean_precision2 = mean_precision2 + (float(TP2)/float(TP2+FP2))
        mean_recall2    = mean_recall2    + (float(TP2)/float(TP2+FN2))
        mean_acuracy2   = mean_acuracy2   + (float(TP2+TN2)/float(TP2+TN2+FP2+FN2))

        # Com expansao + Sinonimos
        documents_retrieval3 = retrieval(terms3, matrix_dt)
        documents_relevants3 = relevants_documents()[i+1]
        TP3                  = len(documents_retrieval3.intersection(documents_relevants3))
        FP3                  = len(documents_retrieval3) - TP3
        FN3                  = len(documents_relevants3) - TP3
        TN3                  = len(matrix_dt) - len(documents_retrieval3)
        SOMA3                = TP3+FP3+FN3+TN3
        Acuracia23           = float(len(documents_retrieval3.intersection(documents_relevants3)) + amount_documents - len(documents_retrieval3))/float(amount_documents)
        doc_rel_rec3         = sorted(list(documents_retrieval3.intersection(documents_relevants3)))

        mean_precision3 = mean_precision3 + (float(TP3)/float(TP3+FP3))
        mean_recall3    = mean_recall3    + (float(TP3)/float(TP3+FN3))
        mean_acuracy3   = mean_acuracy3   + (float(TP3+TN3)/float(TP3+TN3+FP3+FN3))

        # Com expansao + Sinonimos + BM25
        documents_retrieval4   = retrieval(terms4, matrix_dt)
        documents_retrieval4   = set(ranqueamento(matrix_dt, terms_dt, documents_retrieval4, query_token.split(' '), avg))
        documents_relevants4   = relevants_documents()[a+1]
        TP4                    = len(documents_retrieval4.intersection(documents_relevants4))
        FP4                    = len(documents_retrieval4) - TP4
        FN4                    = len(documents_relevants4) - TP4
        TN4                    = len(matrix_dt) - len(documents_retrieval4)
        SOMA4                  = TP4+FP4+FN4+TN4
        Acuracia24             = float(len(documents_retrieval4.intersection(documents_relevants4)) + amount_documents - len(documents_retrieval4))/float(amount_documents)
        doc_rel_rec4           = sorted(list(documents_retrieval4.intersection(documents_relevants4)))

        mean_precision4 = mean_precision4 + (float(TP4)/float(TP4+FP4))
        mean_recall4    = mean_recall4    + (float(TP4)/float(TP4+FN4))
        mean_acuracy4   = mean_acuracy4   + (float(TP4+TN4)/float(TP4+TN4+FP4+FN4))

        #Gráfico
        grPrecision.append(float(TP)/float(TP+FP))
        grPrecision1.append(float(TP1)/float(TP1+FP1))
        grPrecision2.append(float(TP2)/float(TP2+FP2))
        grPrecision3.append(float(TP3)/float(TP3+FP3))
        grPrecision4.append(float(TP4)/float(TP4+FP4))	

        grRecall.append(float(TP)/float(TP+FN))
        grRecall1.append(float(TP1)/float(TP1+FN1))
        grRecall2.append(float(TP2)/float(TP2+FN2))
        grRecall3.append(float(TP3)/float(TP3+FN3))
        grRecall4.append(float(TP4)/float(TP4+FN4))

        print "Query....: " + str(i+1) + " - Sem Expansao"
        print "------------------------------------------"
        print "Qtd.Documentos Relevantes................: " + str(len(documents_relevants))
        print "Qtd.Documentos Recuperados...............: " + str(len(documents_retrieval)) + " (" + str(TP) + ")"
        print "Precision: " + str(float(TP)/float(TP+FP))
        print "Recall...: " + str(float(TP)/float(TP+FN))
        print "Acuracia.: " + str(float(TP+TN)/float(TP+TN+FP+FN))
        print "----------------------------------------------"
        print "Query....: " + str(i+1) + " - Com Expansao (" + str(expansion) +")"
        print "----------------------------------------------"		
        print "Qtd.Documentos Relevantes................: " + str(len(documents_relevants1))
        print "Qtd.Documentos Recuperados...............: " + str(len(documents_retrieval1)) + " (" + str(TP1) + ")"
        print "Precision: " + str(float(TP1)/float(TP1+FP1))
        print "Recall...: " + str(float(TP1)/float(TP1+FN1))
        print "Acuracia.: " + str(float(TP1+TN1)/float(TP1+TN1+FP1+FN1))
        print "------------------------------------------------------"
        print "Query....: " + str(i+1) + " - Sem Expansao + Sinonimos"
        print "------------------------------------------------------"
        print "Qtd.Documentos Relevantes................: " + str(len(documents_relevants2))
        print "Qtd.Documentos Recuperados...............: " + str(len(documents_retrieval2)) + " (" + str(TP2) + ")"
        print "Precision: " + str(float(TP2)/float(TP2+FP2))
        print "Recall...: " + str(float(TP2)/float(TP2+FN2))
        print "Acuracia.: " + str(float(TP2+TN2)/float(TP2+TN2+FP2+FN2))
        print "----------------------------------------------------------"
        print "Query....: " + str(i+1) + " - Com Expansao + Sinonimos (" + str(expansion) +")"
        print "----------------------------------------------------------"
        print "Qtd.Documentos Relevantes................: " + str(len(documents_relevants3))
        print "Qtd.Documentos Recuperados...............: " + str(len(documents_retrieval3)) + " (" + str(TP3) + ")"
        print "Precision: " + str(float(TP3)/float(TP3+FP3))
        print "Recall...: " + str(float(TP3)/float(TP3+FN3))
        print "Acuracia.: " + str(float(TP3+TN3)/float(TP3+TN3+FP3+FN3))
        print "------------------------------------------------------"
        print "Query....: " + str(i+1) + " - Com Expansao + Sinonimos usando BM25"
        print "------------------------------------------------------"
        print "Qtd.Documentos Relevantes................: " + str(len(documents_relevants4))
        print "Qtd.Documentos Recuperados...............: " + str(len(documents_retrieval4)) + " (" + str(TP4) + ")"
        print "Precision: " + str(float(TP4)/float(TP4+FP4))
        print "Recall...: " + str(float(TP4)/float(TP4+FN4))
        print "Acuracia.: " + str(float(TP4+TN4)/float(TP4+TN4+FP4+FN4))
        print "############################################"
        print ""
        pass
    pass
    print "*******************************"
    print "Modelo 1 - Sem expansão"
    print "*******************************"
    print "Precisão..: " + str(round((mean_precision/len(querys)*100),2)) + "%"
    print "Cobertura.: " + str(round((mean_recall/len(querys)*100),2)) + "%"
    print "Acurácia..: " + str(round((mean_acuracy/len(querys)*100),2)) + "%"
    print ""
    print "*******************************"
    print "Modelo 2 - Com expansão (" + str(expansion) +")"
    print "*******************************"
    print "Precisão..: " + str(round((mean_precision1/len(querys)*100),2)) + "%"
    print "Cobertura.: " + str(round((mean_recall1/len(querys)*100),2)) + "%"
    print "Acurácia..: " + str(round((mean_acuracy1/len(querys)*100),2)) + "%"
    print ""
    print "***************************************"
    print "Modelo 3 - Sem expansão e com sinônimos"
    print "***************************************"
    print "Precisão..: " + str(round((mean_precision2/len(querys)*100),2)) + "%"
    print "Cobertura.: " + str(round((mean_recall2/len(querys)*100),2)) + "%"
    print "Acurácia..: " + str(round((mean_acuracy2/len(querys)*100),2)) + "%"
    print ""
    print "*******************************************"
    print "Modelo 4 - Com expansão e com sinônimos (" + str(expansion) +")"
    print "*******************************************"
    print "Precisão..: " + str(round((mean_precision3/len(querys)*100),2)) + "%"
    print "Cobertura.: " + str(round((mean_recall3/len(querys)*100),2)) + "%"
    print "Acurácia..: " + str(round((mean_acuracy3/len(querys)*100),2)) + "%"
    print ""    
    print "*******************************************"    
    print "Modelo 5 - Com expansão, com sinônimos e usando BM25 (" + str(expansion) +")"
    print "*******************************************"
    print "Precisão..: " + str(round((mean_precision4/len(querys)*100),2)) + "%"
    print "Cobertura.: " + str(round((mean_recall4/len(querys)*100),2)) + "%"
    print "Acurácia..: " + str(round((mean_acuracy4/len(querys)*100),2)) + "%"
    print "*******************************************"
    print("done in %fs" % (time() - t0))

############
# Executar #
############
organizes_documents() # Apenas a primeira vez para gerar os objetos (demorada: +- 8hs)
organizes_querys()
matrix_dt           = load_object('objects/matrix_npl.dt')
matrix_tt           = load_object('objects/matrix_npl.tt')
terms_dt            = load_object('objects/terms_npl.dt')
avg = avg_documents(matrix_dt)

main()

pl.clf()
pl.plot(np.sort(grRecall), np.sort(grPrecision)  , label='Sem expansao')
pl.plot(np.sort(grRecall1), np.sort(grPrecision1), label='Com expansao')
pl.plot(np.sort(grRecall2), np.sort(grPrecision2), label='Sem expansao + Sinonimos')
pl.plot(np.sort(grRecall3), np.sort(grPrecision3), label='Sem expansao + Sinonimos')
pl.xlabel('Recall')
pl.ylabel('Precision')
pl.title('Precision-Recall - Colecao: NPL')
pl.legend(loc="upper left")
pl.show()
