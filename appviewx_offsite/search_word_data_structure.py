class Node:
    def __init__(self, val="", children={}):
        self.val = val

        self.children = children
class WordDictionary:

    def __init__(self):
        self.root = Node()
        


    def addWord(self, word):
        def traverse(root, string, index):
            if index >= len(string):
                return

            if word[index] not in root.children.keys():
                new_root = Node(string[index])
                root.children[string[index]] = new_root
            
            root = root.children[string[index]]
            traverse(root.children[string[index]],string, index+1)

        root = self.root
        traverse(root, word, 0)

    def search(self, word):
        def traverse(root,string,index):
            if index >= len(string):
                return True
            elif string[index] == ".":
                return any([traverse(root.children[a], string, index+1) for a in root.children.keys()])
            elif string[index] in root.children:
                return traverse(root.children[string[index]],string, index+1)
            else:
                return False
        return traverse(self.root, word, 0)


# nums = [1,-1]
# k = 1
# s =  Solution()
# out = s.WordDictionary(nums, k)
# print(out)


# funcs = ["WordDictionary","addWord","addWord","addWord","search","search","search","search"]
# inputs = [[],["bad"],["dad"],["mad"],["pad"],["bad"],[".ad"],["b.."]]

wordDictionary = WordDictionary()
# wordDictionary.addWord("bad")
# wordDictionary.addWord("dad")
# wordDictionary.addWord("mad")
# print(wordDictionary.search("pad"))
# print(wordDictionary.search("bad"))
# print(wordDictionary.search(".ad"))
# print(wordDictionary.search("b.."))
print(wordDictionary.search("a"))


