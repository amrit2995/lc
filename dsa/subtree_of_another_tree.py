# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

class Solution:   
    def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:
        
        def check_same_tree(r1, r2):
            if not r1 and not r2:
                return True
            if not r1 or not r2:
                return False
            return (
                r1.val == r2.val
                and check_same_tree(r1.left, r2.left)
                and check_same_tree(r1.right, r2.right)
            )

        def check_sub_tree(r, sr):
            if not r:
                return False
            if check_same_tree(r, sr):
                return True
            return check_sub_tree(r.left, sr) or check_sub_tree(r.right, sr)
            
        return check_sub_tree(root, subRoot)
