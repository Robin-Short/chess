def ripetuto(n):
    if n == 1:
        return '1'
    return ripetuto(n-1)+'\n'+str(n)*n

def palindroma(s):
    if len(s)==0:
        return True
    return palindroma(s[1:-1]) and s[0] == s[-1]

x = ripetuto(5)