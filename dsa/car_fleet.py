class Solution:
    def carFleet(self, target: int, position: List[int], speed: List[int]) -> int:
        
        stack = []
        for p,s in sorted(zip(position, speed))[::-1]:

            t =(target-p)/s

            if not stack or t > stack[-1]:
                stack.append(t)
            print(p,s,t, stack)
            
        return len(stack)