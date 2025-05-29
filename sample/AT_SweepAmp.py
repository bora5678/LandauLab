import numpy as np
from scipy.optimize import fsolve

def AT_SweepAmp(f, Var) -> tuple:
    """ this function calculates deltaU"""
    kappa0 = 0.09140777495737493
    k1 = -0.000257302856496472
    k2 = 0.0003476142363452517
    lambda1 = 9.253057865658614e-6
    lambda2 = -0.000012962566637857543
    kappac = 0.0006030296533052216
    U0 = -7.55872128877901

    rho0 = 2800
    L0 = 49e-6
    b0 = 250e-9
    d0 = 100e-9
    meffinit = rho0 * L0 * b0 * d0 / 2

    def F1(U):
        return np.sqrt((kappa0 + k1 * (U - U0) + lambda1 * (U - U0) ** 2 + kappac) / meffinit)

    def F2(U):
        return np.sqrt((kappa0 + k2 * (U - U0) + lambda2 * (U - U0) ** 2 + kappac) / meffinit)

    def F3(U):
        return np.sqrt(kappac ** 2 / (meffinit ** 2 * F1(U) * F2(U)))

    def equation(U):
        term1 = F1(U) ** 2 + F2(U) ** 2
        term2 = np.sqrt((F1(U) ** 2 - F2(U) ** 2) ** 2 + 4 * F3(U) ** 2 * F1(U) * F2(U))
        return f ** 2 - np.abs(0.5 * (term1 - term2))

    # Solve for U, starting from Var as initial guess
    X_solution = fsolve(equation, Var)
    deltaU = np.abs(X_solution) - np.abs(U0)
    X = X_solution

    return X, deltaU

# Example usage:
# X, deltaU = AT_SweepAmp(1e6, 0)