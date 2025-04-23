import json
import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.mel as mel


def sd():
    sel = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(sel)
    selected_components = om.MObject()
    dag = om.MDagPath()
    sel.getDagPath(0, dag, selected_components)
    itVerts = om.MItMeshVertex(dag, selected_components)

def get_related_skin_cluster(geo):
    """ Get relate skin Cluster From {geo}
    """
    skin_node = mel.eval('findRelatedSkinCluster {}'.format(geo))
    return skin_node

def get_absolute_name(name):
    if ":" in name:
        return name.split(":")[-1]
    else:
        return name


def write_json(data, path):
    # Serializing json
    json_object = json.dumps(data, indent=4)

    # Writing to sample.json
    file = open(path, "w")
    file.write(json_object)

    file.close()


def get_weights(mesh):
    skin_cluster = get_relate_skin_node(mesh)
    bind_obj = mc.listConnections(skin_cluster, type="shape")[0]
    sel_mesh = om.MSelectionList()
    sel_mesh.add(bind_obj)
    dag_mesh = om.MDagPath()
    sel_mesh.getDagPath(0, dag_mesh)

    sel_skin = om.MSelectionList()
    sel_skin.add(skin_cluster)
    mobj_skin = om.MObject()
    sel_skin.getDependNode(0, mobj_skin)
    skin_fn = oma.MFnSkinCluster(mobj_skin)
    get_weights = om.MDoubleArray()
    empty_object = om.MObject()
    util = om.MScriptUtil()
    util.createFromInt(0)
    influ = util.asUintPtr()

    skin_fn.getWeights(dag_mesh, empty_object, get_weights, influ)
    influ_count = len(mc.skinCluster(skin_fn.name(), q=True, inf=True))

    weights = []
    list_indx = 0
    while list_indx < len(get_weights):
        slicing = get_weights[list_indx : (list_indx + influ_count)]
        weights.append(tuple(slicing))
        list_indx += influ_count

    weights = tuple(weights)
    return weights


def get_skin_data(mesh):
    weights = get_weights(mesh)
    skin_node = get_relate_skin_node(mesh)
    influs = mc.skinCluster(skin_node, inf=True, q=True)
    mesh = get_absolute_name(mesh)
    skin_method = mc.getAttr("{}.skinningMethod".format(skin_node))
    poly_count = mc.polyEvaluate(mesh, vertex=True)
    blend_weights = mc.getAttr(
        "{}.blendWeights[0:{}]".format(skin_node, poly_count - 1)
    )

    skin_dict = {
        "name": skin_node,
        "geometry": mesh,
        "polyCount": poly_count,
        "influences": influs,
        "skinMethod": skin_method,
        # "objectSet": set_name,
        "weights": weights,
        "blendWeights": blend_weights,
    }
    print(skin_dict)
    write_json(skin_dict,"C:\Users\Administrator\Desktop\{}_Skin.json".format(mesh))
    return skin_dict

def bind_skin(mesh,data):
    missing_jnts = []
    for jnt in data["influences"]:
        if not mc.objExists(jnt):
            print("{} dones not exist".format(jnt))
            mc.select(cl=True)
            mc.joint(n=jnt)
            missing_jnts.append(jnt)
    for jnt in missing_jnts:
        mc.createNode("joint",n=jnt)

    mc.skinCluster(data["influences"],mesh)

def set_skin_data(skin_node, data):
    """Apply the skin data back to a mesh, creating missing joints and setting weights."""
    inf_count = len(data["influences"])
    # Create missing joints if they don't exist
    # bind_skin(data)
    
    # Set the skin cluster attributes
    mc.rename(skin_node, data["name"])
    mc.setAttr("{}.skinningMethod".format(skin_node), data["skinMethod"])
    mc.setAttr("{}.blendWeights[0:{}]".format(skin_node, data["polyCount"] - 1), *data["blendWeights"])
    
    
    # Get related geometry
    bind_obj = mc.listConnections(skin_node, type="shape")[0]
    sel_mesh = om.MSelectionList()
    sel_mesh.add(bind_obj)
    dag_mesh = om.MDagPath()
    sel_mesh.getDagPath(0, dag_mesh)
    # Get the MObject for the skin cluster
    sel = om.MSelectionList()
    sel.add(skin_node)
    skin_cluster_obj = om.MObject()
    sel.getDependNode(0, skin_cluster_obj)

    # Create the MFnSkinCluster function set
    skin_fn = oma.MFnSkinCluster(skin_cluster_obj)

    # Create an empty MObject to represent the component (all vertices)
    empty_object = om.MObject()

    # Get the current weights
    old_weights = om.MDoubleArray()
    util = om.MScriptUtil()
    util.createFromInt(0)
    inf_count_ptr = util.asUintPtr()

    # Get the weights for the current skin cluster (if needed)
    skin_fn.getWeights(dag_mesh, empty_object, old_weights, inf_count_ptr)

    influence_indices = om.MIntArray()
    [influence_indices.append(ix) for ix in range(0, inf_count)]

    weights = om.MDoubleArray()
    for sublist in data["weights"]:
        for weight in sublist:
            weights.append(weight)
    print("Influence indices:",influence_indices)
    print("Geometry's dag path:",dag_mesh.fullPathName())
    fn_dep_node = om.MFnDependencyNode(skin_cluster_obj)
    print("Weights:",weights)
    print("Weights F:",data["weights"])
    print("Skin cluster name:", fn_dep_node.name())
    # Set the new weights
    # skin_fn.setWeights(
    #     dag_mesh,  # The geometry's dag path
    #     empty_object,  # Empty object representing all vertices
    #     influence_indices,  # Array of influence indices
    #     weights,  # Array of weights to set
    #     False,  # Whether to normalize or not (matches normalize=False)
    #     # old_weights  # Old weights as reference
    # )
    for ix, weight in enumerate(data["weights"]):
        w=0
        for iy,id_w in enumerate(weight):
            print(iy,id_w)
            mc.setAttr(
                "{}.weightList[{}].weights[{}]".format(skin_node, ix, iy),
                id_w,
                # size=len(weight)
            )
            w+=id_w
        print(w)

    for ix,id in enumerate(data[""]):
            mc.setAttr(
                "{sk}.weightList[{id}].weights[*]".format(
                    sk=skin_node, id=ix
                ),
                *weight[ix]
            )


