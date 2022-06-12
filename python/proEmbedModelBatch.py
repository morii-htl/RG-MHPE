# encoding=utf-8
'''
Generate ProxEmbed Model
'''
import numpy
import theano
from theano import tensor

import PModelBatch



def proxEmbedModel(model_options, tparams):
    """
    generate proxEmbed model
    """
    trainingParis = tensor.tensor3('trainingParis', dtype='int64') # 3D tensor,shape=#(triples)*4*2
    subPaths_matrix = tensor.matrix('subPaths_matrix', dtype='int64') # shape=maxlen*subPaths
    subPaths_mask = tensor.matrix('subPaths_mask', dtype=theano.config.floatX)  #shape=maxlen*subPaths
    subPaths_lens = tensor.vector('subPaths_lens', dtype='int64') #shape=subPaths
    wordsEmbeddings = tensor.matrix('wordsEmbeddings', dtype=theano.config.floatX) #shape = nums * dim
    groups_tensor = tensor.tensor3('groups_tensor', dtype=theano.config.floatX)
    path_discount = tensor.vector("path_discount",dtype=theano.config.floatX) #shape = nums

    embs =  PModelBatch.Model(model_options, tparams, subPaths_matrix, subPaths_mask,path_discount,
                                                        wordsEmbeddings)
    groups1 = groups_tensor[0]
    groups2 = groups_tensor[1]
    group_embs1 = groups1[:, :, None] * embs + ((1. - groups1) * (-1000.))[:, :, None]  # shape=tupleNum*seqNum*dim
    embs1 = group_embs1.max(axis=1)  # shape=tupleNum*dim
    group_embs2 = groups2[:, :, None] * embs + ((1. - groups2) * (-1000.))[:, :, None]  # shape=tupleNum*seqNum*dim
    embs2 = group_embs2.max(axis=1)  # shape=tupleNum*dim

    #关系考虑完
    param = model_options['objective_function_param']
    #objective_function_param

    lossVector = -tensor.log(tensor.nnet.sigmoid(
        param * (tensor.dot(embs1, tparams['w']) - tensor.dot(embs2, tparams['w']))))  # shape=tuplesNum
    loss = lossVector.sum()

    cost = loss

    cost += model_options['decay_lstm_W'] * (tparams['lstm_W'] ** 2).sum()
    cost += model_options['decay_lstm_U'] * (tparams['lstm_U'] ** 2).sum()
    cost += model_options['decay_lstm_b'] * (tparams['lstm_b'] ** 2).sum()
    cost += model_options['decay_w'] * (tparams['w'] ** 2).sum()
    #cost += model_options['decay_w'] * (tparams['b'] ** 2).sum()
    return trainingParis, subPaths_matrix, subPaths_mask, subPaths_lens,groups_tensor, path_discount,wordsEmbeddings, cost


def discountModel(alpha, length):
    """
    discount model
    """
    return tensor.exp(alpha * length * (-1))


def numpy_floatX(data):
    return numpy.asarray(data, dtype=theano.config.floatX)  # @UndefinedVariable