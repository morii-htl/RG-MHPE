package dataPrepare.ProEmbed_path;


import java.io.FileWriter;
import java.io.IOException;
import java.util.*;


/**
 * Generate samplings by random walk samplings.
 * 
 * Procedure:
 * 1.Read the whole graph
 * 2.Generate samplings by random walk.
 */
public class RandomWalkSampling {

	/**
	 * Random number generator
	 */
	private Random random=new Random(123);
	
	static String nodesPath=Config.NODES_PATH;
	static String edgesPath=Config.EDGES_PATH;
	static String savePath=Config.SAVE_PATH_FOR_RANDOMWALK_SAMPLINGS;
	static int K=Config.SAMPLING_TIMES_PER_NODE;
	static int L=Config.SAMPLING_LENGTH_PER_PATH;
	static String typeAndTypeIdPath=Config.TYPE_TYPEID_SAVEFILE;
	static int shortest_path_length=Config.SHORTEST_LENGTH_FOR_SAMPLING;

	public static void main(String[] args) {
		ReadWholeGraph rwg=new ReadWholeGraph();
		//1.Read the whole graph
		Set<String> edgeTypes = new HashSet<>();
		Map<Integer,ObjectPath> objectPaths = new HashMap<>();
		Map<Integer,Node> data=rwg.readDataFromFile(
				nodesPath,
				edgesPath,
				typeAndTypeIdPath,
				edgeTypes,
				objectPaths);
		//2.Generate samplings by random walk.
		rwg.setObjectPath(data,objectPaths);
		RandomWalkSampling crws=new RandomWalkSampling();
		crws.randomWalkSampling(data,objectPaths,K, L, savePath);
	}

	/**
	 * Generate samplings by random walk.
	 * @param data
	 * @param k
	 * @param l
	 * @param pathsFile
	 */
	public void randomWalkSampling(Map<Integer,Node> data,Map<Integer,ObjectPath> objectPaths,int k,int l,String pathsFile){
		List<Integer> path=null;
		FileWriter writer=null;
		StringBuilder sb=new StringBuilder();
		try {
			writer=new FileWriter(pathsFile);
		} catch (IOException e) {
			e.printStackTrace();
		}

		for(Node node:data.values()){
			for(int i=0;i<k;i++){
				path=randomWalkPath(node,l,data,objectPaths);
				if(path.size()<shortest_path_length){
					continue;
				}
				sb.delete( 0, sb.length() );
				for(int j=0;j<path.size();j++){
					sb.append(path.get(j)+" ");
				}
				sb.append("\r\n");
				try {
					writer.write(sb.toString());
					writer.flush();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}

		}
	}

	/**
	 * Generate a path by random walk.
	 * @param start
	 * @param l
	 * @param data
	 * @return
	 */
	private List<Integer> randomWalkPath(Node start,int l, Map<Integer,Node> data,Map<Integer,ObjectPath> ObjectPaths){
		List<Integer> path=new ArrayList<>(l+2);
		path.add(start.getId());
		Node now=start;
		Set<String> types_set=new HashSet<>();
		List<String> types=new ArrayList<>();
		Map<String,List<Integer>> neighbours=new HashMap<>();
		String type="";
		List<Integer> list=null;
		ObjectPath nowObjectPath=null;
		for(int i=0;i<l;i++){
			if(now.out_nodes.size()==0){
				break;
			}
			types_set.clear();
			types.clear();
			neighbours.clear();
			for(ObjectPath objectPath : now.objectPaths){
				types_set.add(objectPath.getEdgeType());
				if(neighbours.containsKey(objectPath.getEdgeType())){
					neighbours.get(objectPath.getEdgeType()).add(objectPath.getId());
				}
				else{
					List<Integer> ids=new ArrayList<Integer>();
					ids.add(objectPath.getId());
					neighbours.put(objectPath.getEdgeType(), ids);
				}
			}
			types.addAll(types_set);
			type=types.get(random.nextInt(types.size()));
			list=neighbours.get(type);
			nowObjectPath = ObjectPaths.get(list.get(random.nextInt(list.size())));
			now = now.equals(nowObjectPath.getNode1()) ? nowObjectPath.getNode2():nowObjectPath.getNode1();
			if(nowObjectPath.getId()==null)
				System.out.println("?");
			path.add(nowObjectPath.getId());
		}
		return path;
	}
}
