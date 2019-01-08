from collections import defaultdict, deque
from node_uuid import Node
import json

'''The godId is a dummy identifier to keep the root node itself in the dictionary.
'''

class NestedDictionaryTree():
    def __init__(self, godId=None, root=None, dd=None):
        self.dd = dd
        self.root = root
        self.godId = godId
        # Once the NestedDictionaryTree has been instantiated, 
        # the godId shall remain unchanged through repeated savings.
        if godId is None:
            godNode = Node()
            self.godId = godNode.getId()

    def initialise(self, columnNames):
        self.root = Node(None, columnNames)
        self.dd = defaultdict(list)
        self.dd[self.godId].append(self.root.toList())
            
    def createNDTfromTree(self, root):
        '''Based on the root-node a default-dict is created 
        which can be saved to disk and later on be loaded.
        '''
        dd = defaultdict(list)
        dd[self.godId].append(root.toList())
        qu = deque([root])
        while len(qu) > 0:
            parent = qu.popleft()
            for child in parent.getChildren():
                dd[parent.getId()].append(child.toList())
                qu.append(child)
        return root, dd

    def updateNDTfromTree(self):
        root, self.dd = self.createNDTfromTree(self.root)

    @staticmethod
    def createTreeFromFile(filename):
        dd, godId = NestedDictionaryTree.readDD2File(filename)
        root = Node(None, dd[godId][0][1], dd[godId][0][0])
        qu = deque([root])
        while len(qu) > 0:
            parent = qu.popleft()
            for element in dd[parent.getId()]:
                newNode = Node(parent, element[1], element[0])
                qu.append(newNode)
        return NestedDictionaryTree(godId, root, dd)
    
    def writeDD2File(self, filename):
        with open(filename, 'w') as f:
            f.write(self.godId + '\n')
            json.dump(self.dd, f)

    @staticmethod
    def readDD2File(filename):
        with open(filename, 'r') as f:
            godId = f.readline().strip()
            dd = json.load(f)
        return defaultdict(list, dd), godId

    def getRoot(self):
        return self.root

    def columnCount(self):
        if self.dd is None:
            return 0
        else:
            return len(self.dd[self.godId][0][1])

    def setHeaderData(self, section, value):
        if self.root.content[section] != value:
            self.root.content[section] = value
            self.dd[self.godId][0][1][section] = value
            return True
        return False

    def getEmptyAndValidNode(self):
        '''The item identfier is set. Parent and content 
        are not set and must be provided externally.'''
        columnCount = self.columnCount()
        return Node(None, ['???']*columnCount)

    def insertSiblingAbove(self, node, siblingNode=None):
        parent = node.getParent()
        if parent is None:
            parent = self.getRoot()
        if siblingNode is None:
            siblingNode = self.getEmptyAndValidNode()
            siblingNode.parent = parent
        row = 0
        if parent.childrenCount() > 0:
            row = parent.children.index(node)
        parent.children.insert(row, siblingNode)
        return siblingNode

    def insertSiblingBelow(self, node, siblingNode=None):
        parent = node.getParent()
        if parent is None:
            parent = self.getRoot()
        if siblingNode is None:
            siblingNode = self.getEmptyAndValidNode()
            siblingNode.parent = parent
        row = -1
        if parent.childrenCount() > 0:
            row = parent.children.index(node)
        parent.children.insert(row+1, siblingNode)
        return siblingNode

    def insertChildBelow(self, item, childNode=None):
        if childNode is None:
            childNode = self.getEmptyAndValidNode()
            childNode.parent = item
        item.children.insert(0, childNode)
        return childNode
        
        

if __name__ == '__main__':
    root = Node(None, ['column', 'comment'])
    parent1 = Node(root, ['AAA', 'aaa'])
    parent2 = Node(root, ['BBB', 'bbb'])
    child1 = Node(parent1, ['CCC', 'ccc'])

    ndt = NestedDictionaryTree()
    ndt.createNDTfromTree(root)

    filename = 'tmp.ndt'
    ndt.writeDD2File(filename)

    ndt2 = NestedDictionaryTree.createTreeFromFile(filename)