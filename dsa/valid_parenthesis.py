class Solution:
    def isValid(self, s: str) -> bool:
        
        p_dict = {"[":"]", "(":")", "{":"}" }
        p_stack = []

        for p in s:
            if p in p_dict.keys():
                p_stack.append(p)
            elif not p_stack or p_dict[p_stack[-1]] != p:
                return False
            else:
                p_stack.pop()
        return True if not p_stack else False