"""
This is the final project (assignment) of the cryptography course by UC San Diego & HSE on coursera. 
In this project we will implement an RSA system and will model some simple attacks.  
"""
# this function converts a string message to an integer.
# this function can be modified by for example changing the 16 to higher numbers.
# in this case the ConvertToStr must be modified in turn as well. 
# also note that the length of m should not exceed the modulo. 
# so in the case of a lengthy messages, a higher modulo should be used as the message cannot be changed.
# the reason that 256 has been used is that Ascii codes are from 0-255.
def ConvertToInt(message):
  n = 0
  for i in message:
    n = n * 256 + ord(i)
  return n

# converts a number back to a string
def ConvertToStr(n):
    res = ""
    while n > 0:
        res += chr(n % 256)
        n //= 16
    return res[::-1]

# calculates the binary representation of a number backwards
def ConvertToBinary (a):
    res = ""
    while a > 1:
        res += str (a%2)
        a //= 2
    res += str(a)
    return res

# calculates the congruence of "a" to the power of "n" modulo "mod".
def PowMod(a, n, mod):
    if n == 0:
        return 1
    if n == 1:
        return a % mod
    res = a % mod if n % 2 != 0 else 1
    b = a % mod
    for i in range (1, len(ConvertToBinary (n))):
        b = (b ** 2) % mod
        if ConvertToBinary (n)[i] == '1':
            res *= b
    return res%mod

# returns the gcd of two numbers (greatest common divisor). There is also a built in function in the math library.
def GCD (a,b):
    if b == 0: 
        return a
    return GCD (b, a%b)

# for any a,b,c, this function solves the diophantine equation a*x + b*y = c; that is it finds x and y such that the equation holds.
def certificates (a, b, c):
    if c % GCD(a,b)!=0:
        return "no answer can be found",0
    if b == 0:
        return a//c, 0
    p, q = certificates (b, a%b, c)
    x = q
    y = p - (a//b)*q
    return x,y

# finds the multiplicative inverse of a number "a" modulo n. that is it finds a "b" such that a*b is congruent to 1 modulo n.
def InvertModulo (a, n):
    res, no_res = certificates (a, n, 1)
    if res < 0:
        res = (res % n + n) % n
    return res

# returns the highest number "x" where x**2 <= n
def IntSqrt(n):
    return (int (n**(1/2)))

# this function is the encryption phase of the RSA algorithm.
# the public key in RSA is (n,e) and the private key is (p,q).
# p and q are generated by the reciever and e is a random number generated comprime to (p-1)*(q-1)
# n is equal to p*q and any message which is encrypted is done by calculating the congruent of 
# m**e modulo n
def Encrypt(message, modulo, exponent):
  return PowMod(ConvertToInt(message), exponent, modulo)

# decryption phase of the RSA algorithm
# here we find the multiplicate inverse of "e" modulo (p-1)*(q-1) => we name it as "d"
# we then find c ** d modulo "n" which is congruent to "m" ; and finally we convert it to a string.
def Decrypt(ciphertext, p, q, exponent):
  return ConvertToStr (PowMod(ciphertext, InvertModulo(exponent,(p-1)*(q-1)),p*q))

# Attacks:

# here we simulate a situation where the sender only has a set of messages to send
# for example, "attack" and "don't attack", in that was eave by encrypting all the possible
# messages and comparing them to the encrypted message of the sender, finds out which message
# was initially sent. To solve this porblem one can randomly pad bits to the message
# to increase the number of possiblities. 
def DecipherSimple(ciphertext, modulo, exponent, potential_messages):
  for i in range (len (potential_messages)):
    if ciphertext == Encrypt(potential_messages[i], modulo, exponent):
      return potential_messages[0]
  return "don't know"

# here we simulate what will happen if the one of the two generated prime numbers
# are small. Then in that situation p and q can be obtained and thus the private key 
# can be used by others than the receiver (the RSA algorithm has failed)
# in below we assume that the small prime is lower than 100,001
# usually the prime numbers generated have 2048 digits!
def DecipherSmallPrime(ciphertext, modulo, exponent):
  for i in range (1,100001):
    if modulo % i == 0:
      small_prime = i
      big_prime = modulo // i
      return Decrypt(ciphertext, small_prime, big_prime, exponent)
  return "don't know"

# here we simulate the attack where the difference between the two prime numbers is small (5000)
# this attack rarely ever happens and is mainly a theoretical attack
def DecipherSmallDiff(ciphertext, modulo, exponent):
  for i in range (IntSqrt(modulo) - 5000, IntSqrt(modulo) +1):
    if modulo % i == 0 :
      small_prime = IntSqrt(modulo)
      big_prime = modulo // small_prime
      return Decrypt(ciphertext, small_prime, big_prime, exponent)

# here we discovered that the first prime number p for the private key was generated with 
# the same algorithm and the same random seed by two different senders Alice and Angelina 
# due to insufficient randomness, while the second prime q is different for those two private keys.
# we want to break both ciphers and decipher messages from both Alice and Angelina.
def DecipherCommonDivisor(first_ciphertext, first_modulo, first_exponent, second_ciphertext, second_modulo, second_exponent):
  common_prime = GCD (first_modulo, second_modulo)
  q1 = first_modulo // common_prime
  q2 = second_modulo // common_prime
  return (Decrypt(first_ciphertext, common_prime, q1, first_exponent), Decrypt(second_ciphertext, common_prime, q2, second_exponent))
  
# chinese remainder theorem: if n1 and n2 are comprime then there is a unique n for r1 modulo n1 and r2 modulo n2
def ChineseRemainderTheorem (n1,r1,n2,r2):
    if GCD (n1,n2):
        return "chinese remainder theorem only works when n1 and n2 are coprime."
    x,y = certificates(n1,n2,1)
    return x * n1 * r2 + y * n2 * r1

# Hastad Broad attack
# Bob has sent the same message to Alice and Angelina using two different public keys 
# (n1,e) and (n2, e) where e is equal to 2 in both cases. 
# in this attack if e is large then the attack will not work. 
def DecipherHastad(first_ciphertext, first_modulo, second_ciphertext, second_modulo):
  r = ChineseRemainderTheorem(first_modulo, first_ciphertext, second_modulo, second_ciphertext)
  return ConvertToStr(IntSqrt(r))