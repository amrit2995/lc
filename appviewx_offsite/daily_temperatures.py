class Solution:
    def dailyTemperatures(self, temperatures):
        stack = []
        ans = []
        for t in temperatures[::-1]:
            count = 1
            while stack and stack[-1][0] <= t:
                count += stack.pop()[1]
            ans.append(count if stack else 0)
            stack.append((t, count))
        return ans[::-1]

temperatures = [73,74,75,71,69,72,76,73]
s = Solution()
out = s.dailyTemperatures(temperatures)
print(out)