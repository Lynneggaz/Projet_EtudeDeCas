

import plotly.express as px
import plotly.graph_objects as go
import os

def create_line_chart(df, x_col, y_col, color_col=None, title=''):
    fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title)
    return fig

def create_bar_chart(df, x_col, y_col, color_col=None, title=''):
    fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
    return fig

def create_pie_chart(df, values_col, names_col, title=''):
    fig = px.pie(df, values=values_col, names=names_col, title=title)
    return fig

def export_fig(fig, format='png', filename='export'):
    """
    Exporte une figure Plotly vers un fichier et renvoie le chemin du fichier.
    Nécessite le moteur kaleido pour PNG/PDF.
    """
    if fig is None:
        raise ValueError("Aucune figure à exporter.")

    format = format.lower()
    os.makedirs("exports", exist_ok=True)
    output_path = os.path.join("exports", f"{filename}.{format}")

    try:
        fig.write_image(output_path, format=format, engine="kaleido")
    except Exception as exc:
        raise RuntimeError(f"Echec de l'export ({exc}). Vérifiez que 'kaleido' est installé.")

    return output_path
