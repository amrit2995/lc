# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

class Solution:

    def inorder(self, node: TreeNode):
        
        if not node:
            return

        self.inorder(node.left)

        if self.result:
            return
        self.count -= 1
        if self.count == 0:
            self.result = node.val

        self.inorder(node.right) 

    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:

        self.count = k
        self.result = None
        self.inorder(root)
        return self.result

        
        