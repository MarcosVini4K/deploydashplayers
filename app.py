import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd

# Lê a base
df = pd.read_csv("jogadores.csv", sep=";")
df["P"] = df["P"].astype(str).str.replace(",", ".").astype(float)
df["NomeCartinha"] = df["Player"] + " " + df["Season"] + ".png"
df = df.drop(columns=["ID", "Nacionalidade"])

# Inicializa o app
app = dash.Dash(__name__, external_stylesheets=['/assets/style.css'], meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}])
server = app.server

app.layout = html.Div([ 
    html.Div(html.H1("Extreme Stats Football", style={
        "textAlign": "center",
        "color": "white",
        "fontSize": "32px",
        "marginTop": "20px",
        "fontWeight": "bold",
        "textShadow": "2px 2px 4px rgba(0, 0, 0, 0.7)"
    }), style={ 
        "position": "fixed", 
        "top": "0", 
        "left": "0", 
        "width": "100%", 
        "height": "60px", 
        "background": "linear-gradient(90deg, #2c003e, #5e008c)", 
        "borderBottom": "4px solid gold", 
        "zIndex": "10" 
    }),

    html.Div(id="logo-liga-container", style={ 
        "position": "absolute", 
        "top": "10px", 
        "right": "20px", 
        "zIndex": "1000" 
    }),

    html.Div(id="cartinha-container", style={ 
        "position": "absolute", 
        "top": "85px", 
        "left": "20px", 
        "zIndex": "1" 
    }),

    html.Div([ 
        html.Div([ 
            dcc.Input( 
                id="filtro-jogador", 
                type="text", 
                placeholder="Buscar jogador", 
                debounce=True, 
                style={"width": "170px", "padding": "6px", "height": "38px", "right": "85px"} 
            ),
            dcc.Input( 
                id="filtro-time", 
                type="text", 
                placeholder="Buscar time", 
                debounce=True, 
                style={"width": "170px", "padding": "6px", "height": "38px", "right": "85px"} 
            ),
            dcc.Dropdown( 
                id="filtro-temporada", 
                placeholder="Escolha a temporada", 
                multi=True, 
                style={"width": "200px", "minHeight": "38px"} 
            ),  
            dcc.Dropdown( 
                id="filtro-era", 
                options=[{"label": a, "value": a} for a in sorted(df["Age"].unique())], 
                value=sorted(df["Age"].unique()), 
                placeholder="Escolha a Era", 
                multi=True, 
                style={"width": "180px", "minHeight": "38px"} 
            ), 
           
            dcc.Dropdown( 
                id="filtro-liga", 
                options=[{"label": l, "value": l} for l in sorted(df["League"].unique())], 
                value=sorted(df["League"].unique()), 
                placeholder="Escolha a liga", 
                multi=True, 
                style={"width": "200px"} 
            ) 
        ], style={ 
            "display": "flex", 
            "gap": "10px", 
            "marginTop": "260px", 
            "marginBottom": "20px", 
            "justifyContent": "center", 
            "marginLeft": "-105px" 
        }, className="filtro-container"), 

        html.Div([ 
            dash_table.DataTable( 
                id="tabela-jogadores", 
                columns=[{"name": "Rank", "id": "Rank"}] + [{"name": col, "id": col} for col in df.columns if col != "NomeCartinha"], 
                data=df.sort_values("P", ascending=False).reset_index(drop=True).assign( 
                    Rank=lambda d: d["P"].rank(method="min", ascending=False).astype(int) 
                ).to_dict("records"), 
                sort_action="native", 
                row_selectable="single", 
                selected_rows=[0], 
                page_size=10, 
                style_table={"overflowX": "auto", "width": "100%", "maxHeight": "400px", "marginTop": "-10px"}, 
                style_cell={"textAlign": "left", "fontSize": "12px", "padding": "2px", "width": "70px", "height": "5px"}, 
                style_data={"whiteSpace": "normal", "height": "auto"}, 
                style_header={ 
                    "background": "linear-gradient(90deg, #2c003e, #5e008c)", 
                    "borderBottom": "4px solid gold", 
                    'color': 'white', 
                    'fontWeight': 'bold' 
                } 
            ) 
        ], style={"width": "100%", "display": "flex", "justifyContent": "center"}) 
    ]) 
], style={"position": "relative", "height": "105vh", "overflow": "hidden"}) 

