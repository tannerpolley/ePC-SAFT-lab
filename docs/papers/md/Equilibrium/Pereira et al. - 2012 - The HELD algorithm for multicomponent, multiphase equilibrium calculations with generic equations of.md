\title{
The HELD algorithm for multicomponent, multiphase equilibrium calculations with generic equations of state
}

\author{
Frances E. Pereira, George Jackson, Amparo Galindo, Claire S. Adjiman* \\ Department of Chemical Engineering, Centre for Process Systems Engineering, Imperial College London, London SW7 2AZ, United Kingdom
}

\section*{ARTICLE INFO}

\section*{Article history:}

Received 29 November 2010
Received in revised form 13 July 2011
Accepted 15 July 2011
Available online 22 July 2011

\section*{Keywords:}

Phase equilibrium
Phase stability
Helmholtz free energy
Global optimisation
Equations of state
Statistical associating fluid theory (SAFT)

\begin{abstract}
The HELD (Helmholtz free Energy Lagrangian Dual) algorithm is proposed to solve the isothermal, isobaric phase equilibrium problem ( $P, T$ flash). The flash is posed as a minimisation of the Helmholtz free energy in the volume-composition space, reformulated through duality theory. The proposed solution strategy consists of: an initialisation stage, containing a stability test; a phase identification stage, in which linear and nonconvex optimisation problems are solved alternatively; and an acceleration and convergence stage. The stability test is solved with a tunneling algorithm and the nonconvex part of the second stage with a multistart approach. Examples are presented for three equations of state, SRK, SAFTHS and SAFT-VR. Non-ideal mixtures of up to fifteen components are examined; they exhibit features such as azeotropy, liquid-liquid, and liquid-liquid-liquid equilibria. The HELD algorithm is found to be reliable over a variety of challenging phase behaviour, converging to the best known solution in all of the calculations undertaken.
\end{abstract}
© 2011 Elsevier Ltd. All rights reserved.

\section*{1. Introduction}

The description of phase equilibrium (PE) is a challenging problem, commonly encountered in molecular and process modelling applications. For example, an ability to carry out robust multicomponent, multiphase equilibrium calculations is essential for the design and modelling of many separation processes, and parameters for thermophysical property models are frequently obtained through regression of phase equilibrium data. The solution of PE corresponds to a unique, stable thermodynamic state. This solution is characterised by a phase configuration consisting of a number of stable phases, with discrete compositions and volumes. It occurs at the global minimum of the appropriate state function for the thermodynamic ensemble of interest, such as the Gibbs free energy in the constant mole number, pressure, temperature $(\underline{n}, P, T)$ ensemble. These thermodynamic functions are nonconvex and consequently, there can be local minima, which correspond to states of metastable equilibrium. The physical properties of these metastable solutions do not necessarily bear any relation to the stable equilibrium state; for example, they may contain a different number of phases. Hence, failure to locate the global solution may lead to a completely incorrect prediction of the system phase behaviour.

\footnotetext{
* Corresponding author.

E-mail address: c.adjiman@imperial.ac.uk (C.S. Adjiman).
}

A widely studied example of PE is the isothermal-isobaric ( $P, T$ ) flash. The equilibrium state in this case lies at the global minimum of the system's Gibbs free energy. Much research effort has been devoted to this problem, and numerous solution schemes in the literature follow the framework proposed in the seminal work of Michelsen (Michelsen, 1982a, 1982b; Michelsen \& Mollerup, 2007) for fluid phase equilibria. In this approach, two problems, a stability test and a flash, are solved alternately. A phase configuration is postulated, for example two phases at given compositions, and its stability is tested. The stability test is carried out through the minimisation of the tangent plane distance function, the distance between the Gibbs free energy surface and a plane tangential to the phase being tested for stability, defined over the whole composition domain (Baker, Pierce, \& Luks, 1982; Michelsen, 1982a). When a state is stable, the global minimum of the function is at zero. If the postulated configuration is stable then the equilibrium solution is given by all points that are common to the Gibbs free energy surface and the tangent plane. If not, a flash calculation is used to find a new candidate configuration, which may involve altering the initial guesses for the compositions and volumes of the phases, or the number of phases postulated. Nagarajan, Cullick, and Griewank (1991a, 1991b) have proposed an alternative formulation of the alternating stability test/flash approach, where all calculations are based on the Helmholtz free energy density, with component densities as independent variables. They suggest that reliability is improved by the use of the Helmholtz free energy density, which is a smooth function, since the cusps associated with the transition between liquid and vapour states that appear on the

Gibbs free energy surface are not present in the Helmholtz free energy formulation. However, the use of the Helmholtz free energy density adds an extra dimension to the tangent plane stability problem, and therefore can be expected to increase computational demands. Nevertheless, when using an equation of state (EOS), this approach may bring further benefits as the need to solve for the pressure during the evaluation of the free energy is removed.

The importance of locating the global minimum of the free energy in the PE problem is a motivation for the use of global optimisation in the stability test, and in the PE problem in general. A wide variety of global optimisation approaches have been applied to the problem. The performance of various stochastic global optimisation algorithms has been documented and compared. These include the simulated annealing algorithm (Henderson, de Oliveira Jr., Amaral Souto, \& Pitanga Marques, 2001), a combined simulated annealing and genetic algorithm (Rangaiah, 2001), tabu search (Teh \& Rangaiah, 2002), a combination of simulated annealing and stochastic differential equations (Bonilla-Petriciolet, VázquezRomán, Iglesias-Silva, \& Hall, 2006), tabu search and differential evolution (Srinivas \& Rangaiah, 2007a, 2007b), the tunneling algorithm (Nichita \& Gomez, 2009; Nichita, Gomez, \& Luna, 2002a, 2002b; Nichita, de Los Angeles Duran Valencia, \& Gomez, 2006; Nichita, García-Sánchez, \& Gómez, 2008), the random tunneling algorithm (Srinivas \& Rangaiah, 2006), and the particle swarm method (Rahman, Das, Mankar, \& Kulkarni, 2009).

Several deterministic methods have also been used successfully in this field. These include guaranteed approaches based on decomposition (Harding \& Floudas, 2000a, 2000b; McDonald \& Floudas, 1995a, 1995b, 1997), and interval analysis (Hua, Brennecke, \& Stadtherr, 1996; McKinnon \& Mongeau, 1996, 1998; Xu, Brennecke, \& Stadtherr, 2002) that converge to the global optimum, to within an arbitrary accuracy $\varepsilon$, in finite time. Additionally, there are deterministic algorithms that can be guaranteed to explore the entire solution space if allowed to run for an infinite length of time, and therefore can be guaranteed to converge to the global solution. However, when such an algorithm is terminated after a finite time, there can be no guarantee as to how close the best known solution is to the global solution. These algorithms include the DIRECT algorithm (Jones, Perttunen, \& Stuckman, 1993; Saber \& Shaw, 2008) and terrain methodologies (Lucia, DiMaggio, \& Depa, 2004; Lucia, DiMaggio, Bellows, \& Octavio, 2005). In general, a finite-time guarantee of convergence to the global minimum increases the computational requirements, since the algorithm must rigorously search the entire solution space. The best performing stochastic and infinite-time deterministic global algorithms have similar performance.

There are alternatives to global optimisation methods that exploit physical and mathematical insights into the problem (e.g., Lucia, et al., 2004; Lucia, Padmanabhan, \& Venkataraman, 2000; Iglesias-Silva, Bonilla-Petriciolet, Eubank, Holste, \& Hall, 2003). These are less computationally intensive than their global counterparts, but they lack a mathematical guarantee on the resulting solutions.

Mitsos and Barton (2007) have taken a novel approach to the problem and recently proved that any stable phase can be identified by solving a Lagrangian dual problem, which is related to isothermal, isobaric phase equilibrium. The solution of this dual problem is a supporting hyperplane of the Gibbs free energy surface, and indeed, corresponds to the well-known tangent plane joining all equilibrium phases. The formulation may be solved as a bilevel program in which the outer problem is formulated in the space of chemical potentials, and the inner problem is similar to a stability test. This formulation has interesting characteristics, which differ from an alternating stability/flash approach. In particular, it is not necessary to know a priori the number of phases $n p$ to characterise fully one (arbitrary) stable phase. The dimensionality of the
subproblem thus formulated contains only $n c-1$ variables, where $n c$ is the number of components in the system, as opposed to the $n p \times(n c-1)$ variables required when $n p$ is involved in the formulation. This reduction in dimensionality is particularly valuable when using global optimisation algorithms.

We have recently shown that this interpretation of the $P, T$ flash may be translated to the Helmholtz free energy-composition-volume space $A(\underline{x}, V)$ (Pereira, Jackson, Galindo, \& Adjiman, 2010), removing the implicit requirement that the thermodynamic functions be evaluated at a specified pressure. As discussed by Nagarajan et al. (1991a), it can be shown that the solution of the problem in the $A(\underline{x}, V)$ space nevertheless meets the conditions of mechanical equilibrium (i.e., the equality of the pressure in all phases). Such an approach has the potential to improve computational performance when equations of state that are higher-than-cubic functions in volume are used, such as SAFT (statistical associating fluid theory) (Chapman, Gubbins, Jackson, \& Radosz, 1989, 1990). In our previous work (Pereira et al., 2010), a volume-composition formulation, based on the method of Mitsos and Barton (2007), was developed and tested with a simple prototypical form of the SAFT EOS. A deterministic global optimisation algorithm was implemented, guaranteeing the identification of the stable equilibrium solution. The algorithm was applied successfully to challenging cases such as polymer-solvent mixtures. It is currently being extended to more complex forms of the EOS.

Despite these developments in deterministic global optimisation, there is also a need to consider phase equilibrium and stability algorithms that offer reliable performance at a reduced computational cost, by removing the guarantee of $\varepsilon$-convergence in finite time. One reason for this is that for highly nonlinear functions, such as the SAFT EOS, the performance of deterministic global optimisation algorithms (Floudas, 2000; Floudas \& Gounaris, 2009; Tawarmalani \& Sahinidis, 2002) is heavily influenced by the mathematical form of the problem. An experienced user of global optimisation will often be able to decrease computational cost by reformulating the problem, but the required level of expertise makes it more challenging to apply such approaches to new equations of state. This is particularly relevant in the case of the SAFT EOS, where different versions are available and new developments are the subject of ongoing research (McCabe \& Galindo, 2010; Müller \& Gubbins, 2001; Wei \& Sadus, 2000). Furthermore, the computational cost associated with current deterministic algorithms, even once the formulation has been adapted, is generally too high to permit routine use in process simulations where phase equilibrium calculations are performed thousands of times.

The focus of our current work is therefore to present an algorithm, HELD (Helmholtz free Energy Lagrangian Dual), for the solution of the duality-based formulation of the $P, T$ flash, which builds on the work presented in Pereira et al. (2010), but does not involve the use of guaranteed global optimisation. This reduces the computational demands of the algorithm and also removes the requirement that the functional form of the EOS be supplied to the optimisation routine. This facilitates the application of the algorithm to any EOS, and eases the implementation process. HELD differs from the algorithms presented in Pereira et al. (2010) in a number of ways. Firstly, since deterministic global optimisation is no longer employed to guard against convergence to metastable states, an important guiding principle in the algorithmic design is to maximise the likelihood of converging to the global solution. This is achieved in large part by implementing a carefully constructed initial guess strategy, to strike a balance between improving efficiency by carrying over information between major iterations, and ensuring that the search of the space is as global as possible. In Pereira et al. (2010), deterministic global optimisation is also used to identify all stable phases after convergence of the dual prob-
lem and therefore in HELD, a different route is required to obtain this information. The strategy that we adopt is essentially to add an additional convergence criterion, namely that the algorithm cannot terminate until the mass balance is satisfied. The practical implementation of this idea is discussed in Section 3.3.

Despite the loss of the finite-time $\varepsilon$-convergence guarantee provided by a deterministic global optimisation algorithm, we will show that the proposed approach is highly reliable, solving the $P, T$ flash problem correctly through many thousands of independent calculations, on challenging mixtures. We develop the proposed algorithm for the solution of the volume-composition dual formulation of Pereira et al. (2010). A similar algorithm could equally be applied to the original formulation of Mitsos and Barton (2007) if the optimisation problem is formulated directly in the Gibbs free energy, rather than the Helmholtz free energy.

This article is organised as follows. We begin by discussing the formulation of the PE problem as a dual problem in the Helmholtz free energy-volume-composition space. Subsequently, we introduce the algorithm, which requires the completion of three stages: initialisation/stability testing; the identification of the composition and volume of the stable phases, within a relatively loose tolerance; and an acceleration phase to reach convergence. We then apply the algorithm to a benchmark problem: a binary mixture of hydrogen sulphide and methane, for which the thermodynamic properties are calculated with the Soave-Redlick-Kwong(SRK)EOS (Soave, 1972). Finally, we present sample calculations on challenging systems modelled with the statistical associating fluid theory for a hard-sphere reference (SAFT-HS) EOS (Chapman, Jackson, \& Gubbins, 1988; Green \& Jackson, 1992a, 1992b; Jackson, Chapman, \& Gubbins, 1988) and the statistical associating fluid theory for potentials of variable range (SAFT-VR) EOS (Galindo, Davies, GilVillegas, \& Jackson, 1998; Gil-Villegas et al., 1997). These systems exhibit various key features of non-ideal fluid phase behaviour such as liquid-liquid equilibrium (LLE) and liquid-liquid-liquid equilibrium (LLLE). Most have metastable solutions, and some are in high dimensions (up to fifteen components). We discuss the efficiency and reliability of the proposed algorithm as applied to this wide range of systems.

\section*{2. Problem formulation}

The goal of a $P, T$ flash calculation is to identify the unique, stable, equilibrium state of a system at specified pressure ( $P^{0}$ ), temperature ( $T^{0}$ ), and vector of mole numbers ( $\underline{n}^{0}$ ) of dimension $n c$, where $n c$ is the number of components. This stable phase configuration consists of one or more phases, and is identified by locating the global minimum in the system Gibbs free energy over all phases, the Gibbs free energy being the thermodynamic state function associated with the ( $\underline{n}, P, T$ ) ensemble. This corresponds to solving the following non-standard optimisation problem:

$$
\begin{array}{ll}
\min _{\underline{\mathbf{n}}, n p} & G^{T}\left(\underline{\mathbf{n}}, P^{0}, T^{0}\right) \\
\text { s.t. } & \left(\sum_{j=1}^{n p} n_{i, j}\right)-n_{i}^{0}=0, \quad i=1, \ldots, n c  \tag{1}\\
& n_{i, j} \in\left[0, n_{i}^{0}\right], i=1, \ldots, n c ; j=1, \ldots, n p ; n p \in\left[0, N_{G}\right] \subset \mathbb{N} .
\end{array}
$$

where $G^{T}$ is the total Gibbs free energy of the system, $\underline{\mathbf{n}}$ is a $n c \times n p$ matrix with element $n_{i, j}$ representing the number of moles of component $i$ in phase $j, n p$ is the number of distinct stable phases and $N_{G}$ is the maximum possible number of phases present, obtained from the Gibbs phase rule. $n_{i}^{0}$ is the ith element of vector $\underline{n}^{0}$, i.e.,
the total number of moles of component $i$ in the mixture. The total Gibbs free energy of the system is described by

$$
\begin{equation*}
G^{T}\left(\underline{\mathbf{n}}, P^{0}, T^{0}\right)=\sum_{j=1}^{n p} \sum_{i=1}^{n c} n_{i, j} \mu_{i, j}\left(\underline{n}_{j}, P^{0}, T^{0}\right), \tag{2}
\end{equation*}
$$

where $\mu_{i, j}$ is the chemical potential of component $i$ in phase $j$ and $\underline{n}_{j}$ is the vector of mole numbers in phase $j$. Problem (1) may equally be written in terms of the mole fraction matrix, in which case only $n c-1$ independent mole fractions are considered in each phase as one of the mole fractions in each phase $j$ is obtained though the expression $x_{n c, j}=1-\sum_{i=1}^{n c-1} x_{i, j}$, where $x_{i, j}$ is the mole fraction of component $i$ in phase $j$. This convention is used in the remainder of this paper, and leads to the following formulation:

$$
\begin{array}{ll}
\min _{\underline{\mathbf{x}}, n p, \underline{F}} & g^{T}\left(\underline{\mathbf{x}}, P^{0}, T^{0}\right) \\
\text { s.t. } & \left(\sum_{j=1}^{n p} F_{j} x_{i, j}\right)-x_{i}^{0}=0, \quad i=1, \ldots, n c-1, \\
& \left(\sum_{j=1}^{n p} F_{j}\right)-1=0,  \tag{3}\\
& x_{i, j} \in[0,1], i=1, \ldots, n c-1 ; j=1, \ldots, n p ; \\
& F_{j} \in[0,1], j=1, \ldots, n p, n p \in\left[0, N_{G}\right] \subset \mathbb{N}
\end{array}
$$

where

$$
\begin{align*}
g^{T}\left(\underline{\mathbf{x}}, P^{0}, T^{0}\right)= & \left(\sum_{j=1}^{n p} \sum_{i=1}^{n c-1} x_{i, j} \mu_{i, j}\left(\underline{x}_{j}, P^{0}, T^{0}\right)\right) \\
& +\sum_{j=1}^{n p}\left(1-\sum_{i=1}^{n c-1} x_{i, j}\right) \mu_{n c, j}\left(\underline{x}_{j}, P^{0}, T^{0}\right), \tag{4}
\end{align*}
$$

where $g^{T}$ is the total molar Gibbs free energy of the mixture, $\mathbf{x}$ is a $(n c-1) \times n p$ matrix with elements $x_{i, j}, x_{i}^{0}$ is the $i$ th element of vector $\underline{x}^{0}$, i.e., the total mole fraction of component $i$ in the mixture, and $F_{j}$ is the fraction of material in phase $j$.

