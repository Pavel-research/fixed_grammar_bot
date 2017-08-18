import yaml
class ClassTerm:
    def __init__(self,name,yaml,voc):
        self.name=name;
        self.yaml=yaml;
        self.voc=voc;
        self.properties={}
        self.subTypes=[]
        self.extends=[]
        if ('properties' in yaml):
            props=yaml['properties']
            for p in props:
                voc.propertyTerms[p].domain=self;
                self.properties[p]=voc.propertyTerms[p];

    def __str__(self):
        return self.name;
    def __repr__(self):
        return self.__str__()

    def bindExtends(self):
        if ("extends" in self.yaml):
            super=self.voc.classTerms[self.yaml['extends']];
            self.extends.append(super);
            super.subTypes.append(self)
    def allProperties(self):
        rs={};
        for c in self.extends:
            ps=c.allProperties();
            for p in ps:
                rs[p]=ps[p];
        for p in self.properties:
            rs[p]=self.properties[p]
        return rs;
    def toDict(self,i):
        res={};
        d=dir(i);
        all=self.allProperties();
        for p in all:
            if (p in d):
                val=getattr(i,p)
                if (all[p].range):
                    if (isinstance(val,list)):
                        vl=[]
                        for v in val:
                            vl.append(all[p].range.toDict(v));
                        val=vl
                    else:
                        val=all[p].range.toDict(val)
                res[p]=val;
        return res;

class PropertyTerm:
    def __init__(self,name,yaml,voc):
        self.name=name;
        self.yaml=yaml;
        self.voc=voc;
        self.subProps=[]
        self.extends=[]
        self.domain=None
        self.range=None
        self.inversionOf=None
        if "inverseOf" in yaml:
            self.inverseOf=yaml["inverseOf"]
        else: self.inverseOf=None
    def __str__(self):
        return self.name;
    def __repr__(self):
        return self.__str__()
    def bindExtends(self):
        if ("extends" in self.yaml):
            super=self.voc.propertyTerms[self.yaml['extends']];
            self.extends=super;
            super.subProps.append(self)
        if ('range' in self.yaml):
            rng=self.yaml['range'];
            self.range=self.voc.classTerm(rng)
            if (rng=='integer'):
                self.range=int;
            if (rng=='number'):
                self.range=float;
            if (rng=='string'):
                self.range=str;
        if self.inverseOf!=None:
            self.inverseOf=self.voc.propertyTerms[self.inverseOf];
            self.inverseOf.inversionOf=self;
class Vocabulary:
    def __init__(self,p):
        self.classTerms={}
        self.propertyTerms={}
        self.load(p)
        for z in set(self.propertyTerms.values()):
            if ('sameAs' in z.yaml):
                for s in z.yaml['sameAs']:
                    self.propertyTerms[s]=z;
    def classTerm(self,name):
        if (name in self.classTerms):
          return self.classTerms[name];
        return None
    def prop(self,name):
        if (name in self.propertyTerms):
            return self.propertyTerms[name]
        return None;
    def load(self, s):
        with open(s) as f:
            dataMap = yaml.safe_load(f)
            pt= dataMap['propertyTerms'];
            for p in pt:
                self.propertyTerms[p]=PropertyTerm(p,pt[p],self);
            if 'classTerms' in dataMap:
                ct=dataMap['classTerms'];
                for c in ct:
                    self.classTerms[c]=ClassTerm(c,ct[c],self);
            for v in self.classTerms:
                self.classTerms[v].bindExtends();
            for v in self.propertyTerms:
                self.propertyTerms[v].bindExtends();
class DataGraph:
    def __init__(self,voc):
        self.voc=voc;