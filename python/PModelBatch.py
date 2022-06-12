# encoding=utf-8
import theano
from theano import tensor


def _slice(_x, n, dim):
    if _x.ndim == 3:
        return _x[:, :, n * dim:(n + 1) * dim]
    elif _x.ndim ==2:
        return _x[:, n * dim:(n + 1) * dim]
    else:
        return _x[n * dim:(n + 1) * dim]

def Model(model_options, tparams, sequencesM, masks,pathdiscount, wemb):
    proj = wemb[sequencesM]  # shape = len * num * dim
    masks_T = masks.T  #shape = num*len

    def _step(index, hArr,c_):
        # The following two lines are the method aggregating path heterogeneity, distance awareness and node heterogeneity.
        # If you don not need some steps, you can change the calculation of hi_sum.

        # type bias sigmoid(types dot eta)
        #                                        shape=num*length shape=num*length*type_dim  shape=type_dim
        # shape=num*len*gru_dim    shape=num*len            shape=num*len                   shape=num*len                  shape=num*len

        # If you only want to aggregate the outputs from its predecessors directly, you can do as follows
        # hi_sum= hArr * dependencies[index][:,:,None]
        # or you want to take the distance awareness into consideration, you can do as follows
        # hi_sum= (hArr * dependencies[index][:,:,None] * discountForEachNode_T[:,:,None])
        # Like the above examples, you can customize your own models.
        # shape=num*len*ldim
        hi_sum = hArr[:,index-1,:] #只把第index步的取出来 shape = num*ldim
        c_sum = c_[:,index-1,:] #只把第index步的取出来 shape = num*ldim
        W_i = _slice(tparams['lstm_W'], 0, model_options['dimension'])
        W_f= _slice(tparams['lstm_W'], 1, model_options['dimension'])
        W_o=_slice(tparams['lstm_W'], 2, model_options['dimension'])
        W_c=_slice(tparams['lstm_W'], 3, model_options['dimension'])
        U_i = _slice(tparams['lstm_U'], 0, model_options['dimension'])
        U_f = _slice(tparams['lstm_U'], 1, model_options['dimension'])
        U_o = _slice(tparams['lstm_U'], 2, model_options['dimension'])
        U_c = _slice(tparams['lstm_U'], 3, model_options['dimension'])
        b_i = _slice(tparams['lstm_b'], 0, model_options['dimension'])
        b_f = _slice(tparams['lstm_b'], 1, model_options['dimension'])
        b_o = _slice(tparams['lstm_b'], 2, model_options['dimension'])
        b_c = _slice(tparams['lstm_b'], 3, model_options['dimension'])
        #num * dim             num*ldim  wdim*ldim           num*ldim ldim*ldim    ldim
        i = tensor.nnet.sigmoid(
            tensor.dot(proj[index] , W_i) + tensor.dot(hi_sum,U_i) + b_i
        )
        f = tensor.nnet.sigmoid(
            tensor.dot(proj[index], W_f) + tensor.dot(hi_sum, U_f) + b_f
        )
        o = tensor.nnet.sigmoid(
            tensor.dot(proj[index], W_o) + tensor.dot(hi_sum, U_o) + b_o
        )
        c = tensor.tanh(
            tensor.dot(proj[index], W_c) + tensor.dot(hi_sum, U_c) + b_c
        )
        c = f * c_sum + i * c
        h_t = o * tensor.tanh(c)

        hArr = tensor.set_subtensor(hArr[:, index, :], h_t)  # shape: num *maxlen *dim
        c_ = tensor.set_subtensor(c_[:, index, :], c)  # shape: num *maxlen *dim

        return hArr,c_

    rval, update = theano.scan(
        _step,
        sequences=tensor.arange(sequencesM.shape[0]),
        outputs_info=[tensor.zeros((sequencesM.shape[1], sequencesM.shape[0], model_options['dimension']),
                                  dtype=theano.config.floatX),
                      tensor.zeros((sequencesM.shape[1], sequencesM.shape[0], model_options['dimension']),
                                  dtype=theano.config.floatX)],  # @UndefinedVariable
    )
    embs = rval[0][-1] #num*len*dim
    Embs = embs + ((1. - masks_T) * (-10000.))[:, :, None] # num*len*dim
    fenms = Embs.max(axis=1) # num*dim
    fembs = fenms * pathdiscount[:,None] # num*dim
    return fembs