It can be shown that at the solution of the $P, T$ flash, equilibrium phases must have the same temperature and pressure, and must also have equality of chemical potential for each component (Gibbs, 1874; see, for example, O'Connell \& Haile, 2005, for a clear derivation). The temperature and pressure of the equilibrium phases will correspond to those specified; $T^{0}, P^{0}$. However, coexisting equilibrium phases may (and do) take compositions different from $\underline{x}^{0}$. When a phase split occurs, the multiphase state has a lower Gibbs free energy than the single-phase state, which is therefore not stable.

In recent work, Mitsos and Barton (2007) proposed a new interpretation of phase stability and showed that this can be used to identify one of the stable phases. To arrive at their stability criterion, they considered a primal problem in which the Gibbs free energy of the single-phase system, at the conditions of interest, is minimised, subject to a mass balance constraint:

$$
\begin{array}{ll}
\min _{\underline{x}} & G\left(\underline{x}, P^{0}, T^{0}\right) \\
\text { s.t. } & x_{i}^{0}-x_{i}=0, \quad i=1, \ldots, n c-1 .  \tag{x}\\
& \underline{x} \in X \subset \mathbb{R}^{n c-1}
\end{array}
$$

where $X$ is the set defined as $\left\{\underline{x}: \underline{x} \in[0,1]^{n c-1}\right\}$. Problem ( $\mathrm{P}_{x}$ ) has an equal number of variables and linear constraints, and by construction has only a trivial solution, at $\underline{x}^{0}$. The solution of problem ( $\mathrm{P}_{x}$ ) is equivalent to the evaluation of the Gibbs free energy at the com-
position $\underline{x}^{0}$. Mitsos and Barton (2007) formulated a dual of ( $\mathrm{P}_{x}$ ), in which the $n c-1$ mass balance constraints are dualised:

$$
\begin{array}{cl}
G^{D}=\max _{\underline{\lambda} \in \mathbb{R}^{n c-1}} & \theta(\underline{\lambda}) \\
\text { s.t. } & \theta(\underline{\lambda})=\min _{\underline{x} \in X} L(\underline{x}, \underline{\lambda}) . \tag{x}
\end{array}
$$


Here $L(\underline{x}, \underline{\lambda})$ is the Lagrangian of $\left(\mathrm{P}_{x}\right)$ :

$$
\begin{equation*}
L(\underline{x}, \underline{\lambda})=G\left(\underline{x}, P^{0}, T^{0}\right)+\sum_{i=1}^{n c-1} \lambda_{i}\left(x_{i}^{0}-x_{i}\right) . \tag{5}
\end{equation*}
$$

$\lambda_{i}$ is the Lagrange multiplier for the equality constraint on the mole fraction of component $i$ in problem ( $\mathrm{P}_{x}$ ), and $\theta(\underline{\boldsymbol{\lambda}})$ is the dual function. A general discussion of duality theory may be found in Bazaraa, Sherali, and Shetty (1993). Mitsos and Barton (2007) proved that, under some mild assumptions, the global solutions of problem ( $\mathrm{D}_{x}$ ) correspond to the stable phases of the system at $\underline{x}^{0}, P^{0}, T^{0}$. They also suggested an algorithm for its solution (discussed later in our paper), which they apply to several case studies, in which thermodynamic properties are obtained from the NRTL (Renon \& Prausnitz, 1968) and UNIQUAC (Abrams \& Prausnitz, 1975) models. Additionally, the method has been used in parameter estimation for a number of thermodynamic models (Bollas, Barton, \& Mitsos, 2009; Mitsos, Bollas, \& Barton, 2009).

As mentioned, this duality-based interpretation of phase stability has interesting features. It is free of any assumptions, such as the number or type of phases, or their compositions, and the steps required to solve the dual formulation are identical for all types of fluid phase behaviour. In addition, the outer problem has a unique maximum, a feature which may be exploited in the algorithm.

We have recently developed an alternative formulation, in which calculations at constant pressure are avoided. If the thermodynamic model used is an EOS that is a higher-than-cubic function in volume, then obtaining the correct volume root for a given pressure requires the use of an embedded nonlinear solver. This can entail a significant computational cost and can also introduce additional numerical instability and uncertainty. We may avoid such an inner loop by formulating a primal problem using the Helmholtz free energy instead of the Gibbs free energy, as suggested for the flash problem by Nagarajan et al. (1991a). For this purpose we introduce volume as a variable (Pereira et al., 2010):

$$
\begin{array}{ll}
\min _{\underline{\underline{x}}, V} & A\left(\underline{x}, V, T^{0}\right)+P^{0} V \\
\text { s.t. } & x_{i}^{0}-x_{i}=0 \quad i=1, \ldots, n c-1 \\
& \underline{x} \in X \subset \mathbb{R}^{n c-1} \\
& V \in[\underline{V}, \bar{V}]
\end{array}
$$

where $V$ is molar volume, $\underline{V}$ and $\bar{V}$ are lower and upper bounds on volume, respectively, and $A\left(\underline{x}, V, T^{0}\right)$ is the Helmholtz free energy, at constant temperature $T^{0}$. A lower bound on the volume variable is necessary to ensure that no unphysical values of the volume are considered. In choosing an upper bound on volume, one must take care to choose a value large enough to avoid cutting off one or more stable phases. The usefulness of the volume-composition space in phase equilibrium calculations has been highlighted previously, e.g., Giovanoglou, Galindo, Jackson, and Adjiman (2009) and Giovanoglou, Adjiman, Jackson, and Galindo (2009).

In a manner analogous to problem ( $\mathrm{D}_{x}$ ), the mass balance constraints of problem ( $\mathrm{P}_{x, V}$ ) may be dualised, and we can formulate a dual problem based on the Helmholtz free energy:

$$
G^{D}=\max _{\underline{\boldsymbol{\lambda}} \in \mathbb{R}^{n c-1}} \theta^{V}(\underline{\boldsymbol{\lambda}})=\min _{\underline{\boldsymbol{x}} \in X, V \in[\underline{\boldsymbol{V}}, \overline{\boldsymbol{V}}]} \theta^{V}(\underline{\boldsymbol{\lambda}})=L^{V}(\underline{\boldsymbol{x}}, V, \underline{\boldsymbol{\lambda}}), \quad\left(D_{x, V}\right)
$$

where

$$
\begin{equation*}
L^{V}(\underline{x}, V, \underline{\lambda})=A\left(\underline{x}, V, T^{0}\right)+P^{0} V+\sum_{i=1}^{n c-1} \lambda_{i}\left(x_{i}^{0}-x_{i}\right), \tag{6}
\end{equation*}
$$

where $\underline{\lambda}$ retains the same significance as in problem ( $\mathrm{D}_{x}$ ), $\theta^{V}(\underline{\lambda})$ is the dual function, and $G^{D}$ its maximum. Solution of problem ( $\mathrm{D}_{x, V}$ ) yields the equilibrium Lagrange multipliers ( $\underline{\lambda}^{*}$ ), and the composition and volume of one (arbitrary) stable phase ( $\underline{x}^{*}, V^{*}$ ).

Problem ( $\mathrm{D}_{x, V}$ ) is a bilevel optimisation problem, comprising a concave outer problem and a nonconvex inner problem, and may be equivalently described by

$$
\begin{aligned}
G^{D}= & \max _{v, \underline{\lambda} \in \mathbb{R}^{n c-1}} v \\
& \text { s.t. } \quad v \leq A\left(\underline{x}, V, T^{0}\right)+P^{0} V+\sum_{i=1}^{n c-1} \lambda_{i}\left(x_{i}^{0}-x_{i}\right) \quad\left(\operatorname{SIP}_{x, V}\right) \\
& \forall \underline{x} \in X \subset \mathbb{R}^{n c-1} ; \forall V \in[\underline{V}, \bar{V}] .
\end{aligned}
$$


Problem ( $\operatorname{SIP}_{x, V}$ ) is linear in $v$ and $\underline{\lambda}$ and contains an infinite number of constraints, since it must be satisfied for all values of composition and volume within their respective bounds, $(\underline{x}, V) \in X \times[\underline{V}, \bar{V}]$ and valid constraints can consequently be constructed from all possible (i.e., an infinite number) of ( $\underline{\chi}, V$ ) combinations. By definition, any choice of ( $\underline{x}, V$ ) in this set results in a constraint that overestimates $\theta^{V}(\underline{\lambda})$ and is a valid upper bound on the solution of the dual problem $G^{D}$. Mitsos and Barton (2007) use the outer approximation algorithm of Blankenship and Falk (1976) and Falk and Hoffman (1977) to solve the semi-infinite problem, so that a finite approximation of the outer problem is constructed, and progressively tighter upper and lower bounds are obtained on $G^{D}$. When applied to problem $\left(\mathrm{SIP}_{x, V}\right)$, to ensure that effective constraints are used in the approximation, the inner problem in formulation $\left(D_{X, V}\right)$ is solved for specific values of $\underline{\lambda}^{k}$,

$$
\begin{aligned}
L^{V(k)} & =\min _{\underline{x} \in X, V \in[\underline{V}, \bar{V}]} L^{V}\left(\underline{x}, V, \underline{\lambda}^{(k)}\right) \\
& =\min _{\underline{x} \in X, V \in[\underline{V}, \bar{V}]}\left(A\left(\underline{x}, V, T^{0}\right)+P^{0} V+\sum_{i=1}^{n c-1} \lambda_{i}^{k}\left(x_{i}^{0}-x_{i}\right)\right) . \quad\left(\operatorname{IP}_{x, V}\right)
\end{aligned}
$$


This yields a lower bound $L^{V(k)}$ on $G^{D}$, provided the global solution of problem ( $\mathrm{IP}_{x, V}$ ) has been obtained. As discussed in Pereira et al. (2010), at a solution of problem $\left(\mathrm{IP}_{x, V}\right), \underline{\lambda}^{k}$ is linked to the component chemical potentials by the relationship,

$$
\begin{align*}
\lambda_{i}^{k} & =\left(\frac{\partial A\left(\underline{x}, V, T^{0}\right)}{\partial x_{i}}\right)_{x_{k \neq i, k=1, \ldots, n c-1}, V, T} \\
& =\mu_{i}\left(\underline{x}, V, T^{0}\right)-\mu_{n c}\left(\underline{x}, V, T^{0}\right), \quad i=1, \ldots, n c-1 . \tag{7}
\end{align*}
$$


Additionally, the solution of problem ( $\mathrm{IP}_{x, V}$ ) will be at the specified pressure $P^{0}$, without the imposition of any explicit constraint on the volume. This is due to the first order optimality condition associated with the volume variable, $V$,

$$
\begin{equation*}
\left(\frac{\partial L^{V}\left(\underline{x}, V, \underline{\lambda}^{(k)}\right)}{\partial V}\right)_{\underline{x}, T}=\left(\frac{\partial A\left(\underline{x}, V, T^{0}\right)}{\partial V}\right)_{\underline{x}, T}+P^{0}=-P+P^{0}=0 . \tag{8}
\end{equation*}
$$


The solutions, $\left(\underline{\chi}^{(k)}, V^{(k)}\right)$, obtained from solving problem ( $\mathrm{IP}_{x, V}$ ) for various values of $\underline{\lambda}^{(k)}$ can be used to form an approximation of
$\left(\operatorname{SIP}_{x, V}\right)$, the outer problem,

$$
\begin{aligned}
U B D^{V}= & \max _{v, \underline{\lambda} \in \mathbb{R}^{n c-1}} v \\
& \text { s.t. } \quad v \leq \quad A\left(\underline{x}^{m}, V^{m}, T^{0}\right)+P^{0} V^{m} \\
& +\sum_{i=1}^{n c-1} \lambda_{i}\left(x_{i}^{0}-x_{i}^{m}\right) \quad \forall\left(\underline{x}^{m}, V^{m}\right) \in \mathcal{M} \quad\left(\mathrm{OP}_{x, V}\right) \\
& v \quad \leq G^{P},
\end{aligned}
$$

where $U B D^{V}$ is an upper bound on the solution of the dual problem $G^{D}, \mathcal{M}$ is a set of $(\underline{x}, V)$ vectors, (any $(\underline{x}, V)$ vector that has been included in $\mathcal{M}$ is denoted $\left(\underline{x}^{m}, V^{m}\right)$ ), and $G^{P}$ is the value of the Gibbs free energy at the total composition $\underline{x}^{0}$. Note that the last constraint is not necessary but can help to speed up the convergence of the overall algorithm to the global solution.

In Pereira et al. (2010), we proposed extensions to the algorithm suggested by Mitsos and Barton (2007), and implemented them to solve examples with an augmented van der Waals EOS (Alder \& Hecht, 1969; Carnahan \& Starling, 1972; Jackson, Rowlinson, \& Leng, 1986; Marsh, McGlashan, \& Warr, 1970) and with the SAFT-HS (statistical associating fluid theory for a hard sphere reference) EOS (Chapman et al., 1988; Green \& Jackson, 1992a, 1992b; Jackson et al., 1988), using the Helmholtz free energy formulation of the dual problem ( $\mathrm{D}_{x, V}$ ). We used multistart local optimisation to obtain cutting planes at low computational cost, instead of solving the inner problem globally at each iteration. The global guarantee on the final solution was retained, since an inner problem is solved globally upon convergence to a candidate vector of equilibrium Lagrange multipliers. This modification results in a significant reduction in the computational resources required to solve each $P, T$ flash. Additionally, we found that when the inner problem is solved to global optimality with a deterministic branch and bound algorithm, all the stable phases present at equilibrium may be identified at little extra cost, since they are all equally valid global solutions of the same optimisation problem, and are therefore available from the list of unfathomed nodes in the branch-and-bound tree. Finally, we showed that the reduction of the feasible region of the nonconvex inner problem through the addition of the first-order optimality conditions as redundant constraints leads to improved computational performance.

We proceed now to the main contribution of our current work, a reliable algorithm, HELD, for the solution of the dual formulation of $P, T$ phase equilibrium that uses only local solvers and first derivatives (with respect to volume and mole number) of the Helmholtz free energy, allowing it to be readily applied to any EOS, irrespective of the complexity of its functional form and without the need to provide explicit functional information. We begin by outlining the general scheme of the proposed algorithm, before highlighting some details important for efficiency and reliability. We conclude with numerical examples for systems represented by the Soave-Redlick-Kwong (SRK) (Soave, 1972), the SAFT-HS (Chapman et al., 1988; Green \& Jackson, 1992a, 1992b; Jackson et al., 1988) and the SAFT-VR (Galindo et al., 1998; Gil-Villegas et al., 1997) EOSs.

\section*{3. The HELD algorithm}

The inputs to the HELD algorithm are the specified conditions, $\underline{x}^{0}, P^{0}, T^{0}$, and the outputs are the number of equilibrium phases and their compositions, volumes and phase fractions. No user-specified initial guesses are required as to the number, type, composition or volume of the equilibrium phases. The HELD algorithm is broadly outlined in Fig. 1 and Table 1, and comprises three stages: initialisation and stability test (stage I, Section 3.1); identification of an equilibrium Lagrange multiplier vector $\underline{\lambda}^{*}$ and any

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/a19475d2-f89b-4570-8216-62f59ef156d5-05.jpg?height=1986&width=898&top_left_y=184&top_left_x=1072}
\captionsetup{labelformat=empty}
\caption{Fig. 1. General scheme of the HELD algorithm for the solution of the $P, T$ flash.}
\end{figure}
candidate stable phases, within a relatively loose tolerance (stage II, Section 3.2); acceleration of convergence via free energy minimisation and application of a number of convergence tests/refinement steps (stage III, Section 3.3). The algorithm iterates between stages II and III until enough equilibrium phases have been found to satisfy the overall mass balance. Although volume $V$ is used throughout the development of the theory, in the implementation the dimensionless reduced density (also known as the packing fraction) $\eta$ is

Table 1
HELD algorithm for the solution of the $P, T$ fluid phase equilibrium problem.
```
PROCEDURE HELD( $\underline{x}^{0}, P^{0}, T^{0}$ )
    Stage I: Stability test and initialisation
    Step 1: Stability test at $\underline{x}^{0}$
            Solve stability test $10 n c$ times using tunneling algorithm
            If negative tangent plane distance found, go to Step 2
            If stability test yields stable result, terminate
    Step 2: Initialisation of dual problem
        (a) Set major iteration counter $k=0$;
            Upper bound $U B D^{V}=G^{P}\left(\underline{x}^{0}, P^{0}, T^{0}\right)$;
        (b) Initialise set $\mathcal{M}$ based on strategy in Pereira et al. (2010).
    Stage II: Identification of candidate stable phases
    Step 3: Solve the outer problem ( $\mathrm{OP}_{x, V}$ ).
    Set $\underline{\lambda}^{(k)}=\underline{\lambda}^{*}$ and update best upper bound $U B D^{V}$.
    Step 4: Generation of a cutting plane.
        Solve the inner problem (7) with fixed $\underline{\lambda}^{(k)}$ from different
            starting points until $L^{V(k)} \leq U B D^{V}$.
        Add the corresponding variable values $\left(\underline{\chi}^{(k)}, V^{(k)}\right)$ to $\mathcal{M}$.
    Step 5: Search for candidate stable phases.
        Update set $M^{*}$ using criteria (PP).
        If $M^{*}$ contains 2 or more elements then go to Step 7.
    Step 6: Increment iteration counter $k=k+1$ and go to Step 3.
    Stage III: Acceleration and convergence tests
    Step 7: Minimisation of the Gibbs free energy over all candidate phases.
        Solve problem ( $\mathrm{GM}_{x, V}$ ).
        If the solution of problem ( $\mathrm{GM}_{x, V}$ ) is unsuccessful,
        increment iteration counter $k=k+1$ and go to Step 3.
    Step 8: Convergence test
        Test consistency of Step 7 Gibbs free energy with best $U B D^{V}$
        Test convergence of chemical potentials
        If either test fails, increment iteration counter $k=k+1$ and go to Step 3.
    Step 9: Check for trace components.
        If trace components are present then solve for their true equilibrium
        compositions.
END HELD;
```

used instead because it is well bounded and improves the scaling of the problem. The specific equation for translation between the two variables $V$ and $\eta$ depends on the EOS in question. The equivalence of the solutions obtained when using $\eta$ rather than volume in the inner problem is proven in Pereira et al. (2010). Without loss of generality, it is assumed that the species present in the mixture are numbered in order of decreasing total mass fraction.

\subsection*{3.1. Stage I: stability test and initialisation}

The first step, seen in Table 1 and Fig. 1, is a tangent plane stability test (Baker et al., 1982; Michelsen, 1982a) for the total composition to determine whether a phase split occurs. This is a common procedure in phase equilibrium algorithms, and the problem is given by

$$
\begin{equation*}
\min _{\underline{x} \in X, V \in[\underline{V}, \bar{V}]} d\left(\underline{x}, V, T^{0}\right)=A\left(\underline{x}, V, T^{0}\right)+P^{0} V+\sum_{i=1}^{n c-1} g_{i}^{0}\left(x_{i}^{0}-x_{i}\right), \tag{9}
\end{equation*}
$$

where $g_{i}^{0}$ is $\left(\partial G / \partial x_{i}\right)_{x_{j \neq i}^{0}, P^{0}, T^{0}}$, the gradient of the Gibbs free energy with respect to mole fraction at the specified conditions. Two outcomes are possible: $\underline{x}^{0}$ may be a stable phase, in which case the algorithm terminates. Alternatively, $\underline{x}^{0}$ is not stable, indicating that more than one phase must exist.

The key to reliability, when using non-guaranteed optimisation, is to locate a negative tangent plane distance as early as possible. Tunneling algorithms (Levy \& Gomez, 1985; Levy \& Montalvo, 1985) have proven to be effective for this task, and the use of tunneling in stability testing has been extensively explored by Nichita et al. (2002a, 2002b, 2006, 2008) and Nichita and Gomez (2009). In our current work the exponential tunneling function $f_{T}$ (Barron
\& Gómez, 1991) is used in the stability testing in stage I. It has the general form:

$$
\begin{equation*}
f_{T}(\underline{z})=\left(f(\underline{z})-f\left(\underline{z}^{*}\right)\right) \exp \left(\frac{p^{*}}{\left\|\underline{z}-\underline{z}^{*}\right\|}\right) \tag{10}
\end{equation*}
$$

where $f(\underline{z})$ is the original objective function, $f\left(\underline{z}^{*}\right)$ is the objective function evaluated at the lowest known minimum, $\underline{z}^{*}$ is the variable value at the lowest known minimum, $\|$.$\| is the Euclidian norm,$ and $p^{*}$ represents the strength of the pole created at the minimum at $\underline{z}^{*}$. A value of $p^{*}=10^{-3}$ is used throughout. A suitable tunneling function, in the context of the stability test, is as follows:

$$
\begin{align*}
f_{T}\left(\underline{x}, V, T^{0}\right)= & \left(A\left(\underline{x}, V, T^{0}\right)+P^{0} V+\sum_{i=1}^{n c-1} g_{i}^{0}\left(x_{i}^{0}-x_{i}\right)-d^{*}\right) \\
& \times \exp \left(\frac{p^{*}}{\left(\sum_{i=1}^{n c-1}\left(x_{i}^{*}-x_{i}\right)^{2}\right)^{0.5}}\right), \tag{11}
\end{align*}
$$

