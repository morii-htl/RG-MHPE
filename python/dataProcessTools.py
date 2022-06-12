#encoding=utf-8
'''
methods for processing data
'''

import numpy
import theano

# Set the random number generators' seeds for consistency
SEED = 123
numpy.random.seed(SEED)

def getTrainingData(trainingDataFile):
    '''
        read training data from file
    :type string
    :param trainingDataFile
    '''
    data=[] 
    pairs=[] 
    with open(trainingDataFile) as f:
        for l in f:
            tmp=l.strip().split()
            if len(tmp)<=0:
                continue
            arr=[]
            arr.append(tmp[0]+'-'+tmp[1])
            arr.append(tmp[1]+'-'+tmp[0])
            arr.append(tmp[0]+'-'+tmp[2])
            arr.append(tmp[2]+'-'+tmp[0])
            pairs.append(arr) 
            tmp=[int(x) for x in tmp] 
            data.append(tmp)
            
    return data,pairs

def getWordsEmbeddings(wordsEmbeddings_path):
    """
        read words embeddings from file
            a b
            c d e f ....
            g h j k ....
            a means the num(line) of the data，b means the dimension of the data
            c and g are the index of the corresponding words
            d，e，f，h，j，k，... are the content of embeddings
    :type String
    :param wordsEmbeddings_path
    """
    size=0
    dimension=0
    wemb=[]
    with open(wordsEmbeddings_path) as f:
        for l in f:
            arr=l.strip().split()
            if len(arr)==2: 
                size=int(arr[0])
                dimension=int(arr[1])
                wemb=numpy.zeros((size,dimension),dtype=theano.config.floatX) # @UndefinedVariable
                continue
            id=int(arr[0])
            for i in range(0,dimension):
                wemb[id][i]=float(arr[i+1])
    return wemb,dimension,size

def loadAllSubPaths(subpaths_file,maxlen=1000):
    """
        read all subpaths from file
    :type subpaths_file: String
    :param subpaths_file：file path 
       
    :type maxlen:int
    :param maxlen:
    
    the return value is a map, and the key of this map is made of startNodeId-endNodeId.
    the value of this map is a list made of startNodeId aId bId cId dId... endNodeId
    """
    map={}
    with open(subpaths_file) as f:
        for l in f: 
            splitByTab=l.strip().split('\t')
            if len(splitByTab)<3:
                continue
            key=splitByTab[0]+'-'+splitByTab[1]
            sentence=[int(y) for y in splitByTab[2].split()[:]] 
            if len(sentence)>maxlen: 
                continue
            if key in map:
                map[key].append(sentence)
            else: 
                tmp=[]
                tmp.append(sentence)
                map[key]=tmp
    return map

