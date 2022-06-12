#encoding=utf-8
'''
process dataset by proxEmbed model and then assess
'''

import numpy
import theano
from theano import tensor
from collections import OrderedDict
import proxEmbedProcessModel
import dataProcessTools
import proxEmbedProcessModelBatch
import toolsFunction
import evaluateTools
import time
import Ftools


def load_params(path, params):
    """
    load model params from file
    """
    pp = numpy.load(path) 
    for kk, vv in params.items():
        if kk not in pp:
            raise Warning('%s is not in the archive' % kk)
        params[kk] = pp[kk]

    return params


def get_proxEmbedModel(
                      
                   model_params_path='', # the path of model parameters
                     word_dimension=0, # the dimension of words embedding 
                     dimension=0, # the dimension of path embedding
                     h_output_method='h', # the output way of lstm
                     discount_alpha=0.1, # discount alpha
                     subpaths_pooling_method='max-pooling', # the combine way of sub-paths
                      ):
    """
    get model from file
    """
    model_options = locals().copy()
    
    tparams = OrderedDict()
    tparams['lstm_W']=None
    tparams['lstm_U']=None
    tparams['lstm_b']=None
    tparams['w']=None
    #tparams['b'] = None
    tparams=load_params(model_params_path, tparams) 
    
    subPaths_matrix,subPaths_mask,subPaths_lens,wemb,score=proxEmbedProcessModel.proxEmbedModel(model_options, tparams)
    func=theano.function([subPaths_matrix,subPaths_mask,subPaths_lens,wemb], score) 
    
    return func


def get_batch_proxEmbedModel(

        model_params_path='',  # the path of model parameters
        word_dimension=0,  # the dimension of words embedding
        dimension=0,  # the dimension of path embedding
        h_output_method='h',  # the output way of lstm
        discount_alpha=0.1,  # discount alpha
        subpaths_pooling_method='max-pooling',  # the combine way of sub-paths
):
    """
    get model from file
    """
    model_options = locals().copy()

    tparams = OrderedDict()
    tparams['lstm_W'] = None
    tparams['lstm_U'] = None
    tparams['lstm_b'] = None
    tparams['w'] = None
    # tparams['b'] = None
    tparams = load_params(model_params_path, tparams)

    subPaths_matrix, subPaths_mask, subPaths_lens, groups_tensor, path_discount, wordsEmbeddings, values = proxEmbedProcessModelBatch.proxEmbedModel(model_options,
                                                                                                      tparams)
    func = theano.function(
        [subPaths_matrix, subPaths_mask, subPaths_lens, groups_tensor, path_discount, wordsEmbeddings], values,
        on_unused_input='ignore')
    return func

    return func