where $d^{*}=d\left(\underline{x}^{*}, V^{*}, T^{0}\right)$ is the value of the best minimum found so far, and $\underline{x}^{*}$ is the composition vector at this minimum. As soon as a vector ( $\underline{x}^{*}, V^{*}$ ), that produces a negative value of $d\left(\underline{x}, V, T^{0}\right)$ is found, the phase $\underline{x}^{0}$ may be declared not stable and stage I completed. If a negative value of $d\left(\underline{x}, V, T^{0}\right)$ is not encountered after a given number of tunnelling minimisations (e.g., 10nc) from random starting points, then the state $\left(\underline{x}^{0}, P^{0}, T^{0}\right)$ is considered stable. It should be stressed that this approach does not guarantee to locate instability or metastability and it is possible that the tunnelling minimisations could fail to find a negative tangent plane distance even when it exists, resulting in the premature termination of the algorithm. The only remedy for this, and indeed for the more general issue of assuring a correct solution to the phase equilibrium problem, is to use guaranteed deterministic global optimisation.

The tangent plane stability test at $\underline{\chi}^{0}$ is in fact equivalent to solving the inner problem ( $\mathrm{IP}_{x, V}$ ) for $\lambda_{i}^{0}=g_{i}^{0}$, where the objective function has been offset by $G^{P}$. This is thus equivalent to the initialisation of $\lambda_{i}^{0}=g_{i}^{0}$ in Pereira et al. (2010), in which the initial iteration doubles as a stability test.

If the total composition is found not to be stable, the algorithm proceeds to Step 2 where the initialisation is completed and the set $\mathcal{M}$ is initialised as per the method in Pereira et al. (2010). The iteration counter is set to $k=0$ and the upper bound to $U B D^{V}=G^{P}$. Our initialisation procedure differs from that of Mitsos and Barton (2007), in that we begin with a stability test involving the minimisation of the tangent plane distance function, rather than directly solving an outer problem. Solution of the dual problem itself is equivalent to testing the stability of the feed, and if the solution lies at $G^{P}$ then the specified conditions are stable. However, we find that beginning with the stability test described here improves reliability in the identification of unstable states.

\subsection*{3.2. Stage II: identification of candidate stable phases}

The objective of stage II is the identification of all global solutions of the dual problem ( $\mathrm{OP}_{x, V}$ ), i.e., the vectors of optimal Lagrange multipliers $\underline{\lambda}^{*}$ and chemical potentials $\mu^{*}$, and the composition and volume of all the stable phases ( $\underline{x}^{*}, \overline{V^{*}}$ ). During stage II the dual problem is solved only to a relatively loose level of convergence and this approximate solution is improved during stage III. Stage III is first initiated when two candidate stable phases have been found. If these two phases fail to satisfy the convergence tests in Stage III,
the algorithm returns to Stage II and a different set of candidate stable phases is sought.

\subsection*{3.2.1. Outer and inner problems (Steps 3 and 4)}

The only information required to initialise stage II are the bounds on $\underline{\lambda}$. Bounds are imposed through the specific ( $\underline{x}, V$ ) combinations included in the initial set $\mathcal{M}$. At iteration $k$, the outer problem is first solved in Step 3 to yield $\underline{\lambda}^{(k)}$, using all points ( $\underline{x}, V$ ) in $\mathcal{M}$ up to this iteration. The inner problem ( $\mathrm{IP}_{x, V}$ ) is then solved in Step 4 to generate new values of $(\underline{x}, V)$ using the fixed $\underline{\lambda}^{(k)}$. A multistart approach is employed to solve this nonconvex problem, using different initial guesses for ( $\underline{x}, V$ ) until a minimum is obtained that is below the current upper bound, $U B D^{V}$. This has proven to be more efficient than solving the inner problem locally a fixed number of times and using the lowest solution. The best solution of the inner problem (a point in composition and volume) is included in $\mathcal{M}$, adding a linear constraint to the outer problem $\left(\mathrm{OP}_{x, V}\right)$. More details of the initial guess strategy used in the multistart approach are given in Section 3.4.

\subsection*{3.2.2. Identification of candidate stable phases (Step 5)}
$\mathcal{M}$ contains the solutions to every inner problem ( $\mathrm{IP}_{x, V}$ ) solved during the course of the algorithm, and it is possible to monitor the progress of HELD by keeping track of the contents of this set. We identify candidate stable phases in Step 5 by searching through the set $\mathcal{M}$ to find $m p$ points, i.e., $\left(\underline{x}^{1}, V^{1}\right),\left(\underline{x}^{2}, V^{2}\right) \ldots\left(\underline{x}^{m p}, V^{m p}\right)$, that satisfy the following conditions,

$$
\begin{align*}
& U B D^{V}-L^{V(m)} \leq \varepsilon_{b}, \quad m=1, \ldots, m p,  \tag{PP}\\
& \frac{\left|\left(\frac{\partial A\left(\underline{x}^{m}, V^{m}, T^{0}\right)}{\partial x_{i}^{m}}\right)_{x_{k \neq i}^{m}, V, T}-\lambda_{i}^{(k)}\right|}{\left|\lambda_{i}^{(k)}\right|} \leq \varepsilon_{\lambda},
\end{align*}
$$


$$
\begin{aligned}
& \forall i \in I^{m}, \quad m=1, \ldots, m p \\
& {\left[\left|\eta^{m}-\eta^{n}\right| \geq \varepsilon_{\eta}, \quad \forall m=1, \ldots, m p, \quad m \neq n ; \quad n=1, \ldots, m p ;\right]} \\
& \text { OR }\left[\left|x_{i}^{m}-x_{i}^{n}\right| \geq \varepsilon_{x}, \forall m=1, \ldots, m p, \quad m \neq n ; \quad n=1, \ldots, m p ;\right. \\
& \quad i=1, \ldots, n c-1]
\end{aligned}
$$

where $I^{m}$ is a set of component indices containing at most $n c_{p p}$ elements defined by $i \in I^{m} \Rightarrow x_{i}^{m} \neq x^{l}$, where $x^{l}$ is the lower bound on mole fractions, and $n c_{p p}$ is the number of components to be converged through the solution of the dual problem. This means that any component that is at the lower bound in mole fraction, and hence may be a trace component, is ignored in the convergence test. Trace components are further discussed in Section 3.3.3. For systems containing few components (e.g., $\leq 6$ ) we set $n c_{p p}=n c-1$, but for more components, performance is improved by setting $n c_{p p}$ to a value less than $n c-1$, e.g., $n c_{p p}=5$. This does not affect the quality of the final solution produced by HELD, since the purpose of system (PP) is to provide good initial guesses for the minimisation problem solved in stage III, rather than to ensure that the equilibrium conditions are satisfied.

The set of $m p$ points fulfilling system(PP) is denoted $\mathcal{M}^{*}$. The last constraint in (PP) ensures that points in $\mathcal{M}^{*}$ are separated by a suitable distance in mole fraction, $\varepsilon_{x}$, or in packing fraction (reduced volume) $\varepsilon_{\eta}$. It is sufficient for distinct phases to have a separation either in packing fraction, or in composition, permitting the treatment of azeotropic systems. Note that the second constraint in system (PP) is only imposed for components whose mole fraction does not lie at the lower bound in composition. If the composition of a component in a phase is at this lower bound, as may occur when working with, for example, polymer + solvent mixtures, then its gradient with respect to composition is unlikely to fulfil this con-
dition, and this constraint must be relaxed. The true equilibrium mole fraction of this component is refined post-convergence using the procedure discussed in Section 3.3.3. If $m p \leq 1$ then the iteration counter is incremented and the algorithm returns to Step 3, in which the outer problem is solved. If $m p>1$, then HELD progresses to stage III.

\subsection*{3.3. Stage III: acceleration and convergence tests}

\subsection*{3.3.1. Free energy minimisation (Step 7)}

At the conclusion of HELD we wish to obtain $n p$ phases fulfilling the necessary conditions for equilibrium. It is possible to obtain tight convergence directly through the solution of the dual problem, but a good approximation of the properties of the equilibrium phases may be identified much earlier in the process. At this stage of the algorithm, it is more efficient to proceed through the explicit minimisation of the total Gibbs free energy based on all the phases identified, than to continue to solve alternating outer and inner problems. This minimisation has the form of problem ( $\mathrm{GM}_{x, V}$ ), and is carried out in mass number (assuming a basis of one mole) so that the mass balance constraints are linear and the problem is well scaled,

$$
\begin{aligned}
G^{*}=\min _{\underline{\underline{\mathbf{q}}}, \underline{V}} & \sum_{j=1}^{m p}\left(A\left(\underline{q}_{j}, V_{j}^{\prime}, T^{0}\right)+P^{0} V_{j}^{\prime}\right) \\
\text { s.t. } & \left(\sum_{j=1}^{m p} q_{i, j}\right)-q_{i}^{0}=0, \quad i=1, \ldots, n c, \quad\left(\mathrm{GM}_{x, V}\right) \\
& q_{i, j} \in\left[q_{i, j}^{m}-10^{-3} M W_{i}, q_{i, j}^{m}+10^{-3} M W_{i}\right], \\
& i=1, \ldots, n c, j=1, \ldots, m p,
\end{aligned}
$$

where $m p$ is the number of phases included in the minimisation, $G^{*}$ is the Gibbs free energy at the solution, $\underline{\mathbf{q}}$ is the $m p \times n c$ matrix containing the mass numbers in each phase, $q_{i, j}$ is the mass of component $i$ in phase $j, q_{i, j}^{m}$ is the mass of component $i$ in phase $j$ in the set $\mathcal{M}^{*}$ as produced from stage II, $q_{i}^{0}$ is the total mass of component $i$ in the mixture, $A\left(\underline{q}_{j}, V_{j}^{\prime}, T^{0}\right)$ is the Helmholtz free energy of phase $j$ and $V_{j}^{\prime}$ is the volume of phase $j . M W_{i}$ is the molar mass of component $i$. Note that $A\left(\underline{q}_{j}, V_{j}^{\prime}, T^{0}\right)$ and $V_{j}^{\prime}$ are extensive, rather than molar, quantities.

The initial guesses in composition and volume are obtained from $\mathcal{M}^{*}$. If there are stable phases missing from $\mathcal{M}^{*}$ then the mass balance is infeasible and the algorithm returns to Step 3 in stage II, after incrementing the iteration counter, where iterations between outer and inner problems continue until a candidate phase configuration is identified that satisfies the mass balance, ${ }^{1}$ as shown in Fig. 2. In ( $\mathrm{GM}_{X, V}$ ) the mass numbers $\underline{\mathbf{q}}$ are tightly bounded to avoid the minimisation moving too far away from the initial guesses in an attempt to satisfy the mass balance, in the event that a phase is missing from the simplex. The mass numbers are required to stay within $10^{-3} \times M W_{i}$ in mass number (or $10^{-3}$ moles) of the corresponding candidate phase composition, identified in stage II. Infeasibility in problem ( $\mathrm{GM}_{x, V}$ ) is identified during pre-processing by the nonlinear optimisation solver. If this step is passed successfully and if the initial guesses from $\mathcal{M}^{*}$ are good enough, then it is likely that a minimum will be found. In this case, we denote the set of stable phases characterising this solution $\mathcal{S}^{*}$. We take care to

\footnotetext{
${ }^{1}$ When the stable phase configuration contains more phases than components, e.g., if $n p=n c+1$, then it is possible to satisfy the mass balance with only $n c$ phases. In this case HELD would not necessarily locate all the stable phase corresponding to a given solution of the dual problem.
}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/a19475d2-f89b-4570-8216-62f59ef156d5-08.jpg?height=584&width=865&top_left_y=185&top_left_x=111}
\captionsetup{labelformat=empty}
\caption{Fig. 2. Illustration of the procedure to identify all the stable phases, when the simplex contains three phases. (a) Only one stable phase, labelled I, has been identified and the mixture with total composition $\underline{x}^{0}$ is known to be unstable. Consequently, it is not possible to satisfy the mass balance and problem ( $\mathrm{GM}_{x, V}$ ) is not solved, since it would be infeasible. (b) An additional phase, labelled II, is identified, but the mass balance still is not satisfied, and problem ( $\mathrm{GM}_{x, V}$ ) is infeasible. (c) A third phase, labelled III, is found, which completes the simplex. The mass balance is now satisfied and problem ( $\mathrm{GM}_{x, V}$ ) becomes feasible.}
\end{figure}
eliminate any degenerate phases in $\mathcal{S}^{*}$, i.e., phases with the same mole fractions and volumes. This could occur when multiple points in $\mathcal{M}^{*}$ actually correspond to the same stable phase, but enter $\mathcal{M}^{*}$ as distinct phases due to the loose tolerances used in system (PP). During the solution of problem ( $\mathrm{GM}_{x, V}$ ), these points will converge to the same minimum, a situation that may be readily identified though a simple filtering process. The degenerate phases are then combined as appropriate to ensure only distinct stable phases are reported. A final convergence test is then carried out, as described in the next subsection, to ensure that the solution obtained for problem( $\mathrm{GM}_{x, V}$ ) does in fact correspond to the same phase configuration as that contained in $\mathcal{M}^{*}$, i.e., the solution towards which the dual problem was converging.

\subsection*{3.3.2. Convergence test (Step 8)}

The convergence test consists of the following two steps:
1. The value of $G^{*}$ is compared to $U B D^{V}$, the value of the upper bound at the end of stage II. For $G^{*}$ to be accepted as the solution of the phase equilibrium problem, the following inequality must hold,

$$
\begin{equation*}
0 \leq U B D^{V}-G^{*} \leq \varepsilon_{g}, \tag{12}
\end{equation*}
$$

where $\varepsilon_{g}$ is set to $10^{-6}$. This ensures that $G^{*}$ is less than, but close to $U B D^{V}$. If expression (12) is not satisfied then the iteration counter is incremented and the algorithm returns to Step 3.
2. The convergence of the chemical potentials of all components in all phases in $\mathcal{S}^{*}$ is checked. For HELD to terminate, we require that,

$$
\begin{equation*}
\left|\left(\mu_{i, j}-\mu_{i, j+1}\right) / \mu_{i, j}\right| \leq \varepsilon_{\mu}, \quad \forall i=1, \ldots, n c, \quad \forall j=1, \ldots, m p-1 . \tag{13}
\end{equation*}
$$


If expression (13) is not satisfied, the iteration counter is incremented and the algorithm returns to Step 3. Otherwise, the contents of $\mathcal{S}^{*}$ are considered to be the stable phase simplex and HELD proceeds to the calculation of trace component compositions in Step 9. Unless there are more phases than components, all phases corresponding to ( $U B D^{V}, \underline{\lambda}^{*}$ ) will have been identified. The most likely occurrence of a phase configuration with $n c+1$ components would be a three-phase state in a binary mixture. This is unlikely,
since both the temperature and the pressure specified must lie exactly on the three-phase line of the mixture, and in addition, the composition must lie within the appropriate region. As the number of components increases, the likelihood of such a phase simplex occurring decreases even further. For example, four fluid phases in a three-component system do not occur often. Calculations specifically involving three-phase lines in binary mixtures, for example, in parameter estimation problems, would be more appropriately conducted in the volume-temperature space (i.e., a $V, T$ flash) as opposed to the $P, T$ flash being conducted here, since in $V, T$ space this phase configuration is fully specified by the constraint set.

\subsection*{3.3.3. Dealing with small values of the mole fractions (Step 9)}

If a component $k$ is present in a phase in a quantity smaller than the lower bound on composition of $x^{l}\left(=10^{-8}\right)$, then it is likely that the point $\left(\underline{x}^{m}, V^{m}\right)$ corresponds to a constrained minimum of $\left(\mathrm{IP}_{x, V}\right)$ (i.e., where $x_{k}^{m}=x^{l}$ ). In this case, the gradient with respect to the mole fraction of the trace component cannot be equal to the Lagrange multiplier $\lambda_{k}$, i.e., $\left(\partial A / \partial x_{i}^{m}\right)_{x_{i \neq k}^{m}, V, T} \neq \lambda_{k}$. The true equilibrium mole fraction $x_{k}^{m}$ is found post-convergence in Step 9, through the solution of the problem reformulated in logarithmic space, as discussed in Pereira et al. (2010). The chemical potential of the trace component is equated to that of the same component in the phase in which it is present in the greatest quantity, as obtained after stage III. This is related to the procedure proposed by Lucia et al. (2000), although these authors update the chemical potential of the trace component in a dynamic fashion throughout the course of their algorithm, rather than as a post-processing step. The presence of a component in a phase in a quantity smaller than the lower bound on composition should not inhibit the convergence of the algorithm to the global solution, provided that the convergence criterion for stage II is not too tight. The linear cuts generated by any phases containing trace components are still valid, even though they correspond to constrained minima of the inner problem.

The main concepts of the proposed HELD algorithm have now been exposed. More specific details of its implementation will be discussed, before presenting a variety of numerical case studies. In particular, an analysis will be undertaken of the level of reliability that may be expected, given the lack of a mathematical guarantee of $\varepsilon$-finite convergence to the global solution.

\subsection*{3.4. Efficiency and reliability}

To guarantee convergence of the algorithm to the correct solution, one must in principle solve the inner problem ( $\mathrm{IP}_{x, V}$ ) to global optimality at least once (Pereira et al., 2010). In the HELD algorithm, the identification of the global solution of the inner problem cannot be guaranteed, but several aspects of algorithmic design help to ensure reliability.

Firstly, we note that any solution $\left(\underline{x}^{k}, V^{k}\right)$ of the inner problem ( $\mathrm{IP}_{\chi, V}$ ) can safely be added to the set $\mathcal{M}$, to provide a valid cut for the outer problem $\left(\mathrm{OP}_{x, V}\right)$ in Step 3. If ( $\underline{x}^{k}, V^{k}$ ) happens to be a global solution of the inner problem at $\underline{\lambda}^{k}$, then the corresponding cut is the tightest possible, by virtue of being a supporting hyperplane of the Gibbs free energy surface.

Secondly, by enforcing that the lower bound should always be less than the lowest upper bound in Step 4, we avoid convergence to those local minima that are clearly erroneous. Nevertheless, the proposed algorithm may in principle converge to an incorrect solution if there exists a multiphase solution at a higher Gibbs free energy than the true solution. Such metastable solutions can occur near phase transitions, for example, when moving between two- and three-phase regions, where the metastable two-phase state will yield a feasible phase simplex. Common cases of this are the existence of two-phase liquid-liquid and vapour-liquid
solutions, when the equilibrium state is in fact a three-phase vapour-liquid-liquid state. These metastable states represent local solutions of the inner problem, and serial convergence to these during the solution of the inner problem may lead to failure to find the global solution. In our experience, this can be avoided by adopting a combination of the following initialisation strategies in solving the inner problem in Step 4, until a solution less than the best upper bound is obtained $\left(L^{V(k)} \leq U B D^{V}\right)$ :
- use a random starting point,
- use a previous solution with mole fractions shifted by 0.01 as a starting point,
- use a starting point close to a pure component.

In addition, the inner problem is solved alternately in the space of mole fractions and mass fractions. The use of previous solutions as starting points has been found to decrease the computational cost of the algorithm by up to $50 \%$. In our implementation, the algorithm alternates automatically between these different strategies.

When the outer problem solution approaches a metastable phase, there is a risk that the algorithm might converge to this metastable solution. In principle, it suffices for a point ( $\underline{x}, V$ ) (and consequently a new constraint) to be added to the outer problem such that the new Lagrange multipliers produced by the outer problem $\underline{\lambda}^{(k+1)}$ move the algorithm away from this incorrect solution. The constraint that would be most likely to set the algorithm back on course would be the global solution to the inner problem, and if this is obtained at least once as the algorithm approaches convergence, i.e., when $\underline{\lambda}^{(k)} \approx \underline{\lambda}^{*}$ then it is very likely that HELD will arrive at the correct equilibrium state. This argument can be extended to produce a proof of convergence to the global solution of the dual problem when guaranteed global optimisation is used (Pereira et al., 2010). The concavity of the outer problem ensures that regardless of the type of mixture or phase behaviour, HELD will never diverge. Additionally, with a sufficient number of iterations before Stage III, the algorithm will always identify the global solution.

