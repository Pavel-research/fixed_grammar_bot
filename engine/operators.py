
class Executable:
    def execute(self,ds,context):
        v=[];
        if ("$val" in context):
            v=context["$val"];
        res=self(v);
        context["$val"]=res;
        return res;
class Optionated(Executable):
    def domain(self):
        rs=set([x.domain() for x in self.options])
        rs.remove(object)
        if (len(rs)==1):
            return rs.pop();
        return object;

class Or(Optionated):
    def __init__(self,options):
        self.options=options;
    def __call__(self, *args, **kwargs):
        res=set()
        for option in self.options:
            if (callable(option)):
                result=option(args[0]);
                for v in result:
                    res.add(v);
            else:
                for v in args[0]:
                    if (v==option):
                        res.add(v)
        return res;
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        if len(self.options)==1:
            return str(self.options[0]);
        return "or"+str(self.options);

class And(Optionated):
    def __init__(self,options):
        self.options=options;

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        if len(self.options) == 1:
            return str(self.options[0]);
        return "and" + str(self.options);
    def __call__(self, *args, **kwargs):
        res=None;
        rs=set();
        #print self.options[0].data
        for option in self.options:
            result=option(args[0]);
            if (res==None): res=result;
            else:
                if (isinstance(res,bool)):
                    res=res and res;
                else: res=res.intersection(result);
        return res;
class Not:
    def __init__(self,options):
        self.options=options;
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return "not " + str(self.options);
    def __call__(self, *args, **kwargs):
        if (isinstance(args[0],set) or isinstance(args[0],list)):
           s=set()
           for v in args[0]:
               s.add(v);
           v=self.options(args[0])
           s=s.difference(v);
           return s
        result=self.options(args[0]);
        if (len(result)>0 or result==True):
            return False;
        return True;
    def domain(self):
        return self.options.domain()
class ChildFilter:
    def __init__(self,parent,filter,child):
        self.parent=parent;
        self.filter=filter;
        self.child=child;
    def domain(self):
        return self.parent.domain();
    def __repr__(self):
        return str(self)
    def __str__(self):
        return str(self.parent)+" childFilter"+str(self.filter)+" "+str(self.child)

    def __call__(self, *args, **kwargs):
        parentVals=self.parent.execute(globalContext,args[0]);
        childVals=self.child.execute(globalContext,args[0]);
        rs=[];
        for p in parentVals:
            ch=p.children();
            fc=[]
            for c in ch:
                if (c in childVals):
                    fc.append(c)
            m=self.filter(fc);
            if (m==True):
                rs.append(p);
        return rs;

    def execute(self,ds,v):
        r= self(v)
        v['$val']=r;
        return r;
class CountCompare:
    def __init__(self,options,op):
        self.options=options;
        self.op=op;
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return " count "+self.op+" " + str(self.options);
    def domain(self):
        return object
    def execute(self,ds,v):
        v=v["$val"];
        return set([i for i in v if self(i)==True])
    def __call__(self, *args, **kwargs):
        #print args[0]
        result=self.options(args[0]);
        #for (i in args[0]):
        if (self.op=='>'):
            if (float(str(result))<len(args[0])):
                return True;
            return False;
        else:
            if (float(str(result))>len(args[0])):
                return True;
            return False;

class Compare:
    def __init__(self,options,op,prop):
        self.options=options;
        self.op=op;
        self.prop=prop;
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return str(self.prop)+self.op+" " + str(self.options);
    def domain(self):
        return object
    def __call__(self, *args, **kwargs):
        result=float(str(self.options(args[0])));
        res=set();
        for z in args[0]:
            vv=z[self.prop.name]
            if (vv>result):
                res.add(z);
        return res;

    def execute(self,ds,v):
        vv=v['$val']
        r=self(vv)
        v["$val"]=r;
        return r;
