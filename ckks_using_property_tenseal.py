
import numpy as np
import torch as pt
import tenseal as ts
import math,time
# setup tenseal
# Setup TenSEAL context
context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
          )
context.generate_galois_keys()
context.global_scale = 2**40
# --------------------------------------------------------------
# define function for encrypting the tensor using H property
# cus of the property of numpy.array,tensors and list we have 
# to use the mixture of them in encryption

scalar_value = 1
enc_one = ts.CKKSVector(context,[scalar_value])# set the first element of the vector to the scalar value you want to encrypt
# return encrypte of a tensor like: torch.tensor([[[-1400],[-1399],...[0],[1],....,[1400]]])
values_preset=0
keys_list=[str(i) for i in range(-1400,1400)]
encrypted_dict=dict.fromkeys(keys_list,values_preset)

# ---------------class Tensor as a plain object -------------------
# class Plain_tensor:
    # -----------------------------------------------------
def __init__(self) -> None:
    pass
# complete a dictionry of ckks cipher for an input range list encremented by one
def hash_func(k_list:list)->None:
    vec_first=ts.CKKSVector(context,[k_list[0]])
    enc_list=[i for i in range(len(k_list))]
    enc_list[0]=vec_first
    for i in range(1,len(k_list)):
            enc_list[i]=enc_list[i-1]+enc_one
    for index,element in enumerate(k_list):
        encrypted_dict[str(element)]=enc_list[index]
# ----------------------------------------------------------------
def number_split_true_float(float_number:any)->list:
    true_number=int(math.modf(float_number)[1])
    fraction=math.modf(float_number)[0]
    # Break down the number into its decimal places
    decimals = str(fraction).split('.')[1][:3]  # extract the decimal part as a string upto 3 digit
    place_values = [10**i for i in range(len(decimals))]
    digits = [int(d) for d in decimals[::-1]]# Construct the complete number by multiplying each digit by its corresponding place value
    complete_number = sum([digit*place_value for digit, place_value in zip(digits, place_values)])
    if fraction<0:
        complete_number*=-1
    return true_number,complete_number

def cipher_full(true:int,fracion:int)->ts.CKKSVector:
    true=encrypted_dict[str(true)]
    new_fraction=(encrypted_dict[str(fracion)])*(ts.CKKSVector(context,[0.001]))
    number=true+new_fraction
    return number

# -------------------------------------------------------------
# Python3 program to reshape a list
# according to multidimensional list
		
def reshape(lst1, lst2):
	last = 0
	res = []
	for ele in lst1:
		res.append(lst2[last : last + len(ele)])
		last += len(ele)
	return res

# ------------------------------------------------------------

def encrypt(primitive_tensor:pt.tensor)->list:   
    cipher_list=[i for i in range(pt.numel(primitive_tensor))] 
    dec_list=cipher_list.copy
    # dimension_primitive_tensor=pt._shape_as_tensor(primitive_tensor)
    # first_tensor = pt.tensor(primitive_tensor.tolist())    # Always use type float64!

    # first_element=primitive_tensor.view(1,pt.numel(primitive_tensor))[0][0].tolist()
    # enc_first_element=ts.ckks_vector(context,np.array([first_element]))
    '''make a dictionary for hashing each element in tensor has done in clas beforehand'''
    size_of_primitive_tensor=primitive_tensor.shape #return a list like torch.size()
    primitive_tensor=primitive_tensor.reshape(1,pt.numel(primitive_tensor))
    for i in range(pt.numel(primitive_tensor)):
        value=primitive_tensor[0][i].tolist()
        true_value,fraction_value=number_split_true_float(value)
        cipher_value=cipher_full(true_value,fraction_value)
        cipher_list[i]=cipher_value
        # print("temp decrypt",temp.decrypt())
    return cipher_list
'''
we can not store the CKKSVector
                in any tensor! so return a list!'''
# ---------------------------------------------------------------

f='cifar_net.pth'
model=pt.load(f,map_location=pt.device('cpu'))
keys=[i for i in model]
default_value=[model[key] for key in model]
tensor_collection_file_dict=dict.fromkeys(keys,default_value)
all_file_tensor_list=[model[key].clone() for key in model]
# for key in model:
#     print(model[key].shape)
#     print(model[key])
# print(pt._shape_as_tensor(all_file_tensor_list))
# temporary
# all_file_tensor_list=all_file_tensor_list[:100]
all_file_tensor_element_number=[i for i in range(len(default_value))]

# -----------------------------------------------------------

'''encrypting usually pytorch tensors with usual encryption
schem of tenseal'''
regular_time=[i for i in range(10)]
for i in range(3):
    x=all_file_tensor_list[i]
    start_time=time.time()
    #encrypt of first tensor in the list
    enc_all_file_tensor_list=[i for i in range(pt.numel(x))]
    # encrypted vectors
    enc_all_file_tensor_list = ts.ckks_tensor(context, x.view(1,pt.numel(x)).tolist())
    finish_time=time.time()
    regular_time[i]=finish_time-start_time

dec_all_file_tensor_list=[i for i in range(pt.numel(x))]


method_time=[i for i in range(10)]

# print(dec_all_file_tensor_list[0].tolist(), all_file_tensor_list[0].tolist())
# print((enc_all_file_tensor_list))
# implementing the methode using the H property
hash_func(list(range(-1400,1400)))
# print(encrypt(all_file_tensor_list)[5].decrypt()[0],all_file_tensor_list.view(1,pt.numel(all_file_tensor_list))[0][5].tolist())
# print(number_split_true_float(-1.99737))
# print(cipher_full(-1,-93).decrypt())
# print(encrypted_dict['-123'].decrypt())
for i in range(3):
    x=all_file_tensor_list[i]
    strat_time_mthod=time.time()
    # print(len(all_file_tensor_list))
    cipher_list = encrypt(x)
    finish_time_method=time.time()
    method_time[i]=finish_time_method-strat_time_mthod
#cipher_list = torch.tensor(cipher_list, dtype=torch.float32)
# print(cipher_list[220].decrypt())
# print("dec_list:{}",dec_list)
# print('len of list:{}'.format(len(dec_list)))
# print(all_file_tensor_list.view(1,pt.numel(all_file_tensor_list))[0][220])
print('method time: {}, usual time of the Tenseal time: {}'.format(method_time,regular_time))




    

    

    