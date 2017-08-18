import unittest
import sys
import os
loc=os.path.dirname(__file__)
sys.path.insert(0, loc+'/..')
import parser.grammar_parser as gp;
import engine.operators;
import parser.queryEngine;
class TestParse(unittest.TestCase):

    def test_basic(self):
        compare("issues assigned to gleb","[selector:select(Issue)=>assignee==gleb]")
        compare("created by gleb","[filter:user==gleb]")
        compare("created by gleb and assigned to denis","[filter:and[user==gleb, assignee==denis]]")
        compare("created by gleb assigned to denis", "[filter:and[user==gleb, assignee==denis]]")
        compare("created by gleb assigned to denis  in raml-js-parser-2", "[filter:and[user==gleb, assignee==denis, parent(raml-js-parser-2)]]")
        compare("issues", "[selector:select(Issue)]")
        compare("issues created by gleb", "[selector:select(Issue)=>user==gleb]")
        compare("issues created by gleb or denis", "[selector:select(Issue)=>user==[gleb, denis]]")
        compare("issues created_by gleb or denis in raml-js-parser-2", "[selector:select(Issue)=>and[user==[gleb, denis], parent(raml-js-parser-2)]]")
        compare("issues created_by gleb and not assigned_to denis in raml-js-parser-2", "[selector:select(Issue)=>and[user==gleb, not assignee==denis, parent(raml-js-parser-2)]]")


        compare("created more then 5 issues", "[filter:created matches  count > 5=> in (select(Issue))]")
        compare("users created more then 5 issues", "[selector:select(User)=>created matches and( count > 5,  in (select(Issue)))]")
        compare("labels of issues created_by gleb", "[selector:select(Issue)=>user==gleb[labels]]")
        #compare("raml-js-parser-2 owner", "[selector:raml-js-parser-2[owner]]")
        compare("count issues in raml-js-parser-2", "[count:count(select(Issue)=>parent(raml-js-parser-2))]")
        compare("issues with more then 10 comments","[selector:select(Issue)=>comments> 10]")
        compare("labels of issues with more then 10 comments","[selector:select(Issue)=>comments> 10[labels]]")

        compare("repositories with more then 10 issues","[selector:select(Repository) childFilter count > 10 select(Issue)]")
        compare("issues created by users created more then 5 issues","[selector:select(Issue)=>user matches select(User)=>created matches and( count > 5,  in (select(Issue)))]")

        compare("users created more issues then denis", "[filter:select(User)=>created matches  count > count(denis[created]=> in (select(Issue)))]")
        compare("users created more issues then denis created in raml-js-parser-2", "[filter:select(User)=>created matches  count > count(denis[created]=>parent(raml-js-parser-2)=> in (select(Issue)))]")
    #def test_nested(self):
        #compare2("issues created by users with assigned issues")
if __name__ == '__main__':
    unittest.main()

tm={
    "gleb":("gleb","User"),
    "raml-js-parser-2":("raml-js-parser-2","Repository"),
    "denis":("denis","User"),
}
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

voc=queryEngine.voc
pr=queryEngine.Preprocessor(voc)

def tokenize(s):
    res=[]
    for k in s.split():
        if (k in tm):
            res.append(gp.Token("selector",operators.instance(k,voc.classTerm(tm[k][1]))));
        else:
            if (is_number(k)):
                res.append(gp.Token("selector",operators.instance(k,float)));
            else: res.append(gp.Token("str",k))
    return pr.preprocess(res);

def compare(tp,s):
    if (not s==str(parse(tp))):
        r=parse(tp)
        print  str(parse(tp))+" but should be:"+s
    assert s==str(parse(tp))
def compare2(tp,s):
    gp.debug=True;
    print  parse(tp)
    gp.debug = False;
    r=parse(tp);
    assert s==str(r)

def parse(s):
    vv=tokenize(s)
    if (isinstance(vv,gp.ResultSet)):
        vv=vv.list[0]
    return queryEngine.ruleset.parse(vv);