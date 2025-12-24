import sympy as sp
import numpy as np


# Creates a nomograph of the form f_u + f_v = f_w
def build_parallel(f_u, f_v, f_w, u_vals, v_vals, w_vals, h_1, h_2, w):
    # Calculate the scales
    m_1 = h_1 / (max(u_vals) - min(u_vals))
    m_2 = h_2 / (max(v_vals) - min(v_vals))
    m_3 = m_1 * m_2 / (m_1 + m_2)

    # Calculate the distances of the scales
    a_b = m_1 / m_2
    b = w / (1 + a_b)
    a = a_b * b

    # Caclulate the tick placements
    # f_u_vals = [m_1 * f_u(u) for u in u_vals]
    # f_v_vals = [m_2 * f_v(v) for v in v_vals]
    # f_w_vals = [m_3 * f_w(w) for w in w_vals]
    f_u_vals = m_1 * f_u(u_vals)
    f_v_vals = m_2 * f_v(v_vals)
    f_w_vals = m_3 * f_w(w_vals)

    # Shift them all to place the topmost at 0
    shift_val = min([min(f_u_vals), min(f_v_vals), min(f_w_vals))
    # f_u_vals = [i-shift_val for i in f_u_vals]
    # f_v_vals = [i-shift_val for i in f_v_vals]
    # f_w_vals = [i-shift_val for i in f_w_vals]
    f_u_vals -= shift_val
    f_v_vals -= shift_val
    f_w_vals -= shift_val

    return ((0, a, w), (f_u_vals, f_w_vals, f_v_vals))

possible_types = ["(p)arallel", '(z) chart', 'p(r)oportional', '(c)oncurrent', '(d)eterminant']

if __name__ == "__main__":
    # while True:
    #     type = input(f"What kind of nomograph do you want? [{', '.join(possible_types)}]")
    #
    #     if type == 'p':
    #         pass
    #
    #     else:
    #         print("Not a valid form, try again")
