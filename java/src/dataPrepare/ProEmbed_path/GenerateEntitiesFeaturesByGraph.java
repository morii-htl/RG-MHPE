package dataPrepare.ProEmbed_path;



import java.io.*;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Generate entity features by information from neighbours -- just for asymmetric
 */
public class GenerateEntitiesFeaturesByGraph {

	private Set<String> types = new HashSet<String>();
	private Map<String, Integer> type2Typeid = new HashMap<String, Integer>();
	private Map<Integer, String> typeid2Type = new HashMap<Integer, String>();
	private Set<String> edgeType_set = new HashSet<String>();
	private Map<String, Integer> edgeType2Typeid = new HashMap<String, Integer>();
	private Map<Integer, String> edgeTypeid2Type = new HashMap<Integer, String>();
	static String nodes_path = Config.NODES_PATH;
	static String edges_path = Config.EDGES_PATH;
	static String entities_feature_file = Config.NODES_FEATURE_SAVE_PATH;
	static String typeAndTypeIdPath = Config.TYPE_TYPEID_SAVEFILE;
	static double feature_type_value = Config.FEATURE_TYPE_VALUE;
	static Set<String> edgeTypes = new HashSet<>();
	static Map<Integer, ObjectPath> objectPaths = new HashMap<>();

	public static void main(String[] args) {

		ReadWholeGraph rwg = new ReadWholeGraph();
		Map<Integer, Node> graph = rwg.readDataFromFile(nodes_path, edges_path, typeAndTypeIdPath, edgeTypes, objectPaths);
		rwg.setObjectPath(graph, objectPaths);
		GenerateEntitiesFeaturesByGraph gefb = new GenerateEntitiesFeaturesByGraph();
		gefb.analyseTypes(graph, objectPaths);
		gefb.generateFeaturesByGraph(graph, entities_feature_file, feature_type_value);
		gefb.genrateObjectPathFeatureByGraph(entities_feature_file, objectPaths);
	}

	/**
	 * Analyse nodes types
	 */
	public void analyseTypes(Map<Integer, Node> graph, Map<Integer, ObjectPath> objectPaths) {
		for (Node n : graph.values()) {
			types.add(n.getType());
			if (!type2Typeid.containsKey(n.getType())) {
				type2Typeid.put(n.getType(), type2Typeid.size());
				typeid2Type.put(typeid2Type.size(), n.getType());
			}
		}
		for (ObjectPath objectPath : objectPaths.values()) {
			edgeType_set.add(objectPath.getEdgeType());
			if (!edgeType2Typeid.containsKey(objectPath.getEdgeType())) {
				edgeType2Typeid.put(objectPath.getEdgeType(), edgeType2Typeid.size());
				edgeTypeid2Type.put(edgeTypeid2Type.size(), objectPath.getEdgeType());
			}
		}
	}

	/**
	 * Generate nodes features
	 */
	public void generateFeaturesByGraph(Map<Integer, Node> graph, String saveFile, double typeValue) {
		int dimension = types.size() + 1 + edgeType_set.size() + 1;
		int nodesNum = graph.size();
		StringBuilder sb = new StringBuilder();
		String type = null;
		int typeId = 0;
		double value = 0;
		double sum = 0;
		Map<String, Integer> typesNum = new HashMap<String, Integer>();
		FileWriter writer = null;
		try {
			writer = new FileWriter(saveFile);
			writer.write(nodesNum + " " + dimension + "\r\n");
			writer.flush();
			for (Node now : graph.values()) {
				sb.delete(0, sb.length());
				typesNum.clear();

				sb.append(now.getId() + " ");
				type = now.getType();
				typeId = type2Typeid.get(type);

				for (int i = 0; i < types.size(); i++) {
					if (i == typeId) {
						sb.append(typeValue + " ");
					} else {
						sb.append(0.0 + " ");
					}
				}

				value = now.objectPaths.size();
				sb.append(Math.log(value + 1.0) + " ");

				for (ObjectPath objectPath : now.objectPaths) { //这里我要使用ObjectPath来进行对度，和邻居分布的赋值
					type = objectPath.getEdgeType();
					if (typesNum.containsKey(type)) {
						typesNum.put(type, typesNum.get(type) + 1);
					} else {
						typesNum.put(type, 1);
					}
				}
				for (int i = 0; i < edgeTypeid2Type.size(); i++) {
					type = edgeTypeid2Type.get(i);
					if (typesNum.containsKey(type)) {
						sb.append(Math.log(typesNum.get(type) + 1) + " ");
					} else {
						sb.append(0.0 + " ");
					}
				}

				value = 0;
				sum = 0;
				for (int num : typesNum.values()) {
					value = (num + 0.0) / now.in_nodes.size();
					sum += -value * Math.log(value);
				}
				sb.append(sum);

				sb.append("\r\n");
				writer.write(sb.toString());
				writer.flush();
			}
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			try {
				if (writer != null) {
					writer.close();
					writer = null;
				}
			} catch (Exception e2) {
				e2.printStackTrace();
			}
		}
	}

	public void genrateObjectPathFeatureByGraph(String saveFile, Map<Integer, ObjectPath> objectPaths) {
		Map<Integer, String> nodeFeature = new HashMap<>();
		File file = new File(saveFile);
		File file2 = new File(saveFile + "_objectpath");
		BufferedReader bufferedReader = null;
		BufferedWriter bufferedWriter = null;
		try {
			bufferedReader = new BufferedReader(new FileReader(file));
			bufferedWriter = new BufferedWriter(new FileWriter(file2));
			String s;
			String[] arr;
			StringBuilder sb = new StringBuilder(200);
			while ((s = bufferedReader.readLine()) != null) {
				s = s.trim();
				arr = s.split(" ", 2);
				int nodeid = Integer.parseInt(arr[0]);
				nodeFeature.put(nodeid, arr[1]);
			}
			sb.append(objectPaths.size());
			sb.append(" ");
			sb.append(2 * (types.size() + 1 + edgeType_set.size() + 1) + edgeType_set.size());
			bufferedWriter.write(sb.toString());
			bufferedWriter.newLine();
			bufferedWriter.flush();
			int i = 0;
			for (Map.Entry<Integer, ObjectPath> entry : objectPaths.entrySet()) {
				i += 1;
				Integer key = entry.getKey();
				ObjectPath objectPath = entry.getValue();
				String edgeType = objectPath.getEdgeType();
				if (sb.length() > 0)
					sb.delete(0, sb.length());
				sb.append(key);
				sb.append(" ");
				Node node1 = objectPath.getNode1();
				Node node2 = objectPath.getNode2();
				sb.append(nodeFeature.get(node1.getId()));
				sb.append(" ");
				sb.append(nodeFeature.get(node2.getId()));
				sb.append(" ");
				//sb.append(edgeType2Typeid.get(edgeType));
				for (int k = 0; k < edgeType_set.size(); k++) {
					if (k == edgeType2Typeid.get(edgeType)) {
						sb.append(1.0);
					} else {
						sb.append(0.0);
					}
					sb.append(" ");
				}
				bufferedWriter.write(sb.toString());
				bufferedWriter.newLine();
				bufferedWriter.flush();
			}
			System.out.println(i);
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			if (bufferedReader != null) {
				try {
					bufferedReader.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
	}
}