def prepareDataForTraining(trainingDataTriples,trainingDataPairs,subpaths_map,alpha):
    """
        prepare data for training
    """
    trainingDataPairsValid = []  # 留下有效的训练数据，剔除都不在的
    for tuples in trainingDataPairs:
        if (tuples[0] not in subpaths_map and tuples[1] not in subpaths_map) or (
                tuples[2] not in subpaths_map and tuples[3] not in subpaths_map):
            continue
        trainingDataPairsValid.append(tuples)
    n_triples = len(trainingDataPairsValid)
    trainingDataPairs=trainingDataPairsValid

    triples_matrix=numpy.zeros([n_triples,4,2]).astype('int64') #这里就是后面用的格式啊！！！真缺德啊不早点写

    maxlen=0 
    n_subpaths=0 
    allPairs=[] 
    for list in trainingDataPairs:
        for l in list:
            allPairs.append(l)
    for key in allPairs: 
        if key not in subpaths_map: 
            continue;
        list=subpaths_map[key]
        n_subpaths+=len(list) 
        for l in list:
            if len(l)>maxlen:
                maxlen=len(l)

    groups_tensor3 = numpy.zeros([2, n_triples, n_subpaths]).astype(
        theano.config.floatX)  # @UndefinedVariable

    subPaths_matrix=numpy.zeros([maxlen,n_subpaths]).astype('int64') #每一列是一个句子，不到最长长度的用0填充
    
    subPaths_mask=numpy.zeros([maxlen,n_subpaths]).astype(theano.config.floatX)  # @UndefinedVariable #这个mask代表哪一位是被填充的，nlp的常用方法
    
    subPaths_lens=numpy.zeros([n_subpaths,]).astype('int64') #每个句子的长度

    path_discount=numpy.zeros([n_subpaths]).astype(theano.config.floatX)
    print path_discount.shape
    
    current_index=0 
    path_index=0 
    valid_triples_count=0 
    for i in range(len(trainingDataPairs)): 
        pairs=trainingDataPairs[i]
        valid_triples_count+=1 
        for j in range(len(pairs)): 
            pair=pairs[j]
            list=None
            if pair in subpaths_map: 
                list=subpaths_map[pair] #对应一个字典 key：0-1 values：[[句子1]，[句子2]，[句子3]]
            if list is not None:
                triples_matrix[i][j][0]=current_index
                current_index+=len(list)
                triples_matrix[i][j][1]=current_index #[i][j][1]-[i][j][0]为对应pair 2-3 路径的数量，即给路径编号，这里都用从几号到几号的路径，这里注意subpaths_map的格式
                for x in range(len(list)):
                    index=path_index+x 
                    path=list[x] 
                    subPaths_lens[index]=len(path)
                    length = len(path)
                    discount = discountForPathlength(alpha, length)
                    path_discount[index]=discount
                    for y in range(len(path)): 
                        subPaths_matrix[y][index]=path[y] #每一列对应一个路径
                        subPaths_mask[y][index]=1. #不是填充的点，给标记

                    if j == 0 or j == 1:
                        groups_tensor3[0][i][index] = 1.  # 为了后续矩阵运算做准备
                        # [0]是相似的，i是第几组
                        # currentIndex是第几个路径为什么要这么写呢
                    else:
                        groups_tensor3[1][i][index] = 1.
                path_index+=len(list) #更新路径的index

            else : #如果路径是空的就不更新呀！！！想的周到啊
                triples_matrix[i][j][0]=current_index 
                current_index+=0
                triples_matrix[i][j][1]=current_index 
                
    count=0
    for i in range(len(triples_matrix)):
        if triples_matrix[i][0][0]!=triples_matrix[i][1][1] and triples_matrix[i][2][0]!=triples_matrix[i][3][1]: #这是在说明路径非空吧
            count+=1
    triples_matrix_new=numpy.zeros([count,4,2]).astype('int64')
    index=0
    for i in range(len(triples_matrix)):
        if triples_matrix[i][0][0]!=triples_matrix[i][1][1] and triples_matrix[i][2][0]!=triples_matrix[i][3][1]:
            triples_matrix_new[index]=triples_matrix[i]
            index+=1
    triples_matrix=triples_matrix_new #这一步明显是把空的路径给去掉

    return triples_matrix, subPaths_matrix, subPaths_mask, subPaths_lens,groups_tensor3,path_discount
    
    
def prepareDataForTest(query,candidate,subpaths_map):
    """
   prepare data for test
    """
    key1=bytes(query)+'-'+bytes(candidate)
    key2=bytes(candidate)+'-'+bytes(query)
    if key1 not in subpaths_map and key2 not in subpaths_map:
        return None,None,None
    subpaths=[]
    if key1 in subpaths_map:
        subpaths.extend(subpaths_map[key1]) 
    if key2 in subpaths_map:
        subpaths.extend(subpaths_map[key2]) 
    maxlen=0
    for subpath in subpaths:
        if len(subpath)>maxlen:
            maxlen=len(subpath)
    subPaths_matrix=numpy.zeros([maxlen,len(subpaths)]).astype('int64') #老规矩，给出对应请求的subpath
    subPaths_mask=numpy.zeros([maxlen,len(subpaths)]).astype(theano.config.floatX)  # @UndefinedVariable
    subPaths_lens=numpy.zeros([len(subpaths),]).astype('int64')
    for i in range(len(subpaths)):
        subpath=subpaths[i]
        subPaths_lens[i]=len(subpath) 
        for j in range(len(subpath)):
            subPaths_matrix[j][i]=subpath[j]
            subPaths_mask[j][i]=1.  
    
    return subPaths_matrix,subPaths_mask,subPaths_lens

    
