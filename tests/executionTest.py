
import sys
import os
loc=os.path.dirname(__file__)
sys.path.insert(0, loc+'/..')
import unittest
import grammar_parser as gp;
import queryEngine as qe;

engine=qe.QueryEngine();

class TestParse(unittest.TestCase):
    # def test_which(self):
    #     gp.debug=True
    #     res=engine.query("Which repositories have more then 10 issues?").execute();
    #     print len(res)
    #     assert len(res)==781;
    def test_define2(self):
        gp.debug=True
        res=engine.query("define raml 1 parser as raml-js-parser-2").execute();
        res=engine.query("raml 1 parser issues").execute();
        #print len(res)
        assert len(res)==781;

    def test_company1(self):
        gp.debug=True
        res=engine.query("issues created by users from CISCO").execute();
        # #res=engine.query("onpositive issues").execute();
        print len(res)

    def test_company(self):
        #gp.debug=True
        res=engine.query("users company OnPositive").execute();
        # #res=engine.query("onpositive issues").execute();
        # print len(res)
        assert len(res)==3;

    def test_define(self):
        gp.debug=True
        res=engine.query("define onpositive issues as open issues in raml-js-parser-2 or raml-typesystem or raml-definition-system").execute();
        res=engine.query("onpositive issues").execute();
        #print len(res)
        assert len(res)==83;
        #assert len(res)==476;
    def test_alias(self):
        #gp.debug=True
        res=engine.query("open issues").execute();
        #print len(res);
        assert len(res)==476;

    def test_alias2(self):
        #gp.debug=True;
        res=engine.query("open issues in raml-js-parser").execute();
        #print len(res);
        assert len(res)==21;
    def test_denis(self):
        gp.debug=True
        res=engine.query("open Denis issues").execute();
        assert len(res)==18
    def test_basic(self):
        res=engine.query("issues").execute();
        assert len(res)==2604;

    def test_basic1(self):
        res=engine.query("issues assigned to Gleb").execute();
        assert len(res)==40;
        res=engine.query("issues assigned to Konstantin").execute();
        assert len(res),237
    def test_basic2(self):
        res=engine.query("issues created by gleb and assigned to Konstantin").execute()
        assert len(res)==1
        res=engine.query("issues created by gleb assigned to Konstantin").execute()
        assert len(res)==1

        res=engine.query("issues created by gleb, assigned to Konstantin").execute()
        assert len(res)==1
    def test_basic3(self):
        res=engine.query("issues created by gleb assigned to Konstantin  in raml-js-parser-2").execute()
        assert str(res)=="set([Parser wrongly complain about non-existing subtypes])"
    def test_basic4(self):
        res=engine.query("issues created by gleb or denis").execute()
        assert len(res)==len(engine.query("issues created by gleb").execute())+len(engine.query("issues created by denis").execute())
        res=engine.query("issues created by gleb or denis in raml-js-parser-2").execute()
        assert len(res)==181
        res=engine.query("issues created by gleb or denis in raml-js-parser-2 or raml-js-parser").execute()
        assert len(res)==181
    def test_not(self):
        res=engine.query("issues created_by gleb and not assigned_to konstantin").execute();
        assert len(res)==len(engine.query("issues created_by gleb").execute())-len(engine.query("issues created_by gleb and assigned_to konstantin").execute())
        res=engine.query("issues created_by gleb and not assigned_to konstantin in raml-js-parser-2").execute();
        assert(len(res)==40);
    def test_propVal(self):
        res=engine.query("labels of issues created_by gleb").execute()
        assert(len(res)==4)
    def test_count(self):
        res=engine.query("count issues in raml-js-parser-2").execute()
        assert res==781;
    def test_created(self):
        res=engine.query("users created more then 40 issues").execute()
        assert len(res)==12
    def testChild(self):
        res=engine.query("repositories with more then 100 issues").execute();
        assert len(res)==6;
    def testNested(self):
        res=engine.query("issues created by users created more then 100 issues").execute();
        assert len(res)==891
    def testComparative(self):
        #gp.debug=True
        res=engine.query("users created more issues then denis").execute()
        assert len(res)==2
        res=engine.query("users created more issues then denis created in raml-js-parser-2").execute()
        assert len(res)==3
    def testComparison(self):
        res=engine.query("issues with more then 30 comments").execute()
        assert len(res)==3
        res=engine.query("labels of issues with more then 30 comments").execute()
        assert len(res)==1