Once the best upper bound is below the free energy of any metastable states, cases of convergence to a local minimum during the solution of the inner problem are disregarded automatically and the algorithm will converge to the global solution. The reliability of HELD is investigated in the next section.

\section*{4. Numerical case studies}

The HELD algorithm is implemented in FORTRAN and solvers from the Numerical Algorithms Group (NAG) libraries are used in both the inner and outer problems. The inner problems are solved with the SQP algorithm of Gill, Murray, Saunders, and Wright (1986a, 1986b), problem (GM ${ }_{X, V}$ ) with SNOPT (Gill, Murray, \& Saunders, 2002) and the linear optimisations with a method of Gill and Murray (1978), also described in Gill, Murray, Saunders, and Wright (1991). Analytical derivatives are used throughout. The bounds on composition are [ $10^{-8},\left(1-10^{-8}\right)$ ]. The HELD tolerances are set as follows: $\varepsilon_{\lambda}=0.5, \varepsilon_{b}=10^{-2}, \varepsilon_{x}=10^{-3}, \varepsilon_{\eta}=10^{-3}, \varepsilon_{\mu}=10^{-6}$ and $\varepsilon_{g}=10^{-6}$.

The proposed algorithm is applied to the fluid phase equilibria of a number of different mixtures. For each mixture two types of calculation are carried out. Firstly, the reliability of the algorithm is tested. The global composition, pressure and temperature of the mixture are randomly selected and if this point is found to be unstable then 100 calculations are carried out at the specified conditions. This procedure is repeated for 100 sets of randomly selected, unstable conditions and the consistency of the reported solutions to the PE problem is examined. The results of those 10,000 calculations
are checked against the known phase diagrams for mixtures of up to three components.

Following the tests over randomly selected conditions, point calculations are carried out, to investigate the performance of the algorithm in more detail. Each point calculation is repeated 100 times and multiple statistics are presented for each point. These include the mean and standard deviation for the number of major iterations, the number of EOS evaluations and the CPU time required to solve the entire phase equilibrium problem. This involves checking that the Gibbs free energies of the solutions agree to an accuracy of $10^{-6}$, and that the number of phases predicted is the same. Finally, no initial guesses, or any other information, is carried over between calculations. All calculations are carried out in Linux, on an Intel Xeon 2.4 GHz machine. To clarify further the progression of the HELD algorithm, the individual steps for a point calculation with a ternary mixture, discussed in this section, are presented in Appendix A.

The first example is a binary mixture of methane and hydrogen sulphide $\left(\mathrm{CH}_{4}+\mathrm{H}_{2} \mathrm{~S}\right)$, modelled with the Soave-Redlich-Kwong (SRK) EOS (Soave, 1972). Following this, the HELD algorithm is applied to various systems: a binary mixture of ethane and carbon dioxide $\left(\mathrm{C}_{2} \mathrm{H}_{6}+\mathrm{CO}_{2}\right)$ exhibiting an azeotrope, and two ternary mixtures of polypropylene glycol (PPG) and polyethylene glycol (PEG) and water, exhibiting LLE and LLLE. Finally, an analysis of the scaling of the algorithmic performance in higher dimensions is undertaken. The example chosen is VLE in a mixture of light gases and polyethylene, such as could be present in a gasphase polymerisation reaction mixture. Calculations are carried out for very similar conditions in five, ten and fifteen component mixtures, and the progression of the performance measures is observed.

In the remainder of this section, the systems studied are first introduced, and then the results of the computational tests are discussed. The EOS parameters for all mixtures are summarised in Appendix B. The intensive Gibbs free energy of mixing is shown for the binary mixtures. For two components, this is defined as: $\Delta G^{\text {MIX }}\left(\underline{x}, P^{0}, T^{0}\right)=G\left(\underline{x}, P^{0}, T^{0}\right)-x_{1} G^{1}\left(P^{0}, T^{0}\right)- x_{2} G^{2}\left(P^{0}, T^{0}\right)$, where $G^{1}\left(P^{0}, T^{0}\right)$ and $G^{2}\left(P^{0}, T^{0}\right)$ are the Gibbs free energy of the pure components 1 and 2 , respectively, at the specified pressure and temperature $P^{0}$ and $T^{0}$.

\subsection*{4.1. System I: binary mixture of methane and hydrogen sulphide, SRK}

This binary mixture is one of the benchmark test problems for fluid phase equilibrium algorithms. The system contains methane and hydrogen sulphide, modelled with the SRK EOS. The point calculations are at 190 K and 40 atm , conditions studied by, among others, Michelsen (1982a), Nichita et al. (2002a), Sun and Seider (1995) and also Hua, Brennecke, and Stadtherr (1998). The packing fraction $\eta$ for the SRK EOS is obtained from the expression $\eta=N b / 4 V$, where $b$ is the SRK parameter relating to molecular size. The $T-x$ phase diagram for this mixture at 40 atm and the Gibbs free energy of mixing at 190 K and 40 atm are shown in Fig. 3(a) and (b), respectively. The temperature of 190 K is below, but very close to, the three-phase line at 40 atm . Depending on the overall composition, both VLE and LLE occur at these conditions. There are consequently metastable solutions corresponding to both types of equilibria, making phase equilibrium calculations in this region challenging. Following the 10,000 calculations for this mixture, the results of the reliability testing are reported in Table 2, while Table 3 contains details of the phase splits for the VLE and LLE states at the given conditions, and Table 4 contains the performance statistics for these point calculations.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/a19475d2-f89b-4570-8216-62f59ef156d5-10.jpg?height=466&width=1528&top_left_y=183&top_left_x=251}
\captionsetup{labelformat=empty}
\caption{Fig. 3. Fluid phase behaviour and Gibbs free energy of system I , a binary mixture of $\mathrm{H}_{2} \mathrm{~S}+\mathrm{CH}_{4}$, modelled with the SRK EOS. (a) Temperature-composition phase diagram at a pressure of 40 atm . The dash-dotted line corresponds to 190 K ; (b) reduced Gibbs free energy of mixing at $T=190 \mathrm{~K}$ and $P=40 \mathrm{~atm}$.}
\end{figure}

\subsection*{4.2. Calculations with SAFT: systems II to VI}

An important requirement for this work is that the phase equilibrium algorithm should be easily integrated with any EOS, irrespective of its functional form. This facilitates its use with complex EOSs, such as SAFT (Chapman et al., 1989, 1990). The SAFT family of EOSs allows for detailed models of intermolecular interactions to be considered, such that non-sphericity and molecular association are modelled explicitly, and provides predictive capabilities for a wide range of mixtures and conditions (McCabe \& Galindo, 2010; Müller \& Gubbins, 2001; Wei \& Sadus, 2000).

Example calculations are shown for mixtures represented through the SAFT-HS (Chapman et al., 1988; Green \& Jackson, 1992a, 1992b; Jackson et al., 1988) and SAFT-VR EOSs (Galindo et al., 1998; Gil-Villegas et al., 1997). SAFT-VR has been applied to the modelling of a variety of systems, including carbon dioxide $+n$ alkane mixtures (Blas \& Galindo, 2002; Galindo \& Blas, 2002), monoethanolamine + carbon dioxide + water (Mac Dowell, Llovell, Adjiman, Jackson, \& Galindo, 2010), alkane + perfluoroalkane mixtures (Morgado, McCabe, \& Filipe, 2005), petroleum fluids (Sun, Zhao, \& McCabe, 2007), and mixtures containing polymers (Clark, Galindo, Jackson, Rogers, \& Burgess, 2008; Haslam et al., 2006; McCabe, Galindo, Nieves García-Lisbona, \& Jackson, 2001). This list includes mixtures that exhibit highly non-ideal fluid phase equilibria, thus providing excellent case studies on which to test the robustness and efficiency of our algorithm. A selection of systems exhibiting various features of non-ideal fluid phase behaviour have been chosen, including azeotropy, liquid-liquid
and liquid-liquid-liquid states. The systems contain between two and fifteen components, to permit investigation of the scaling of the performance measures as the number of components present in the mixtures is increased.

It is an assumption of HELD that the EOS evaluations do not fail. In principle it should be possible to fulfil this requirement, even when associating systems are being treated, provided that the conditions remain within the range of applicability of the EOS. The nonlinear association system of SAFT has a unique solution (Kakalis, Kakhu, \& Pantelides, 2006; Michelsen \& Hendriks, 2001; Xu et al., 2002), and reliable algorithms exist for its solution (Kakalis et al., 2006; Michelsen \& Hendriks, 2001; von Solms, Michelsen, \& Kontogeorgis, 2003; Xu et al., 2002). When association is present, the related system of equations is solved as an independent inner loop at each EOS evaluation using the hybrid successive substitution/ modified Newton algorithm of Kakalis et al. (2006).

As with SRK, reliability testing involves 10,000 calculations per mixture. In the case of the SAFT mixtures studied here, the packing fraction $\eta$ is defined as $\eta=N \pi /(6 V) \sum_{i=1}^{n c} x_{i} m_{i} \sigma_{i}^{3}$, where $N$ is the number of molecules present and $x_{i}$ and $\sigma_{i}$ are SAFT parameters for component $i$.

\subsection*{4.2.1. System II: binary athermal polymer-colloid system -SAFT-HS (TPT1)}

In this subsection we examine the athermal binary model colloid + polymer mixture, as studied by Paricaud, Varga, and Jackson (2003). The athermal version of the SAFT-HS EOS is used in this case (which essentially corresponds to the Wertheim TPT1 approach) in

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 2
Statistics for reliability testing on systems I to VII for 100 independent repeated calculations carried out at each of 100 randomly selected, unstable compositions, temperatures and pressures, resulting in 10,000 calculations for each system. The bounds on the random selection of the global composition vector are [ $10^{-4}, 0.9999$ ] in all cases (where $\sum_{i=1}^{n c} x_{i}^{0}=1$ ). Range $T^{0}$ denotes the bounds on the random selection in temperature, and Range $P^{0}$ the same for the pressure. EOS Eval. is the mean number of times the equation of state is evaluated, and CPU is the mean number of seconds required to solve the PE problem, both averaged over the 10,000 calculations. Sd. is the corresponding standard deviation. A failure to obtain the correct solution was not observed in any system during the calculations.}
\begin{tabular}{|l|l|l|l|l|}
\hline Range $P^{0}[\mathrm{MPa}]$ & Range $T^{0}$ [K] & IT (Sd.) & EOS Eval. (Sd.) & CPU (Sd.) [s] \\
\hline \multicolumn{5}{|l|}{I: $\mathbf{H}_{\mathbf{2}} \mathbf{S} \boldsymbol{(} \mathbf{1} \boldsymbol{)} \boldsymbol{+} \mathbf{C H}_{\mathbf{4}} \boldsymbol{(} \mathbf{2} \boldsymbol{)} \boldsymbol{-} \mathbf{S R K}$} \\
\hline 0.1-10.0 & 150-350 & 19.52 (10.34) & 480.94 (196.01) & 0.005 (0.005) \\
\hline \multicolumn{5}{|l|}{II: Athermal polymer (1) + colloid (2) ( $\left.T^{*}=k T /\left(P \sigma_{\text {colloid }}^{3}\right)\right)$-SAFT-HS (TPT1)} \\
\hline n/a & 0.01-1.1 ( $T^{*}$ ) & 10.29 (2.89) & 469.62 (123.67) & 0.006 (0.005) \\
\hline \multicolumn{5}{|l|}{III: $\mathbf{C}_{\mathbf{2}} \mathbf{H}_{\mathbf{6}}(\mathbf{1})+\mathbf{C O}_{\mathbf{2}}(\mathbf{2})$-SAFT-VR} \\
\hline 0.1-10.0 & 150-300 & 14.77 (9.64) & 427.81 (201.90) & 0.006 (0.005) \\
\hline \multicolumn{5}{|l|}{IVa: PPG-400 (1) + PEG-600 (2) + $\mathrm{H}_{2} \mathrm{O}$ (3)-SAFT-VR} \\
\hline 0.1-10.0 & 250-450 & 28.76 (5.75) & 1240.98 (241.78) & 0.106 (0.024) \\
\hline \multicolumn{5}{|l|}{IVb: PPG-400 (1) + PEG-21200 (2) + H2 O (3)-SAFT-VR} \\
\hline 0.1-10.0 & 250-450 & 40.52 (23.46) & 1559.91 (821.21) & 0.136 (0.053) \\
\hline \multicolumn{5}{|l|}{V: $\mathrm{N}_{2}(1), \mathrm{C}_{3} \mathrm{H}_{8}(2), \mathrm{C}_{2} \mathrm{H}_{4}(3), \mathrm{C}_{4} \mathrm{H}_{8}(4)$ and PE $\mathbf{1 2 , 0 0 0 ~} \mathrm{g} \mathrm{mol}^{-1}(5)$-SAFT-VR} \\
\hline 0.1-10.0 & 250-450 & 88.17 (27.18) & 3162.29 (1012.0) & 0.202 (0.0709) \\
\hline \multicolumn{5}{|l|}{VI: $\mathrm{N}_{2}(1), \mathrm{C}_{3} \mathrm{H}_{8}(2), \mathrm{C}_{2} \mathrm{H}_{4}(3), \mathrm{C}_{4} \mathrm{H}_{8}(4), \mathrm{nC}_{6}-\mathrm{nC}_{10}(5)-(9)$ and PE $12,000 \mathrm{~g} \mathrm{~mol}^{-1}(10)$-SAFT-VR} \\
\hline 0.1-10.0 & 250-450 & 293.17 (110.55) & 19577.15 (8715.10) & 8.37 (3.58) \\
\hline \multicolumn{5}{|l|}{VII: $\mathrm{N}_{2}(1), \mathrm{C}_{3} \mathrm{H}_{8}(2), \mathrm{C}_{2} \mathrm{H}_{4}(3), \mathrm{C}_{4} \mathrm{H}_{8}(4), \mathrm{nC}_{6}-\mathrm{nC}_{15}(5)-(14)$ and PE 12,000 g mol ${ }^{-1}(15)$-SAFT-VR} \\
\hline 0.1-10.0 & 250-450 & 690.89 (217.74) & 69561.14 (25070.76) & 81.27 (10.28) \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 3
Solution of fluid phase equilibrium with the HELD algorithm for selected point calculations with systems I to IV. The composition vectors listed are in mole fraction.}
\begin{tabular}{|l|l|l|l|}
\hline & $\underline{x}$ & $\eta$ & $V\left[\mathrm{~m}^{3} / \mathrm{mol}\right]$ \\
\hline \multicolumn{4}{|l|}{I: $\mathrm{H}_{2} \mathrm{~S}(1)+\mathrm{CH}_{4}(2)$ at 190 K and $4.53 \mathrm{MPa}-\mathrm{SRK}$} \\
\hline $\underline{x}^{0}$ & [0.05,0.95] & & \\
\hline Phase I (V) & [ $1.731 \times 10^{-2}, 0.98269$ ] & 0.03580 & $2.08 \times 10^{-4}$ \\
\hline Phase II (L) & [0.06618,0.93382] & 0.11283 & $6.62 \times 10^{-5}$ \\
\hline $\underline{x}^{0}$ & [0.5,0.5] & & \\
\hline Phase I (L) & [0.07969,0.92031] & 0.11752 & $6.35 \times 10^{-5}$ \\
\hline Phase II (L) & [0.88861,0.11139] & 0.20553 & $3.65 \times 10^{-5}$ \\
\hline \multicolumn{4}{|l|}{II: Athermal polymer (1) + colloid (2)-SAFT-HS (TPT1)} \\
\hline $x^{0}$ & [0.2,0.8] & & \\
\hline $T^{*}$ & 0.2 & & \\
\hline Phase I (L) & [ $1.10 \times 10^{-4}, 0.99989$ ] & 0.39312 & $8.02 \times 10^{-4}$ \\
\hline Phase II (V) & [0.86668,0.13332] & 0.04044 & 0.00177 \\
\hline $x^{0}$ & [0.12,0.78] & & \\
\hline $T^{*}$ & 0.97 & & \\
\hline Phase I (L) & [0.09775,0.90225] & 0.15469 & 0.00186 \\
\hline Phase II (L) & [0.12991,0.87009] & 0.14164 & 0.00197 \\
\hline \multicolumn{4}{|l|}{III: $\mathrm{C}_{2} \mathrm{H}_{6}(1)+\mathrm{CO}_{2}(2)$ at 223.25 K and $0.9 \mathrm{MPa}-$ SAFT-VR} \\
\hline $\underline{x}^{0}$ & [0.6,0.4] & & \\
\hline Phase I (V) & [0.59092, 0.40908] & 0.01419 & $1.76010 \times 10^{-3}$ \\
\hline Phase II (L) & [0.71543, 0.28457] & 0.32959 & $7.93441 \times 10^{-5}$ \\
\hline \multicolumn{4}{|l|}{III: $\mathrm{C}_{2} \mathrm{H}_{6}(1)+\mathrm{CO}_{2}(2)$ at 293.15 K and $6.1 \mathrm{MPa}-$ SAFT-VR} \\
\hline $\underline{x}^{0}$ & [0.09,0.01] & & \\
\hline Phase I (V) & [0.09568,0.90432] & 0.09999 & $2.03547 \times 10^{-4}$ \\
\hline Phase II (L) & [0.08460, 0.91540] & 0.20806 & $9.73197 \times 10^{-5}$ \\
\hline \multicolumn{4}{|l|}{IVa: PPG-400 (1)+PEG-600 (2)+ $\mathrm{H}_{2} \mathrm{O}$ (3) at 278 K and 5 MPa -SAFT-VR} \\
\hline $\underline{x}^{0}$ & [0.01,0.001,0.989] & & \\
\hline Phase I (L) & [0.02955,0.00675,0.96370] & 0.48926 & $3.39 \times 10^{-5}$ \\
\hline Phase II (L) & [0.00913,0.00074,0.99013] & 0.49629 & $2.20 \times 10^{-5}$ \\
\hline \multicolumn{4}{|l|}{IVb: PPG-400 (1)+PEG-21200 (2) + $\mathrm{H}_{2} \mathrm{O}$ (3) at 380 K and 0.25 MPa -SAFT-VR} \\
\hline $\underline{x}^{0}$ & [0.01,0.001,0.989] & & \\
\hline Phase I (L) & [ $8.8 \times 10^{-8}, 5.3 \times 10^{-11}, 1.0$ ] & 0.45886 & $1.92 \times 10^{-5}$ \\
\hline Phase II (L) & [0.02426,0.00243,0.97331] & 0.43132 & $7.96 \times 10^{-5}$ \\
\hline $\underline{x}^{0}$ & [0.0001,0.0001,0.9998] & & \\
\hline Phase I (L) & [0.00005,0.00052,0.99943] & 0.45263 & $2.92 \times 10^{-5}$ \\
\hline Phase II (L) & [ $2.1 \times 10^{-8}, 1.8 \times 10^{-6}, 1.0$ ] & 0.45884 & $1.92 \times 10^{-5}$ \\
\hline Phase III (L) & [0.00661,0.00172,0.99167] & 0.43833 & $5.63 \times 10^{-5}$ \\
\hline
\end{tabular}
\end{table}
which components are considered as hard fully-repulsive (athermal) particles so that only the ideal, hard sphere and chain terms are considered to contribute to the SAFT-HS Helmholtz free energy. The polymer and colloid comprise spherical segments of diameter $\sigma_{\text {polymer }}$ and $\sigma_{\text {colloid }}$, respectively. The colloid contains only one segment $m_{\text {colloid }}=1$, while the polymer contains $m_{\text {polymer }} \gg 1$. In this type of system, there are only two parameters that affect
the phase behaviour: the number of spherical segments in the polymer chain, and the ratio of the diameters of the spherical segments used to represent the two components. Such a system was examined by Paricaud, Galindo, and Jackson (2003) with a polymer chain length of $m=500$, and a polymer/colloid diameter ratio of $\sigma_{\text {polymer }} / \sigma_{\text {colloid }}=0.06$. The temperature-composition phase diagram of this system is presented in Fig. 4(a). In this case we employ

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 4
Statistics for selected point fluid phase equilibria calculations for systems I to IV, as denoted by $\underline{x}^{0}, P^{0}$ and $T^{0}$, averaged over 100 repeated calculations. IT is the mean total number of major iterations required for the solution of the dual, Sol. IT is the mean major iteration at which the solution is obtained, EOS Eval. is the mean number of times the equation of state is evaluated, and CPU is the mean number of seconds required to solve the whole problem. Sd. is the corresponding standard deviation.}
\begin{tabular}{|l|l|l|l|l|l|l|}
\hline State & $\underline{x}^{0}$ & $P^{0}[\mathrm{MPa}]$ & $T^{0}[\mathrm{~K}]$ & IT (Sd.) & EOS Eval. (Sd.) & CPU (Sd.) [s] \\
\hline \multicolumn{7}{|l|}{I: $\mathbf{H}_{2} \mathbf{S} \boldsymbol{(} \mathbf{1} \boldsymbol{)} \boldsymbol{+} \mathbf{C H}_{4} \boldsymbol{(} \mathbf{2} \boldsymbol{)} \boldsymbol{-} \mathbf{S R K}$} \\
\hline VLE & [0.05,0.095] & 4.53 & 190 & 21.23 (12.13) & 707.4 (329.64) & 0.006 (0.005) \\
\hline LLE & [0.5,0.5] & 4.53 & 190 & 17.82 (6.48) & 542.60 (185.24) & 0.005 (0.004) \\
\hline \multicolumn{7}{|l|}{II: Athermal polymer (1) + colloid (2)-SAFT-HS (TPT1)} \\
\hline VLE & [0.2,0.8] & n/a & $T^{*}=0.2$ & 11.61 (3.48) & 493.48 (118.344) & 0.006 (0.004) \\
\hline VLE & [0.2,0.8] & n/a & $T^{*}=0.9$ & 12.26 (3.22) & 587.27 (133.64) & 0.006 (0.005) \\
\hline \multicolumn{7}{|l|}{III: $\mathbf{C}_{\mathbf{2}} \mathbf{H}_{\mathbf{6}}(\mathbf{1})+\mathbf{C O}_{\mathbf{2}}(\mathbf{2})$-SAFT-VR} \\
\hline VLE & [0.6,0.4] & 0.9 & 223.25 & 13.78 (3.29) & 405.06 (99.59) & 0.006 (0.004) \\
\hline VLE & [0.09,0.01] & 6.1 & 293.15 & 30.59 (14.62) & 778.21 (302.27) & 0.008 (0.004) \\
\hline \multicolumn{7}{|l|}{IVa: PPG-400 (1) + PEG-600 (2) + $\mathrm{H}_{2} \mathrm{O}$ (3)-SAFT-VR} \\
\hline LLE & [0.01,0.001,0.989] & 5.0 & 278 & 24.26 (5.46) & 1144.12 (215.18) & 0.10 (0.03) \\
\hline \multicolumn{7}{|l|}{IVb: PPG-400 (1) + PEG-21200 (2) + H2O (3)-SAFT-VR} \\
\hline LLE & [0.01,0.001,0.989] & 0.25 & 380 & 37.44 (9.66) & 1826.23 (459.88) & 0.152 (0.046) \\
\hline LLLE & [0.0001,0.0001,0.9998] & 0.25 & 380 & 36.23 (6.90) & 1887.24 (306.67) & 0.147 (0.052) \\
\hline
\end{tabular}
\end{table}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/a19475d2-f89b-4570-8216-62f59ef156d5-12.jpg?height=1060&width=1530&top_left_y=176&top_left_x=249}
\captionsetup{labelformat=empty}
\caption{Fig. 4. Fluid phase behaviour and free energy of system II, an athermal polymer + colloid mixture, modelled with the SAFT-HS (TPT1) EOS. (a) Reduced temperature-composition phase diagram. The dashed lines correspond to $T^{*}=0.2, T^{*}=0.97$ and $T^{*}=1.1$; reduced Gibbs free energy of mixing (b) at $T^{*}=0.2$, (c) at $T^{*}=0.97$, and (d) at $T^{*}=1.1$.}
\end{figure}
a reduced temperature $T^{*}$ defined as $T^{*}=k T /\left(P \sigma_{\text {colloid }}^{3}\right)=1 / P^{*}$. One may specify either $T^{*}$ or $P^{*}$, but not both.

