class Solution:
    def countPrimes(self, n):
        dp = []
        if n <= 2:
            return 0
        for i in range(2, n):
            index = 0
            prime = True
            while dp and i//2 >= dp[index]:
                if i%dp[index] == 0:
                    prime = False
                    break
                else:
                    index += 1
            if prime:
                dp.append(i)
        return len(dp)

s = Solution()
out = s.countPrimes(10)
print(out)