def set_weight(skin_node, weight):
    pass


class SkinCluster(object):
    """
    skinCluster class for get and set data

    Args:
        skin_cluster_node(str)

    """

    def __init__(self, skin_cluster):
        self.bind_shape = mc.skinCluster(skin_cluster, query=True, geometry=True)[0]
        self.bind_obj = mc.listRelatives(self.bind_shape,p=True)[0]
        sel_mesh = om.MSelectionList()
        sel_mesh.add(self.bind_obj)
        self.dag_mesh = om.MDagPath()
        sel_mesh.getDagPath(0, self.dag_mesh)

        sel_skin = om.MSelectionList()
        sel_skin.add(skin_cluster)
        mobj_skin = om.MObject()
        sel_skin.getDependNode(0, mobj_skin)
        self.skin_fn = oma.MFnSkinCluster(mobj_skin)

        self.influ = mc.skinCluster(self.skin_fn.name(), q=True, inf=True)
        self.influ_count = len(
            mc.skinCluster(self.skin_fn.name(), q=True, inf=True)
        )

    def get_weights(self):
        get_weights = om.MDoubleArray()
        empty_object = om.MObject()
        util = om.MScriptUtil()
        util.createFromInt(0)
        influ = util.asUintPtr()

        self.skin_fn.getWeights(
            self.dag_mesh, empty_object, get_weights, influ
        )

        weights = []
        list_indx = 0
        while list_indx < len(get_weights):
            slicing = get_weights[list_indx : (list_indx + self.influ_count)]
            weights.append(tuple(slicing))
            list_indx += self.influ_count

        weights = tuple(weights)
        return weights

    def set_weights(self, weight, vtx_id, slicing=False):
        """
        set current skin weight of the "vtx_id" from "weight"
        "index_slicing" set to enable slicing ~ Ex.[0, 5] = [0:5]

        Args:
            weight (tuple): A tuple of weight from "get_weights" Method.
            vtx_id (list): List of the target vertex id.
            index_slicing (bolean) : enable index slicing

        """
        if slicing == False:
            ids = vtx_id
        else:
            ids = range(min(vtx_id), max(vtx_id) + 1)
        for i in ids:
            mc.setAttr(
                "{sk}.weightList[{id}].weights[*]".format(
                    sk=self.skin_fn.name(), id=i
                ),
                *weight[i]
            )

    def get_affected_vertex(self):
        weights = self.get_weights()
        data = {jnt: [] for jnt in self.influ}

        for vtx_id, vtx_weights in enumerate(weights):
            for weight, jnt  in zip(vtx_weights,self.influ):
                if weight > 0.0:
                    data[jnt].append(vtx_id)
        
        return data
    
    def get_affected_vertex_from_influence(self,jnt):      
        return self.get_affected_vertex()[jnt]
    
    def get_vtx_weight_cluster(self):

        def select_more(vtxs):
            edge = mc.polyListComponentConversion(vtxs, toEdge=True)
            vtx = mc.ls(mc.polyListComponentConversion(edge, tv=True), fl=True)
            return vtx

        data = self.get_affected_vertex()
        cluster_data = {}

        for jnt in self.influ:
            all_affected_vtx = ["{}.vtx[{}]".format(self.bind_obj,ix) for ix in data[jnt]]
            affected_vtx = all_affected_vtx
            tmp_list = []
            
            for ix,vtx in enumerate(affected_vtx):
                subed_vtx = vtx
                old_subed = []

                while old_subed != subed_vtx:
                    old_subed = subed_vtx
                    growth_vtx = select_more(subed_vtx)
                    subed_vtx = list(set(all_affected_vtx) & set(growth_vtx))
                
                # Remove
                for check_vtx in subed_vtx:
                    affected_vtx.remove(check_vtx)
                tmp_list.append(subed_vtx)

            if len(tmp_list) > 1:
                cluster_data[jnt] = tmp_list

        return cluster_data
