from __future__ import absolute_import
import theano
import theano.tensor as T
import numpy as np

from .utils.theano_utils import sharedX, shared_zeros, shared_ones


def get_fans(shape):
    fan_in = shape[0] if len(shape) == 2 else np.prod(shape[1:])
    fan_out = shape[1] if len(shape) == 2 else shape[0]
    return fan_in, fan_out


def uniform(shape, scale=0.05):
    return sharedX(np.random.uniform(low=-scale, high=scale, size=shape))


def normal(shape, scale=0.05):
    return sharedX(np.random.randn(*shape) * scale)

def kaldi_nnet1(shape, visible=False, param_stddev_factor=0.1, with_glorot=True):
    # Optionaly scale
    def Glorot(dim1, dim2, with_glorot=True):
        if with_glorot:
            # 35.0 = magic number, gives ~1.0 in inner layers for hid-dim 1024dim,
            return 35.0 * math.sqrt(2.0/(dim1+dim2)); 
        else:
            return 1.0

    import math
    if visible:
        scale = param_stddev_factor * Glorot(shape[0], shape[1], with_glorot) * math.sqrt(1.0/12.0)
    else:
        scale = param_stddev_factor * Glorot(shape[0], shape[1], with_glorot) 
        
    W_values = np.random.standard_normal(shape) * scale
    W_values = W_values.astype(T.config.floatX)
    return W_values
    #return normal(shape, scale)

    
def lecun_uniform(shape):
    ''' Reference: LeCun 98, Efficient Backprop
        http://yann.lecun.com/exdb/publis/pdf/lecun-98b.pdf
    '''
    fan_in, fan_out = get_fans(shape)
    scale = np.sqrt(3. / fan_in)
    return uniform(shape, scale)


def glorot_normal(shape):
    ''' Reference: Glorot & Bengio, AISTATS 2010
    '''
    fan_in, fan_out = get_fans(shape)
    s = np.sqrt(2. / (fan_in + fan_out))
    return normal(shape, s)


def glorot_uniform(shape):
    fan_in, fan_out = get_fans(shape)
    s = np.sqrt(6. / (fan_in + fan_out))
    return uniform(shape, s)


def he_normal(shape):
    ''' Reference:  He et al., http://arxiv.org/abs/1502.01852
    '''
    fan_in, fan_out = get_fans(shape)
    s = np.sqrt(2. / fan_in)
    return normal(shape, s)


def he_uniform(shape):
    fan_in, fan_out = get_fans(shape)
    s = np.sqrt(6. / fan_in)
    return uniform(shape, s)


def orthogonal(shape, scale=1.1):
    ''' From Lasagne. Reference: Saxe et al., http://arxiv.org/abs/1312.6120
    '''
    flat_shape = (shape[0], np.prod(shape[1:]))
    a = np.random.normal(0.0, 1.0, flat_shape)
    u, _, v = np.linalg.svd(a, full_matrices=False)
    # pick the one with the correct shape
    q = u if u.shape == flat_shape else v
    q = q.reshape(shape)
    return sharedX(scale * q[:shape[0], :shape[1]])


def identity(shape, scale=1):
    if len(shape) != 2 or shape[0] != shape[1]:
        raise Exception("Identity matrix initialization can only be used for 2D square matrices")
    else:
        return sharedX(scale * np.identity(shape[0]))


def zero(shape):
    return shared_zeros(shape)


def one(shape):
    return shared_ones(shape)


from .utils.generic_utils import get_from_module
def get(identifier):
    return get_from_module(identifier, globals(), 'initialization')