def get_minibatches_idx(n, minibatch_size, shuffle=False):
    """
    Used to shuffle the dataset at each iteration.
    """
    idx_list = numpy.arange(n, dtype="int32")

    if shuffle:
        numpy.random.shuffle(idx_list)

    minibatches = []
    minibatch_start = 0
    for i in range(n // minibatch_size):
        minibatches.append(idx_list[minibatch_start:
                                    minibatch_start + minibatch_size])
        minibatch_start += minibatch_size

    if (minibatch_start != n):
        # Make a minibatch out of what is left
        minibatches.append(idx_list[minibatch_start:])

    return zip(range(len(minibatches)), minibatches)# 将(index,minibatch)设置成tuple（所有的tuple组成一个list），然后返回这个list


# just for test
def loadAllSubPathsByTyplesRemoveRepeatPaths(subpaths_file, tuples, maxlen=1000):
    """
    """
    map={}
    with open(subpaths_file) as f:
        for l in f: #
            splitByTab=l.strip().split('\t')
            key=splitByTab[0]+'-'+splitByTab[1] #
            sentence=[int(y) for y in splitByTab[2].split()[:]] #
            if len(sentence)>maxlen: #
                continue
            if key not in tuples:
                continue
            if key in map:
                map[key].add(splitByTab[2])
            else:
                tmp=set()
                tmp.add(splitByTab[2])
                map[key]=tmp
    result={}
    for key in map:
        result[key]=[]
        for path in map[key]:
            result[key].append([int(y) for y in path.split()[:]])
        print len(result)
    return result
def prepareDataForTestBatch(query, candidates, subpaths_map, alpha):
    sequencesNum = 0
    maxlen = 0
    for candidate in candidates:
        key1 = bytes(query) +'-' +bytes(candidate) #这里原文加了bytes 不能理解
        key2 = bytes(candidate) + "-" +bytes(query)
        if key1 in subpaths_map:
            sequencesNum += len(subpaths_map[key1])
            for subpath in subpaths_map[key1]:
                if maxlen < len(subpath):
                    maxlen = len(subpath)
        if key2 in subpaths_map:
            sequencesNum += len(subpaths_map[key2])
            for subpath in subpaths_map[key2]:
                if maxlen < len(subpath):
                    maxlen = len(subpath)
    subPaths_matrix =  numpy.zeros([maxlen, sequencesNum]).astype('int64')
    subPaths_mask =  numpy.zeros([maxlen, sequencesNum]).astype(theano.config.floatX)
    subPaths_lens = numpy.zeros([sequencesNum]).astype('int64')

    path_discount = numpy.zeros([sequencesNum]).astype(theano.config.floatX)  # @UndefinedVariable
    groups_tensor = numpy.zeros([len(candidates), sequencesNum]).astype(theano.config.floatX)  # @UndefinedVariable
    #subPaths_matrix, subPaths_mask, subPaths_lens, groups_tensor, path_discount
    path_index = 0
    for tupleIndex in range(len(candidates)):
        candidate=candidates[tupleIndex]
        key1 = bytes(query) + '-' + bytes(candidate)
        key2 = bytes(candidate) + '-' + bytes(query)
        subpaths = []
        if key1 in subpaths_map:
            subpaths.extend(subpaths_map[key1])
        if key2 in subpaths_map:
            subpaths.extend(subpaths_map[key2])
        for x in range(len(subpaths)):
            index = x + path_index
            subpath = subpaths[x]
            length = len(subpath)
            subPaths_lens[index] = length
            discount = discountForPathlength(alpha, length)
            path_discount[index] = discount
            for y in range(len(subpath)):
                subPaths_matrix[y][index] = subpath[y]  # 每一列对应一个路径
                subPaths_mask[y][index] = 1
            groups_tensor[tupleIndex][index] = 1
        path_index += len(subpaths)
    return subPaths_matrix,subPaths_mask,subPaths_lens,path_discount,groups_tensor






def discountForPathlength(alpha, length):
    return numpy.exp(-alpha*length)




