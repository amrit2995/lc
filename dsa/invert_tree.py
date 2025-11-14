# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        def invert_subtree(root):
            if not root:
                return
            root.right, root.left = invert_subtree(root.left), invert_subtree(root.right)
            return root
        return invert_subtree(root)