The point calculations are at $T^{*}=0.2$ for a global composition of $\underline{x}^{0}=[0.2,0.8]^{T}$, and $T^{*}=0.97$ for a global composition of $\underline{x}^{0}= [0 . \overline{1} 2,0.78]^{T}$. The details of these phase splits are given in Table 3. At $T^{*}=0.2$ the phase split is very extreme, with almost no polymer in the less dense phase, and $T^{*}=0.97$ is very close to the critical point. The reduced Gibbs free energies of mixing for the two different $T^{*}$ values are presented in Fig. 4(b) and (c). For comparison, the free energy of mixing of a super-critical state, at $T^{*}=1.1$ is also presented, in Fig. 4(d). The results of the reliability testing are reported in Table 2, and Table 4 contains the performance statistics for the point calculations.

\subsection*{4.2.2. System III: binary mixture of ethane and carbon dioxide-SAFT-VR}

The first system modelled with SAFT-VR is a binary mixture of ethane ( $\mathrm{C}_{2} \mathrm{H}_{4}$ ) and carbon dioxide ( $\mathrm{CO}_{2}$ ), as examined by Galindo and Blas (2002). This system was chosen because it exhibits positive (minimum boiling) azeotropy at some conditions. In Fig. 5(a) the $P-x$ phase diagrams for the mixture at 223.25 and 293.15 K are shown, as represented in Galindo and Blas (2002). At these conditions the azeotrope is clearly seen, and additionally, the higher temperature is close to the critical region.

The point calculations are undertaken at two sets of conditions; $223.25 \mathrm{~K}, 9.0 \times 10^{5} \mathrm{~Pa}$ and $\underline{x}^{0}=[0.6,0.4]^{T}$ and 293.15 K , $6.1 \times 10^{6} \mathrm{~Pa}$ and $\underline{x}^{0}=[0.09,0.01]^{T}$. The reduced Gibbs free energy of mixing for both conditions is plotted in Fig. 5(b) and the two separate regions of VLE in both cases are clearly seen. The results of the reliability testing are reported in Table 2, while Table 3 contains details of the phase splits for the fluid states at the given conditions and Table 4 contains the performance statistics for these point calculations.

\subsection*{4.2.3. Systems IVa and IVb: ternary mixtures of PPG, PEG and water-SAFT-VR}

The next two systems are ternary associating mixtures of the polymers polypropylene glycol (PPG, $\left.\mathrm{HO}-\left[\mathrm{CH}_{2}-\mathrm{CH}(-\mathrm{CH})_{3}-\mathrm{O}\right)\right]_{n} \mathrm{H}$ ) and polyethylene glycol (PEG, $\mathrm{H}-\left[\mathrm{O}-\mathrm{CH}_{2}-\mathrm{CH}_{2}\right]_{n}-\mathrm{OH}$ ) with water $\left(\mathrm{H}_{2} \mathrm{O}\right)$. Two different ternary mixtures are studied, selected from models presented in the PhD thesis of Clark (2007). The first is an aqueous solution of PPG of molecular weight $400 \mathrm{~g} \mathrm{~mol}^{-1}$ and PEG of $600 \mathrm{~g} \mathrm{~mol}^{-1}$, and the phase diagram of this system at 278 K and 5 MPa is shown in Fig. 6(a). At these conditions, the mixture exhibits a closed loop of liquid-liquid immiscibility that does not touch the sides of the triangular diagram, since all three binary pairs are fully miscible. The second mixture is also an aqueous solution of PPG of $400 \mathrm{~g} \mathrm{~mol}^{-1}$, but the size of the PEG is increased to $21,200 \mathrm{~g} \mathrm{~mol}^{-1}$. At 380 K and 0.25 MPa this mixture exhibits three liquid phases in equilibrium, LLLE, as illustrated in Fig. 6(b).

The statistics from the reliability testing for both systems are shown in Table 2. One point calculation is shown for system IVa, inside the LLE region, while two point calculations are shown for system IVb at different global compositions, in the LLE and LLLE regions. The details of these phase splits and associated performance statistics are presented in Tables 3 and 4. This system presents particular challenges as there are strong association interactions between the various components in the mixtures, and a large size asymmetry between the two polymers and water, both factors that contribute to highly non-ideal behaviour. In spite of this, the HELD algorithm performs reliably in all calculations and the computational load remains very modest.

\subsection*{4.2.4. System V: five component mixture of light gases and polyethylene-SAFT-VR}

The fluid phase equilibria of this system has been modelled with SAFT-VR by Haslam et al. (2006), in the context of predicting the

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/a19475d2-f89b-4570-8216-62f59ef156d5-13.jpg?height=1097&width=1554&top_left_y=176&top_left_x=279}
\captionsetup{labelformat=empty}
\caption{Fig. 5. Fluid phase behaviour and Gibbs free energy of mixing of system III, a binary mixture of $\mathrm{C}_{2} \mathrm{H}_{6}+\mathrm{CO}_{2}$, modelled with the SAFT-VR EOS. (a) and (b) Pressure-composition $(P-x)$ phase diagrams at 223.25 and 293.15 K , respectively. (c) Reduced Gibbs free energy of mixing for $T=223.25 \mathrm{~K}$ and $P=0.9 \mathrm{MPa}$ (continuous curve), and $T=293.15 \mathrm{~K}$ and $P=6.1 \mathrm{MPa}$ (dotted curve).}
\end{figure}
absorption (VLE) of various light gases in polyethylene. Successful prediction of gas absorption is important for accurate modelling of gas-phase polymer production processes. Solution of the fluid phase equilibria in systems such as this is complicated by the asymmetry in size of the molecules. This can produce phase splits in which some components are only present in very small quantities in some phases; for example, this often occurs with polymer components in the vapour phase. In addition, these systems exhibit multiple liquid phases at some conditions. The mixture contains polyethylene (PE) of molecular weight $12,000 \mathrm{~g} \mathrm{~mol}^{-1}$, nitrogen,
propane, ethene, and but-1-ene. The mole fractions of four of the five components, in each phase, are plotted against pressure, at a constant temperature of $T=353 \mathrm{~K}$ in Fig. 7(a) and (b). The statistics for calculations with this system are reported in Tables 2, 5 and 7. The mole fractions of polymer in the vapour phases of this, and systems VI and VII, are very low. In Table 7 this is simply recorded as zero but the value obtained from resolution of the logarithmic problem described in Pereira et al. (2010), to refine the mole fraction of the trace component, is of the order of $10^{-200}$ mole fraction, which is well below meaningful values.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/a19475d2-f89b-4570-8216-62f59ef156d5-13.jpg?height=563&width=1519&top_left_y=1911&top_left_x=292}
\captionsetup{labelformat=empty}
\caption{Fig. 6. (a) Fluid phase diagram for system IVa, a ternary mixture of PPG-400+PEG-600+ water $\left(\mathrm{H}_{2} \mathrm{O}\right)$ at $T=278 \mathrm{~K}$ and $P=5 \mathrm{MPa}$ and (b) fluid phase diagram for system IVb, a ternary mixture of PPG-400+PEG-21200+water $\left(\mathrm{H}_{2} \mathrm{O}\right)$ at $T=380 \mathrm{~K}$ and $P=0.25 \mathrm{MPa}$. The continuous curve is the phase boundary, the dashed lines are tie lines joining the stable equilibrium phases, and both phase diagrams are in mass fraction.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/a19475d2-f89b-4570-8216-62f59ef156d5-14.jpg?height=499&width=1640&top_left_y=180&top_left_x=195}
\captionsetup{labelformat=empty}
\caption{Fig. 7. Phase separation in system V, a five component mixture of $\mathrm{N}_{2}(1), \mathrm{C}_{3} \mathrm{H}_{8}(2), \mathrm{C}_{2} \mathrm{H}_{4}(3), \mathrm{C}_{4} \mathrm{H}_{8}(4)$ and PE $12,000 \mathrm{~g} \mathrm{~mol}^{-1}(5)$ at 353 K and an overall composition of $\underline{x}^{0}=[0.5,0.2,0.1,0.19,0.01]^{T}$. (a) The mole fraction of each component in the liquid phase is shown (apart from $\mathrm{C}_{2} \mathrm{H}_{4}$, which is only present at around $10^{-4}$ mole fraction). (b) The mole fraction of each component in the vapour phase is shown (apart from PE, which is present in very small quantities, with values below the lower bound on composition, $10^{-8}$ ).}
\end{figure}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 5
Solution of fluid phase equilibrium with the HELD algorithm for selected point calculations with systems V to VII. The composition vectors listed are in mole fraction.}
\begin{tabular}{|l|l|l|l|}
\hline & $\underline{x}$ & $\eta$ & $V\left[\mathrm{~m}^{3} / \mathrm{mol}\right]$ \\
\hline \multicolumn{4}{|l|}{V: $\mathrm{N}_{2}(1), \mathrm{C}_{3} \mathrm{H}_{8}(2), \mathrm{C}_{2} \mathrm{H}_{4}(3), \mathrm{C}_{4} \mathrm{H}_{8}(4)$ and PE $12,000 \mathrm{~g} \mathrm{~mol}^{-1}(5)$ at 353 K and 2 MPa -SAFT-VR} \\
\hline $\underline{x}^{0}$ & [0.5,0.2,0.1, 0.19,0.01] & & \\
\hline Phase I (V) & [0.59550,0.16542, 0.12073,0.11836,0.0] & 0.01343 & $9.24 \times 10^{-4}$ \\
\hline Phase II (L) & [0.04078,0.36617,0.00030,0.53468,0.05807] & 0.39673 & 0.00146 \\
\hline \multicolumn{4}{|l|}{V: $\mathrm{N}_{2}(1), \mathrm{C}_{3} \mathrm{H}_{8}(2), \mathrm{C}_{2} \mathrm{H}_{4}(3), \mathrm{C}_{4} \mathrm{H}_{8}(4)$ and PE $12,000 \mathrm{~g} \mathrm{~mol}^{-1}(5)$ at 450 K and 5 MPa -SAFT-VR} \\
\hline $\underline{x}^{0}$ & [0.4,0.3,0.05, 0.19,0.06] & & \\
\hline Phase I (V) & [0.67534,0.14857,0.11093,0.06516,0.0] & 0.02346 & $7.72 \times 10^{-4}$ \\
\hline Phase II (L) & [0.18638,0.41749,0.00271,0.28687,0.10656] & 0.36958 & $1.74 \times 10^{-3}$ \\
\hline \multicolumn{4}{|l|}{\multirow{2}{*}{\begin{tabular}{l}
VI: $\mathrm{N}_{2}$ (1), $\mathrm{C}_{3} \mathrm{H}_{8}$ (2), $\mathrm{C}_{2} \mathrm{H}_{4}$ (3), $\mathrm{C}_{4} \mathrm{H}_{8}$ (4), $\mathrm{nC}_{6}-\mathrm{nC}_{10}$ (5)-(9) and PE $12,000 \mathrm{~g} \mathrm{~mol}^{-1}$ (10) at 353 K and 2 MPa -SAFT-VR \\
$\underline{x}^{0}$ \\
[0.5,0.2,0.1,0.14,0.01,0.01,0.01,0.01,0.01,0.01]
\end{tabular}}} \\
\hline & & & \\
\hline Phase I (V) & [0.61881,0.16567,0.12567,0.08520,0.00225, $\left.0.00136,6.16 \times 10^{-4}, 3.12 \times 10^{-4}, 1.48 \times 10^{-4}, 0.0\right]$ & 0.01308 & 0.00146 \\
\hline Phase II (L) & $\left[0.03880,0.33383,2.88 \times 10^{-4}, 0.35242,0.04010\right.$, 0.04370,0.04631,0.04780,0.04811,0.04876] & 0.39573 & $8.05 \times 10^{-4}$ \\
\hline \multicolumn{4}{|l|}{VI: $\mathrm{N}_{2}(1), \mathrm{C}_{3} \mathrm{H}_{8}(2), \mathrm{C}_{2} \mathrm{H}_{4}(3), \mathrm{C}_{4} \mathrm{H}_{8}(4), \mathrm{nC}_{6}-\mathrm{nC}_{10}(5)-(9)$ and PE $12,000 \mathrm{~g} \mathrm{~mol}^{-1}(10)$ at 450 K and $5 \mathrm{MPa}-$ SAFT-VR} \\
\hline $\underline{x}^{0}$ & [0.4,0.3,0.05,0.14,0.01,0.01,0.01,0.01,0.01,0.06] & & \\
\hline Phase I (V) & [0.68610,0.14806,0.11365,0.04769,0.00167, 0.00124,0.00076,0.00051,0.00033,0.0] & 0.02325 & $7.73 \times 10^{-4}$ \\
\hline Phase II (L) & [0.18753,0.41278,0.00275,0.20860,0.01619, 0.01649,0.01686,0.01706,0.01717,0.10459] & 0.36951 & $1.72 \times 10^{-3}$ \\
\hline
\end{tabular}
\end{table}

\subsection*{4.2.5. Systems VI and VII: ten and fifteen component mixtures of light gases and polyethylene}

