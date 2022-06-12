#encoding=utf-8
'''
some tools methods
'''

def mapSortByValueDESC(map,top):
    """
    sort by value desc
    """
    if top>len(map): 
        top=len(map)
    items=map.items() 
    backitems=[[v[1],v[0]] for v in items]  
    backitems.sort(reverse=True) 
    e=[ backitems[i][1] for i in range(top)]
    return e

def mapSortByValueDESC2(map,top):
    """
    sort by value desc
    """
    if top>len(map):
        top=len(map)
    items=map.items()
    backitems=[[v[1],v[0]] for v in items]
    backitems.sort(reverse=True)
    e=[ backitems[i][1] for i in range(top)]
    e2 = [backitems[i][0] for i in range(top)]
    return e,e2


def mapSortByValueASC(map,top):
    """
    sort by value asc
    """
    if top>len(map): 
        top=len(map)
    items=map.items() 
    backitems=[[v[1],v[0]] for v in items]  
    backitems.sort() 
    e=[ backitems[i][1] for i in range(top)]  
    return e

