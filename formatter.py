# This Python file uses the following encoding: utf-8
MAX_ITEMS=30;
import engine.operators as operators
def format(res):
    result=""
    num=0;
    try:
        if (not isinstance(res,list) and not isinstance(res,set)):
            result=str(res)
            return "Single thing:"+result;
        if (len(res)==0):
            return "Nothing found"
        for i in res:
            try:

                vl=str(i);
                #print "A"+vl
                if (isinstance(i,operators.instance) and "html_url" in i.data):
                    result=result+u"• "+"<"+i["html_url"]+"|"+vl+">\n";
                else: result=result+(u"• "+unicode(vl)).encode("utf-8")+"\n"
            except:
                result=result+(u"• Can not encode item".encode("utf-8"))+"\n"
            num=num+1;
            if (num>MAX_ITEMS):
                result+="Printed first 30 results of:"+str(len(res))+", ask more to get more"
                break;
        return result;
    except:
        return str(res);
w=""
