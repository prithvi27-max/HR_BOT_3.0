import plotly.express as px
import pandas as pd


# ==================================================
# TABLE RENDERING
# ==================================================
def render_table(data):
    """
    Converts Series / scalar to DataFrame for display
    """
    if isinstance(data, (int, float)):
        return pd.DataFrame({"Value": [data]})

    if isinstance(data, pd.Series):
        return data.reset_index()

    return data


# ==================================================
# CHART RENDERING
# ==================================================
def build_chart(data, chart_type):
    """
    Builds chart ONLY when explicitly requested
    """
    if data is None or len(data) == 0:
        return None

    df_plot = data.reset_index()
    x_col, y_col = df_plot.columns

    if chart_type == "LINE":
        return px.line(df_plot, x=x_col, y=y_col, markers=True)

    if chart_type == "PIE":
        return px.pie(df_plot, names=x_col, values=y_col)

    # Default BAR
    return px.bar(df_plot, x=x_col, y=y_col, text_auto=True)