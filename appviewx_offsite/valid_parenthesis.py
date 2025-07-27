class Solution:
    def isValid(self, s: str) -> bool:
        brackets = {"}":"{",")":"(","]":"["}
        stack = []
        for i in s:
            if i in brackets.keys():
                if brackets[i] != stack[-1]:
                    return False
                else:
                    stack.pop()
            else:
                stack.append(i)
        return True

s = Solution()
su = "{[]}"
print(s.isValid(su))