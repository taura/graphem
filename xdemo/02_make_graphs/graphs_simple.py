#!/usr/bin/python3

import lots_plots as lp
db = "a.sqlite"

g = lp.lots_plots()

def mnk_vs_t_over_mnk():
    """ a simplest example:
          x-axis = M*N*K
          y-axis = T/(M*N*K)
    """
    g.graphs((db, r"""select M*N*K,avg((T+0.0)/(M*N*K)) from a group by M,N,K"""),
    )


def m_vs_t_with_nk_plots():
    g.graphs((db, r"""select M,avg(T) from a where N={N} and K={K} group by M"""),
             N=g.do_sql(db, "select distinct N from a order by N"),
             K=g.do_sql(db, "select distinct K from a order by K"),
    )

def m_vs_t_with_n_plots_k_graphs():
    g.graphs((db, r"""select M,avg(T) from a where N={N} and K={K} group by M"""),
             graph_vars=["K"],
             N=g.do_sql(db, "select distinct N from a order by N"),
             K=g.do_sql(db, "select distinct K from a order by K"),
    )


mnk_vs_t_over_mnk()
m_vs_t_with_nk_plots()
m_vs_t_with_n_plots_k_graphs()