def compute_proxEmbed(
                     wordsEmbeddings=None, # words embeddings
                     wordsEmbeddings_path=None, # the file path of words embeddings
                     word_dimension=0, #  dimension of words embeddings
                     dimension=0, # the dimension of paths embeddings
                     wordsSize=0, # the size of words vocabulary
                     subpaths_map=None, # contains sub-paths
                     subpaths_file=None,# the file which contains sub-paths
                     maxlen_subpaths=1000, # the max length for sub-paths
                     maxlen=100,  # Sequence longer then this get ignored 
                     main_dir="",
                     test_data_file='', # the file path of test data
                     top_num=10, # the top num to predict
                     ideal_data_file='', # ground truth
                     func=None, # model function
                   ):
    """
    compute the result of the model
    """
    
    model_options = locals().copy()

    if wordsEmbeddings is None:
        if wordsEmbeddings_path is not None: 
            wordsEmbeddings,dimension,wordsSize=dataProcessTools.getWordsEmbeddings(wordsEmbeddings_path)
        else: 
            print 'There is not path for wordsEmbeddings, exit!!!'
            exit(0) 

    if subpaths_map is None: 
        if subpaths_file is not None: 
            subpaths_map=dataProcessTools.loadAllSubPaths(subpaths_file, maxlen_subpaths)
        else: 
            print 'There is not path for sub-paths, exit!!!'
            exit(0)

    line_count=0 
    test_map={}
    testmap2={}
    testmap3 = {}
    print 'Compute MAP and nDCG for file ',test_data_file
    start_time = time.time()
    print 'start time ==',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time))
    with open(test_data_file) as f: 
        for l in f: 
            arr=l.strip().split()
            query=int(arr[0])
            map={} 
            for i in range(1,len(arr)): 
                candidate=int(arr[i]) 
                subPaths_matrix_data,subPaths_mask_data,subPaths_lens_data=dataProcessTools.prepareDataForTest(query, candidate, subpaths_map)
                if subPaths_matrix_data is None and subPaths_mask_data is None and subPaths_lens_data is None: 
                    map[candidate]=-1000. 
                else: 
                    value=func(subPaths_matrix_data,subPaths_mask_data,subPaths_lens_data,wordsEmbeddings) 
                    map[candidate]=value
                    print value
            
            tops_in_line,top2=toolsFunction.mapSortByValueDESC2(map, top_num) #返回一个节点的列表，节点按相似度分数大小排序，排前top个点，若长度<top，有多少排多少
            test_map[line_count]=tops_in_line  #字典 key：第几个序列，value：对应的相似节点列表
            testmap2[query]=tops_in_line
            testmap3[query] = top2
            line_count += 1
    end_time = time.time()
    print 'end time ==',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end_time))
    print 'Testing finished! Cost time == ', end_time-start_time,' s'
    line_count=0 
    ideal_map={}
    ideal_map2={}
    with open(ideal_data_file) as f: 
        for l in f: 
            arr=l.strip().split()
            arr=[int(x) for x in arr]
            ideal_map[line_count]=arr[1:]
            ideal_map2[arr[0]]=arr[1:]
            line_count+=1
    #Ftools.createDictCSV(testDict=testmap2,idealDict=ideal_map2,fileName=main_dir+"/result_",main_dir=main_dir)
    Ftools.createDictCSV2(testDict1=testmap2, testDict2=testmap3,idealDict=ideal_map2, fileName=main_dir + "/result_", main_dir=main_dir)
    """
    ideal_map={}
    test_map={}
    with open ("/mnt/pdata/relust_num.csv") as f:
        i = 0
        for l in f:
            arr = l.strip().split(',')
            query = int(arr[0])
            map = {}
            arr = [int(x) for x in arr]
            if(i%2 == 0):
                test_map[query]=arr[1:]
            else:
                ideal_map[query]=arr[1:]
            i+=1
    """
    MAP=evaluateTools.get_MAP(top_num, ideal_map2, testmap2,main_dir)
    MnDCG=evaluateTools.get_MnDCG(top_num, ideal_map, test_map)
    
    return MAP,MnDCG


