from stanfordcorenlp import StanfordCoreNLP
from nltk.stem import PorterStemmer
import re
from django.conf import settings

class PreprocessPipeline:
    Stanford_corenlp_lib = settings.CORENLP
    Stopword_dictionary = Stanford_corenlp_lib+'\patterns\stopwords.txt'
    nlp = None
    
    def __init__(self):
        if(PreprocessPipeline.nlp is None):
            PreprocessPipeline.nlp = StanfordCoreNLP(PreprocessPipeline.Stanford_corenlp_lib)
        return 
    
    def process(self, words):
        if not (words is None):
            #tokenize 
            words = PreprocessPipeline.nlp.word_tokenize(words)
            #normalize to lower case, remove stopwords and punctuation
            words = self.remove_stopword(words)
            #perform remove none alphabatic and perform porter stemming
            words = self.stemming(words)
            return words
        else:
            return
    
    def remove_nonalpha(self,charseq):
        if not (charseq is None):
            return re.sub('[^A-Za-z]', '', charseq) 
        
    def stemming(self,words):
        if not (words is None):
            ps = PorterStemmer()
            index=0
            for word in words:
                words[index]=self.remove_nonalpha(word)
                words[index]=ps.stem(words[index])
                index=index+1
            return [x for x in words if x]
        else:
            return
    def remove_stopword(self,words):
        if not (words is None):
            fname = PreprocessPipeline.Stopword_dictionary
            f = open(fname,'r')
            stopwords = f.read().split('\n')
            f.close()
            i=len(words)-1;
            while 1:
                if i<0:
                    break
                words[i] = words[i].lower()
                if words[i] in stopwords:
                    del words[i]   
                i=i-1  
            return words
        else:
            return
        
    def close(self):
        PreprocessPipeline.nlp=None
        PreprocessPipeline.nlp.close()
        return
      