In order to investigate the performance of the proposed algorithm in higher dimensions, more components are added to the mixture of system V, and the evolution of the algorithmic statistics is examined. System VI contains all of the five components present in system V, and the additional five components are linear alkanes of carbon chain length 6 to 10, present in small quantities. The components in this mixture are: $\mathrm{N}_{2}(1), \mathrm{C}_{3} \mathrm{H}_{8}$
(2), $\mathrm{C}_{2} \mathrm{H}_{4}$ (3), $\mathrm{C}_{4} \mathrm{H}_{8}$ (4), $\mathrm{nC}_{6}-\mathrm{nC}_{10}$ (5)-(9) and PE $12,000 \mathrm{~g} \mathrm{~mol}^{-1}$ (10). In system VII, yet more linear alkanes are added to system VI, and the system comprises: $\mathrm{N}_{2}(1), \mathrm{C}_{3} \mathrm{H}_{8}(2), \mathrm{C}_{2} \mathrm{H}_{4}(3)$, $\mathrm{C}_{4} \mathrm{H}_{8}$ (4), $\mathrm{nC}_{6}-\mathrm{nC}_{15}$ (5)-(14) and PE $12,000 \mathrm{~g} \mathrm{~mol}^{-1}$ (15). The SAFT-VR parameters for the linear alkanes are obtained from Paricaud, Galindo, and Jackson (2004). The reliability testing for both systems is documented in Table 2. The details of the phase splits for the point calculations for system VI are shown in Table 5, and for system VII in Table 6. Finally, the statistics for

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 6
Solution of fluid phase equilibrium with the HELD algorithm for selected point calculations for system VII. The composition vectors listed are in mole fraction.}
\begin{tabular}{|l|l|l|l|}
\hline & $\underline{x}$ & $\eta$ & $V\left[\mathrm{~m}^{3} / \mathrm{mol}\right]$ \\
\hline \multicolumn{4}{|l|}{VII: $\mathrm{N}_{2}$ (1), $\mathrm{C}_{3} \mathrm{H}_{8}$ (2), $\mathrm{C}_{2} \mathrm{H}_{4}$ (3), $\mathrm{C}_{4} \mathrm{H}_{8}(4), \mathrm{nC}_{6}-\mathrm{nC}_{15}(5)-(14)$ and PE $12,000 \mathrm{~g} \mathrm{~mol}^{-1}(15)$ at 353 K and 2 MPa -SAFT-VR} \\
\hline $\underline{x}^{0}$ & [0.5,0.2,0.1,0.09,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01] & & \\
\hline \multicolumn{4}{|c|}{
![](https://cdn.mathpix.com/cropped/a19475d2-f89b-4570-8216-62f59ef156d5-14.jpg?height=33\&width=671\&top_left_y=2288\&top_left_x=373)} \\
\hline Phase II (L) & [0.02007,0.32459,0.00016,0.11124,0.00874,0.06072,0.06086,0.06073,0.06051, 0.05966,0.05856,0.05581,0.05025,0.03931,0.02879] & 0.35986 & $1.647 \times 10^{-4}$ \\
\hline \multicolumn{4}{|l|}{VII: $\mathrm{N}_{2}$ (1), $\mathrm{C}_{3} \mathrm{H}_{8}$ (2), $\mathrm{C}_{2} \mathrm{H}_{4}$ (3), $\mathrm{C}_{4} \mathrm{H}_{8}(4), \mathrm{nC}_{6}-\mathrm{nC}_{15}(5)-(14)$ and PE $12,000 \mathrm{~g} \mathrm{~mol}^{-1}(15)$ at 450 K and $5 \mathrm{MPa}-$ SAFT-VR} \\
\hline $\underline{x}^{0}$ & [0.4,0.3,0.05,0.09,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.06] & & \\
\hline Phase I (V) & [0.41829,0.30054,0.05253, & 0.03418 & $7.132 \times 10^{-4}$ \\
\hline & 0.14265,0.06069,0.00044,0.00091,0.00105,0.00160,0.0023,0.00274,0.00336,0.00390,0.00438,0.00464] & & \\
\hline \multicolumn{4}{|c|}{} \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 7
Statistics for selected fluid phase point calculations with the HELD algorithm for systems V to VII, as denoted by $\underline{x}^{0}, P^{0}$ and $T^{0}$, averaged over 100 repeat runs. IT is the mean total number of major iterations required for solution of the dual, Sol. IT is the mean major iteration at which the solution is obtained, EOS Eval. is the mean number of times the equation of state is evaluated, and CPU is the mean number of seconds required to solve the whole problem. Sd. is the corresponding standard deviation.}
\begin{tabular}{|l|l|l|l|l|l|l|}
\hline State & $\underline{x}^{0}[\mathrm{MPa}]$ & $P^{0}[\mathrm{~K}]$ & $T^{0}$ & IT (Sd.) & EOS Eval. (Sd.) & CPU (Sd.) [s] \\
\hline \multicolumn{7}{|l|}{V: $\mathrm{N}_{2}$ (1), $\mathrm{C}_{3} \mathrm{H}_{8}$ (2), $\mathrm{C}_{2} \mathrm{H}_{4}$ (3), $\mathrm{C}_{4} \mathrm{H}_{8}$ (4) and PE $12,000 \mathrm{~g} \mathrm{~mol}^{-1}$ (5)-SAFT-VR} \\
\hline VLE & [0.5,0.2,0.1,0.19,0.01] & 2.0 & 353.0 & 85.17 (22.40) & 2846.61 (692.52) & 0.194 (0.06) \\
\hline VLE & [0.4,0.3,0.050.19,0.01] & 5.0 & 450.0 & 74.28 (20.25) & 2520.29 (703.38) & 0.181 (0.05) \\
\hline \multicolumn{7}{|l|}{VI: $\mathrm{N}_{2}$ (1), $\mathrm{C}_{3} \mathrm{H}_{8}$ (2), $\mathrm{C}_{2} \mathrm{H}_{4}$ (3), $\mathrm{C}_{4} \mathrm{H}_{8}(4), \mathrm{nC}_{6}-\mathrm{nC}_{10}(5)-(9)$ and PE $12,000 \mathrm{~g} \mathrm{~mol}^{-1}(10)$-SAFT-VR} \\
\hline VLE & [0.5,0.2,0.1,0.14,0.01,0.01,0.01,0.01,0.01,0.01] & 2.0 & 353.0 & 225.37 (48.54) & 14782.73 (3213.82) & 6.55 (2.90) \\
\hline VLE & [0.4,0.3,0.05,0.14,0.01,0.01,0.01,0.01,0.01,0.06] & 5.0 & 450.0 & 338.67 (118.01) & 24370.40 (9598.25) & 8.01 (2.67) \\
\hline \multicolumn{7}{|l|}{VII: $\mathrm{N}_{2}(1), \mathrm{C}_{3} \mathrm{H}_{8}(2), \mathrm{C}_{2} \mathrm{H}_{4}(3), \mathrm{C}_{4} \mathrm{H}_{8}(4), \mathrm{nC}_{6}-\mathrm{nC}_{15}(5)-(14)$ and PE $12,000 \mathrm{~g} \mathrm{~mol}^{-1}(15)-$ SAFT-VR} \\
\hline VLE & [0.5,0.2,0.1,0.09,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01] & 2.0 & 353.0 & 508.61 (112.25) & 50023.32 (10782.24) & 60.72 (30.0) \\
\hline VLE & [0.4,0.3,0.05,0.09,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.06] & 5.0 & 450.0 & 790.65 (126.94) & 83440.10 (13784.35) & 90.90 (45.21) \\
\hline
\end{tabular}
\end{table}
these points calculations are presented in Table 7, for both systems.

\section*{5. Discussion}

The analysis of the HELD algorithm begins with the reliability tests. The results of these are shown in Table 2, which summarises the 80,000 solutions of PE that have been carried out during the testing. The range of conditions included in the random selection is wide, providing a rigorous test for the proposed algorithm, since the point calculations presented cover a range of challenging types of fluid phase behaviour. No failures are observed in any of the 80,000 calculations, meaning that the algorithm converged to the correct phase split in all cases. Consequently, the proposed HELD algorithm is shown to be reliable, at least for the systems considered in this work, which are chosen primarily for the high degree of non-ideality in the phase behaviour that they exhibit. We do acknowledge, however, that there is no standardised set of test cases for phase equilibrium algorithms dealing with complex EOS. Such a set would provide an invaluable route to verifying the reliability of phase equilibrium algorithms, in an objective manner.

In terms of performance, the computational demands are reasonable, particularly for the lower dimensions. The longest CPU time for a binary example is only around 0.007 s , in the case of the $\mathrm{C}_{2} \mathrm{H}_{6}+\mathrm{CO}_{2}$ mixture. In general, the CPU time increases significantly with the number of components. Calculations on the five-component mixture require on the order of 0.2 s , while the tencomponent mixture requires around 9 s and the fifteen component around 80 s . The longer computational time is due to increases in the total number of major iterations required to solve the problem, in the number of compositional derivatives that need to be evaluated at each iteration of the algorithm, and in the number of iterations required by the SQP solver. A smaller contribution is due to the increased cost of the thermodynamic function evaluations.

HELD fits into the category of stochastic global optimisation algorithms, and it would be interesting to compare its performance with other methods of this type. Whilst detailed computational statistics have been published describing the performance of various methods in stability testing, there is relatively little information of this sort available for the entire stability + phase-split calculation. Nichita et al. (2002b) do report function evaluations (FE) for the entire stability-phase split calculation, applying a tunnelling global optimisation algorithm to examples with cubic equations of state. They report the number of function evaluations required for calculations on various binary mixtures as $\sim 600-1800 \mathrm{FE}$, and for a ternary mixture of methane + ethane + nitrogen as $\sim 3000-4700 \mathrm{FE}$. If one makes an assumption that each function evaluation in this work requires a call to the EOS, then we may compare the figures with those for HELD. Under such analysis, the computational requirements of the two approaches are roughly comparable.

When comparing the computational performance of various methods, one should also keep in the mind the properties of the test systems presented. In this work, we have endeavored to demonstrate the generality of HELD by carrying out calculations with highly non-ideal mixtures, such as highly asymmetric polymer + solvent mixtures. Many phase-split methods in the literature are based on successive substitution schemes, which would often not converge when faced with the degree of non-ideality present in some of the example mixtures presented here.

\section*{6. Conclusions}

The HELD algorithm for the solution of $P, T$ phase equilibrium (PE) has been presented. This algorithm is used to solve the PE problem formulated as the dual of a Helmholtz free energy minimisation in the volume-composition space. No user supplied initial guesses are required for any aspect of the algorithm. The HELD algorithm is based on three stages: initialisation, solution of the dual formulation of the Helmholtz free minimisation, and acceleration and convergence tests. In the initialisation stage, a nonconvex stability test is solved using a tunneling method. In the second stage, a series of nonconvex inner problems is solved through multistart optimisation. Throughout the algorithm, steps are taken to avoid convergence to a local solution. In the final stage, the feasibility of the mass balance is tested and a refined solution of the free energy minimisation problem is obtained, including accurate values for trace component compositions.

The proposed method is implemented for a benchmark binary system of hydrogen sulphide and methane, with properties calculated using the SRK EOS. Further case studies are presented, in which properties are obtained through the SAFT-HS and the SAFT-VR EOSs. These systems comprise between two and fifteen components, including polymers, carbon dioxide and various hydrocarbons. The HELD algorithm is found to be reliable, where reliability is defined as the successful identification of the best known solution of a large number (i.e., 80,000 ) independent calculations. No failures are encountered during any of the calculations, even when working with very challenging systems. The computational demands increase significantly with dimensionality, and both algorithmic and computational approaches to improving the performance in higher dimensions are currently being explored. We are also exploring the relative merits of using a formulation in the volume-composition space or one in the composition space, where it is necessary to find the volume roots at the pressure of interest at each evaluation of the free energy.

\section*{Acknowledgements}
F.E.P. is grateful to the Engineering and Physical Sciences Research Council (EPSRC) of the UK for a PhD studentship and
a PhD Plus scholarship. Additional funding to the Molecular Systems Engineering Group from the EPSRC (grants GR/T17595, GR/N35991, GR/R09497, and EP/E016340), the Joint Research Equipment Initiative (JREI) (GR/M94427), and the Royal SocietyWolfson Foundation refurbishment grant is also acknowledged.

\section*{Appendix A. An example calculation with the HELD algorithm}

The steps involved in the calculation of the phase equilibrium with system IVb, a ternary mixture of PPG-400+ PEG-21200 + water $\left(\mathrm{H}_{2} \mathrm{O}\right)$ are described here. The system is modelled with the SAFT-VR EOS (Galindo et al., 1998; Gil-Villegas et al., 1997) and at the conditions of $T=380 \mathrm{~K}, P=0.25 \mathrm{~atm}$ and $\underline{x}^{0}=(0.0001,0.0001,0.9998)^{T}$, the stable equilibrium state is liquid-liquid-liquid equilibrium (LLLE).

\section*{Step 1: Stability test}

Find packing fraction $\eta^{0}$ that has the lowest Gibbs free energy at the feed conditions.
Minimisation 1 of tangent plane distance:
Random initial guess: $\underline{x}=(0.99914,0.00011,0.00075)^{T}$, $\eta=0.68664$.
Solution: $\quad \underline{x}^{*}=(0.28538,0.00888,0.70574)^{T}, \quad \eta^{*}=0.41340$, $d\left(\underline{x}^{*}, \eta^{*}\right)=-0.63551575$.
A negative value of $d\left(\underline{x}^{*}, \eta^{*}\right)=-0.63551575$ indicates instability and the stability test finishes.

\section*{Step 2: Initialisation}

Evaluate bounding vectors $\underline{\hat{x}}^{1}$ and $\underline{\mathcal{x}}^{1}$.

$$
\begin{aligned}
& \hat{x}_{1}^{1}=\frac{x_{1}^{0}}{2}=0.0005 ; \hat{x}_{2}^{1}=\frac{1-\hat{x}_{1}^{1}}{2}=0.49998 ; \hat{x}_{3}^{1}=\frac{1-\hat{x}_{1}^{1}}{2}=0.49998 . \\
& \bar{x}_{1}^{1}=\frac{1+x_{1}^{0}}{2}=0.50005 ; \bar{x}_{2}^{1}=\frac{1-\bar{x}_{1}^{1}}{2}=0.24998 ; \bar{x}_{3}^{1}=\frac{1-\bar{x}_{1}^{1}}{2}=0.24998 . \\
& \hat{x}_{2}^{2}=\frac{x_{2}^{0}}{2}=0.49998 ; \quad \hat{x}_{1}^{2}=\frac{1-\hat{x}_{2}^{2}}{2}=0.00005 ; \hat{x}_{3}^{2}=\frac{1-\hat{x}_{2}^{2}}{2}=0.49998 . \\
& \bar{x}_{2}^{2}=\frac{1+x_{2}^{0}}{2}=0.24998 ; \bar{x}_{1}^{2}=\frac{1-\bar{x}_{2}^{2}}{2}=0.50005 ; \bar{x}_{3}^{2}=\frac{1-\bar{x}_{2}^{2}}{2}= \\
& 0.24998 .
\end{aligned}
$$


Allocate arbitrary values for $\hat{\eta}^{1}, \bar{\eta}^{1}, \hat{\eta}^{2}$ and $\bar{\eta}^{2}$ to reduce computational cost; $\hat{\eta}^{1}=0.1, \bar{\eta}^{1}=0.1, \hat{\eta}^{2}=0.1$ and $\bar{\eta}^{2}=0.1$.

Contents of initial upper bounding set $\mathcal{M}= \left\{\left(\underline{\hat{x}}^{1}, \hat{\eta}^{1}\right),\left(\underline{\bar{x}}^{1}, \bar{\eta}^{1}\right),\left(\underline{\hat{x}}^{2}, \hat{\eta}^{2}\right),\left(\bar{x}^{2}, \bar{\eta}^{2}\right)\right\}$.
Initialise $U B D=G^{P}=3.57119477$ and $L B D=-\infty$.

\section*{Major iteration 1}

Step 1.3: Solve outer problem

$$
\begin{array}{ll}
\max _{\underline{\lambda}, v} & v \\
\text { s.t. } & v \leq G^{P} \\
& v \leq A\left(\underline{\hat{x}}^{1}, \hat{\eta}^{1}, T^{0}\right)+P^{0} f\left(\hat{\eta}^{1}\right)+\sum_{i=1}^{n c-1} \lambda_{i}\left(x_{i}^{0}-\hat{x}_{i}^{1}\right) \\
& v \leq A\left(\underline{\bar{x}}^{1}, \bar{\eta}^{1}, T^{0}\right)+P^{0} f\left(\bar{\eta}^{1}\right)+\sum_{i=1}^{n c-1} \lambda_{i}\left(x_{i}^{0}-\bar{x}_{i}^{1}\right) \\
& v \leq A\left(\underline{\hat{x}}^{2}, \hat{\eta}^{2}, T^{0}\right)+P^{0} f\left(\hat{\eta}^{2}\right)+\sum_{i=1}^{n c-1} \lambda_{i}\left(x_{i}^{0}-\hat{x}_{i}^{2}\right) \\
& v \leq A\left(\underline{\bar{x}}^{2}, \bar{\eta}^{2}, T^{0}\right)+P^{0} f\left(\bar{\eta}^{2}\right)+\sum_{i=1}^{n c-1} \lambda_{i}\left(x_{i}^{0}-\bar{x}_{i}^{2}\right)
\end{array}
$$


Solution: $\quad U B D^{V}=3.57119477, \quad \lambda_{1}^{(1)}=-25.65538775, \quad \lambda_{2}^{(1)}=$ -1106.32787750.

\section*{Step 1.4: Generation of a cutting plane}

Inner problem:

$$
\begin{array}{ll}
\min _{\underline{x}, \eta} & L^{V}(\underline{x}, \eta)=A(\underline{x}, \eta)+P^{0} f(\eta)+\sum_{i=1}^{n c-1} \lambda_{i}^{(1)}\left(x_{i}^{0}-x_{i}\right) \\
\text { s.t. } & L^{V}(\underline{x}, \eta) \leq U B D^{V}
\end{array}
$$


Local minimisation 1:

Random initial guess: $\underline{x}=(0.17027,0.41610,0.41363)^{T}$ and $\eta=0.00815$.
Solution: $\underline{x}^{*(1,1)}=(0.23736,0.07443,0.75520)^{T}, \eta^{*(1,1)}=0.41453$, $L^{*(1,1)}=3.10696513$.

An objective function value below the upper bound is obtained from local minimisation 1 and consequently the solution is accepted, and no further minimisations are carried out.
$L^{V(1)}=L^{*(1,1)}, \underline{\chi}^{(1)}=\underline{\chi}^{*(1,1)}, \eta^{(1)}=\eta^{*(1,1)}$.
Add $\left(\underline{\chi}^{(1)}, \eta^{(1)}\right)$ to $\mathcal{M}$.

\section*{Step 1.5: Search for candidate stable phases}

No points are found that satisfy system (PP).

\section*{Step 1.6: Increment iteration counter $k=2$. End of major iteration 1}

Major iterations continue but the details have been omitted.

\section*{Major iteration 24}

\section*{Step 24.3: Solve outer problem}

Solution: $U B D^{V}=3.57055119, \quad \lambda_{1}^{(24)}=-31.66573411, \quad \lambda_{2}^{(24)}=$ -1094.05619363.

\section*{Step 24.4: Generation of a cutting plane}

Local minimisation 1:

Random initial guess: $\underline{x}=(0.21326,0.00528,0.78146)^{T}$ and $\eta=0.00373$.
Solution: $\quad x^{*(24,1)}=(0.00661,0.00172,0.99167)^{T}, \quad \eta^{*(24,1)}= 0.43832, L^{*(24,1)}=3.57055119$.

An objective function value below the upper bound is obtained from local minimisation 1 and consequently no further minimisations are carried out.
$L^{V(24)}=L^{*(24,1)}, \underline{\chi}^{(1)}=\underline{\chi}^{*(24,1)}, \eta^{(24)}=\eta^{*(24,1)}$.
Add $\left(\underline{x}^{(24)}, \eta^{(24)}\right)$ to $\mathcal{M}$.

\section*{Step 24.5: Search for candidate stable phases}

Search through $\mathcal{M}$ for points fulfilling system (PP). One point found: $\underline{x}^{(m, 1)}=(0.00661,0.00172,0.99167)^{T}, \eta^{(m, 1)}=0.43832$.

At least two candidate phases are required to proceed to Stage III, since the mass balance cannot be feasible with only a single candidate stable phase.
Step 24.6: Increment iteration counter $k=25$.

\section*{End of major iteration 24}

\section*{Major iteration 25}

\section*{Step 25.3: Solve outer problem}

Solution: $U B D^{V}=3.57055119, \lambda_{1}^{(25)}=-31.66573411, \lambda_{2}^{(25)}=$ -1094.05619363.

\section*{Step 25.4: Generation of a cutting plane}

Local minimisation 1:

Random initial guess: $\underline{x}=(0.00018,0.04026,0.95956)^{T}$ and $\eta=0.07039$.
Solution: $\quad \underline{x}^{*(25,1)}=(0.000048,0.00052,0.99943)^{T}$, $\eta^{*(25,1)}=0.45260, L^{*(25,1)}=3.57055119$.

An objective function value below the upper bound is obtained from local minimisation 1 and consequently no further minimisations are carried out.
$L^{V(25)}=L^{*(25,1)}, \underline{x}^{(1)}=\underline{x}^{*(25,1)}, \eta^{(25)}=\eta^{*(25,1)}$.
Add $\left(\underline{x}^{(25)}, \eta^{(25)}\right)$ to $\mathcal{M}$.

\section*{Step 25.5: Search for candidate stable phases}

Search through $\mathcal{M}$ for points fulfilling system (PP).
Two points found: $\underline{x}^{(m, 1)}=(0.00661,0.00172,0.99167)^{T}$, $\eta^{(m, 1)}=0.43832 \quad$ and $\quad \underline{\bar{x}}^{(m, 2)}=(0.00018,0.04026,0.95956)^{T}$, $\eta^{(m, 2)}=0.45260$.

\section*{Step 25.7: Formulate $\left(\mathrm{GM}_{x, V}\right)$ and solve}

Convert $\underline{\chi}^{(m, 1)}$ and $\underline{\chi}^{(m, 2)}$ to mass number.

$$
\begin{array}{cl}
\underline{q}_{1}^{m}=\underline{\chi}^{(m, 1)} \underline{M W^{T}}=(2.644,36.464,17.865)^{T}, \\
\underline{q}_{2}^{m}=\underline{\chi}^{(m, 2)} \underline{M W^{T}}=(0.072,853.512,17.287)^{T} \\
\min _{\underline{q}_{1}, \underline{q}_{2}, V_{1}, V_{2}} & \left(A\left(\underline{q}_{1}, V_{1}^{\prime}, T^{0}\right)+P^{0} V_{1}^{\prime}+A\left(\underline{q}_{2}, V_{2}^{\prime}, T^{0}\right)+P^{0} V_{2}^{\prime}\right) \\
\text { s.t. } & q_{1,1}+q_{1,2}-q_{1}^{0}=0, \\
& q_{2,1}+q_{2,2}-q_{2}^{0}=0, \\
& q_{3,1}+q_{3,2}-q_{3}^{0}=0,  \tag{14}\\
& q_{1,1} \in[2.244,3.044], q_{2,1} \in[15.264,57.664], \\
& q_{3,1} \in[17.847,17.883], \\
& q_{1,2} \in\left[10^{-8}, 0.472\right], q_{2,2} \in[832.312,874.712], \\
& q_{3,2} \in[17.268,17.304] . \\
& V_{1} \in[\underline{V}, \bar{V}], V_{2} \in[\underline{V}, \bar{V}] .
\end{array}
$$


The linear constraints in problem (14) are infeasible, and therefore the algorithm continues.

\section*{Step 25.6: Increment iteration counter $k=26$.}

\section*{End of major iteration 25}

\section*{Major iteration 26}

\section*{Step 26.3: Solve outer problem}

Solution: $\quad U B D^{V}=3.57055119, \quad \lambda_{1}^{(26)}=-31.66573411$, $\lambda_{2}^{(26)}=-1094.05619363$.

\section*{Step 26.4: Generation of a cutting plane}

Local minimisation 1:
Random initial guess: $\underline{x}=(0.11160,0.098823,0.78957)^{T}$ and $\eta=0.73793$.
Solution: $\quad x^{*(26,1)}=\left(2.1 \times 10^{-8}, 1.79 \times 10^{-6}, 1.0\right)^{T}, \quad \eta^{*(26,1)}= 0.45884, L^{*(2 \overline{6}, 1)}=3.57055119$.

An objective function value below the upper bound is obtained from local minimisation 1 and consequently no further minimisations are carried out.
$L^{V(26)}=L^{*(26,1)}, \underline{\chi}^{(1)}=\underline{\chi}^{*(26,1)}, \eta^{(26)}=\eta^{*(26,1)}$.
Add ( $\underline{\chi}^{(26)}, \eta^{(26)}$ ) to $\mathcal{M}$.

\section*{Step 26.5: Search for candidate stable phases}

Search through $\mathcal{M}$ for points fulfilling system (PP).
Three points found:
$\underline{x}^{(m, 1)}=(0.00661,0.00172,0.99167)^{T}, \eta^{(m, 1)}=0.43832$,
$\underline{\bar{x}}^{(m, 2)}=(0.00018,0.04026,0.95956)^{T}, \eta^{(m, 2)}=0.45260$
and $\underline{x}^{(m, 3)}=\left(2.1 \times 10^{-8}, 1.79 \times 10^{-6}, 1.0\right)^{T}, \eta^{(m, 3)}=0.45884$.

\section*{Step 26.7: Formulate $\left(\mathrm{GM}_{X, V}\right)$ and solve}

Convert $\underline{\chi}^{(m, 1)}, \underline{\chi}^{(m, 2)}$ and $\underline{\chi}^{(m, 3)}$ to mass number.

$$
\begin{align*}
\underline{q}_{1}^{m}= & \underline{x}^{(m, 1)} \underline{M W^{T}}=(2.644,36.464,17.865)^{T}, \\
\underline{q}_{2}^{m}= & \underline{x}^{(m, 2)} \underline{M W^{T}}=(0.072,853.512,17.287)^{T} \\
\underline{q}_{3}^{m}=\underline{x}^{(m, 3)} \underline{M W}^{T} & =\left(8.4 \times 10^{-6}, 0.0379,18.015\right)^{T} \\
& \min _{\underline{q}_{1}, \underline{q}_{2}, \underline{q}_{3}, V_{1}, V_{2}, V_{3}}\left(A\left(\underline{q}_{1}, V_{1}^{\prime}, T^{0}\right)+P^{0} V_{1}^{\prime}+A\left(\underline{q}_{2}, V_{2}^{\prime}, T^{0}\right)+P^{0} V_{2}^{\prime}\right. \\
& \left.+A\left(\underline{q}_{3}, V_{3}^{\prime}, T^{0}\right)+P^{0} V_{3}^{\prime}\right) \\
& \text { s.t. } \\
& q_{1,1}+q_{1,2}-q_{1}^{0}=0, \\
& q_{2,1}+q_{2,2}-q_{2}^{0}=0, \\
& q_{3,1}+q_{3,2}-q_{3}^{0}=0,  \tag{15}\\
& q_{1,1} \in[2.244,3.044], q_{2,1} \in[15.264,57.664], \\
& q_{3,1} \in[17.847,17.883], \\
& q_{1,2} \in\left[10^{-8}, 0.472\right], q_{2,2} \in[832.312,874.712], \\
& q_{3,2} \in[17.268,17.304], \\
& q_{1,3} \in\left[10^{-8}, 0.40\right], q_{2,3} \in\left[10^{-8}, 21.238\right], \\
& q_{3,3} \in[17.997,18.033] . \\
& V_{1}, V_{2}, V_{3} \in[\underline{V}, \bar{V}] .
\end{align*}
$$


The linear constraints in problem (15) are feasible, and the subsequent minimisation of the Gibbs free energy over all phases is successful. The solution is as follows,
$G^{*}=3.57055119$, and $\mathcal{S}^{*}=\underline{\chi}^{(*, 1)}=(0.00661,0.00172,0.99167)^{T}$, $\eta^{(*, 1)}=0.43832$,
$\underline{x}^{(*, 2)}=(0.00018,0.04026,0.95956)^{T}, \eta^{(*, 2)}=0.45260 \quad$ and
$\underline{\boldsymbol{x}}^{(*, 3)}=\left(2.1 \times 10^{-8}, 1.79 \times 10^{-6}, 1.0\right)^{T}$,
$\bar{\eta}^{(*, 3)}=0.45884$.
No degenerate phases are identified and there are no phases containing components at their lower bound in composition, therefore HELD terminates.

\section*{End of major iteration 26}

\section*{Appendix B. Parameters used in example calculations}

Details of the notation for the parameters shown here can be found in Soave (1972) for the SRK equation of state, in Jackson et al. (1988), Chapman et al. (1988), Green and Jackson (1992a,b) for the SAFT-HS equation of state and in Gil-Villegas et al. (1997) and Galindo et al. (1998) for the SAFT-VR equation of state.

\section*{System I: binary mixture of methane (1) and hydrogen sulphide (2), SRK}
$T_{c}^{1}=190.6 \mathrm{~K} ; T_{c}^{2}=373.2 \mathrm{~K}$
$P_{c}^{1}=459600 \mathrm{~Pa} ; P_{c}^{2}=893700 \mathrm{~Pa}$
$\omega^{1}=0.008 ; ~ \omega^{2}=0.100$
$k_{12}=0.08$

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table B. 1
Parameters for system III: binary mixture of ethane and carbon dioxide-SAFT-VR (Galindo \& Blas, 2002). There are no association sites in this mixture and the subscript $c$ indicates that the parameters used in the example are those that were rescaled to the critical region by Galindo and Blas (2002). $\xi_{i j}$ and $\gamma_{i j}$ are the binary interaction coefficients relating to $\varepsilon_{i}$ and $\lambda_{i}$, such that $\varepsilon_{i j}=\xi_{i j} \sqrt{\varepsilon_{i i} \varepsilon_{i j}}$ and $\lambda_{i j}=\gamma_{i j}\left(\lambda_{i i} \sigma_{i i}+\lambda_{j j} \sigma_{j j} /\left(\sigma_{i i}+\sigma_{j j}\right)\right.$.}
\begin{tabular}{|l|l|l|l|l|l|l|}
\hline Component $i$ & $m_{i}$ & $\sigma_{c, i i} / \AA$ & $\left(\varepsilon_{c, i i} / k_{B}\right) / \mathrm{K}$ & $\lambda_{i i}$ & $\xi_{12}$ & $\gamma_{12}$ \\
\hline $\mathrm{C}_{2} \mathrm{H}_{6}$ & 1.333 & 4.0920 & 192.49 & 1.5326 & 0.88 & 0.989 \\
\hline $\mathrm{CO}_{2}$ & 2.0 & 3.1364 & 168.89 & 1.5157 & 0.88 & 0.989 \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table B. 2
Pure component parameters for systems IVa and IVb: ternary mixtures of PPG, PEG and water-SAFT-VR (Clark, 2007). $i$ refers to a component $i, m_{i}$ is the number of segments comprising a molecule, $\sigma_{i i} / \AA$ is the diameter of a sphere in $\AA, \varepsilon_{i i} / k_{B}$ is the dispersion energy reduced by the Boltzmann constant $k_{B}$ in the units of K , and $\lambda_{i i}$ is the range of the square well interaction. Several components in this mixture have association sites. $\mathrm{NST}_{i}$ is number of site types and $\mathrm{NS}_{i}$ ' a ' is the number of sites of type a , where both refer to component $i$.}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|}
\hline Component $i$ & $m_{i}$ & $\sigma_{i i} / \AA$ & $\left(\varepsilon_{i i} / k_{B}\right) / \mathrm{K}$ & $\lambda_{i i}$ & $\mathrm{NST}_{i}$ & $\mathrm{NS}_{i} 1$ & $\mathrm{NS}_{i} 2$ & $\mathrm{NS}_{i} 3$ \\
\hline PPG-400 $\mathrm{g} \mathrm{mol}^{-1}$ & 11.63894 & 3.89932 & 287.382 & 1.47695 & 3 & 6 & 4 & 2 \\
\hline PEG-600 $\mathrm{g} \mathrm{mol}^{-1}$ & 14.22727 & 3.81239 & 287.601 & 1.46189 & 3 & 24 & 4 & 2 \\
\hline PEG-21200 $\mathrm{g} \mathrm{mol}^{-1}$ & 482.40909 & 3.81239 & 287.601 & 1.46189 & 3 & 960 & 4 & 2 \\
\hline $\mathrm{H}_{2} \mathrm{O}$ & 1.0 & 3.0342 & 250.0 & 1.7889 & 2 & 2 & 2 & - \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table B. 3
$\xi_{i j}$ binary interaction parameters for systems IVa and IVb: ternary mixtures of PPG, PEG and water-SAFT-VR (Clark, 2007). All $\gamma_{i j}=0.0$.}
\begin{tabular}{llll}
\hline & PPG & PEG & $\mathrm{H}_{2} \mathrm{O}$ \\
\hline PPG & - & 1.1 & 1.137 \\
PEG & & - & 1.053 \\
$\mathrm{H}_{2} \mathrm{O}$ & & & - \\
\hline
\end{tabular}
\end{table}

