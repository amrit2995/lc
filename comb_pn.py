class Solution:
    def letterCombinations(self, digits):
        out = []
        digits_dict = {
            "2":"abc",
            "3":"def",
            "4":"ghi",
            "5":"jkl",
            "6":"mno",
            "7":"pqrs",
            "8":"tuv",
            "9":"wxyz"
        }

        def dfs(digits, path, index):
            if index == len(digits):
                if path:
                    out.append(path)
                return

            for option in digits_dict[digits[index]]:
                dfs(digits,path+option,index+1)

        dfs(digits,"",0)

        return out

s = Solution()
digits = ""
out = s.letterCombinations(digits)
print(out)