def compute_proxEmbed2(
        wordsEmbeddings=None,  # words embeddings
        wordsEmbeddings_path=None,  # the file path of words embeddings
        word_dimension=0,  # dimension of words embeddings
        dimension=0,  # the dimension of paths embeddings
        wordsSize=0,  # the size of words vocabulary
        subpaths_map=None,  # contains sub-paths
        subpaths_file=None,  # the file which contains sub-paths
        maxlen_subpaths=1000,  # the max length for sub-paths
        maxlen=100,  # Sequence longer then this get ignored

        test_data_file='',  # the file path of test data
        top_num=10,  # the top num to predict
        ideal_data_file='',  # ground truth
        func=None,  # model function
):
    """
    compute the result of the model
    """

    model_options = locals().copy()

    if wordsEmbeddings is None:
        if wordsEmbeddings_path is not None:
            wordsEmbeddings, dimension, wordsSize = dataProcessTools.getWordsEmbeddings(wordsEmbeddings_path)
        else:
            print 'There is not path for wordsEmbeddings, exit!!!'
            exit(0)

    if subpaths_map is None:
        if subpaths_file is not None:
            subpaths_map = dataProcessTools.loadAllSubPaths(subpaths_file, maxlen_subpaths)
        else:
            print 'There is not path for sub-paths, exit!!!'
            exit(0)

    line_count = 0
    test_map = {}
    testmap2 = {}
    print 'Compute TP and FR for file ', test_data_file
    start_time = time.time()
    print 'start time ==', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
    with open(test_data_file) as f:
        for l in f:
            arr = l.strip().split()
            query = int(arr[0])
            map = {}
            for i in range(1, len(arr)):
                candidate = int(arr[i])
                subPaths_matrix_data, subPaths_mask_data, subPaths_lens_data = dataProcessTools.prepareDataForTest(
                    query, candidate, subpaths_map)
                if subPaths_matrix_data is None and subPaths_mask_data is None and subPaths_lens_data is None:
                    map[candidate] = 0
                else:
                    value = func(subPaths_matrix_data, subPaths_mask_data, subPaths_lens_data, wordsEmbeddings)
                    map[candidate] = value

            tops_in_line = toolsFunction.mapSortByValueDESC(map,
                                                            top_num)  # 返回一个节点的列表，节点按相似度分数大小排序，排前top个点，若长度<top，有多少排多少
            test_map[
                line_count] = map  # key-value：节点-相似度的字典
            testmap2[query] = map
            line_count += 1
    end_time = time.time()
    print 'end time ==', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
    print 'Testing finished! Cost time == ', end_time - start_time, ' s'
    line_count = 0
    ideal_map = {}
    ideal_map2 = {}
    with open(ideal_data_file) as f:
        for l in f:
            arr = l.strip().split()
            arr = [int(x) for x in arr]
            ideal_map[line_count] = arr[1:]
            ideal_map2[arr[0]] = arr[1:]
            line_count += 1
    # Ftools.createDictCSV(testDict=testmap2,idealDict=ideal_map2,fileName="/mnt/datasets/wyfdata/prox2/ddata/result_")
    tp=0
    tn=0
    fp=0
    fn=0
    for line,values in test_map.items():
        tpset=set(ideal_map[line])
        for node,score in values.items():
                if node in tpset:
                    if(score > 0.5):
                        tp+=1
                    else:
                        fp+=1
                else:
                    if(score>0.5):
                        fn+=1
                    else:
                        tn+=1
    print (tp)
    print (fp)
    print (fn)
    print (tn)

    return 1, 1


