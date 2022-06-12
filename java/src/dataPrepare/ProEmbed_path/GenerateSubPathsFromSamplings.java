package dataPrepare.ProEmbed_path;

import dataPrepare.ProEmbed_path.Config;

import java.io.*;
import java.util.*;

/**
 * Generate sub-paths by samplings.
 */
public class GenerateSubPathsFromSamplings {

    static String nodes_path= Config.NODES_PATH;
    static String conditional_random_walk_sampling_paths= Config.SAVE_PATH_FOR_RANDOMWALK_SAMPLINGS;
    static String truncated_type_name= Config.TRUNCATED_TYPE_NAME;
    static String subpaths_save_path= Config.SUBPATHS_SAVE_PATH;
    static int longest_length_for_window= Config.LONGEST_ANALYSE_LENGTH_FOR_SAMPLING;
    static int longest_lenght_for_subpaths= Config.LONGEST_LENGTH_FOR_SUBPATHS;
    Map <Integer,ObjectPath> objectPaths ;

    public static void main(String[] args) {
        GenerateSubPathsFromSamplings g=new GenerateSubPathsFromSamplings();
        ReadWholeGraph rwg = new ReadWholeGraph();
        String nodesPath = Config.NODES_PATH;
        String edgesPath = Config.EDGES_PATH;
        String typeAndTypeIdPath = Config.TYPE_TYPEID_SAVEFILE;
        Set<String> edgeTypes = new HashSet<>();
        Map<Integer,ObjectPath> objectPaths = new HashMap<>();
        rwg.readDataFromFile(nodesPath,edgesPath,typeAndTypeIdPath,edgeTypes,objectPaths);
        g.generateSubPathsFromSamplings(
                nodes_path,
                conditional_random_walk_sampling_paths,
                truncated_type_name,
                subpaths_save_path,
                longest_length_for_window,
                longest_lenght_for_subpaths,
                objectPaths);
    }

