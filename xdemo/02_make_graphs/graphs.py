#!/usr/bin/python3

import lots_plots as lp
db = "a.sqlite"

g = lp.lots_plots()
# g.default_terminal = 'png'
g.default_terminal = 'epslatex color size 11cm,6.5cm font "" 10'
# g.default_terminal = 'pdf'
# g.default_terminal = 'eps'

def mnk_vs_t_over_mnk():
    """ a simplest example:
          x-axis = M*N*K
          y-axis = T/(M*N*K)
    """
    g.graphs((db, r"""select M*N*K,avg((T+0.0)/(M*N*K)) from a group by M,N,K"""),
             graph_title="MNK vs T/(MNK)",
             output="graphs/mnk_vs_t_over_mnk",
             plot_with="points",
             plot_title="results",
             xlabel="MNK",
             ylabel="T/(MNK)",
    )


def m_vs_t_with_nk_plots():
    g.graphs((db, r"""select M,avg(T) from a where N={N} and K={K} group by M"""),
             graph_title="MNK vs T/(MNK)",
             output="graphs/m_vs_t_with_nk_plots",
             xlabel="M",
             ylabel="T",
             plot_title="N={N}, K={K}",
             plot_with="linespoints",
             N=g.do_sql(db, "select distinct N from a order by N"),
             K=g.do_sql(db, "select distinct K from a order by K"),
    )

def m_vs_t_with_n_plots_k_graphs():
    g.graphs((db, r"""select M,avg(T) from a where N={N} and K={K} group by M"""),
             graph_vars=["K"],
             graph_title="M vs T with K={K}",
             output="graphs/m_vs_t_with_n_plots_k_graphs_{K}",
             plot_title="N={N}, K={K}",
             plot_with="linespoints",
             xlabel="M",
             ylabel="T",
             N=g.do_sql(db, "select distinct N from a order by N"),
             K=g.do_sql(db, "select distinct K from a order by K"),
    )


mnk_vs_t_over_mnk()
m_vs_t_with_nk_plots()
m_vs_t_with_n_plots_k_graphs()