\section*{System II: binary athermal polymer-colloid system-SAFT-HS (TPT1)}
$m_{\text {polymer }}=500$
$m_{\text {colloid }}=1$
$\sigma_{\text {colloid }} / \sigma_{\text {polymer }}=0.06$

\section*{System III: binary mixture of ethane and carbon dioxide-SAFTVR}

See Table B.1.

\section*{Systems IVa and IVb: ternary mixtures of PPG, PEG and water-SAFT-VR}

See Tables B.2-B.4.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table B. 5
Pure component parameters for system V: five component mixture of light gases and polyethylene modelled with the SAFT-VR EOS (Haslam et al., 2006). $i$ refers to a component $i, m_{i}$ is the number of spheres comprising a molecule, $\sigma_{i i} / \AA$ is the diameter of a sphere in $\AA, \varepsilon_{i i} / k_{B}$ is the dispersion energy reduced by the Boltzmann constant $k_{B}$ in the units of K , and $\lambda_{i i}$ is the range of the square well interaction. None of the components in this mixture are modelled as associating.}
\begin{tabular}{lllcl}
\hline Component $i$ & $m_{i}$ & $\sigma_{i i} / \AA$ & $\left(\varepsilon_{i i} / k_{B}\right) / \mathrm{K}$ & $\lambda_{i i}$ \\
\hline $\mathrm{PE}\left(12,000 \mathrm{~g} \mathrm{~mol}^{-1}\right)$ & 285.12 & 4.0100 & 230.04 & 1.694 \\
$\mathrm{~N}_{2}$ & 1.3 & 3.1940 & 84.53 & 1.5340 \\
$\mathrm{C}_{3} \mathrm{H}_{8}$ & 1.6667 & 3.8899 & 260.91 & 1.4537 \\
$\mathrm{C}_{2} \mathrm{H}_{4}$ & 1.333 & 3.6627 & 222.17 & 1.4432 \\
$\mathrm{C}_{4} \mathrm{H}_{8}$ & 2.0 & 3.7706 & 228.49 & 1.5564 \\
\hline
\end{tabular}
\end{table}

\section*{System V: five component mixture of light gases and polyethylene-SAFT-VR}

See Tables B. 5 and B.6.

\section*{Systems VI and VII: ten and fifteen component mixtures of light gases and polyethylene}

These systems contain all five components described in Table B. 5 plus linear alkanes, the parameters of which are taken from Paricaud et al. (2004). The binary interaction coefficients between

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table B. 4
Association parameters for systems IVa and IVb: ternary mixtures of PPG, PEG and water-SAFT-VR (Clark, 2007). PPG 1 refers to site type 1 of PPG, etc. $\varepsilon_{i j a b}^{H B} / k_{B}$ is the reduced hydrogen bounding energy in K, where $k_{B}$ is the Boltzmann constant, and $r_{c, i j a b}$ is the range of the hydrogen bonding interaction in Å. In both cases the subscript $i j a b$ indicates an interaction between site types $a$ and $b$ of components $i$ and $j$ respectively.}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|l|l|}
\hline \multirow[t]{2}{*}{Component} & \multicolumn{2}{|l|}{\multirow[t]{2}{*}{Site type}} & \multicolumn{3}{|l|}{PPG} & \multicolumn{3}{|l|}{PEG} & \multicolumn{2}{|l|}{$\mathrm{H}_{2} \mathrm{O}$} \\
\hline & & & 1 & 2 & 3 & 1 & 2 & 3 & 1 & 2 \\
\hline \multirow[t]{5}{*}{PPG} & \multirow[t]{2}{*}{1} & $\varepsilon_{i j a b}^{H B} / k_{B}$ & - & - & 1000.0 & - & - & 1000.0 & - & 2750.0 \\
\hline & & $r_{c, i j a b}$ & - & - & 2.2 & - & - & 3.1448 & - & 1.9 \\
\hline & \multirow[t]{2}{*}{2} & $\varepsilon_{i j a b}^{H B} / k_{B}$ & & - & 1000.0 & - & - & 1000.0 & - & 2100.0 \\
\hline & & $r_{c, i j a b}$ & & - & 2.2 & - & - & 3.1448 & - & 1.9 \\
\hline & \multirow[t]{2}{*}{3} & $\varepsilon_{i j a b}^{H B} / k_{B}$ & & & - & 1000.0 & 1000.0 & - & 2100.0 & - \\
\hline & & $r_{c, i j a b}$ & & & - & 3.1448 & 3.1448 & - & 1.9 & - \\
\hline \multirow[t]{6}{*}{PEG} & \multirow[t]{2}{*}{1} & $\varepsilon_{i j a b}^{H B} / k_{B}$ & & & & - & - & 1000.0 & - & 1500.0 \\
\hline & & $r_{c, i j a b}$ & & & & - & - & 3.2 & - & 2.188 \\
\hline & \multirow[t]{2}{*}{2} & $\varepsilon_{i j a b}^{H B} / k_{B}$ & & & & & - & 1000.0 & - & 2400.0 \\
\hline & & $r_{c, i j a b}$ & & & & & - & 3.2 & - & 2.188 \\
\hline & \multirow[t]{2}{*}{3} & $\varepsilon_{i j a b}^{H B} / k_{B}$ & & & & & & - & 2400.0 & - \\
\hline & & $r_{c, i j a b}$ & & & & & & - & 2.188 & - \\
\hline \multirow[t]{4}{*}{$\mathrm{H}_{2} \mathrm{O}$} & \multirow[t]{2}{*}{1} & $\varepsilon_{i j a b}^{H B} / k_{B}$ & & & & & & & - & 1400.0 \\
\hline & & $r_{c, i j a b}$ & & & & & & & - & 2.1082 \\
\hline & \multirow[t]{2}{*}{2} & $\varepsilon_{i j a b}^{H B} / k_{B}$ & & & & & & & & - \\
\hline & & $r_{c, i j a b}$ & & & & & & & & - \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table B. 6
$\xi_{i j}$ binary interaction parameters for system V: five component mixture of light gases and polyethylene modelled with the SAFT-VR EOS Haslam et al. (2006).}
\begin{tabular}{lllll}
\hline & $\mathrm{N}_{2}$ & $\mathrm{C}_{3} \mathrm{H}_{8}$ & $\mathrm{C}_{2} \mathrm{H}_{4}$ & $\mathrm{C}_{4} \mathrm{H}_{8}$ \\
\hline $\mathrm{PE}\left(12,000 \mathrm{~g} \mathrm{~mol}^{-1}\right)$ & 0.85 & 0.98 & 0.943 & 0.98 \\
\hline
\end{tabular}
\end{table}

