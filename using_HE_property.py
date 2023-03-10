


import numpy as np
from Pyfhel import Pyfhel,PyCtxt,PyPtxt
import h5py as hp
import time
from numpy import isclose as isclose

HE = Pyfhel()           # Creating empty Pyfhel object
ckks_params = {
    'scheme': 'CKKS',   # can also be 'ckks'
    'n': 2**14,         # Polynomial modulus degree. For CKKS, n/2 values can be
                        #  encoded in a single ciphertext. 
                        #  Typ. 2^D for D in [10, 16]
    'scale': 2**30,     # All the encodings will use it for float->fixed point
                        #  conversion: x_fix = round(x_float * scale)
                        #  You can use this as default scale or use a different
                        #  scale on each operation (set in HE.encryptFrac)
    'qi_sizes': [60, 30, 30, 30, 60] # Number of bits of each prime in the chain. 
                        # Intermediate values should be  close to log2(scale)
                        # for each operation, to have small rounding errors.
}
HE.contextGen(**ckks_params)  # Generate context for bfv scheme
HE.keyGen()             # Key Generation: generates a pair of public/secret keys
HE.rotateKeyGen()

# %%
# 2. Float Array Encoding & Encryption
# ----------------------------------------
# we will define two integer arrays, encode and encrypt them:
# arr_x = [1, 2, -3] (length 3)
# arr_y = [-1.5, 2.3, 4.7] (length 3)
dset=np.array(range(1,601))
_r = lambda x: np.round(x, decimals=10)
dim=dset.shape
m=len(dset)
# n=dim[1]
r_x=np.zeros((1,m), dtype=np.float64)
start_time_1=time.time()
# diff_decr_actual=np.zeros((m,n))
a=dset[0]

strt_time_1=time.time()
arr_x = np.array([a], dtype=np.float64)    # Always use type float64!

ptxt_x = HE.encodeFrac(arr_x)   # Creates a PyPtxt plaintext with the encoded arr_x

ctxt_x = HE.encryptPtxt(ptxt_x) # Encrypts the plaintext ptxt_x and returns a PyCtxt
time_finish_1=time.time()
# Otherwise, a single call to `HE.encrypt` would detect the data type,
#  encode it and encrypt it
#> ctxt_x = HE.encrypt(arr_x)
start_time_2=time.time()
y=ctxt_x+ctxt_x
time_finish_2=time.time()


# print("\n2. Fixed-point Encoding & Encryption, ")
# print("->\tarr_x ", arr_x,'\n\t==> ptxt_x ', ptxt_x,'\n\t==> ctxt_x ', ctxt_x)


pre_ctxt_x_obtained=np.zeros((1,m))[0]
ctxt_x_obtained_plain=HE.encodeFrac(pre_ctxt_x_obtained)
ctxt_x_obtained=HE.encryptPtxt(ctxt_x_obtained_plain)
ctxt_x_obtained_bytes=ctxt_x_obtained.to_bytes()
#---------------------------------------------------------
# plain text+ciphertext
b=0
arr_xx = np.array([b], dtype=np.float64)
ptxt_xxx=HE.encodeFrac(arr_xx)   # Creates a PyPtxt plaintext with the encoded arr_x

ctxt_xx = HE.encryptPtxt(ptxt_xxx)
HE.relinKeyGen()

# def encrypt(i):
#     encrypted_data=ctxt_xx
#     if i==1:
#         encrypted_data=ctxt_x
#     elif i==0:
#         pass
#     else:
#             encrypted_data=(encrypt(i-1)+ctxt_x) 
#     return  encrypted_data
def encrypt(array)-> list:
    
    arr_xx_f = np.array([1], dtype=np.float64)    # Always use type float64!

    ptxt_xx_f = HE.encodeFrac(arr_xx_f)   # Creates a PyPtxt plaintext with the encoded arr_x

    ctxt_xx_f = HE.encryptPtxt(ptxt_xx_f) 
    
    arr_x_f = np.array([array[0]], dtype=np.float64)    # Always use type float64!

    ptxt_x_f = HE.encodeFrac(arr_x_f)   # Creates a PyPtxt plaintext with the encoded arr_x

    ctxt_x_f = HE.encryptPtxt(ptxt_x_f) 
    encrypted_total=[i for i in range(1,len(array)+1)]
    encrypted_total[0]=ctxt_x_f
    for i in range(1,len(array)):
        encrypted_total[i]=encrypted_total[i-1]+ctxt_xx_f
    return encrypted_total

