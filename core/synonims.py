import yaml
class SynBase:


    def __init__(self,ps):
        self.dict={};
        self.load(ps);
    def load(self,s):
            with open(s) as f:
                dataMap = yaml.safe_load(f)
                for k in dataMap:
                    vals=[k]+dataMap[k];
                    for k0 in vals:
                      for k1 in vals:
                          if k0!=k1:
                            if (k0 in self.dict):
                                self.dict[k0].append(k1);
                            else:
                                self.dict[k0]=[k0,k1];


    def get(self,s):
        if s in self.dict:
            return self.dict[s]
        return [s]