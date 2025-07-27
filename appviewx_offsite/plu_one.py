class Solution:
    def plusOne(self, digits):
        n = len(digits)
        stack = []
        carry = 1
        while n>0:
            n-=1
            stack.append(digits[n]+carry)
            carry = stack[-1]//10
            stack[-1] %= 10

        if carry:
            stack.append(1)

        return stack[::-1]


s = Solution()
digits = [1,2,3]
out = s.plusOne(digits)
print(out)