package dataPrepare.ProEmbed_path;

public class ObjectPath {
    private Node node1;
    private Node node2;
    private Integer id;
    private String edgeType;

    public Node getNode1() {
        return node1;
    }

    public void setNode1(Node node1) {
        this.node1 = node1;
    }

    public Node getNode2() {
        return node2;
    }

    public void setNode2(Node node2) {
        this.node2 = node2;
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getEdgeType() {
        return edgeType;
    }

    public void setEdgeType(String edgeType) {
        this.edgeType = edgeType;
    }

    @Override
    public String toString() {
        return "ObjectPath{" +
                "node1=" + node1 +
                ", node2=" + node2 +
                ", id=" + id +
                ", edgeType='" + edgeType + '\'' +
                '}';
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ObjectPath that = (ObjectPath) o;
        return (node1.equals(that.node1) &&
                node2.equals(that.node2))|| (node1.equals(that.node2)&& node2.equals(that.node1))&&
                edgeType.equals(that.edgeType);
    }

    @Override
    public int hashCode() {
        return 31*edgeType.hashCode() + node1.hashCode() + node2.hashCode();
    }
}
