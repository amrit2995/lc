class Solution:
    def trap(self, height):
        

        base_depth = 0
        area = 0
        stack = []
        i = 0
        while i in range(len(height)):
            base_depth = 0
            while stack:
                length = i - stack[-1][1]-1
                depth = min(stack[-1][0], height[i]) - base_depth
                area += length*depth
                if stack[-1][0] <= height[i]:
                    base_depth = stack.pop()[0]
                else:
                    break

            stack.append((height[i],i))
            i += 1

        return area

# height = [0,1,0,2,1,0,1,3,2,1,2,1]
height = [4,2,0,3,2,5]
s = Solution()
area = s.trap(height)
print(area)