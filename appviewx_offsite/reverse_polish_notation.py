class Solution:
    def evalRPN(self, tokens):
        def is_neg(v):
            return True if v[0] == '-' and len(v)>1 and v[1:].isnumeric() else False

        stack = []
        operations = {"+","/", "*","-"}
        for n in tokens:
            if n.isnumeric() or is_neg(n):
                stack.append(f"({n})")

            if n in operations:
                b,a = stack.pop(),stack.pop()

                if n == '/':
                    stack.append(f"({str(round(eval(a+n+b)))})")
                else:    
                    stack.append(f"({str(eval(a+n+b))})")
        return int(stack[-1][1:-1])

tokens = ["2","1","+","3","*"]
tokens = ["4","13","5","/","+"]
tokens = ["10","6","9","3","+","-11","*","/","*","17","+","5","+"]

s =  Solution()
out = s.evalRPN(tokens)
print(out)