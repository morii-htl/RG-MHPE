# encoding=utf-8
'''
proxEmbed model for compute some dataset
'''

import numpy
import theano
from theano import tensor

import PModelBatch
import lstmModel
import proEmbedModelBatch


def proxEmbedModel(model_options, tparams):
    """
       build ProxEmbed model
    """
    subPaths_matrix = tensor.matrix('subPaths_matrix', dtype='int64')  # shape=maxlen*subPaths
    subPaths_mask = tensor.matrix('subPaths_mask', dtype=theano.config.floatX)  # shape=maxlen*subPaths
    subPaths_lens = tensor.vector('subPaths_lens', dtype='int64')  # shape=subPaths
    wordsEmbeddings = tensor.matrix('wordsEmbeddings', dtype=theano.config.floatX)  # shape = nums * dim
    groups_tensor=tensor.matrix('groups_tensor', dtype=theano.config.floatX)
    path_discount = tensor.vector("path_discount", dtype=theano.config.floatX)  # shape = nums

    embs=PModelBatch.Model(model_options, tparams, subPaths_matrix, subPaths_mask,path_discount,
                                                        wordsEmbeddings)
    group_embs=groups_tensor[:,:,None]*embs + ((1.-groups_tensor)*(-1000))[:,:,None]
    group_embs=group_embs.max(axis=1) # shape=tupleNum*dim
    """
    # 一下增加了路径数量的考虑，不合适可以删除
    groups_num = groups_tensor.sum(axis = 1) #shape=tupleNum
    group_embs = tensor.log(1 + groups_num[:,None]) * group_embs
    #路径数量考虑结束
    """
    values = tensor.dot(group_embs, tparams['w']) # shape=tupleNum
    return subPaths_matrix, subPaths_mask, subPaths_lens, groups_tensor, path_discount, wordsEmbeddings, values


def discountModel(alpha, length):
    """
    discount model
    """
    return tensor.exp(alpha * length * (-1))
