class Solution:
    def generateParenthesis(self, n: int) -> List[str]:

        final_out = []
        def dfs(s, o):

            if o < 0 or o >n or len(s)>n*2:
                return
            if o == 0 and n * 2 == len(s):
                final_out.append(s)
                return
            print(s)
            dfs(s+'(', o+1)
            dfs(s+')', o-1)

        dfs('', 0)
        return final_out