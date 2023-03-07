
import subprocess
import csv
import numpy as np
import numpy as np
from Pyfhel import Pyfhel,PyCtxt,PyPtxt
import h5py as hp
import time 
# define Pyfhel Class
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

def encrypt(i):
     if i==0 or 1:
          encrypted_data=ctxt_x
     else:
          encrypted_data=ctxt_xx
          for k in range(i):
               encrypted_data=encrypted_data+ctxt_x
     return encrypted_data
# creat CSV file
dset=np.array(range(1,601), np.float64)
file="/home/hosein/Documents/encryption_Library/HE/vector.csv"
# change_dir= subprocess.run(["cd", path])
creat_csv_file = subprocess.run(["touch", file])
with open('vector.csv', 'w', newline='') as file:
     writer = csv.writer(file)  
     writer.writerow(dset)
time_start=time.time()
with open('vector.csv', 'r') as file:
     reader=csv.reader(file)
     for row in reader:
          dset=row
     dset=[eval(d_baby) for d_baby in dset]
     dset=np.array(dset,np.float64)
     array_csv_read=np.array(dset, np.float64)
     arr_x = array_csv_read    # Always use type float64!
     ptxt_x = [i for i in range(1,601)]
     ctxt_x = [i for i in range(1,601)]
     # b=np.array(range(1,601), dtype=np.float64)
     for i in range(len(arr_x)):
          ptxt_x[i] = HE.encodeFrac(np.array([arr_x[i]]))  # Creates a PyPtxt plaintext with the encoded arr_x
          ctxt_x[i] = HE.encryptPtxt(ptxt_x[i]) # Encrypts the plaintext ptxt_x and returns a PyCtxt
with open('vector.csv', 'w', newline='') as file:
     writer = csv.writer(file)  
     writer.writerow(ctxt_x)
time_finish=time.time()

#using the H Property for encrypting CSV file
dset=np.array(range(1,601), np.float64)
# change_dir= subprocess.run(["cd", path])

with open('vector.csv', 'w+') as file:
     reader=file.truncate()

with open('vector.csv', 'w', newline='') as file:
     writer = csv.writer(file)  
     writer.writerow(dset)
time_start_1=time.time()
with open('vector.csv', 'r') as file:
     reader=csv.reader(file)
     for row in reader:
          dset=row
     dset=[eval(d_baby) for d_baby in dset]
     dset=np.array(dset,np.float64)
     array_csv_read=np.array(dset, np.float64)
     arr_x = array_csv_read    # Always use type float64!
     a=array_csv_read[0]
     arr_x = np.array([a], dtype=np.float64)    # Always use type float64!

     ptxt_x = HE.encodeFrac(arr_x)   # Creates a PyPtxt plaintext with the encoded arr_x

     ctxt_x = HE.encryptPtxt(ptxt_x)
     b=0
     arr_xx = np.array([b], dtype=np.float64)
     ptxt_xxx=HE.encodeFrac(arr_xx)   # Creates a PyPtxt plaintext with the encoded arr_x

     ctxt_xx = HE.encryptPtxt(ptxt_xxx)

encrypted_total=[i for i in range(1,600+1)]
for i in range(600):
    encrypted_total[i]=encrypt(i)
     

with open('vector.csv', 'w', newline='') as file:
     writer = csv.writer(file)  
     writer.writerow(encrypted_total)
time_finish_1=time.time()
diff_time1=time_finish-time_start
diff_time2=time_finish_1-time_start_1
print(diff_time1, diff_time2)