    /**
     * Generate sub-paths by samplings.
     */
    public void generateSubPathsFromSamplings(String nodesPath,String samplingsPath,String truncatedNodeType,String subPathsSavePath,int window_maxlen,int subpath_maxlen,Map<Integer,ObjectPath> objectPaths){
        Set<Integer> truncatedNodeIds=new HashSet<Integer>();
        Set<String> truncatedTypes=new HashSet<String>();
        String[] arr=truncatedNodeType.split(" ");
        truncatedTypes.addAll(Arrays.asList(arr));
        BufferedReader br=null;
        arr=null;
        try {
            br = new BufferedReader(new InputStreamReader(new FileInputStream(nodesPath), "UTF-8"));
            String temp = null;
            while ((temp = br.readLine()) != null ) {
                temp=temp.trim();
                if(temp.length()>0){
                    arr=temp.split("	"); //这里是换行
                    if(truncatedTypes.contains(arr[1])){
                        truncatedNodeIds.add(Integer.parseInt(arr[0]));
                    }
                }
            }
        } catch (Exception e2) {
            e2.printStackTrace();
        }
        finally{
            try {
                if(br!=null){
                    br.close();
                    br=null;
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        FileWriter writer =null;
        String t=null;
        List<Integer> path=new ArrayList<Integer>();
        try {
            br = new BufferedReader(new InputStreamReader(new FileInputStream(samplingsPath), "UTF-8"));
            writer = new FileWriter(subPathsSavePath);
            String temp = null;
            int cou = 0;
            while ((temp = br.readLine()) != null ) {
                if(cou%10000==0)
                    System.out.println("正在处理第"+cou+"路径");
                cou++;
                temp=temp.trim();
                if(temp.length()>0){
                    path.clear();
                    arr=temp.split(" ");
                    for(String s:arr){
                        if(s==null ||s.length()==0 ||s.equals("")||cou==278477)
                            System.out.println("123");
                        path.add(Integer.parseInt(s));
                    }
                    t=analyseOnePath(path, truncatedNodeIds, window_maxlen, subpath_maxlen,objectPaths);
                    if(t.length()>0){
                        writer.write(t);
                        writer.flush();
                    }
                }
            }
        } catch (Exception e2) {
            e2.printStackTrace();
        }
        finally{
            try {
                if(writer!=null){
                    writer.close();
                    writer=null;
                }
                if(br!=null){
                    br.close();
                    br=null;
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    /**
     * Generate sub-paths by one specific sampling path.
     */
    private String analyseOnePath(List<Integer> path,Set<Integer> truncatedNodeIds,int maxWindowLen,int maxSubpathLen,Map<Integer,ObjectPath> objectPaths){
        StringBuilder sb=new StringBuilder();
        int start=0;
        int nextstart = -1;
        int end = -1;
        //我的path 除了 第一个id 代表node 其他都代表ObjectPath的id
        List<Integer> subpath=new ArrayList<Integer>();
        start = path.get(0);
        for(int i=1;i<path.size();i++){
            if(i>1)
                start = nextstart;
            ObjectPath objectPath = objectPaths.get(path.get(i));
            if(objectPath.getNode1()==null)
            {
                System.out.println("123");
            }
            int id1 = objectPath.getNode1().getId();
            int id2 = objectPath.getNode2().getId();
            nextstart = (id1 == start ? id2 : id1); //除了启示结点的下个结点，就是下一个结点的开始
            if(!truncatedNodeIds.contains(start)){
                continue;
            }
            for(int j=i;j<path.size();j++){
                ObjectPath endObjectPath = objectPaths.get(path.get(j));
                if(endObjectPath==null)
                {
                    System.out.println("13");
                }
                int eid1 = endObjectPath.getNode1().getId();
                int eid2 = endObjectPath.getNode2().getId();
                if(j==i)
                    end = nextstart;
                else {
                    end = (eid1==end ? eid2:eid1);
                }
                if(!truncatedNodeIds.contains(end)){
                    continue;
                }

                if(maxWindowLen>0 && (j-i)>maxWindowLen){
                    break;
                }

                subpath.clear();
                for(int x=i;x<=j;x++){
                    subpath.add(path.get(x)+0);
                }
                List<Integer> subpathNoRepeat=deleteRepeat(subpath,start,objectPaths);
                if(subpathNoRepeat.size()<2){
                    subpathNoRepeat=null;
                    continue;
                }

                if(maxSubpathLen>0 && subpathNoRepeat.size()>maxSubpathLen){
                    continue;
                }

                sb.append(start+"\t"+ end + "\t");
                for(int x=0;x<subpathNoRepeat.size();x++){
                    sb.append(subpathNoRepeat.get(x)+" ");
                }
                sb.append("\r\n");
                subpathNoRepeat=null;
            }
        }
        return sb.toString();
    }

    /**
     * Delete repeat segments for sub-paths
     */
    public List<Integer> deleteRepeat(List<Integer> path,int start,Map<Integer,ObjectPath> objectPaths){
        Map<Integer,Integer> map=new HashMap<Integer,Integer>();
        int node=0;
        int end=0;
        List<Integer> result=new ArrayList<Integer>();
        int formerIndex=0;
        map.put(start,0);
        for(int i=0;i<path.size();i++){
            Integer objectPath_id = path.get(i);
            ObjectPath objectPath = objectPaths.get(objectPath_id);
            int node1 = objectPath.getNode1().getId();
            int node2 = objectPath.getNode2().getId();
            if(i==0){
                end = node1==start ? node2:node1;
            }
            else {
                end = node1==end ? node2:node1;
            }
            if(!map.containsKey(end)){
                map.put(end, i+1);
            }
            else{
                formerIndex=map.get(end);
                for(int j=formerIndex;j<=i;j++){
                    if(path.get(j)==-1)
                        continue;
                    Integer o_id = path.get(j);
                    ObjectPath oPath = objectPaths.get(o_id);
                    if(oPath==null)
                        System.out.println("?");
                    int n1= oPath.getNode1().getId();
                    int n2= oPath.getNode2().getId();
                    if(map.containsKey(n1))
                    {
                        map.remove(n1);
                    }
                    if(map.containsKey(n2))
                    {
                        map.remove(n2);
                    }
                    path.set(j, -1);
                }
                map.put(end, i+1);
            }
        }
        for(int i=0;i<path.size();i++){
            if(path.get(i)!=-1){
                result.add(path.get(i));
            }
        }
        if(result.size()%2==1)
            System.out.println(result);
        return result;
    }
}