def compute_proxEmbedbatch(
        wordsEmbeddings=None,  # words embeddings
        wordsEmbeddings_path=None,  # the file path of words embeddings
        word_dimension=0,  # dimension of words embeddings
        dimension=0,  # the dimension of paths embeddings
        wordsSize=0,  # the size of words vocabulary
        subpaths_map=None,  # contains sub-paths
        subpaths_file=None,  # the file which contains sub-paths
        maxlen_subpaths=1000,  # the max length for sub-paths
        maxlen=100,  # Sequence longer then this get ignored
        main_dir="",
        test_data_file='',  # the file path of test data
        top_num=10,  # the top num to predict
        ideal_data_file='',  # ground truth
        alpha=0,
        func=None,  # model function
        batch_size = 8
):
    """
    compute the result of the model
    """

    model_options = locals().copy()

    if wordsEmbeddings is None:
        if wordsEmbeddings_path is not None:
            wordsEmbeddings, dimension, wordsSize = dataProcessTools.getWordsEmbeddings(wordsEmbeddings_path)
        else:
            print 'There is not path for wordsEmbeddings, exit!!!'
            exit(0)

    if subpaths_map is None:
        if subpaths_file is not None:
            subpaths_map = dataProcessTools.loadAllSubPaths(subpaths_file, maxlen_subpaths)
        else:
            print 'There is not path for sub-paths, exit!!!'
            exit(0)

    line_count = 0
    test_map = {}
    testmap2 = {}
    testmap3 = {}
    errCount = 0
    print 'Compute MAP and nDCG for file ', test_data_file
    start_time = time.time()
    print 'start time ==', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
    with open(test_data_file) as f:
        for l in f:
            arr = l.strip().split()
            query = int(arr[0])
            map = {}
            candidates = []
            for i in range(1, len(arr)):
                key1 = arr[0] + '-' + arr[i]
                key2 = arr[i] + '-' + arr[0]
                if key1 in subpaths_map or key2 in subpaths_map:
                    candidates.append(int(arr[i]))
                else:
                    map[int(arr[i])]= -1000.
                    errCount+=1
            subPaths_matrix,subPaths_mask,subPaths_lens,path_discount,groups_tensor = dataProcessTools.prepareDataForTestBatch(
                query, candidates, subpaths_map,alpha)
            print(len(subPaths_matrix))
            if len(subPaths_matrix) > 0 :
                scores =func(subPaths_matrix, subPaths_mask, subPaths_lens, groups_tensor, path_discount, wordsEmbeddings)
                for index in range(len(candidates)):
                    map[candidates[index]] = scores[index]
            else:
                for i in range(1, len(arr)):
                    map[int(arr[i])] = -1.


            tops_in_line, top2 = toolsFunction.mapSortByValueDESC2(map,
                                                                   top_num)  # 返回一个节点的列表，节点按相似度分数大小排序，排前top个点，若长度<top，有多少排多少
            test_map[
                line_count] = tops_in_line  # 字典 key：第几个序列，value：对应的相似节点列表
            testmap2[query] = tops_in_line
            testmap3[query] = top2
            line_count += 1
    end_time = time.time()
    print 'end time ==', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
    print 'Testing finished! Cost time == ', end_time - start_time, ' s'
    line_count = 0
    ideal_map = {}
    ideal_map2 = {}
    with open(ideal_data_file) as f:
        for l in f:
            arr = l.strip().split()
            arr = [int(x) for x in arr]
            ideal_map[line_count] = arr[1:]
            ideal_map2[arr[0]] = arr[1:]
            line_count += 1
    # Ftools.createDictCSV(testDict=testmap2,idealDict=ideal_map2,fileName=main_dir+"/result_",main_dir=main_dir)
    Ftools.createDictCSV2(testDict1=testmap2, testDict2=testmap3, idealDict=ideal_map2, fileName=main_dir + "/result_",
                          main_dir=main_dir)
    """
    ideal_map={}
    test_map={}
    with open ("/mnt/pdata/relust_num.csv") as f:
        i = 0
        for l in f:
            arr = l.strip().split(',')
            query = int(arr[0])
            map = {}
            arr = [int(x) for x in arr]
            if(i%2 == 0):
                test_map[query]=arr[1:]
            else:
                ideal_map[query]=arr[1:]
            i+=1
    """
    MAP = evaluateTools.get_MAP(top_num, ideal_map2, testmap2, main_dir)
    MnDCG = evaluateTools.get_MnDCG(top_num, ideal_map, test_map)

    return MAP, MnDCG