start_time=time.time()
encrypted_array=encrypt(range(600))
time_finish=time.time()
       
# %%
# 4. CKKS relinearization: What, why, when
# -----------------------------------------
# Ciphertext-ciphertext multiplications increase the size of the polynoms 
# representing the resulting ciphertext. To prevent this growth, the 
# relinearization technique is used (typically right after each c-c mult) to 
# reduce the size of a ciphertext back to the minimal size (two polynoms c0 & c1).
# For this, a special type of public key called Relinearization Key is used.
#
# In Pyfhel, you can either generate a relin key with HE.RelinKeyGen() or skip it
# and call HE.relinearize() directly, in which case a warning is issued.
# first usual method
start_time_5=time.time()
array_classic_methode=np.array(range(600), np.float64)
arr_all = np.array(array_classic_methode, dtype=np.float64)    # Always use type float64!

ptxt_x_all = HE.encodeFrac(arr_all)   # Creates a PyPtxt plaintext with the encoded arr_x

ctxt_x_all = HE.encryptPtxt(ptxt_x_all) # Encrypts the plaintext ptxt_x and returns a PyCtxt
finish_time_5=time.time()
#print(ctxt_x_obtained_bytes)
start_time_3=time.time()
# ptxt_x_bytes=HE.decryptFrac(encrypted_total[573])
finish_time_3=time.time()
# print(ptxt_x_bytes)
# print(ptxt_x_bytes)

# %%
# 6. Decrypt & Decode results
# ------------------------------
# Time to decrypt results! We use HE.decryptFrac for this. 
#  HE.decrypt() could also be used, in which case the decryption type would be
#  inferred from the ciphertext metadata. 
# r_x= HE.decryptFrac(ctxt_x_obtained_plain)

# Note: results are approximate! if you increase the decimals, you will notice
#  the errors
# print("6. Decrypting results")
# print(" Original ciphertexts: ")
# print("   ->\tfirst element of ctxt_x --(decr)--> ", _r(r_x)[0])
# sphinx_gallery_thumbnail_path = 'static/thumbnails/float.png'

# diff_decr_actual[i][j]=dset[i][j]-r_x[i][j]

# print(np.sqrt(np.mean(diff_decr_actual)**2))
# f=hp.File('testfile.hdf5','w')
# dset_f=f.create_dataset('my_dataset', (m,n),dtype=int)
# dset_f=r_x
# time_finish=time.time()
# diff_time=np.abs(strt_time-time_finish)
# print(encrypted_total)
print('enc(1) time',start_time_2-time_finish_2)
print('H Add time: ', time_finish_1-start_time_1)
print('decrypted time: ', finish_time_3-start_time_3)
print(' encryption loop time: ', time_finish-start_time) 
print(type(ctxt_x))
print('''for classic methode when you encrypte 
      an array with CSSK at once the time is (sec): \n''', finish_time_5-start_time_5)
# print(encrypted_total[9].to_bytes())
print(HE.decryptFrac(encrypted_array[548])[0])
print(len(HE.decryptFrac(ctxt_x_all)))
for i in range(600):
    if ~(np.isclose((HE.decryptFrac(encrypted_array[i]))[0],(HE.decryptFrac(ctxt_x_all))[i],atol=1e-5)):
        print('the encryption of ',i, 'does not fit in!')
        
        