class Flow:
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if len(self.chain) == 1:
            return str(self.chain[0]);
        res=""
        for i in range(0,len(self.chain)):
            res=res+str(self.chain[i]);
            if (i<len(self.chain)-1):
                res=res+"=>";
        return res;

    def domain(self):
        d=self.chain[0];
        for q in self.chain:
            d1=q.domain();
            if (not isinstance(d1,type)):
                d=d1;
        return d
    def __init__(self,*args):
        if (len(args)==1):
            self.chain=args[0];
        else:
            self.chain=args;
        self.res=None;
    def __call__(self, *args, **kwargs):
        v=args[0];
        if (self.res!=None):return self.res;
        for op in self.chain:
            if (isinstance(op,FilterByVals)):
                op.inFlow=True
            v=op(v);
        self.res=v;
        return v;
    def execute(self,ds,context):
        for op in self.chain:
            v=op.execute(ds,context);
            context["$val"]=v;
        return context["$val"]
class Eq:
    def __init__(self,val):
        self.val=val;
    def __call__(self, *args, **kwargs):
        res=set();
        for v in args[0]:
            if (v==self.val): res.add(v);
        return res;
class ParentValueFilter:
    def __init__(self,val):
        self.val=val;
    def __call__(self, *args, **kwargs):
        res=set();
        if (args[0]==None):
            return res;
        for v in args[0]:
            if (isinstance(v,instance)):
                if (v.references(self.val)):
                        res.add(v);
            # else:
            #     print "AAA"
        return res;
    def execute(self,ds,v):
        return self(v["$val"])
    def __repr__(self):
        return self.__str__()

    def domain(self):
        return object;

    def __str__(self):
        return "parent("+str(self.val)+")"
class CountInstances:
    def __init__(self,toCount):
        self.toCount=toCount
    def __repr__(self):
        return self.__str__()

    def __str__(self):
            return "count("+str(self.toCount)+")"

    def domain(self):
        return int
    def __call__(self, *args, **kwargs):
        if (self.toCount!=None):
            vl=self.toCount(*args);
            return len(vl)
        return len(args[0]);
    def execute(self,ds,v):
        val=[];
        if "$val" in v:
            val=v["$val"]
        r= self(val)
        v['$val']=r;
        return r;

globalContext=None;
class SelectInstances:
    def __init__(self,class_name):
        self.class_name=class_name;

    def __repr__(self):
        return self.__str__()

    def domain(self):
        return self.class_name;

    def __call__(self, *args, **kwargs):
        return self.execute(globalContext,{})

    def execute(self,ds,context):
        globalContext=ds;
        res= ds.instances(self.class_name);
        context['$val']=res;
        return res;
    def __str__(self):
            return "select("+str(self.class_name)+")"


class FilterByVals:
    def __init__(self,vals):
        self.vals=vals;
        self.inFlow=False;
    def domain(self):
        return object

    def __repr__(self):
        return self.__str__()

    def execute(self,ds,s):
        return self(ds,s)
    def __call__(self, *args, **kwargs):
        v=self.vals();
        if (isinstance(args[0],list)or isinstance(args[0],set)):
            if (self.inFlow):
                s=set(args[0]);
                r=s.intersection(v);
                return r;
            for m in args[0]:
                if m in v:
                    return True;
            return False;

        return args[0] in v;
    def __str__(self):
            return " in ("+str(self.vals)+")"


class FilterGoodVals:
    def __init__(self,vals):
        self.vals=[vals];
        self.inFlow=False;
    def domain(self):
        return object

    def __repr__(self):
        return self.__str__()
    def execute(self,ds,v):
        r= self()
        v["$val"]=r;
        return r;
    def __call__(self, *args, **kwargs):
        v=self.vals;
        res=set();
        for m in globalContext.cache.values():
            for k in m:
                if (m[k] in self.vals):
                    res.add(instance(m,m["$type"].clazz));
                elif isinstance(m[k],dict):
                    for z in self.vals:
                        if (isinstance(z,instance) and 'url' in m[k]):
                            if z['url']==m[k]['url']:
                                #print z['url']+":"+m[k]['url']
                                res.add(instance(m,m["$type"].clazz));

        #print len(res)
        return res;
    def __str__(self):
        return " has_value ("+str(self.vals)+")"