# Atualiza opções do filtro de temporada com base na era selecionada
@app.callback(
    Output("filtro-temporada", "options"),
    Input("filtro-era", "value")
)
def atualizar_temporadas_com_base_na_era(era_selecionada):
    df_filtrado = df[df["Age"].isin(era_selecionada)]
    temporadas = sorted(df_filtrado["Season"].unique())
    return [{"label": t, "value": t} for t in temporadas]

# Atualiza tabela com base nos filtros e rank dinâmico
@app.callback( 
    Output("tabela-jogadores", "data"), 
    Input("filtro-temporada", "value"), 
    Input("filtro-liga", "value"), 
    Input("filtro-jogador", "value"), 
    Input("filtro-time", "value"),
    Input("filtro-era", "value"), 
    Input("tabela-jogadores", "sort_by") 
) 
def atualizar_tabela(temporadas, ligas, nome_jogador, nome_time, eras, sort_by): 
    df_filtrado = df.copy() 

    if eras: 
        df_filtrado = df_filtrado[df_filtrado["Age"].isin(eras)]
    if temporadas: 
        df_filtrado = df_filtrado[df_filtrado["Season"].isin(temporadas)] 
    if ligas: 
        df_filtrado = df_filtrado[df_filtrado["League"].isin(ligas)] 
    if nome_jogador: 
        df_filtrado = df_filtrado[df_filtrado["Player"].str.lower().str.contains(nome_jogador.lower())] 
    if nome_time: 
        df_filtrado = df_filtrado[df_filtrado["Team"].str.lower().str.contains(nome_time.lower())] 

    # Rank dinâmico
    if sort_by and len(sort_by) > 0: 
        coluna_ordem = sort_by[0]['column_id'] 
        ordem_crescente = sort_by[0]['direction'] == 'asc' 
        if coluna_ordem in df_filtrado.columns: 
            df_filtrado = df_filtrado.sort_values(by=coluna_ordem, ascending=ordem_crescente).reset_index(drop=True) 
            df_filtrado["Rank"] = df_filtrado[coluna_ordem].rank(method="min", ascending=ordem_crescente).astype(int) 
        else: 
            df_filtrado["Rank"] = None 
    else: 
        df_filtrado = df_filtrado.sort_values("P", ascending=False).reset_index(drop=True) 
        df_filtrado["Rank"] = df_filtrado["P"].rank(method="min", ascending=False).astype(int)

    return df_filtrado.to_dict("records")

# Atualiza a cartinha exibida com base na seleção
@app.callback( 
    Output("cartinha-container", "children"), 
    Input("tabela-jogadores", "derived_virtual_data"), 
    Input("tabela-jogadores", "derived_virtual_selected_rows") 
) 
def atualizar_cartinha(dados, linhas_selecionadas): 
    if dados is None or linhas_selecionadas is None or len(linhas_selecionadas) == 0: 
        return html.P("Nenhum jogador selecionado") 

    jogador = dados[linhas_selecionadas[0]] 
    nome_arquivo = jogador["Player"] + " " + jogador["Season"] + ".png" 
    caminho = f"/assets/cartinhas/{nome_arquivo}" 

    return html.Img( 
        src=caminho, 
        style={ 
            "height": "220px", 
            "border": "4px solid gold", 
            "border-radius": "20px" 
        } 
    ) 

# Atualiza logo da liga
@app.callback( 
    Output("logo-liga-container", "children"), 
    Input("filtro-liga", "value") 
) 
def atualizar_logo_liga(ligas): 
    if not ligas: 
        return html.Div() 

    imagens = [] 
    for liga in ligas: 
        caminho_logo = f"/assets/logos_ligas/{liga}.png" 
        img = html.Img(src=caminho_logo, style={ 
            "height": "160px", 
            "margin": "0 10px", 
            "borderTop": "4px solid gold",  # Borda superior dourada 
            "borderLeft": "4px solid gold", # Borda esquerda dourada 
            "borderRight": "4px solid gold", # Borda direita dourada 
            "borderBottom": "4px solid gold" ,
            "borderRadius": "10px",  # Arredondamento nas bordas 
        }) 
        imagens.append(img) 

    return html.Div(imagens, style={"display": "flex", "justify-content": "flex-end"}) 

if __name__ == "__main__": 
    app.run(debug=True)
