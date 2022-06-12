package dataPrepare.ProEmbed_path;



public class Main {

    public static void main(String[] args) {

        //random walk sampling
        long starttime=System.currentTimeMillis();
        System.out.println("Start random walk sampling......");
        RandomWalkSampling.main(null);

        //generate entities features by information from this graph.
        System.out.println("Start generating entities' features......");
        GenerateEntitiesFeaturesByGraph.main(null);//Generate entity features by information from neighbours -- just for asymmetric
//		GenerateEntitiesFeatureByTypes.main(null);//Generate entity features only by type information -- just for symmetric
        //generate sub-paths
        System.out.println("Start generating sub-paths from samplings......");
        GenerateSubPathsFromSamplings.main(null);//Generate sub-paths from samplings.
        long endtime=System.currentTimeMillis();
        System.out.println("Cost time == "+(endtime-starttime)+" ms");
    }
}