class FilterPropertyValue:
    def __init__(self,pn,pred):
        self.pn=pn;
        self.pred=pred;
        if (isinstance(pred,FilterGoodVals)):
            self.pred=pred.vals

    def __repr__(self):
            return self.__str__()

    def domain(self):
        return self.pn.domain

    def execute(self,ds,context):
        if not isinstance(context,dict):
            print "Ha"
        v=context["$val"];
        res=self(v);
        context["$val"]=res;
        return res;

    def __str__(self):
        if (callable(self.pred) and not isinstance(self.pred,instance)):
            return str(self.pn)+" matches "+str(self.pred)

        return str(self.pn)+'=='+str(self.pred);
    def __call__(self, *args, **kwargs):
        res=set();
        n= self.pn.name

        for v in args[0]:
            if isinstance(v,list):
                print "A"
            if (callable(self.pred) and not isinstance(self.pred,instance)):
                vs=v[n];
                am=self.pred(vs)
                if isinstance(am,bool):
                    if (am==True):
                        res.add(v);
                elif vs in am:
                   res.add(v);
            else:
                #print v[n]
                if v[n]==self.pred:
                    res.add(v)
                if (isinstance(self.pred,list)):

                    for q in self.pred:
                        if (v[n]==q):
                            res.add(v)
        return res;
class Count:
    def __init__(self,pred):
        self.pred=pred;
    def __call__(self, *args, **kwargs):
        return len(self.pred(args[0]));
    def execute(self,ds,v):
        return self(v["$val"])
import json;
class TakePropertyValue(Executable):
    def __init__(self,pred,pn):
        self.pn=pn;
        self.pred=pred;

    def execute(self,ds,context):
        return self(ds,context);

    def __call__(self, *args, **kwargs):
        res=set();
        if len(args)>1:
            rr=self.pred.execute(args[0],args[1])
        else:
            rr=self.pred.execute(globalContext,{ "$val":args[0]});
        for v in rr:
            #res.add(json.JSONEncoder().encode(v.data.keys()))
            vals=v[self.pn.name];
            if (vals!=None):
                if (isinstance(vals,list)):
                    for q in vals:

                        res.add(q);
                else: res.add(vals)
        if len(args)>1:
            args[1]['$val']=res;
        print len(res)
        return res;
    def __repr__(self):
        return self.__str__()
    def domain(self):
        return self.pn.range
    def __str__(self):
         return str(self.pred)+"["+str(self.pn)+"]"

class instance:
    def __init__(self,data,type):
        self.data=data;
        self.type=type;
        if (data==None):
            raise ValueError()
    def __call__(self, *args, **kwargs):
        if (type(self.data)==type):
            return self.data;
        return self;
    def references(self,vl):
        if (isinstance(vl,list) or isinstance(vl,set)):
            for q in self.data:
                if(self[q] in vl):
                    return True
        if (isinstance(self.data,dict)):
            for q in self.data:
                if(self[q]==vl):
                    return True

        return False
    def __hash__(self):
        return self.data['url'].__hash__();

    def execute(self,ds,v):
        return [self]

    def children(self):
        return globalContext.children(self.type,self);

    def __getitem__(self, item):
        if not item in self.data:
            ps=self.type.allProperties();
            if (item in ps):
                if (ps[item].inverseOf!=None):
                    return globalContext.inversion(self,ps[item]);

            return None;

        r=self.data[item];
        if (r!=None):
            if (isinstance(r,dict)):
                if "$type" in r:
                   r=instance(r,r["$type"].clazz);
            if (isinstance(r,list)):
                rs=[]
                for q in r:
                    if (isinstance(q,dict)):
                        if "$type" in q:
                            q=instance(q,q["$type"].clazz);
                            rs.append(q);
                            continue;
                    rs.append(q);
                return rs;

        return r;
    def __eq__(self, other):
        if (other==None):
            return False

        if (isinstance(other,instance)):
            return self.data['url']==other.data['url']
    def __str__(self):
        if (isinstance(self.data,dict)):
            if 'name' in self.data and self.data['name']!=None:
                return self.data["name"];
            if 'title' in self.data and self.data['title']!=None:
                return self.data['title'];
            if 'login' in self.data and self.data['login']!=None:
                return self.data["login"];
            if 'html_url' in self.data  and self.data['html_url']!=None:
                return self['html_url'];
            if 'url' in self.data and self.data['url']!=None:
                return self.data['url']
            return "Unknown"
        return str(self.data)
    def __repr__(self):
        return str(self)
    def domain(self):
        return self.type;