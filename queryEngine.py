import engine.Collector as Collector
import core.vocabulary as vocabulary
import grammar_parser as gp;
import engine.operators as operators;
import os

loc=os.path.dirname(__file__)
ruleset=gp.RuleSet(loc+'/definitions/grammar.yaml');
voc=vocabulary.Vocabulary(loc+'/definitions/definition.yaml')
defs=Collector.Definifion(loc+'/definitions/api.yaml',voc,load=True)
defs.load("Organization",{"id":"raml-org"})
#defs.storeCache()

class Matcher:


    def match(self,s1,s2):
        return s1.toLower()==s2.toLower()

max_len=7;


class Preprocessor:

    def writeTerm(self,s,t):
        if (s in self.terms):
            self.terms[s].append(t);
        else: self.terms[s]=[t];

    def __init__(self,v,defs=None,matcher=Matcher()):
        self.matcher=matcher;
        self.voc=v;
        self.defs=defs;

        self.terms={};
        for k in self.voc.propertyTerms:
            self.writeTerm(k.lower(),self.voc.propertyTerms[k]);
        for k in self.voc.classTerms:
            self.writeTerm(k.lower(),self.voc.classTerms[k]);
            self.writeTerm(k.lower()+"s",self.voc.classTerms[k]);
            self.writeTerm(k.lower()[0:len(k)-1]+"ies",self.voc.classTerms[k]);

    def preprocess(self,ts):
        while (True):
            parsed=False;
            for i in range(0,len(ts)):
                m,j=self.tryMatch(i, ts)

                if m:
                    if (len(m)==1):
                        parsed=True;
                        m=m[0]
                        tp,m=self.tokenType(m);
                        ts=ts[0:i]+[gp.Token(tp,m)]+ts[i+j+1:len(ts)];
                        break;
                    else:
                        rs=[]
                        for x in m:
                            tp,m = self.tokenType( x)
                            v=self.preprocess(ts[i+j+1:len(ts)]);
                            if (isinstance(v,gp.ResultSet)):
                                for q in v.list:
                                    rs.append(ts[0:i]+[gp.Token(tp,x)]+q);
                            else: rs.append(ts[0:i]+[gp.Token(tp,x)]+v);
                        return gp.ResultSet(rs);
            if not parsed:
                break;
        return ts;

    def tokenType(self,  x):
        tp = "";
        if (isinstance(x, vocabulary.ClassTerm)):
            tp = "cn";
        if (isinstance(x, operators.FilterGoodVals)):
            tp = "gv";
        if (isinstance(x, vocabulary.PropertyTerm)):
            tp = "pn";
        if (isinstance(x, operators.instance)):
            tp = "selector";
        if (isinstance(x,Query)):
            tp="selector";
            x=x.executionRules[0].val;
        return tp,x

    def tryMatch(self, i, ts):
        if (ts[i].name!="str"): return None,0;
        for j in range(max_len, -1, -1):
            last = i + j + 1;
            if last > len(ts):
                last = len(ts);
            tp = ts[i:last];

            toMatch = reduce(lambda y, j: str(y) + " " + str(j), [str(v.val) for v in tp]);
            m = self.tryMatchText(toMatch);
            if (m!=None):
                return m,j
        return None,0
    def tryMatchText(self,t):
        t=t.lower();
        if (t in self.terms):
            return self.terms[t];
        if (self.defs!=None):
            c=self.defs.recognize(t);
            if (c!=None):
                return [c];
        t=t.replace(" ","_");
        if (t in self.terms):
            return self.terms[t];
        if (self.defs!=None):
            t=self.defs.recognize(t);
            if (t!=None):
                return [t];
        return None;

pr=Preprocessor(voc,defs)
operators.globalContext=defs;

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

skip=["hello","hi","who","that","what","are","is","was","were","a","the","?","Who","What","Which","have"]

def tokenize(s):
    res=[]
    for k in s.split():
        if (k in skip):
            continue
        if (is_number(k)):
            res.append(gp.Token("selector",operators.instance(k,float)));
        else: res.append(gp.Token("str",k))
    return pr.preprocess(res);

class Query:
    def __init__(self,executionRules):
        self.executionRules=executionRules;

    def execute(self,context={}):
        rule=self.executionRules[0].val;
        for v in self.executionRules:
            if (v.name=="str"):
                return ["Unable to understand how to deal with "+v.val]
        return rule.execute(defs,context);

    def __str__(self):
        return str(self.executionRules);

    def __repr__(self):
        return self.__str__()

class QueryEngine():
    def welcome(self):
        return "Hello I am a bot for API query, I consumed small subset of Github API definition and I will be glad to answer on questions about:"+", ".join([x.lower()+"s" for x in voc.classTerms])
    def query(self,query):
        query=query.replace(",","")
        query=query.replace("?","")
        if (query.startswith("define")):
            v=query.index("as");
            name=query[7:v].strip();
            val=query[v+2:len(query)].strip()
            toRecord=Query(ruleset.parse(tokenize(val)));
            defs.recodNamedStuff(name,toRecord);
            defs.recodNamedStuff(name.lower(),toRecord);
            #t=defs.recognize(name);
            return toRecord;
        ts=tokenize(query);
        return Query(ruleset.parseRules(ts));