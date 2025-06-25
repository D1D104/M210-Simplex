import streamlit as st
import pandas as pd
from programacao_linear import pLinear
import copy

st.set_page_config(
    page_title="Calculadora Simplex",
    layout="wide"
)

st.title("🔷 Calculadora Simplex")

if "previous_result" not in st.session_state:
    st.session_state.previous_result = None
if "previous_input" not in st.session_state:
    st.session_state.previous_input = {}


def validate_decimal(value):
    return round(value, 2) if value is not None else value

# Entrada de dados
num_cols = st.columns(2)
with num_cols[0]:
    num_variaveis = st.number_input("Número de variáveis", min_value=1, step=1, key="num_variaveis")
with num_cols[1]:
    num_restricoes = st.number_input("Número de restrições", min_value=1, step=1, key="num_restricoes")

# Coeficientes da F.O.
st.subheader("Coeficientes da Função Objetivo (FO)")
fo_data = []
for i in range(int(num_variaveis)):
    coef = validate_decimal(st.number_input(f"Coeficiente X{i+1}", key=f"coef_fo_{i}"))
    fo_data.append((f"X{i+1}", coef))

st.table(pd.DataFrame(fo_data, columns=["Variável", "Coeficiente"]))

# Coeficientes das restrições
st.subheader("Coeficientes das Restrições")
rest_columns = [f"X{j+1}" for j in range(int(num_variaveis))] + ["Sinal", "Limite"]
restricoes = []
for i in range(int(num_restricoes)):
    st.markdown(f"**Restrição {i+1}**")
    row = []
    for j in range(int(num_variaveis)):
        coef = validate_decimal(st.number_input(f"Coef X{j+1} (R{i+1})", key=f"coef_{i}_{j}"))
        row.append(coef)
    sinal = st.selectbox(f"Sinal (R{i+1})", ("<=", ">="), key=f"sinal_{i}")
    limite = validate_decimal(st.number_input(f"Limite (R{i+1})", key=f"limite_{i}"))
    row.extend([sinal, limite])
    restricoes.append(row)

# Exibição
st.subheader("Função Objetivo")
fo_equacao = " + ".join([f"{coef:.4f}·{var}" for var, coef in fo_data])
st.write(f"Max Z = {fo_equacao}")

st.subheader("Restrições")
df_restr = pd.DataFrame(restricoes, columns=rest_columns)
st.table(df_restr)

# Solução atual
try:
    result = pLinear(int(num_variaveis), [coef for _, coef in fo_data], restricoes)
    st.session_state.previous_result = result
    st.session_state.previous_input = {
        "restricoes": copy.deepcopy(restricoes),
        "psombra": result[2]
    }

    st.subheader("Solução Ótima")
    df_sol = pd.DataFrame([(f"X{i+1}", val) for i, val in enumerate(result[0])], columns=["Variável", "Valor Ótimo"])
    st.table(df_sol)
    st.write(f"**Lucro Ótimo (Z):** {result[1]:.4f}")

    st.subheader("Preços Sombra")
    df_ps = pd.DataFrame([(f"R{i+1}", ps) for i, ps in enumerate(result[2])], columns=["Restrição", "Preço Sombra"])
    st.table(df_ps)

except Exception as e:
    st.error(f"Erro ao calcular solução inicial: {e}")

# Alterações
st.subheader("Propor Alterações nas Restrições")
alteracoes = []
for i in range(len(restricoes)):
    alter = validate_decimal(st.number_input(f"Alteração no Limite R{i+1}", key=f"alt_{i}"))
    alteracoes.append(alter)
    restricoes[i][-1] += alter

# Botão de verificação de viabilidade
def verificar_viabilidade_avancada():
    try:
        novo_resultado = pLinear(int(num_variaveis), [coef for _, coef in fo_data], restricoes)
        psombra_antigo = st.session_state.previous_input["psombra"]
        psombra_novo = novo_resultado[2]
        
        if all(abs(psombra_novo[i] - psombra_antigo[i]) < 1e-4 for i in range(len(psombra_novo))):
            st.success("As alterações propostas são viáveis. Base ótima mantida.")
            st.write(f"Novo Lucro Ótimo (Z): {novo_resultado[1]:.4f}")
        else:
            st.error("As alterações propostas NÃO são viáveis. Os preços sombra foram alterados.")

    except Exception as e:
        st.error(f"Erro ao verificar viabilidade: {e}")

if st.button("Verificar Viabilidade"):
    verificar_viabilidade_avancada()
