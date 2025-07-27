class Solution:
    def exist(self, board, word):
        board_dict = {}
        for i in range(len(board)):
            for j in range(len(board[0])):
                board_dict[board[i][j]] = board_dict.get(board[i][j],0) + 1

        for c in word:
            if c not in board_dict:
                return False
            board_dict[c] = board_dict.get(c)-1
            if board_dict[c] == 0:
                board_dict.pop(c)

        def dfs(ar,ac,index, word):
            if board[ar][ac] != word[index]:
                return False
            if index == len(word)-1:
                return True

            tmp = board[ar][ac]
            dirr = [(-1,0),(1,0),(0,1),(0,-1)]
            board[ar][ac] = -1

            found = False
            for dr,dc in dirr:
                r,c = ar+dr, ac+dc
                if r in range(len(board)) and c in range(len(board[0])):
                    found = found or dfs(r,c,index+1, word)
            board[ar][ac] = tmp
            return found

        found = False
        for i in range(len(board)):
            for j in range(len(board[0])):
                found = found or dfs(i,j,0,word)
        return found


board = [["a","a"]]
word = "aaa"

# board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]
# word = "ABCCED"

s = Solution()
out = s.exist(board, word)
print(out)