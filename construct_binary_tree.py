# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
class Solution:
    def buildTree(self, preorder, finorder):

        def bt(pi, inorder):
            
            if not inorder:
                return (None, pi-1)

            tmp = TreeNode(preorder[pi])

            ii = 0
            while preorder[pi] != inorder[ii]:
                ii+=1

            tmp.left, pi = bt(pi+1, inorder[:ii])
            tmp.right,pi = bt(pi+1, inorder[ii+1:])

            return (tmp,pi)
            

        return bt(0, finorder)[0]

out = []
def pot(root):
    if not root:
        return 
    out.append(root.val)
    pot(root.left)
    pot(root.right)


preorder = [3,9,20,15,7]
inorder = [7,15,20,9,3]
s = Solution()
root = s.buildTree(preorder, inorder)
pot(root)
print(out)
