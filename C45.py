import math
import pdb
import HTMLParser

class MyHTMLParser( HTMLParser.HTMLParser):
    categoryValues = {}
    currentCategory = ""
    firstTime = True;
    listOfPairs = []
    def handle_starttag(self, tag, attrs):
        #print("Start tag:", tag)
        if (tag == 'variable'):            
            for (name, category )in attrs:
                #print("Category" + category)
                if(self.firstTime == True ):
                    self.currentCategory = category;
                else:
                    self.currentCategory = category;
                    self.listOfPairs = []                                                                                                                                                  
        elif(tag == 'group'):
                listOfAttributes = []               
                for (name, groupName )in attrs:
                    listOfAttributes.append(groupName)                                                          
                pairValues = (listOfAttributes[0],listOfAttributes[1])            
                self.categoryValues[self.currentCategory] = self.listOfPairs             
                self.listOfPairs.append(pairValues)   
        self.firstTime = False;                                                   

class Node:
    def __init__(self, isLeaf, label, threshold):
        self.label = label
        self.threshold = threshold
        self.isLeaf = isLeaf
        self.children = []

class C45:
    def __init__(self, data, names):
        self.data = data
        self.names = names
        self.avals = {}
        self.att = []
        self.items = []
        self.classes = []
        self.atts = -1
        self.tree = None

    def fetcher(self):       
        with open(self.names, "r") as file:
            parser = MyHTMLParser()
            #HTML Parser
            for line in file:
                parser.feed(line)                
            for key in parser.categoryValues.keys():
                print key
                print(parser.categoryValues[key])
            for attributeKey in parser.categoryValues.keys():
                values = []
                for pairs in parser.categoryValues[attributeKey]:
                    values.append(pairs[0])
                self.avals[attributeKey] = values   
                print(values)                              
        self.atts = len(self.avals.keys())
        self.att = list(self.avals.keys())       
        lineCount = 0
        
        with open(self.data, "r") as file:
            for line in file:
                lineCount += 1
                if(lineCount > 3):
                    row = [x.strip() for x in line.split(",")]
                    if row != [] or row != [""]:
                        self.items.append(row)
    
    def processData(self):
        for index in enumerate(self.items):
            for aindex in range(self.atts):
                if(not self.discrete(self.att[aindex])):
                    self.items[index][aindex] = float(self.items[index][aindex])
    
    def generateTree(self):
        self.tree = self.rTree(self.items, self.att)

    def rTree(self, data, attributes):
        same = self.allsame(data)
        if len(data) == 0:
            return Node(True, "Fail", None)
        elif same is not False:
            return Node(True, same, None)
        elif len(attributes) == 0:
            majClass = self.getMajClass(data)
            return Node(True, majClass, None)
        else:
            (best, bestt, split) = self.splitter(data, attributes)
            rest = attributes[:]
            rest.remove(best)
            node = Node(False, best, bestt)
            node.children = [self.rTree(subset, rest)for subset in split]
            return node

    def getMajClass(self, data):
        freq = [0] * len(self.classes)
        for r in data:
            index = self.classes.index(r[-1])
            freq[index] += 1
        maxIndex = freq.index(max(freq))
        return self.classes[maxIndex]

    def allsame(self, data):
        for r in data:
            if r[-1] != data[0][-1]:
                return False
        return data[0][-1]

    def discrete(self, attribute):
        if attribute not in self.att:
            raise ValueError("Attributes not listed")
        elif len(self.avals[attribute]) == 1 and self.avals[attribute][0] == "continuous":
            return False
        else:
            return True
    
    def splitter(self, data, Attributes):
        split = []
        maxEnt = -1 * float("inf")
        ideala = -1
        idealt = None
        for a in Attributes:
            index = self.att.index(a)
            if self.discrete(a):
                values = self.avals[a]
                subsets = [[] for a in values]
                for r in data:
                    print("data")
                    print(r)
                    for i in range(len(values)):
                        if r[i] == values[i]:
                            subsets[i].append(r)
                            break
                e = self.gain(data, subsets)
                if e > maxEnt:
                    maxEnt = e
                    split = subsets
                    ideala = a
                    idealt = None
            else:
                data.sort(key = lambda x : x[index])
                for j in range(0, len(data) - 1):
                    if data[j][index] != data[j + 1][index]:
                        threshold = (data[j][index] + data[j + 1][index]) / 2
                        less = []
                        great = []
                        for row in data:
                            if(row[index] > threshold):
                                great.append(row)
                            else:
                                less.append(row)
                        e = self.gain(data, [less, great])
                        if e >= maxEnt:
                            split = [less, great]
                            maxEnt = e
                            ideala = a
                            idealt = threshold
        return (ideala, idealt, split)

    def gain(self, set, subsets):
        S = len(set)
        prior = self.entropy(set)
        weights = [len(subset) / S for subset in subsets]
        after = 0
        for i in range(len(subsets)):
            after += weights[i] * self.entropy(subsets[i])
        totalGain = prior - after
        return totalGain

    def entropy(self, dat):
        S = len(dat)
        if S == 0:
            return 0
        nclass = [0 for i in self.classes]
        for i in dat:
            classIndex = list(self.classes).index(i[-1])
            nclass[classIndex] += 1
        nclass = [x / S for x in nclass]
        ent = 0
        for num in nclass:
            ent += num * self.logger(num)
        return ent * -1

    def logger(self, x):
        if x == 0:
            return 0
        else:
            return math.log(x, 2)

    def printTree(self):
        self.printNode(self.tree)

    def printNode(self, node, indent = ""):
        if not node.isLeaf:
            if node.threshold is None:
                for index, child in enumerate(node.children):
                    if child.isLeaf:
                        print('{} {} = {} : {}'.format(indent, node.label, self.atts[index], child.label))
                    else:
                        print('{} {} = {} :'.format(indent, node.label, self.atts[index]))
                        self.printNode(child, indent + "    ")
            else:
                left = node.children[0]
                right = node.children[1]
                if left.isLeaf:
                    print('{} {} <= {} : {}'.format(indent, node.label, str(node.threshold), left.label))
                else:
                    print('{} {} <= {} :'.format(indent, node.label, str(node.threshold)))
                    self.printNode(left, indent + "    ")
                if right.isLeaf:
                    print('{} {} > {} : {}'.format(indent, node.label, str(node.threshold), right.label))
                else:
                    print('{} {} > {} : '.format(indent, node.label, str(node.threshold)))
                    self.printNode(right, indent + "    ")


if __name__ == "__main__":
    c = C45("tree02/tree02-20-words.csv", "domain.xml")
    c.fetcher()
    c.processData()
    c.generateTree()
    ##c.printTree()