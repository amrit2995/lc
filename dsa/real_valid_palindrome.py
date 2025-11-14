class Solution:
    def isPalindrome(self, s: str) -> bool:
        
        def get_acceptable_range():
            alpha_range = []
            num_range = []
            for i in range(ord('A'), ord('z')+1):
                alpha_range.append(i)
            for i in range(ord('0'), ord('9')+1):
                num_range.append(i)
            return alpha_range,num_range

        right = len(s) - 1 
        left = 0

        alpha_range, num_range = get_acceptable_range()

        while left < right :
            print(left, right)
            if ord(s[left]) not in alpha_range+num_range:
                left += 1
            elif ord(s[right]) not in alpha_range+num_range:
                right -= 1
            elif s[left].lower() != s[right].lower():
                return False
            else:
                left += 1
                right -= 1

        return True