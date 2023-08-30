class Node:
    def __init__(self,val='', val_exist=False, children={}):
        self.val = val
        self.children = children
        self.val_exist = val_exist

class Trie:

    def __init__(self):
        self.root = Node()
        
    def traverse(self,string):
        i = 0
        curr = self.root
        while i < len(string) and string[i] in curr.children.keys():
            curr = curr.children[string[i]]
            i += 1
        return curr

    def insert(self, word):
        node = self.traverse(word)

        if node.val == word:
            node.val_exist = True
            return None

        for a in word[len(node.val):]:
            node.children[a] = Node(node.val + a)
            node = node.children[a]
        node.val_exist = True
        return None
        
    def search(self, word):
        node = self.traverse(word)
        return word == node.val and node.val_exist 

    def startsWith(self, prefix):
        node = self.traverse(prefix)
        return prefix == node.val and node.children != None


trie = Trie()
print(trie.startsWith("a"))


# print(trie.insert("apple"))
# print(trie.search("apple"))
# print(trie.search("app"))
# print(trie.startsWith("app"))
# print(trie.insert("app"))
# print(trie.search("app"))

