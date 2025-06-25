import pulp as pl

def pLinear(nvar, f_obj, rest):
    model = pl.LpProblem("Maximize", pl.LpMaximize)
    vars = [pl.LpVariable(chr(97+i), lowBound=0) for i in range(nvar)]
    model += sum(f_obj[i]*vars[i] for i in range(nvar))
    for r in rest:
        lhs = sum(r[j]*vars[j] for j in range(nvar))
        if r[-2] == "<=": model += lhs <= r[-1]
        else: model += lhs >= r[-1]
    model.solve()
    p_otimo = [v.varValue for v in vars]
    lucro = pl.value(model.objective)
    ps = [model.constraints[name].pi for name in model.constraints]
    return [p_otimo, lucro, ps]

def verify_viability(rest):
    infeasible = []
    for idx, restr in enumerate(rest, start=1):
        soma = sum(restr[:-2])
        if soma > restr[-1]:
            infeasible.append(idx)
    return (len(infeasible)==0, infeasible)