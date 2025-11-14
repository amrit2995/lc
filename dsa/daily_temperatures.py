class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        stack = []
        out = []
        for i in range(len(temperatures)-1, -1, -1):
            while stack and (temperatures[stack[-1]] <= temperatures[i]):
                stack.pop()
            diff = (stack[-1] - i) if stack else 0
            out.insert(0, diff )
            stack.append(i)
        return out