Any $\xi_{i j}$ not listed here is equal to 1.0 , and all $\gamma_{i j}=1.0$. Note that $\xi_{i j}=1-k_{i j}$, where $k_{i j}$ is the binary interaction coefficient as presented in Haslam et al. (2006).

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table B. 7
Pure component parameters for the linear alkanes in systems VI and VII, in which the thermodynamic properties are obtained from the SAFT-VR EOS. The parameters are taken from Paricaud et al. (2004). $i$ refers to a component $i, m_{i}$ is the number of spheres comprising a molecule, $\sigma_{i i} / \AA$ is the diameter of a sphere in $\AA, \varepsilon_{i i} / k_{B}$ is the dispersion energy reduced by the Boltzmann constant $k_{B}$ in the units of K , and $\lambda_{i i}$ is the range of the square well interaction. None of the components here are modelled as associating.}
\begin{tabular}{|l|l|l|l|l|}
\hline Component $i$ & $m_{i}$ & $\sigma_{i i} / \AA$ & $\left(\varepsilon_{i i} / k_{B}\right) / \mathrm{K}$ & $\lambda_{i i}$ \\
\hline $\mathrm{C}_{6} \mathrm{H}_{14}$ & 2.6667 & 3.9396 & 251.66 & 1.5492 \\
\hline $\mathrm{C}_{7} \mathrm{H}_{16}$ & 3.0 & 3.9567 & 253.28 & 1.5574 \\
\hline $\mathrm{C}_{8} \mathrm{H}_{18}$ & 3.3333 & 3.9455 & 249.52 & 1.5751 \\
\hline $\mathrm{C}_{9} \mathrm{H}_{20}$ & 3.6667 & 3.9635 & 251.53 & 1.5745 \\
\hline $\mathrm{C}_{10} \mathrm{H}_{22}$ & 4.0 & 3.9675 & 247.08 & 1.5925 \\
\hline $\mathrm{C}_{11} \mathrm{H}_{24}$ & 4.3333 & 3.9775 & 252.65 & 1.5854 \\
\hline $\mathrm{C}_{12} \mathrm{H}_{26}$ & 4.6667 & 3.9663 & 243.03 & 1.6101 \\
\hline $\mathrm{C}_{13} \mathrm{H}_{28}$ & 5.0 & 3.9583 & 227.31 & 1.6479 \\
\hline $\mathrm{C}_{14} \mathrm{H}_{30}$ & 5.3333 & 3.9745 & 249.74 & 1.6023 \\
\hline
\end{tabular}
\end{table}
the linear alkanes and PE is considered to the equal to that between propane and PE, $\xi_{i j}=0.98$, and all other $\xi_{i j}=1.0$.

See Table B.7.

\section*{References}

Abrams, D. S., \& Prausnitz, J. M. (1975). Statistical thermodynamics of liquid mixtures: A new expression for the excess Gibbs energy of partly or completely miscible systems. AIChE Journal, 21, 116.
Alder, B. J., \& Hecht, C. E. (1969). Studies in molecular dynamics. VII. Hard-sphere distribution functions and an augmented van der Waals theory. Journal of Chemical Physics, 50, 2032.
Baker, L. E., Pierce, A. C., \& Luks, K. D. (1982). Gibbs energy analysis of phase equilibria. SPE Journal, 22, 731.
Barron, C., \& Gómez, S. (1991). The exponential tunneling method. Report 1 (3). Universidad Nacional Autonoma de Mexico.
Bazaraa, M. S., Sherali, H. D., \& Shetty, C. M. (1993). Nonlinear programming: Theory and algorithms (second ed.). New York: John Wiley and Sons.
Blankenship, J. W., \& Falk, J. E. (1976). Infinitely constrained optimization problems. Journal of Optimization Theory and Applications, 19, 261.
Blas, F. J., \& Galindo, A. (2002). Study of the high pressure phase behaviour of $\mathrm{CO}_{2}+n-$ alkane mixtures using the SAFT-VR approach with transferable parameters. Fluid Phase Equilibria, 194, 501.
Bollas, G. M., Barton, P. I., \& Mitsos, A. (2009). Bilevel optimization formulation for parameter estimation in vapor-liquid (-liquid) phase equilibrium problems. Chemical Engineering Science, 64, 1768.
Bonilla-Petriciolet, A., Vázquez-Román, R., Iglesias-Silva, G. A., \& Hall, K. R. (2006). Performance of stochastic global optimization methods in the calculation of phase stability analyses for nonreactive and reactive mixtures. Industrial and Engineering Chemistry Research, 45, 4764.
Carnahan, N. F., \& Starling, K. E. (1972). Intermolecular repulsions and the equation of state for fluids. AIChE Journal, 18, 1184.
Chapman, W. G., Gubbins, K. E., Jackson, G., \& Radosz, M. (1989). SAFT: Equation-ofstate solution model for associating fluids. Fluid Phase Equilibria, 52, 31.
Chapman, W. G., Gubbins, K. E., Jackson, G., \& Radosz, M. (1990). New reference equation of state for associating liquids. Industrial and Engineering Chemistry Research, 29, 1709.
Chapman, W. G., Jackson, G., \& Gubbins, K. E. (1988). Phase equilibria of associating fluids: Chain molecules with multiple bonding sites. Molecular physics, 65, 1057.
Clark, G. N. I. (2007). Molecular modelling of the phase behaviour of water-soluble polymers. Ph.D. thesis. Imperial College London, U.K.
Clark, G. N. I., Galindo, A., Jackson, G., Rogers, S., \& Burgess, A. N. (2008). Modeling and understanding closed-loop liquid-liquid immiscibility in aqueous solutions of poly(ethylene glycol) using the SAFT-VR approach with transferable parameters. Macromolecules, 41, 6582.
Falk, J. E., \& Hoffman, K. (1977). A nonconvex max-min problem. Naval Research Logistics Quarterly, 24, 441.
Floudas, C. A. (2000). Deterministic global optimization; Theory, methods and applications. Dordrecht: Kluwer Academic Publishers.

Floudas, C. A., \& Gounaris, C. E. (2009). A review of recent advances in global optimization. Journal of Global Optimization, 45, 3.
Galindo, A., \& Blas, F. J. (2002). Theoretical examination of the global fluid phase behavior and critical phenomena in carbon dioxide +n -alkane binary mixtures. The Journal of Physical Chemistry B, 106, 4503.
Galindo, A., Davies, L. A., Gil-Villegas, A., \& Jackson, G. (1998). The thermodynamics of mixtures and the corresponding mixing rules in the SAFT-VR approach for potentials of variable range. Molecular Physics, 93, 241.
Gibbs, J. W. (1874). On the equilibrium of heterogeneous substances. First Part (pp. 108-248). Transactions of the Connecticut Academy of Arts and Sciences, vol. 3.
Gil-Villegas, A., Galindo, A., Whitehead, P. J., Mills, S. J., Jackson, G., \& Burgess, A. N. (1997). Statistical associating fluid theory for chain molecules with attractive potentials of variable range. Journal of Chemical Physics, 106, 4168.
Gill, P. E., \& Murray, W. (1978). Numerically stable methods for quadratic programming. Mathematical Programming, 14, 349.
Gill, P. E., Murray, W., \& Saunders, M. A. (2002). SNOPT: An SQP algorithm for largescale constrained optimization. SIAM Journal of Optimization, 12, 979.
Gill, P. E., Murray, W., Saunders, M. A., \& Wright, M. H. (1986a). Some theoretical properties of an augmented lagrangian merit function. Report SOL 86-6R. Systems Optimization Lab, Stanford University.
Gill, P. E., Murray, W., Saunders, M. A., \& Wright, M. H. (1986b). User's guide for NPSOL (Version 4.0): A fortran package for nonlinear programming. Report SOL 86-2. Systems Optimization Lab, Stanford University.
Gill, P. E., Murray, W., Saunders, M. A., \& Wright, M. H. (1991). Inertia-controlling methods for general quadratic programming. SIAM Review, 33, 1.
Giovanoglou, A., Adjiman, C. S., Jackson, G., \& Galindo, A. (2009). Fluid phase stability and equilibrium calculations in binary mixtures. Part II: Application to singlepoint calculations and the construction of phase diagrams. Fluid Phase Equilibria, 275, 95.
Giovanoglou, A., Galindo, A., Jackson, G., \& Adjiman, C. S. (2009). Fluid phase stability and equilibrium calculations in binary mixtures. Part I: Theoretical development for non-azeotropic mixtures. Fluid Phase Equilibria, 275, 79.
Green, D. G., \& Jackson, G. (1992a). Theory of phase equilibria and closed-loop liquid-liquid immiscibility for model aqueous solutions of associating chain molecules: Water + alkanol mixtures. Journal of Chemical Physics, 97, 8672.
Green, D. G., \& Jackson, G. (1992b). Theory of phase equilibria for model aqueous solutions of chain molecules: water + alkane mixtures. Journal of the Chemical Society Faraday Transactions, 88, 1395.
Harding, S. T., \& Floudas, C. A. (2000a). Locating all heterogeneous and reactive azeotropes in multicomponent mixtures. Industrial and Engineering Chemistry Research, 39, 1576.
Harding, S. T., \& Floudas, C. A. (2000b). Phase stability with cubic equations of state: Global optimization approach. AIChE Journal, 46, 1422.
Haslam, A. J., von Solms, N., Adjiman, C. S., Galindo, A., Jackson, G., Paricaud, P., Michelsen, M. L., \& Kontogeorgis, G. M. (2006). Predicting enhanced absorption of light gases in polyethylene using simplified PC-SAFT and SAFT-VR. Fluid Phase Equilibria, 243, 74.
Henderson, N., de Oliveira, J. R., Amaral Souto, H. P., \& Pitanga Marques, R., Jr. (2001). Modeling and analysis of the isothermal flash problem and its calculation with the simulated annealing algorithm. Industrial and Engineering Chemistry Research, 40, 6028.
Hua, J. Z., Brennecke, J. F., \& Stadtherr, M. A. (1996). Reliable prediction of phase stability using an interval Newton method. Fluid Phase Equilibria, 116, 52.
Hua, J. Z., Brennecke, J. F., \& Stadtherr, M. A. (1998). Enhanced interval analysis for phase stability: Cubic equation of state models. Industrial and Engineering and Chemical Research, 37, 1519.
Iglesias-Silva, G. A., Bonilla-Petriciolet, A., Eubank, P. T., Holste, J. C., \& Hall, K. R. (2003). An algebraic method that includes Gibbs minimization for performing phase equilibrium calculations for any number of components or phases. Fluid Phase Equilibria, 210, 229.
Jackson, G., Chapman, W. G., \& Gubbins, K. E. (1988). Phase equilibria of associating fluids. Spherical fluids with multiple bonding sites. Molecular Physics, 65, 1.
Jackson, G., Rowlinson, J. S., \& Leng, C. A. (1986). Phase equilibria in model mixtures of spherical molecules of different sizes, Journal of the Chemical Society. Faraday Transactions, 1(82), 3461.
Jones, D. R., Perttunen, C. D., \& Stuckman, B. E. (1993). Lipschitzian optimization without the Lipschitz constant. Journal of Optimization Theory and Applications, 79, 157.
Kakalis, N. M. P., Kakhu, A. I., \& Pantelides, C. C. (2006). Efficient solution of the association term equations in the statistical associating fluid theory equation of state. Industrial and Engineering Chemistry Research, 45, 6056.
Levy, A. V., \& Gomez, S. (1985). The tunneling method applied to global optimization. In P. T. Boggs, R. H. Byrd, \& R. B. Schnabel (Eds.), Numerical optimization (p. 213). Philadelphia: SIAM.
Levy, A. V., \& Montalvo, A. (1985). The tunneling algorithm for the global minimization of functions. SIAM Journal on Scientific Computing, 6, 15.
Lucia, A., DiMaggio, P. A., Bellows, M. L., \& Octavio, L. M. (2005). The phase behavior of $n$-alkane systems. Computers and Chemical Engineering, 29, 2363.
Lucia, A., DiMaggio, P. A., \& Depa, P. (2004). A geometric terrain methodology for global optimisation. Journal of Global Optimisation, 29, 297.
Lucia, A., Padmanabhan, L., \& Venkataraman, S. (2000). Multiphase equilibrium flash calculations. Computers and Chemical Engineering, 24, 2557.
Mac Dowell, N., Llovell, F., Adjiman, C. S., Jackson, G., \& Galindo, A. (2010). Modeling the fluid phase behavior of carbon dioxide in aqueous solutions of monoethanolamine using transferable parameters with the SAFT-VR approach. Industrial and Engineering Chemistry Research, 49, 1883.

Marsh, K. N., McGlashan, M. L., \& Warr, C. (1970). Thermodynamic excess functions of mixtures of simple molecules according to several equations of state. Transactions of the Faraday Society, 66, 2453.
McCabe, C., \& Galindo, A. (2010). SAFT associating fluids and fluid mixtures. In R. H. Goodwin, J. V. Sengers, \& C. J. Peters (Eds.), Applied thermodynamics of fluids. Cambridge: RCS Publishing.
McCabe, C., Galindo, A., Nieves García-Lisbona, M., \& Jackson, G. (2001). Examining the adsorption (vapor-liquid equilibria) of short-chain hydrocarbons in lowdensity polyethylene with the SAFT-VR approach. Industrial and Engineering Chemistry Research, 40, 3835.
McDonald, C. M., \& Floudas, C. A. (1995a). Global optimization and analysis for the Gibbs free energy function using the UNIFAC, Wilson and ASOG equations. Industrial and Engineering Chemistry Research, 34, 1674.
McDonald, C. M., \& Floudas, C. A. (1995b). Global optimization for the phase stability problem. AIChE Journal, 41, 1798.
McDonald, C. M., \& Floudas, C. A. (1997). GLOPEQ: A new computational tool for the phase and chemical equilibrium problem. Computers \& Chemical Engineering, 21, 1.

McKinnon, K., \& Mongeau, M. (1998). A generic global optimization algorithm for the chemical and phase equilibrium problem. Journal of Global Optimization, 12, 325.

Michelsen, M. L. (1982a). The isothermal flash problem. Part I. Stability. Fluid Phase Equilibria, 9, 1.
Michelsen, M. L. (1982b). The isothermal flash problem. Part II. Phase-split calculation. Fluid Phase Equilibria, 9, 21.
Michelsen, M. L., \& Hendriks, E. M. (2001). Physical properties from association models. Fluid phase equilibria, 180, 165.
Michelsen, M. L., \& Mollerup, J. M. (2007). Thermodynamic models: Fundamentals and computational aspects (Second Edition). Holte, Denmark: Tie-line Publications.
Mitsos, A., \& Barton, P. I. (2007). A dual extremum principle in thermodynamics. AIChE Journal, 53, 2131.
Mitsos, A., Bollas, G. M., \& Barton, P. I. (2009). Bilevel optimization formulation for parameter estimation in liquid-liquid phase equilibrium problems. Chemical Engineering Science, 64, 548.
Morgado, P., McCabe, C., \& Filipe, E. J. M. (2005). Modelling the phase behaviour and excess properties of alkane + perfluoroalkane binary mixtures with the SAFT-VR approach. Fluid Phase Equilibria, 228, 389.
Müller, E. A., \& Gubbins, K. E. (2001). Molecular-based equations of state for associating fluids: A review of SAFT and related approaches. Industrial and Engineering Chemistry Research, 40, 2193.
Nagarajan, N. R., Cullick, A. S., \& Griewank, A. (1991a). New strategy for phase equilibrium and critical point calculations by thermodynamic energy analysis. Part 1. Stability analysis and flash. Fluid Phase Equilibria, 62, 191.

Nagarajan, N. R., Cullick, A. S., \& Griewank, A. (1991b). New strategy for phase equilibrium and critical point calculations by thermodynamic energy analysis. Part II. Critical point calculations. Fluid Phase Equilibria, 62, 211.

Nichita, D. V., de Los Angeles Duran Valencia, C., \& Gomez, S. (2006). Volume-based thermodynamics global phase stability analysis. Chemical Engineering Communications, 193, 1194.
Nichita, D. V., García-Sánchez, F., \& Gómez, S. (2008). Phase stability analysis using the PC-SAFT equation of state and the tunneling global optimization method. Chemical Engineering Journal, 140, 509.
Nichita, D. V., \& Gomez, S. (2009). Efficient location of multiple global minima for the phase stability problem. Chemical Engineering Journal, 152, 251.
Nichita, D. V., Gomez, S., \& Luna, E. (2002a). Multiphase equilibria calculation by direct minimization of gibbs free energy with a global optimization method. Computers and Chemical Engineering, 26, 1703.
Nichita, D. V., Gomez, S., \& Luna, E. (2002b). Phase stability analysis with cubic equations of state by using a global optimization method. Fluid Phase Equilibria, 194, 411.

O'Connell, J. P., \& Haile, J. M. (2005). Thermodynamics: fundamentals for applications. New York: Cambridge University Press.
Paricaud, P., Galindo, A., \& Jackson, G. (2003). Understanding liquid-liquid immiscibility and LCST behaviour in polymer solutions with a Wertheim TPT1 description. Molecular Physics, 101, 2575.
Paricaud, P., Galindo, A., \& Jackson, G. (2004). Modeling the cloud curves and the solubility of gases in amorphous and semicrystalline polyethylene with the SAFT-VR approach and Flory theory of crystallization. Industrial and Engineering Chemistry Research, 43, 6871.
Paricaud, P., Varga, S., \& Jackson, G. (2003). Study of the demixing transition in model athermal mixtures of colloids and flexible self-excluding polymers using the thermodynamic perturbation theory of Wertheim. Journal of Chemical Physics, 118, 8525.
Pereira, F. E., Jackson, G., Galindo, A., \& Adjiman, C. S. (2010). A duality-based approach to the $(P, T)$ phase equilibrium problem in the volume-composition space. Fluid Phase Equilibria, 299, 1.
Rahman, I., Das, A. K., Mankar, R. B., \& Kulkarni, B. D. (2009). Evaluation of repulsive particle swarm method for phase equilibrium and phase stability problems. Fluid Phase Equilibria, 282, 65.
Rangaiah, G. P. (2001). Evaluation of genetic algorithms and simulated annealing for phase equilibrium and stability problems. Fluid Phase Equilibria, 187, 83.
Renon, H., \& Prausnitz, J. M. (1968). Local compositions in thermodynamic excess functions for liquid mixtures. AIChE Journal, 14, 135.
Saber, N., \& Shaw, J. M. (2008). Rapid and robust phase behaviour stability analysis using global optimization. Fluid Phase Equilibria, 264, 137.
Soave, G. (1972). Equilibrium constants from a modified Redlich-Kwong equation of state. Chemical Engineering Science, 27, 1197.
Srinivas, M., \& Rangaiah, G. P. (2006). Implementation and evaluation of random tunneling algorithm for chemical engineering applications. Computers and Chemical Engineering, 30, 1400.
Srinivas, M., \& Rangaiah, G. P. (2007a). Differential evolution with tabu list for global optimization and its application to phase equilibrium and parameter estimation problems. Industrial and Engineering Chemistry Research, 46, 3410.

Srinivas, M., \& Rangaiah, G. P. (2007b). A study of differential evolution and tabu search for benchmark, phase equilibrium and phase stability problems. Computers and Chemical Engineering, 31, 760.
Sun, A. C., \& Seider, W. D. (1995). Homotopy-continuation method for stability analysis in the global minimization of the Gibbs free energy. Fluid Phase Equilibria, 103, 213.
Sun, L., Zhao, H., \& McCabe, C. (2007). Predicting the phase equilibria of petroleum fluids with the SAFT-VR approach. AIChE Journal, 53, 720.
Tawarmalani, M., \& Sahinidis, N. V. (2002). Convexification and global optimization in continuous and mixed-integer nonlinear programming: theory, algorithms, software, and applications. Dordrecht: Kluwer Academic Publishers.
Teh, Y. S., \& Rangaiah, G. P. (2002). A study of equation solving and gibbs free energy minimisation methods for phase equilibrium calculations. Chemical Engineering Research and Design, 80, 745.
von Solms, N., Michelsen, M. L., \& Kontogeorgis, G. M. (2003). Computational and physical performance of a modified PC-SAFT equation of state for highly asymmetric and associating mixtures. Industrial and Engineering Chemistry Research, 42, 1098.
Wei, Y. S., \& Sadus, R. J. (2000). Equations of state for the calculation of fluid-phase equilibria. AIChE Journal, 46, 169.
Xu, G., Brennecke, J. F., \& Stadtherr, M. A. (2002). Reliable computation of phase stability and equilibrium from the SAFT equation of state. Industrial and Engineering Chemistry Research, 41, 938.