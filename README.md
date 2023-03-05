
![image](https://user-images.githubusercontent.com/49864164/222956178-b1268426-8ce0-4403-a53f-44edd97fe9c7.png)

# RG-MHPE
这里提供了论文[基于多重异质图的恶意软件相似性度量方法](http://www.jos.org.cn/jos/article/abstract/6538?bsh_bid=5671491964)所提出模型的源代码

# background
现有恶意软件相似性度量易受混淆技术影响, 同时缺少恶意软件间复杂关系的表征能力, 提出一种基于多重异质图的恶意软件相似性度量方法RG-MHPE (API relation graph enhanced multiple heterogeneous ProxEmbed)解决上述问题. 方法首先利用恶意软件动静态特征构建多重异质图, 然后提出基于关系路径的增强型邻近嵌入方法, 解决邻近嵌入无法应用于多重异质图相似性度量的问题. 此外, 从MSDN网站的API文档中提取知识, 构建API关系图, 学习Windows API间的相似关系, 有效减缓相似性度量模型老化速度.

# Usage

本项目实现参考ProxEmbed基础上更改 [Semantic Proximity Search on Heterogeneous Graph by Proximity Embedding](https://dl.acm.org/doi/10.5555/3298239.3298263)

java代码用于关系路径生成
python代码用于邻近嵌入
