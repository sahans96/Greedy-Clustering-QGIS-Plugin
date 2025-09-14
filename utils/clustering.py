from qgis.core import QgsVectorFileWriter, QgsField, QgsProject
from PyQt5.QtCore import QVariant

def run_clustering(layer, hours_field, max_sum, output_path):
    """
    Perform greedy clustering on a QGIS layer.
    
    Parameters:
        layer (QgsVectorLayer): The input layer.
        hours_field (str): The name of the field containing numeric values (e.g. HOURS).
        max_sum (float): Maximum sum allowed per cluster.
        output_path (str): Path to save the output file.

    Returns:
        str: The output path where the clustered layer is saved.
    """
    # ✅ Collect features
    features = [f for f in layer.getFeatures()]
    if not features:
        raise ValueError("No features found in input layer.")

    if hours_field not in [field.name() for field in layer.fields()]:
        raise ValueError(f"Field '{hours_field}' not found in layer.")

    # Prepare clustering
    points = {}  # feature_id: (x, y)
    values = {}  # feature_id: value
    feature_map = {}  # feature_id: feature
    for f in features:
        geom = f.geometry().asPoint()
        points[f.id()] = (geom.x(), geom.y())
        try:
            values[f.id()] = float(f[hours_field])
        except Exception:
            values[f.id()] = 0.0
        feature_map[f.id()] = f

    # Add Cluster_ID field if missing
    if "Cluster_ID" not in [field.name() for field in layer.fields()]:
        layer.dataProvider().addAttributes([QgsField("Cluster_ID", QVariant.Int)])
        layer.updateFields()

    unassigned = set(points.keys())
    clusters = {}  # feature_id: cluster_id
    cluster_id = 1

    while unassigned:
        center_id = next(iter(unassigned))
        cluster_points = [center_id]
        current_sum = values[center_id]
        unassigned.remove(center_id)

        while True:
            nearest_point = None
            min_dist = float("inf")
            for fid in unassigned:
                for clustered_id in cluster_points:
                    d = ((points[fid][0] - points[clustered_id][0]) ** 2 + (points[fid][1] - points[clustered_id][1]) ** 2) ** 0.5
                    if d < min_dist:
                        min_dist = d
                        nearest_point = fid
            if nearest_point is None or (current_sum + values[nearest_point]) > max_sum:
                break
            cluster_points.append(nearest_point)
            current_sum += values[nearest_point]
            unassigned.remove(nearest_point)

        for fid in cluster_points:
            clusters[fid] = cluster_id
        cluster_id += 1

    # Prepare output: pass cluster assignments and features
    clustered_features = [(feature_map[fid], clusters.get(fid, None)) for fid in feature_map]

    # ✅ Save to output layer
    save_clustered_layer(layer, clustered_features, output_path)

    # ✅ Automatically add new layer to QGIS project
    add_layer_to_project(output_path)

    return output_path


def save_clustered_layer(source_layer, features, output_path):
    """Save clustered features to a new layer at output_path."""
    fields = source_layer.fields()
    # Add Cluster_ID field if missing
    if "Cluster_ID" not in [f.name() for f in fields]:
        fields.append(QgsField("Cluster_ID", QVariant.Int))

    writer = QgsVectorFileWriter(
        output_path,
        "UTF-8",
        fields,
        source_layer.wkbType(),
        source_layer.sourceCrs(),
        "GPKG" if output_path.lower().endswith(".gpkg") else "ESRI Shapefile"
    )

    cluster_id_idx = fields.indexFromName("Cluster_ID")
    for f, cluster_id in features:
        out_feat = f.__class__()
        out_feat.setGeometry(f.geometry())
        attrs = list(f.attributes())
        if len(attrs) < len(fields):
            attrs += [None] * (len(fields) - len(attrs))
        attrs[cluster_id_idx] = cluster_id
        out_feat.setAttributes(attrs)
        writer.addFeature(out_feat)

    del writer  # Finalize write process


def find_nearest(current_feature, unassigned):
    """Find nearest unassigned feature based on geometry distance."""
    current_geom = current_feature.geometry()
    nearest_feature = None
    min_distance = float("inf")

    for feature in unassigned.values():
        distance = current_geom.distance(feature.geometry())
        if distance < min_distance:
            min_distance = distance
            nearest_feature = feature
    return nearest_feature


def add_layer_to_project(output_path):
    """Load the newly created layer into the current QGIS project."""
    from qgis.core import QgsVectorLayer
    layer = QgsVectorLayer(output_path, "Clustered_Output", "ogr")
    if layer.isValid():
        QgsProject.instance().addMapLayer(layer)
    else:
        print(f"⚠️ Failed to load layer from {output_path}")
