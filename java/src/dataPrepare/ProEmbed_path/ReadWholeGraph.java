package dataPrepare.ProEmbed_path;

import dataPrepare.ProEmbed_path.Config;

import java.io.*;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Read the while graph, and then save the info into Map<Integer,Node>
 *     每次都是从graphedge逐行读取的边信息，故id也是按行进行编号
 */
public class ReadWholeGraph {

	static Map<Integer,String> typeid2Type=new HashMap<Integer, String>();
	static Map<String,Integer> type2Typeid=new HashMap<String, Integer>();

	/**
	 * Read whole graph info
	 * @param nodesPath
	 * @param edgesPath
	 * @param typeAndTypeIdPath
	 * @param objectPaths
	 * @return
	 */
	public Map<Integer,Node> readDataFromFile(String nodesPath, String edgesPath, String typeAndTypeIdPath, Set<String> edgeTypes, Map<Integer,ObjectPath> objectPaths){
		Map<Integer,Node> data=new HashMap<Integer,Node>();
		BufferedReader br=null;
		String[] arr=null;
		Node node=null;
		try {
			br = new BufferedReader(new InputStreamReader(new FileInputStream(nodesPath), "UTF-8"));
			String temp = null;
			while ((temp = br.readLine()) != null ) {
				temp=temp.trim();
				if(temp.length()>0){
					arr=temp.split("\t");
					node=new Node();
					node.setId(Integer.parseInt(arr[0]));
					node.setType(arr[1]);
					if(arr.length == 3) //这里有特殊情况 ，有个域名是空
						node.setName(arr[2]);
					if(type2Typeid.containsKey(arr[1])){
						node.setTypeId(type2Typeid.get(arr[1]));
					}
					else{
						type2Typeid.put(arr[1], type2Typeid.size());
						typeid2Type.put(typeid2Type.size(), arr[1]);
						node.setTypeId(type2Typeid.get(arr[1]));
					}
					data.put(Integer.parseInt(arr[0]), node);
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
		int start=0;
		int end=0;
		Node startNode=null;
		Node endNode=null;
		try {
			System.out.println(edgesPath);
			br = new BufferedReader(new InputStreamReader(new FileInputStream(edgesPath), "UTF-8"));
			String temp = null;
			Set<ObjectPath> objectPathSet= new HashSet<>();
			while ((temp = br.readLine()) != null ) {
				temp=temp.trim();
				if(temp.length()>0){
					arr=temp.split("\t");
					if(Integer.parseInt(arr[0])==80 &&Integer.parseInt(arr[1])==16804)
						System.out.println("?");
					start=Integer.parseInt(arr[0]);
					end=Integer.parseInt(arr[1]);
					startNode=data.get(start);
					endNode=data.get(end);
					startNode.out_ids.add(end);
					startNode.out_nodes.add(endNode);
					endNode.in_ids.add(start);
					endNode.in_nodes.add(startNode);
					if(arr.length<=2)
						System.out.println("what");
					String edgeType = arr[2];
					edgeTypes.add(edgeType);
					ObjectPath objectPath = new ObjectPath();
					objectPath.setEdgeType(edgeType);
					objectPath.setNode1(startNode);
					objectPath.setNode2(endNode);
					if(!objectPathSet.contains(objectPath)) {
						objectPath.setId(objectPathSet.size());
						objectPathSet.add(objectPath);
						objectPaths.put(objectPath.getId(), objectPath);
					}
				}
			}
			System.out.println(objectPathSet.size());
			System.out.println(objectPaths.size());
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
		FileWriter writer = null;
		try {
			writer = new FileWriter(typeAndTypeIdPath);
			for(String type:type2Typeid.keySet()){
				writer.write(type+" "+type2Typeid.get(type)+"\r\n");
				writer.flush();
				}
			} catch (Exception e) {
			e.printStackTrace();
		}
		finally{
			try {
				if(writer!=null){
					writer.close();
					writer=null;
				}
			} catch (Exception e2) {
				e2.printStackTrace();
			}
		}

		return data;
	}
	public void setObjectPath(Map<Integer,Node> data, Map<Integer,ObjectPath> objectPaths)
	{
		for (ObjectPath  objectPath : objectPaths.values())
		{
			Node node1 = objectPath.getNode1();
			Node node2 = objectPath.getNode2();
			node1.types.add(objectPath.getEdgeType());
			node2.types.add(objectPath.getEdgeType());
			node1.objectPaths.add(objectPath);
			node2.objectPaths.add(objectPath);
		}
	}
	public static void main(String[] args) {
		ReadWholeGraph rwg=new ReadWholeGraph();
		String nodesPath = Config.NODES_PATH;
		String edgesPath = Config.EDGES_PATH;
		String typeAndTypeIdPath = Config.TYPE_TYPEID_SAVEFILE;
		Set<String> edgeTypes = new HashSet<>();
		Map<Integer,ObjectPath> objectPaths = new HashMap<>();
		//1.Read the whole graph
		Map<Integer,Node> data=rwg.readDataFromFile(
				nodesPath,
				edgesPath,
				typeAndTypeIdPath,
				edgeTypes,
				objectPaths
				);
		rwg.setObjectPath(data,objectPaths);
		System.out.println(objectPaths.get(49093));
		System.out.println(objectPaths.get(216380));
		System.out.println(objectPaths.get(317145));
		System.out.println(objectPaths.get( 164531));
		//2.Generate samplings by random walk.
	}
}
//[49093, 216380, 317145]