def compute_proxEmbedbatch2(
        wordsEmbeddings=None,  # words embeddings
        wordsEmbeddings_path=None,  # the file path of words embeddings
        word_dimension=0,  # dimension of words embeddings
        dimension=0,  # the dimension of paths embeddings
        wordsSize=0,  # the size of words vocabulary
        subpaths_map=None,  # contains sub-paths
        subpaths_file=None,  # the file which contains sub-paths
        maxlen_subpaths=1000,  # the max length for sub-paths
        maxlen=100,  # Sequence longer then this get ignored
        main_dir="",
        test_data_file='',  # the file path of test data
        top_num=10,  # the top num to predict
        ideal_data_file='',  # ground truth
        alpha=0,
        func=None,  # model function
        batch_size = 4
):
    """
    compute the result of the model
    """

    model_options = locals().copy()

    if wordsEmbeddings is None:
        if wordsEmbeddings_path is not None:
            wordsEmbeddings, dimension, wordsSize = dataProcessTools.getWordsEmbeddings(wordsEmbeddings_path)
        else:
            print 'There is not path for wordsEmbeddings, exit!!!'
            exit(0)

    if subpaths_map is None:
        if subpaths_file is not None:
            subpaths_map = dataProcessTools.loadAllSubPaths(subpaths_file, maxlen_subpaths)
        else:
            print 'There is not path for sub-paths, exit!!!'
            exit(0)

    line_count = 0
    test_map = {}
    testmap2 = {}
    testmap3 = {}
    errCount = 0
    print 'Compute MAP and nDCG for file ', test_data_file
    start_time = time.time()
    print 'start time ==', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
    with open(test_data_file) as f:
        for l in f:
            arr = l.strip().split()
            query = int(arr[0])
            map = {}
            candidates = []
            for i in range(1, len(arr)):
                key1 = arr[0] + '-' + arr[i]
                key2 = arr[i] + '-' + arr[0]
                if key1 in subpaths_map or key2 in subpaths_map:
                    candidates.append(int(arr[i]))
                else:
                    map[int(arr[i])]= -1000.
                    errCount+=1
            canindex = 0
            nextlen = min(len(candidates) - canindex,batch_size)
            sub_candidates = candidates[canindex : canindex + nextlen]
            while(canindex < len(candidates) ):
                subPaths_matrix,subPaths_mask,subPaths_lens,path_discount,groups_tensor = dataProcessTools.prepareDataForTestBatch(
                    query, sub_candidates, subpaths_map,alpha)
                if len(subPaths_matrix) > 0 :
                    scores =func(subPaths_matrix, subPaths_mask, subPaths_lens, groups_tensor, path_discount, wordsEmbeddings)
                    for index in range(len(sub_candidates)):
                        map[sub_candidates[index]] = scores[index]
                else:
                    for index in range(len(sub_candidates)):
                        map[sub_candidates[index]] = -1000.
                canindex += nextlen
                nextlen = min(len(candidates) - canindex, batch_size)
                sub_candidates = candidates[canindex: canindex + nextlen]


            tops_in_line, top2 = toolsFunction.mapSortByValueDESC2(map,
                                                                   top_num)  # 返回一个节点的列表，节点按相似度分数大小排序，排前top个点，若长度<top，有多少排多少
            test_map[
                line_count] = tops_in_line  # 字典 key：第几个序列，value：对应的相似节点列表
            testmap2[query] = tops_in_line
            testmap3[query] = top2
            line_count += 1
    end_time = time.time()
    print 'end time ==', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
    print 'Testing finished! Cost time == ', end_time - start_time, ' s'
    line_count = 0
    ideal_map = {}
    ideal_map2 = {}
    with open(ideal_data_file) as f:
        for l in f:
            arr = l.strip().split()
            arr = [int(x) for x in arr]
            ideal_map[line_count] = arr[1:]
            ideal_map2[arr[0]] = arr[1:]
            line_count += 1
    # Ftools.createDictCSV(testDict=testmap2,idealDict=ideal_map2,fileName=main_dir+"/result_",main_dir=main_dir)
    Ftools.createDictCSV2(testDict1=testmap2, testDict2=testmap3, idealDict=ideal_map2, fileName=main_dir + "/result_",
                          main_dir=main_dir)
    """
    ideal_map={}
    test_map={}
    with open ("/mnt/pdata/relust_num.csv") as f:
        i = 0
        for l in f:
            arr = l.strip().split(',')
            query = int(arr[0])
            map = {}
            arr = [int(x) for x in arr]
            if(i%2 == 0):
                test_map[query]=arr[1:]
            else:
                ideal_map[query]=arr[1:]
            i+=1
    """
    MAP = evaluateTools.get_MAP(top_num, ideal_map2, testmap2, main_dir)
    MnDCG = evaluateTools.get_MnDCG(top_num, ideal_map, test_map)

    return MAP, MnDCG
    