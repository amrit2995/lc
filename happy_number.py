class Solution:
    def isHappy(self, n: int) -> bool:
        visited = set()
        def recur(num):
            if num == 1:
                return True

            val = 0

            while num:
                digit = num%10
                val += pow(digit, 2)
                num //=10

            if val in visited:
                return False
            else:
                visited.add(val)
            return recur(val)
        return recur(n)


s = Solution()
n = 19
out = s.isHappy(n)
print(out)