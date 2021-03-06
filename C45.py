import math
import pdb

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
            classes = file.readline()
            self.classes = [x.strip() for x in classes.strip(",")]
            for line in file:
                [attribute, values] = [x.strip() for x in line.split(":")]
                values = [x.strip() for x in values.split(",")]
                self.avals[attribute] = values
        self.atts = len(self.avals.keys())
        self.att = list(self.avals.keys())
        with open(self.data, "r") as file:
            for line in file:
                row = [x.strip() for x in line.split(",")]
                if row != [] or row != [""]:
                    self.items.append(row)
    
    def processData(self):
        for index in enumerate(self.items):
            for aindex in range(self.atts):
                if(not self.discrete(self.atts[aindex])):
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
        if attribute not in self.atts:
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
            index = self.atts.index(a)
            if self.discrete(a):
                values = self.avals[a]
                subsets = [[] for a in values]
                for r in data:
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
    c = C45("iris/iris.data", "iris/iris.names")
    c.fetcher()
    c.processData()
    c.generateTree()
    c.printTree()