from modules.schema_registry import DIMENSIONS
from modules.metric_registry import HR_METRICS
from modules.filter_engine import apply_filters

def compute_metric(df, metric, dimension, filters=None):
    metric_cfg = HR_METRICS.get(metric)
    if not metric_cfg:
        return None

    if filters:
        df = apply_filters(df, filters)

    if dimension:
        col = DIMENSIONS.get(dimension)
        if col not in df.columns:
            return None
        grp = df.groupby(col)
    else:
        grp = df

    if metric_cfg["type"] == "count":
        return grp["Employee_ID"].count()

    if metric_cfg["type"] == "avg":
        return grp[metric_cfg["column"]].mean()

    if metric_cfg["type"] == "ratio":
        df["_flag"] = (df["Status"] == metric_cfg["positive"]).astype(int)
        return grp["_flag"].mean() * 100

    return None
