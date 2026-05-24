\title{
Phase stability criteria and fluid-phase equilibria in strong-electrolyte systems
}

\author{
Felipe A. Perdomo ${ }^{\mathrm{a}(\mathrm{D}, 1}$, George Jackson ${ }^{\mathrm{a}(\mathrm{D})}$, Alexander Mitsos ${ }^{\mathrm{b}, \mathrm{c}, \mathrm{d}(\mathrm{D})}$, Amparo Galindo ${ }^{\mathrm{a}(\mathrm{D})}$, Claire S. Adjiman ${ }^{\text {a }}$ (D,* \\ ${ }^{\mathrm{a}}$ Department of Chemical Engineering, Sargent Centre for Process Systems Engineering, Institute for Molecular Science and Engineering, Imperial College London, London, SW7 2AZ, United Kingdom \\ ${ }^{\mathrm{b}}$ JARA-CSD, Aachen, 52056, Germany \\ ${ }^{\mathrm{c}}$ Process Systems Engineering (AVT.SVT), RWTH Aachen University, Forckenbeckstr. 51, Aachen, 52074, Germany \\ ${ }^{\mathrm{d}}$ Institute of Energy and Climate Research, Energy Systems Engineering (IEK-10), Forschungszentrum Juelich GmbH, Juelich, 52425, Germany
}

\section*{ARTICLE INFO}

Dataset link: https://doi.org/10.5281/zenodo. 1 3646853

\section*{Keywords:}

Multiphase multicomponent equilibria
SAFT- $\gamma$ Mie group-contribution approach
Mixed solvents
Tangent-plane distance
Duality theory

\begin{abstract}
Although the presence of salts can significantly affect the fluid-phase equilibria, phase stability and equilibrium calculations remain challenging due to the nonlinearity of thermodynamic models and to the negligible amounts of ions that can be present in some phases. To address this, we introduce a new variable transformation and present the first formal proof of a stability criterion for strong (fully-dissociated) electrolyte solutions based on the tangent-plane distance under the electroneutrality constraint. The criterion can also be recast based on duality theory, yielding two alternative formulations with/without reformulation in the volume-composition space. We use these theoretical results to extend the Helmholtz free Energy Lagrangian Dual (HELD) algorithm (Pereira et al., Comput. Chem. Eng. 36 (2012) 99) to strong electrolyte mixtures. The resulting HELD2.0 algorithm provides reliable calculations of the nonideal phase behaviour of mixtures of organic molecules and water with alkali halide salts for a wide range of thermodynamic states.
\end{abstract}

\section*{1. Introduction}

The thermodynamic behaviour and phase equilibria of electrolyte solutions are of central relevance to many fields of scientific enquiry and industrial application, such as the understanding of partitioning in biochemical systems (Fu et al., 2017), the study of high-pressure aquifers and reservoirs wherein natural gas or carbon dioxide is in equilibrium with brines (Wang et al., 2013; Hosseinzadeh Dehaghani et al., 2022), the development of novel electrochemical energy storage and conversion devices (Sevov et al., 2017), the design of processes for precipitation (Sassenburg et al., 2022), crystallization (Takano et al., 2002), water desalination (Pantoja et al., 2015; Creusen et al., 2013), and water-pollution control (Murphy et al., 1992; Kiendrebeogo et al., 2021). For instance, in the context of lithium-ion batteries, the choice of electrolyte affects battery performance through the decomposition of salts and solvents at low potentials as well as the complex interactions of the electrode materials and solvent medium (Hayashi et al., 2016; Lavi et al., 2020; Bazak et al., 2017).

The study and design of systems involving electrolyte solutions can be facilitated through the use of modelling approaches. Given a thermodynamic model, a challenge in characterizing its phase behaviour lies
in the correct identification of the stable phases in coexistence at equilibrium and of the corresponding distribution of ionic and molecular species across these phases. In the case of mixtures of molecular species, stability criteria have been derived (Baker et al., 1982; Smith et al., 1993; Mitsos and Barton, 2007) and used to construct algorithms to solve for phase equilibria (e.g., Michelsen, 1982b; Wasylkiewicz et al., 1999; Mitsos and Barton, 2007; Pereira et al., 2012; Xu et al., 2005; McDonald and Floudas, 1995). There has, however, been limited work on stability criteria for electrolyte systems, even for the simpler case of solutions of strong electrolytes. In strong-electrolyte solutions, which are the focus of our current work, the electrolytes are fully dissociated and there is no need to consider the presence of chemical reactions. In this context, Tsanas et al. (2022) proposed a modification of the stability criterion defined for mixtures of molecular species by replacing the chemical potential in the tangent-plane distance (Baker et al., 1982) by the electrochemical potential (Guggenheim, 1935; Michelsen and Mollerup, 2018). Ascani et al. (2022) briefly discussed the application of the tangent-plane distance criterion to electrolyte solutions via a variable transformation, but without specifying the role of the electrochemical potential in the tangent-plane distance function. To the

\footnotetext{
* Corresponding author.

E-mail address: c.adjiman@imperial.ac.uk (C.S. Adjiman).
${ }^{1}$ Current address: School of Engineering, University of Greenwich, Medway Campus, Chatham Maritime, Kent ME4 4TB, United Kingdom.
}
best of our knowledge, no formal derivation of a stability criterion for electrolyte solutions, taking into account the requirement for the electroneutrality of each phase, has been reported.

There has been much greater focus on the theoretical development of necessary conditions for phase equilibrium for strong and weak electrolyte solutions, i.e., conditions that any equilibrium state can be expected to meet such as the equality across all stable phases of the pressures, the temperatures, and the chemical potentials of each component, which however are not sufficient. Several derivations of these conditions have been reported, e.g., in the work of Großmann and Maurer (1995), Nikolaidis et al. (2022), and Tsanas et al. (2022) for the case of two-phase systems (and, in Nikolaidis et al. (2022), with a focus on strong electrolytes). Ascani et al. (2022) extended the approach of Großmann and Maurer (1995) to any number of phases and introduced a variable transformation based on the condition of electroneutrality. The equilibrium conditions are generally expressed in terms of electrochemical potentials or mean-ionic chemical potentials and include conditions for the electroneutrality of each phase at equilibrium.

The solution of the phase-equilibrium conditions is a highly demanding task because of the nonlinearity of the underlying thermodynamic models and because ionic species may be present at extremely small concentrations in some of the phases (Schreckenberg et al., 2014). Several algorithmic approaches have been developed for this purpose, including, in particular, methods based on the minimization of the Gibbs free energy. This includes the approach of Gautam and Seider (1979c) who extended their earlier RAND algorithm (Gautam and Seider, 1979a) to strong electrolyte solutions, combining it with a phase-split algorithm (Gautam and Seider, 1979b) to determine the number of stable phases at equilibrium. A key assumption in the approach is that no ions are present in the vapour phase. Cheluget et al. (1987) proposed a method based on free-energy minimization to deal with ionic equilibria involving one, or more than one, pure solid in addition to a solution phase. Lantagne et al. (1988) considered the use of a penalty function that combines the Gibbs potential function, mass balances, electroneutrality, and non-negativity constraints, and investigated a second-order Newton method and a quasi-Newton method for the solution of the resulting unconstrained problem. Several strategies have recently appeared for the numerical solution of phase equilibrium, in the case of strong electrolytes (Nikolaidis et al., 2022), or for systems that also involve chemical equilibrium with liquidliquid equilibria (Zuend and Seinfeld, 2013), two fluid phases (Tsanas et al., 2022), or any number of fluid phases (Ascani et al., 2022). It is, however, not sufficient to find points that satisfy the optimality conditions, as these are also satisfied by metastable or even unstable phase combinations. Any phase combination that meets the optimality must be subjected to a stability check to confirm its validity. Such a check is integrated in the solution approaches of Tsanas et al. (2022) and Ascani et al. (2022).

The main goals of our current work are to develop a theoretical formalism for phase stability in mixtures of strong electrolytes and to apply this to design an algorithm for isothermal $P, T$ flash calculations. These developments should be applicable to mixtures containing any given (positive and finite) number $C$ of components consisting of strong electrolytes and molecular species. The formulation should also be applicable to stable states comprising one or more phases at the given conditions of temperature $T$, pressure $P$, and mole numbers $n$. We focus exclusively on fluid phases, i.e., vapour and liquid, and do not consider solid precipitation. However, we do not make any assumptions on the number and amount of ionic species present in any of the stable phases and consider instead that all components can be present in all phases. A stability criterion for non-reactive electrolyte systems is derived formally, cast in a reduced composition space via a variable transformation, so that fewer than $C$ compositions are considered. We also propose two alternative formulations of this criterion, based on the dual extremum principle introduced by Mitsos and Barton (2007).

The first is expressed in the isothermal-isobaric ensemble in terms of the natural variables $T, P$, and $n$ while the second is expressed in the canonical ensemble in terms of $T$, molar volume $V$, and $\boldsymbol{n}$ (Pereira et al., 2010), following a recasting of the Gibbs free energy in terms of the Helmholtz free energy (Nagarajan et al., 1991).

On the basis of these theoretical developments and of our previously proposed Helmholtz free energy Lagrangian dual (HELD) algorithm (Pereira et al., 2012, 2010), we present an isothermal $P, T$ flash algorithm for the identification of all the stable equilibrium phases and their compositions. It is based on an iterative strategy in which we identify candidate stable phases by solving a dual (max-min) optimization problem and then test whether the combination of phases identified is complete (i.e., whether it satisfies the mass-balance constraints). As demonstrated through thousands of calculations (e.g., Pereira et al., 2012; Rodriguez et al., 2012; Artola et al., 2011), the HELD algorithm has been found to reliably identify the stable solution of the isothermal $P, T$ flash for mixtures of molecular species, without requiring any assumptions on the number of phases nor initial guesses for compositions. Of particular relevance to dealing with strong electrolytes is the successful use of the algorithm to generate the phase diagrams of challenging polymer-solvent mixtures in which the mole fraction of the polymer can be vanishingly small in one of the phases, as was demonstrated in the original paper (Pereira et al., 2012). Such problems can be solved with HELD through the use of a logarithmic transformation without imposing that the polymer be present in only one phase, as many alternative algorithms assume. As we will show, an added benefit of this framework when applied to electrolyte solutions is that the dual problem involves only $C-1$ variables for a mixture with $C$ components, regardless of the number of stable phases. In the case of solutions involving molecular species only, the dual problem involves $C$ variables.

The current article is organized as follows. In Section 2, we introduce the notation and equations relevant to electrolyte solutions, focusing on the impact of electroneutrality on chemical potentials. In Section 3, we derive a criterion for phase stability based on the tangentplane distance concept and present reformulations of the criterion via duality theory. In Section 4, we build on this formalism to extend the HELD algorithm, adapting each step of the algorithm as needed. The performance of the resulting HELD2.0 algorithm for mixtures that include strong electrolytes is illustrated in Section 5 by studying the effect of symmetric and asymmetric alkali halides on the fluidphase equilibria of mixed solvents. Some proofs and all of the model parameters used are provided in the Appendices, while supporting data are made available in the Zenodo repository, as described in the Data Statement at the end of the paper.

\section*{2. Preliminaries}

\subsection*{2.1. From salts to ionic species}

Let us consider an electrolyte (salt) of type $Y_{\nu^{+}} X_{\nu^{-}}$that fully dissociates in a polar solvent as follows:
$Y_{v^{+}} X_{v^{-}} \longrightarrow v^{+} Y^{z^{+}}+v^{-} X^{z^{-}}$.
where $v^{+}$and $v^{-}$are stoichiometric coefficients, $z^{+}$is the (positive) charge of cation $Y^{z^{+}}$, and $z^{-}$the (negative) charge of anion $X^{z^{-}}$, such that $v^{+} z^{+}+v^{-} z^{-}=0$.

The extension to multiple salts requires care in terms of identifying an independent set of ionic species (Nikolaidis et al., 2022). Consider a mixture of $M$ strong electrolytes and $S$ molecular species, $Y_{m, v_{m}^{+}} X_{m, v_{m}^{-}}$, $m=1, \ldots, M$, where $v_{m}^{+}$and $v_{m}^{-}$are stoichiometric coefficients specific to salt $m$. These salts will dissociate into a number $E_{C}$ of cations and a number $E_{A}$ of anions, where $E_{C} \leq M$ and $E_{A} \leq M$ since two or more salts may share the same anion or cation. For each salt $m$, we define the pair ( $c_{m}, a_{m}$ ), where $c_{m} \in\left\{1, \ldots, E_{C}\right\}$ denotes the index of the cation present in salt $m$, and $a_{m} \in\left\{1, \ldots, E_{A}\right\}$ denotes the index of the anion
present in salt $m$. The dissociation of salt $m$ is then given by

$$
\begin{equation*}
Y_{m, v^{+}} X_{m, v^{-}} \longrightarrow v_{m}^{+} Y_{c_{m}}^{z^{+}}+v_{m}^{-} X_{a_{m}}^{z^{-}}, \quad m=1, \ldots, M \tag{2}
\end{equation*}
$$


From a macroscopic point of view, any phase containing ions exhibit bulk neutrality (Guggenheim, 1935), which can be represented as

$$
\begin{equation*}
\sum_{c=1}^{E_{C}} z_{c}^{+} x_{c}^{+}+\sum_{a=1}^{E_{A}} z_{a}^{-} x_{a}^{-}=0 \tag{3}
\end{equation*}
$$

where $x_{c}^{+}$and $x_{a}^{-}$represent the mole fractions of cation $c$ and anion $a$, respectively, in the given phase. These mole fractions are calculated by considering that the mixture contains $C$ components, with $C= E_{A}+E_{C}+S$, where $S$ is the number of species that cannot undergo dissociation (molecular species or solvents). Electroneutrality of each equilibrium phase, and hence of the mixture at its total composition, is assumed throughout. As a result, the maximum value that can be taken on by $x_{c}^{+}$and $x_{a}^{-}$is always strictly less than 1 and upper bounds on the mole fractions can be set as follows:
$x_{c}^{+, U}=1-\frac{z_{c}^{+}}{z_{c}^{+}+\max _{a \in E_{A}}\left|z_{a}^{-}\right|}, c=1, \ldots, E_{C}$,

$$
\begin{equation*}
x_{a}^{-, U}=1-\frac{\left|z_{a}^{-}\right|}{\left|z_{a}^{-}\right|+\max _{c \in E_{C}} z_{c}^{+}}, \quad a=1, \ldots, E_{A} . \tag{4}
\end{equation*}
$$


\subsection*{2.2. The (electro)chemical potential and electroneutrality}

Let us now consider a mixture at temperature $T$ and pressure $P$ containing $C$ components, including $E=E_{A}+E_{C}$ ionic species ( $E \geq 2$ ), derived from $M$ salts that fully dissociate in solution ( $M \geq 1$ ) as shown in the previous section, as well as $S$ molecular species ( $S \geq 1$ ), such that $C=E+S$. The overall (total) composition of the mixture is represented by the vector $\mathbf{n}$ of size $C$, whose first $E$ components are the total mole numbers of ions and components $E+1$ to $C$ are the total mole numbers of the molecular species. The charge of component $i, i=1, \ldots, C$, is represented by $z_{i}$, where $z_{i}$ is positive or negative for $i=1, \ldots, E$ (corresponding to ionic species $i$ ), and is zero for $i=E+1, \ldots, C$ (corresponding to molecular species $i-E$ ).

The mixture satisfies the principle of macroscopic electroneutrality so that

$$
\begin{equation*}
\sum_{i=1}^{C} z_{i} n_{i}=0, \tag{6}
\end{equation*}
$$

where $n_{i}$ is the $i$ th component of $\mathbf{n}$. The total number of moles, $n_{t}$, in the mixture is given by

$$
\begin{equation*}
n_{t}=\sum_{i=1}^{C} n_{i} . \tag{7}
\end{equation*}
$$


It is important to notice that the summation is over the set of ionic species (anions and cations) and molecular species, and does not involve any of the salts.

We denote the extensive Gibbs free energy for a single phase by $\underline{G}(T, P, \mathbf{n})$, where underline denotes that the property is extensive. To determine a stable state of the system, we seek a global minimum of the Gibbs free energy with the constraint that every stable phase must satisfy the electroneutrality condition. Under this constraint, it can be shown that the equality across all phases of (i) temperatures, (ii) pressures, (iii) electrochemical potentials for $E-1$ charged species, and (iv) chemical potentials for all molecular species are necessary conditions for a given combination of phases and compositions to be stable (Guggenheim, 1935; Zemaitis et al., 2010). Note that only $E-1$ charge species are needed by use of the electroneutrality condition. The electrochemical potential of species $i$, $\tilde{\mu}_{i}$, is defined as the partial molar Gibbs free energy for the electroneutral (constrained) system and is related to its chemical potential, $\mu_{i}$, by Cohen et al. (2007)

$$
\begin{equation*}
\tilde{\mu}_{i}=\mu_{i}+z_{i} F \Phi, \tag{8}
\end{equation*}
$$

where $F$ is the Faraday constant, and $\Phi$ is the potential difference, also referred to as the local electrostatic potential.

It is convenient to define a constrained Gibbs free energy function, $\underline{G}^{e l}$, which is obtained by imposing the electroneutrality condition on all phases. To do this, we first introduce a reduced mole number vector, $\mathbf{n}^{(E)}$, with components $n_{i}^{(E)}, i \in \mathcal{C}^{(E)}=\{1, \ldots, E-1, E+1, \ldots, C\}$, where the ${ }^{(E)}$ superscript denotes that component $E$ has been removed. Vector $n_{i}^{(E)}$ is thus a ( $C-1$ )-dimensional vector. It is derived from $\mathbf{n}$ by eliminating the mole number of one charged species through the application of the electroneutrality condition:

$$
\begin{equation*}
n_{E}=\sum_{i \in \mathcal{C}^{(E)}}-\frac{z_{i}}{z_{E}} n_{i}=\sum_{i \in \mathcal{C}^{(E)}}-\frac{z_{i}}{z_{E}} n_{i}^{(E)}, \tag{9}
\end{equation*}
$$

where $n_{i}^{(E)}=n_{i}, \forall i \in \mathcal{C}^{(E)}$. Note that any charged species could have been removed and species $E$ has been chosen without loss of generality. The constrained Gibbs free energy can then be written as follows for a single phase:

$$
\begin{align*}
\underline{G}^{e l}\left(T, P, \mathbf{n}^{(E)}\right) & =\underline{G}\left(T, P, n_{1}^{(E)}, \ldots, n_{E}\left(\mathbf{n}^{(E)}\right), \ldots, n_{C}^{(E)}\right),  \tag{10}\\
& =\underline{G}\left(T, P, n_{1}, \ldots, n_{E}\left(\mathbf{n}^{(E)}\right), \ldots, n_{C}\right) . \tag{11}
\end{align*}
$$


The constrained Gibbs function is thus the intersection of the Gibbs function with the plane $\left\{\mathbf{n} \in \mathbb{R}_{+}^{C-1}: n_{E}=\sum_{i \in \mathcal{C}^{(E)}}-\frac{z_{i}}{z_{E}} n_{i}\right\}$. At all points $\mathbf{n}$ that belong to this set and corresponding $\mathbf{n}^{(E)}$, we have

$$
\begin{equation*}
\underline{G}(T, P, \mathbf{n})=\underline{G}^{e l}\left(T, P, \mathbf{n}^{(E)}\right) . \tag{12}
\end{equation*}
$$


We are interested in the relationship between two types of partial molar quantities: those obtained from the unconstrained Gibbs free energy $\underline{G}$ (the chemical potential) and those obtained from the constrained Gibbs free energy $\underline{G}^{e l}$ (the electrochemical potential). For this purpose, we use the following relationship:

$$
\begin{equation*}
\left(\frac{\partial n_{i}}{\partial n_{i}^{(E)}}\right)_{\substack{n_{j, j \neq i}^{(E)} \\ r_{j}}}=1, \tag{13}
\end{equation*}
$$

as well as the partial derivative of $n_{E}$ with respect to $n_{i}^{(E)}$, obtained using Eq. (9):

$$
\begin{equation*}
\left(\frac{\partial n_{E}}{\partial n_{i}^{(E)}}\right)_{\substack{(E) \\ n_{j, j \neq i}}}=-\frac{z_{i}}{z_{E}}, \quad \forall i \in \mathcal{C}^{(E)} \tag{14}
\end{equation*}
$$


Using the chain rule in a way similar to Modell and Reid (1983) and Walas (1985), we then have

$$
\begin{align*}
\left(\frac{\partial G^{e l}\left(T, P, \mathbf{n}^{(E)}\right)}{\partial n_{i}^{(E)}}\right)_{n_{j, j \neq i}^{(E)}} & =\left(\frac{\partial \underline{G}(T, P, \mathbf{n})}{\partial n_{i}}\right)_{T, P, n_{k, k \neq i}}-\frac{z_{i}}{z_{E}}\left(\frac{\partial \underline{G}(T, P, \mathbf{n})}{\partial n_{E}}\right)_{n_{k, k \neq E}}, \quad \forall i \in \mathcal{C}^{(E)} \\
& =\mu_{i}(T, P, \mathbf{n})-\frac{z_{i}}{z_{E}} \mu_{E}(T, P, \mathbf{n}), \quad \forall i \in \mathcal{C}^{(E)}, \\
& \equiv \mu_{i}^{e l}\left(T, P, \mathbf{n}^{(E)}\right), \quad \forall i \in \mathcal{C}^{(E)} . \tag{15}
\end{align*}
$$


\subsection*{2.3. Remarks}
- Eq. (15) applies equally to charged and molecular species. For a molecular species $i, i>E$, we recover $\mu_{i}^{e l}=\mu_{i}$ since $z_{i}=0$.
- From the definitions of the electrochemical potential in Eqs. (8) and (15), we note that

$$
\begin{equation*}
\boldsymbol{F} \boldsymbol{\Phi}=-\frac{\mu_{E}}{z_{E}}, \tag{16}
\end{equation*}
$$

thereby establishing a link between the chemical potential and the potential difference for the case of electrochemically neutral systems.
- Applying Eq. (16) to Eq. (8) for $i=E$, we find that $\mu_{E}^{e l}=0$, so that the electrochemical potential of component $E$ is trivially equal across all phases. This is consistent with the definition of $\underline{G}^{e l}$ as independent of $n_{E}$ and with the fact that only $C-1$ equilibrium conditions are independent when charged species are present.

\section*{3. Stability criteria for mixtures with strong electrolytes}

In this section, we derive a tangent-plane distance stability criterion for mixtures containing strong electrolytes. The criterion is recast based on duality theory and this is presented as equivalent formulations in the temperature-pressure-composition or temperature-volume-composition spaces. For mixtures of molecular species, the tangent-plane distance criterion of Baker et al. (1982) can be expressed in the space of $C-1$ mole fractions. Analogously, with the introduction of charged species and of the corresponding electroneutrality condition, the equivalent criterion can be expected to be a function of $C-2$ independent mole fractions, with the tangent taken with respect to the constrained Gibbs free energy $\underline{G}^{e l}$ surface, rather than the Gibbs free energy.

Here, we first show how the gradients of the tangent plane are related to the electrochemical potential. In the course of the derivations, we find it is convenient to introduce a change of variables that results in the complete elimination of $n_{E}$, the number of moles of electrically charged species $E$. We then provide a formal proof of the tangentplane stability criterion. We derive the dual extremum principle in the presence of fully dissociating salts, as an alternative stability criterion which we recast in terms of the Helmholtz free energy.

\subsection*{3.1. Derivatives of the constrained Gibbs free energy surface}

In order to formulate the tangent-plane distance criterion, we require a relationship between the derivatives of the constrained Gibbs free energy surface with respect to the $C-2$ independent mole fractions and known thermodynamic quantities, such as the chemical potentials. Consider a $C$-dimensional vector of mole fractions, $\mathbf{x}$, with components ordered as previously. To reduce the dimensionality of this vector, one mole fraction can be eliminated by using the fact that the mole fractions must sum to 1 . We choose to eliminate the mole fraction $x_{C}$ of species $C$, i.e., the last molecular species. The vector of $C-1$ mole fractions that excludes $x_{C}$ is denoted by $\mathbf{x}^{(C)}$, with elements $x_{i}^{(C)}, i \in \mathcal{C}^{(C)}=\{1, \ldots, C-1\}$. A second mole fraction can be eliminated through the electroneutrality condition, Eq. (6). Without loss of generality, we eliminate $x_{E}$ by using the following expression:
$x_{E}=\sum_{i \in \mathcal{C}^{(E)}}-\frac{z_{i}}{z_{E}} x_{i}$.

The set of remaining component indices is denoted by $\mathcal{C}^{(E C)}=\{1, \ldots, E-1, E+1, \ldots, C-1\}$ and the resulting ( $C-2$ )-dimensional vector of mole fractions is denoted by $\mathbf{x}^{(E C)}$. We thus have $x_{i}^{(E C)}=x_{i}^{(C)}=x_{i}, \forall i \in \mathcal{C}^{(E C)}$ and $x_{E}^{(C)}=x_{E}$. We use the chain rule (Modell and Reid, 1983; Walas, 1985) to express the relationship between the derivatives of the intensive free energies $G^{e l}\left(T, P, \mathbf{x}^{(E C)}\right)$ and $G\left(T, P, \mathbf{x}^{(C)}\right)$ as follows:

$$
\begin{align*}
G_{x_{i}^{(E C)}}^{e l}\left(T, P, \mathbf{x}^{(E C)}\right) & \equiv\left(\frac{\partial G^{e l}}{\partial x_{i}^{(E C)}}\right)_{T, P, x_{j, j \neq i}^{(E C)}}, \quad \forall i \in \mathcal{C}^{(E C)}, \\
& =\left(\frac{\partial G}{\partial x_{i}^{(C)}}\right)_{T, P, x_{j, j \neq i}^{(C)}}+\left(\frac{\partial G}{\partial x_{E}^{(C)}}\right)_{T, P, x_{j, j \neq E}^{(C)}}\left(\frac{\partial x_{E}^{(C)}}{\partial x_{i}^{(C)}}\right)_{x_{j, j \neq i}^{(C)}}, \quad \forall i \in \mathcal{C}^{(E C)}, \\
& =G_{x_{i}^{(C)}}\left(T, P, \mathbf{x}^{(C)}\right)-\frac{z_{i}}{z_{E}} G_{x_{E}^{(C)}}\left(T, P, \mathbf{x}^{(C)}\right), \quad \forall i \in \mathcal{C}^{(E C)}, \tag{18}
\end{align*}
$$

where the generic notation $G_{x_{i}}$ denotes the partial derivative of function $G$ with respect to mole fraction $x_{i}$. Introducing the standard thermodynamic relation for the partial derivative of the Gibbs free energy with respect to $C-1$ independent mole fractions (the gradients of the tangent plane in the case of molecular species), i.e.,
$G_{x_{i}^{(C)}}=\mu_{i}-\mu_{C}, \quad i=1, \ldots, C-1$,
we find that
$G_{x_{i}^{(E C)}}^{e l}=\mu_{i}-\mu_{C}-\frac{z_{i}}{z_{E}}\left(\mu_{E}-\mu_{C}\right), \quad \forall i \in C^{(E C)}$.

Re-arranging and using the fact that the electrochemical and chemical potentials of molecular species are equal, this yields
$G_{x_{i}^{(E C)}}^{e l}=\mu_{i}^{e l}-\left(1-\frac{z_{i}}{z_{E}}\right) \mu_{C}^{e l}, \quad i \in C^{(E C)}$.

Of particular note is the fact that the prefactor of $\mu_{C}^{e l}$ (equivalently $\mu_{C}$, since $\mu_{i}^{e l}=\mu_{i}$ for molecular species) depends on the charge $z_{i}$ of species $i$ so that the gradients of the constrained Gibbs free energy for any charged species $i, i=1, \ldots, E-1$, are such that $G_{x_{i}^{(E C)}}^{e l} \neq \mu_{i}^{e l}-\mu_{C}^{e l}$. Overall, the gradients of the constrained Gibbs free energy in the reduced variable space are given by

$$
G_{x_{i}^{(E C)}}^{e l}= \begin{cases}\mu_{i}^{e l}-\left(1-\frac{z_{i}}{z_{E}}\right) \mu_{C}^{e l}, & i=1, \ldots, E-1,  \tag{22}\\ \mu_{i}-\mu_{C}, & i=E+1, \ldots, C-1 .\end{cases}
$$


\subsection*{3.2. Changes of variables}

We now introduce a change of variables that enables one to formulate the phase stability criterion in a form analogous to the case when only molecular species are present. This change in variable is different to that proposed in Ascani et al. (2022), which is based on the consideration of pairs of independent anions and cations, rather than on individual ionic species. The proposed transformation results in a reduction in the dimensionality of the problem.

\subsection*{3.2.1. Modified mole numbers}

We consider the modified ( $C-1$ )-dimensional vector of mole numbers, $\overline{\mathbf{n}}$, defined as
$\bar{n}_{i}^{(E)}=\left(1-\frac{z_{i}}{z_{E}}\right) n_{i}=\left(1-\frac{z_{i}}{z_{E}}\right) n_{i}^{(E)}, \quad \forall i \in \mathcal{C}^{(E)}$,
where the following holds for molecular species with charge $z_{i}=0$ :
$\bar{n}_{i}^{(E)}=n_{i}=n_{i}^{(E)}, \quad \forall i \in\{E+1, \ldots, C\}$,
i.e., the mole numbers for molecular species are invariant with respect to the proposed transformation. Nevertheless, we use the generalized formulation of Eq. (23) as it applies equally to all species.

The vector $\overline{\mathbf{n}}^{(E)}$ holds a simple relationship to the total mole number:
$\sum_{i \in \mathcal{C}^{(E)}} \bar{n}_{i}^{(E)}=n_{t}$,
and $n_{E}$ can be calculated from $\overline{\mathbf{n}}^{(E)}$ :
$n_{E}=\sum_{i \in \mathcal{C}^{(E)}}-\frac{z_{i}}{z_{E}}\left(1-\frac{z_{i}}{z_{E}}\right)^{-1} \bar{n}_{i}^{(E)}$.

The extensive Gibbs free energy as a function of $\overline{\mathbf{n}}^{(E)}$ is referred to as the modified Gibbs function, $\underline{\bar{G}}^{e l}\left(T, P, \overline{\mathbf{n}}^{(E)}\right)$. Trivially, for any pair $\left(\overline{\mathbf{n}}^{(E)}, \mathbf{n}^{(E)}\right)$ related by Eq. (23),
$\underline{\bar{G}}^{e l}\left(T, P, \overline{\mathbf{n}}^{(E)}\right)=\underline{G}^{e l}\left(T, P, \mathbf{n}^{(E)}\right)$.

Furthermore, using the chain rule, we can derive a relationship between the relevant partial molar quantities:

$$
\begin{align*}
\bar{\mu}_{i}^{e l} & \equiv\left(\frac{\partial \bar{G}^{e l}\left(T, P, \overline{\mathbf{n}}^{(E)}\right)}{\partial \bar{n}_{i}^{(E)}}\right)_{T, P, \bar{n}_{j, j \neq i}^{(E)}}, \quad \forall i \in \mathcal{C}^{(E)} \\
& =\left(1-\frac{z_{i}}{z_{E}}\right)^{-1}\left(\frac{\partial \underline{G}^{e l}\left(T, P, \mathbf{n}^{(E)}\right)}{\partial n_{i}^{(E)}}\right)_{T, P, n_{j, j \neq i}^{(E)}}, \quad \forall i \in \mathcal{C}^{(E)}  \tag{28}\\
& =\left(1-\frac{z_{i}}{z_{E}}\right)^{-1} \mu_{i}^{e l}, \quad \forall i \in \mathcal{C}^{(E)} .
\end{align*}
$$

$\bar{\mu}_{i}^{e l}$ is referred to as the modified electrochemical potential. Since the pre-factor that relates the modified and classical electrochemical potentials is independent of composition, the equality of electrochemical potentials of $C-1$ components across all phases is equivalent to the equality of the modified electrochemical potentials of $C-1$ components
across all phases:

$$
\begin{equation*}
\bar{\mu}_{i}^{e l}\left(T, P, \overline{\mathbf{n}}^{(E), j}\right)=\bar{\mu}_{i}^{e l}\left(T, P, \overline{\mathbf{n}}^{(E), j^{*}}\right), \quad \forall i \in \mathcal{C}^{(E)}, \quad \forall j \in J, \tag{29}
\end{equation*}
$$

where $J$ is an index set defining the stable equilibrium phases, $j^{*} \in J$ denotes one of the stable phases (chosen arbitrarily) and $\overline{\mathbf{n}}^{j}$ is the modified mole number vector in a phase $j, j \in J$.

\subsection*{3.2.2. Modified mole fractions}

A further transformation involves the usual change to mole fractions, where the modified mole fractions, $\bar{x}_{i}^{(E)}, i \in \mathcal{C}^{(E)}$, are of interest here:

$$
\begin{equation*}
\bar{x}_{i}^{(E)}=\frac{\bar{n}_{i}^{(E)}}{n_{t}}=\left(1-\frac{z_{i}}{z_{E}}\right) x_{i}^{(E)}, \quad \forall i \in \mathcal{C}^{(E)} . \tag{30}
\end{equation*}
$$


Using Eq. (25), we find that the sum of the modified mole fractions equals 1 ,

$$
\begin{equation*}
\sum_{i \in \mathcal{C}^{(E)}} \bar{x}_{i}^{(E)}=1, \tag{31}
\end{equation*}
$$

even though the set $\mathcal{C}^{(E)}$ does not include component $E$. Using this property and a standard approach to eliminate the last mole fraction $\bar{x}_{C}^{(E)}$ (see for example, p. 121 of Walas, 1985), we introduce vector $\overline{\mathbf{x}}^{(E C)}$ with dimensionality $C-2$ and we express the modified electrochemical potential in terms of the derivatives, $\bar{G}_{\bar{x}_{i}^{(E C)}}^{e l}$, of the modified Gibbs function with respect to $\bar{x}_{i}^{(E C)}, i \in \mathcal{C}^{(E C)}$. Specifically, defining $\bar{G}^{e l}$ as the intensive modified Gibbs free energy, we find that

$$
\begin{equation*}
\bar{\mu}_{i}^{e l}\left(T, P, \overline{\mathbf{n}}^{(E)}\right)=\bar{G}^{e l}+\bar{G}_{\bar{x}_{i}^{(E C)}}^{e l}-\sum_{j \in \mathcal{C}^{(E C)}} \bar{G}_{\bar{x}_{j}^{(E C)}}^{e l} \bar{x}_{j}^{(E C)}, \quad \forall i \in \mathcal{C}^{(E C)}, \tag{32}
\end{equation*}
$$

and

$$
\begin{equation*}
\bar{\mu}_{C}^{e l}\left(T, P, \overline{\mathbf{n}}^{(E)}\right)=\bar{G}^{e l}-\sum_{j \in \mathcal{C}^{(E C)}} \bar{G}_{\bar{x}_{j}^{(E C)}}^{e l} \bar{x}_{j}^{(E C)}, \tag{33}
\end{equation*}
$$

so that

$$
\begin{equation*}
\bar{\mu}_{i}^{e l}\left(T, P, \overline{\mathbf{n}}^{(E)}\right)=\bar{\mu}_{C}^{e l}\left(T, P, \overline{\mathbf{n}}^{(E)}\right)+\bar{G}_{\bar{x}_{i}^{(E C)}}^{e l}, \quad \forall i \in \mathcal{C}^{(E C)} . \tag{34}
\end{equation*}
$$


\subsection*{3.3. The tangent plane criterion for electrolyte systems}

We now present a stability criterion for electrolyte systems, based on the tangent plane distance stability criterion (Baker et al., 1982) and the formalism of Theorem 5 in Mitsos and Barton (2007). We show that the criterion holds for the plane tangent to the proposed modified Gibbs function.

Theorem 3.1. Consider a system of $C$ species, of which species 1 to $E$ are charged, $E<C$, at given $T$ and $P$ and total modified mole numbers $\bar{n}_{o, i}^{(E)}>0, i \in \mathcal{C}^{(E)}=\{1, \ldots, E-1, E+1, \ldots, C\}$. Denote $\bar{n}_{t, o}=\sum_{i \in \mathcal{C}^{(E)}} \bar{n}_{o, i}^{(E)}$. Consider a state described by a collection of electroneutral phases with index $J$ and modified mole fractions $\overline{\mathbf{x}}^{(E C), j} \in \operatorname{int}\left(\bar{X}^{(E C)}\right)$ where

$$
\begin{equation*}
\bar{X}^{(E C)}=\left\{\overline{\mathbf{x}}^{(E C)} \in[0,1]^{C-2}: \sum_{i \in \mathcal{C}^{(E C)}} \bar{x}_{i}^{(E C)}<1\right\}, \tag{35}
\end{equation*}
$$

and with nonzero total mole numbers in each phase, $\bar{n}_{t}^{(E), j}>0$, such that $\bar{n}_{o, i}^{(E)}=\sum_{j \in J} \bar{n}_{i}^{(E), j}, i \in \mathcal{C}^{(E)}$.

Consider the tangent to the modified intensive Gibbs free energy function, $\bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right)$, at $\overline{\mathbf{x}}^{(E C), j^{*}}$ for some $j^{*} \in J$ :

$$
\begin{align*}
T_{G}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right)= & \bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{E C, j^{*}}\right) \\
& +\sum_{i \in \mathcal{C}^{(E C)}} \bar{G}_{\bar{x}_{i}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j^{*}}\right)\left(\bar{x}_{i}^{(E C)}-\bar{x}_{i}^{(E C), j^{*}}\right) . \tag{36}
\end{align*}
$$


The state is stable if and only if

$$
\begin{equation*}
T_{G}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right) \leq \bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right), \quad \forall \overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)} \tag{37}
\end{equation*}
$$

and

$$
\begin{align*}
T_{G}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right)= & \bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right) \\
& +\sum_{i \in \mathcal{C}^{(E C)}} \bar{G}_{\bar{x}_{i}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right)\left(\bar{x}_{i}^{(E C)}-\bar{x}_{i}^{(E C), j}\right),  \tag{38}\\
& \quad \forall \overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)}, \quad \forall j \in J .
\end{align*}
$$


A proof of this Theorem is given in Appendix A. As previously mentioned, the tangent-plane stability criterion for solutions of strong electrolytes is expressed in terms of $C-2$ mole fractions, reflecting the fact that the equality of electrochemical potentials applies to $C-1$ components. The criterion is analogous to that for mixtures of molecular compounds, but formulated in the (reduced) space of modified mole fractions. Furthermore, from Eq. (34), we note that the gradients of the tangent plane are given by

$$
\begin{equation*}
\bar{G}_{\bar{x}_{i}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right)=\bar{\mu}_{i}^{e l}\left(T, P, \overline{\mathbf{n}}^{(E C)}\right)-\bar{\mu}_{C}^{e l}\left(T, P, \overline{\mathbf{n}}^{(E C)}\right), \quad \forall i \in \mathcal{C}^{(E C)} . \tag{39}
\end{equation*}
$$


This is again analogous to the molecular case where the gradients of the tangent plane are given by Eq. (19). Furthermore, it is straightforward to show that the two equations derived for the tangent-plane gradients, Eqs. (21) and (39), are equivalent.

Theorem 3.1 can be used to determine whether a given state described by $J$ phases with modified mole fractions $\overline{\mathbf{x}}^{(E C), j} \in \operatorname{int}(\bar{X})^{(E C)}$ is unstable by examining whether there exists $\overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)}$ such that the distance $d\left(\overline{\mathbf{x}}^{(E C)} ; \overline{\mathbf{x}}^{(E C), j}\right)$ between the modified Gibbs free energy and the corresponding tangent for some $j \in J$ is non-positive. This can be stated as

$$
\begin{align*}
& \exists \overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)}: d\left(\overline{\mathbf{x}}^{(E C)} ; \overline{\mathbf{x}}^{(E C), j}\right) \\
& \equiv \bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right)-\bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right)  \tag{40}\\
&-\sum_{i \in \mathcal{C}^{(E C)}} \bar{G}_{\bar{x}_{i}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right)\left(\bar{x}_{i}-\bar{x}_{i}^{(E C), j}\right)<0
\end{align*}
$$


As suggested in Michelsen (1982a), this can be framed as a minimization of the distance function $d\left(\overline{\mathbf{x}}^{(E C)} ; \overline{\mathbf{x}}^{(E C), j}\right)$ over all $\overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)}$ and incorporated into the classical Michelsen iterative algorithm for phase equilibria and phase stability (Michelsen, 1982b). Indeed, as in the work of Smith et al. (1993) on chemical equilibrium and stability, the standard tangent-plane distance criterion used for phase equilibrium (Baker et al., 1982; Michelsen, 1982a) is a special case of the more general criterion in Theorem 3.1.

The proposed stability criterion can be compared to that stated by Tsanas et al. (2019). A key difference is that the tangent-plane distance function in Tsanas et al. (2019) is given as a summation over all $C$ components in the mixture, subject to a mass balance constraint on the trial phase. The electroneutrality condition is not stated explicitly as a constraint although it is introduced later in the paper, in the numerical-solution procedure. One would expect, however, that a stability criterion based on a tangent plane defined over $C$ mole numbers should include an explicit electroneutrality constraint so that the tangent-plane distance minimization is in fact a constrained optimization problem.

\subsection*{3.4. Dual extremum principle}

We now consider an equivalent duality-based stability criterion for mixtures with strong electrolytes, based on concepts from duality theory (Bazaraa et al., 2013). We define a primal problem and the corresponding dual problem formulation for a mixture of $C$ components as described in Theorem 3.1, before extending the dual extremum principle of Mitsos and Barton (2007) to electrolyte systems. Consider the trivial optimization problem,

$$
\begin{array}{ll}
\min _{\overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)}} & \bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right)  \tag{41}\\
\text { s.t. } & \bar{x}_{o, i}^{(E C)}-\bar{x}_{i}^{(E C)}=0, \quad \forall i \in \mathcal{C}^{(E C)}
\end{array}
$$

where

$$
\begin{equation*}
\bar{X}^{(E C)}=\left\{\overline{\mathbf{x}} \in[0,1]^{C-2}: \sum_{i \in \mathcal{C}^{(E C)}} \bar{x}_{i}^{(E C)}<1\right\} . \tag{42}
\end{equation*}
$$


This primal problem has a corresponding dual problem (Bazaraa et al., 2013) given by

$$
\begin{equation*}
\max _{\bar{\lambda} \in \mathbb{R}^{C-2}} \min _{\overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)}} \bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right)+\sum_{i \in \mathcal{C}^{(E C)}} \bar{\lambda}_{i}\left(\bar{x}_{o, i}^{(E C)}-\bar{x}_{i}^{(E C)}\right), \tag{43}
\end{equation*}
$$

where the objective function of the lower-level problem (the minimization with respect to $\overline{\mathbf{x}}^{(E C)}$ ) is the Lagrange function corresponding to primal problem (41):

$$
\begin{equation*}
\overline{\mathcal{L}}^{e l}\left(\overline{\mathbf{x}}^{(E C)}, \bar{\lambda}\right)=\bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right)+\sum_{i \in \mathcal{C}^{(E C)}} \bar{\lambda}_{i}\left(\bar{x}_{o, i}^{(E C)}-\bar{x}_{i}^{(E C)}\right) . \tag{44}
\end{equation*}
$$


It can be shown that there is a strict equivalence between the stable equilibrium states and the solutions of Problem (43), i.e., all solutions of (43) are stable equilibrium states and vice versa. This is stated in the following theorem.

Theorem 3.2. Consider a system of $C$ species, of which species 1 to $E$ are charged, $E<C$, at given $T, P$, and total modified mole numbers $\bar{n}_{o, i}^{(E)}>0$, $i \in \mathcal{C}^{(E)}=\{1, \ldots, E-1, E+1, \ldots, C\}$. Denote $\bar{n}_{t, o}^{(E)}=\sum_{i \in \mathcal{C}^{(E)}} \bar{n}_{o, i}^{(E)}$. Consider a solution $\left(\bar{\lambda}^{*}, \overline{\mathbf{x}}^{(E C), *)}\right.$ of dual problem (43). The hyperplane

$$
\begin{equation*}
T_{G}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right)=\bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), *}\right)+\sum_{i \in \mathcal{C}^{(E C)}} \bar{\lambda}_{i}^{*}\left(\bar{x}_{i}^{(E C)}-\bar{x}_{i}^{(E C), *}\right) \tag{45}
\end{equation*}
$$

is a supporting hyperplane of $\bar{G}^{e l}$ on $\bar{X}^{(E C)}$, i.e.,

$$
\begin{equation*}
T_{G}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right) \leq \bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right), \quad \forall \overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)} . \tag{46}
\end{equation*}
$$


Moreover, let $\bar{X}^{(E C), *}$ be the set of common points between $T_{G}$ as defined in Eq. (45) and the modified Gibbs function $\bar{G}^{e l}$, i.e.,

$$
\begin{equation*}
\bar{X}^{(E C), *}=\left\{\overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)}: T_{G}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right)=\bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right)\right\} . \tag{47}
\end{equation*}
$$


Then,

$$
\begin{equation*}
\overline{\mathbf{x}}_{o}^{(E C)} \in \operatorname{conv}\left(\bar{X}^{(E C), *}\right) . \tag{48}
\end{equation*}
$$


Finally, a state described by a collection of phases with index set $J$ and modified mole fractions $\overline{\mathbf{x}}^{(E C), j} \in \bar{X}^{(E C)}$ and with nonzero total number of moles in each phase $j, \bar{n}_{t}^{(E), j}>0$, and such that $\overline{\mathbf{x}}_{o}^{(E C)} \in \operatorname{conv}\left(\bar{X}^{(E C), *}\right)$, is stable if and only if $\overline{\mathbf{x}}^{(E C), j} \in \bar{X}^{(E C), *}, \forall j \in J$, or equivalently all pairs ( $\bar{\lambda}^{*}, \overline{\mathbf{x}}^{(E C), j}$ ) are (global) solutions of the dual problem.

A proof of this theorem is not given here as it is similar to that in Mitsos and Barton (2007). It relies on the fact that a global minimum in the Gibbs free energy subject to the electroneutrality constraint is also a global minimum in the modified Gibbs free energy. This stems from Eqs. (12) and (27) which hold over all feasible points, i.e., all points that satisfy the electroneutrality condition and mass balance. Once this is established, the remainder of the proof follows the reasoning in Mitsos and Barton (2007), together with associated propositions and lemmas.

As in Mitsos and Barton (2007), an important implication of this alternative stability criterion is that the stable equilibrium states of a given mixture can be found by identifying all global solutions of the dual problem (43), without the need to postulate the number of phases a priori. Specifically, one must find all global solutions of the dual variables, $\bar{\lambda}^{*}$, and the corresponding solutions of the primal problem, $\overline{\boldsymbol{x}}^{(E C), *}$.

\subsection*{3.5. Helmholtz free energy formulation of the dual extremum principle}

As was shown in the case of molecular mixtures (Pereira et al., 2010, 2012), the primal problem can be recast in terms of the Helmholtz free energy with the addition of the molar volume $V$ as a variable. This is numerically advantageous for equations of state expressed with natural canonical variables $T, V$ and $\mathbf{n}$, as is the case for the SAFT family of
equations (Chapman et al., 1988; Eriksen et al., 2016; Shaahmadi et al., 2023; McCabe and Galindo, 2010). To reformulate, we introduce the function $\hat{G}^{e l}\left(T, P_{o}, V, \overline{\mathbf{x}}\right)=\bar{A}^{e l}\left(T, V, \overline{\mathbf{x}}^{(E C)}\right)+P_{o} V$, in which the system pressure $P_{o}$ is a parameter and the constrained Helmholtz free energy, $\bar{A}^{e l}$, is expressed in terms of the modified mole fractions $\overline{\mathbf{x}}^{(E C)}$ and molar volume $V$. The function $\hat{G}^{e l}$ is only defined at mole fractions that satisfy the electroneutrality conditions, thanks to the use of the modified mole fractions, but it can be evaluated at molar volumes that do not correspond to pressure $P_{o}$. The primal problem is given by

$$
\begin{array}{ll}
\min _{\overline{\mathbf{x}}^{(E C)}, V} & \bar{A}^{e l}\left(T, V, \overline{\mathbf{x}}^{(E C)}\right)+P_{o} V \\
\text { s.t. } & \bar{x}_{o, i}^{(E C)}-\bar{x}_{i}^{(E C)}=0, \quad \forall i \in \mathcal{C}^{(E C)}  \tag{49}\\
& \overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)} \\
& V \in\left[V^{L}, V^{U}\right]
\end{array}
$$

where $V^{L}$ and $V^{U}$ are lower and upper bounds on the molar volume, respectively. The Lagrange function corresponding to this problem is

$$
\begin{equation*}
\overline{\mathcal{L}}^{e l, V}\left(\overline{\mathbf{x}}^{(E C)}, V, \bar{\lambda}\right)=\bar{A}^{e l}\left(T, V, \overline{\mathbf{x}}^{(E C)}\right)+P_{o} V+\sum_{i \in \mathcal{C}^{(E C)}} \bar{\lambda}_{i}\left(\bar{x}_{o, i}^{(E C)}-\bar{x}_{i}^{(E C)}\right) . \tag{50}
\end{equation*}
$$


This can be used to formulate the dual of Problem (49) as

$$
\begin{equation*}
\max _{\bar{\lambda} \in \mathbb{R}^{C-2}} \min _{\overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)}, V \in\left[V^{L}, V^{U}\right]} \overline{\mathcal{L}}^{e l, V}\left(\overline{\mathbf{x}}^{(E C)}, V, \bar{\lambda}\right) . \tag{51}
\end{equation*}
$$


For a given $\bar{\lambda}$, the solution $\left(\overline{\mathbf{x}}^{(E C), *}, V^{*}\right)$ of the lower-level minimization, i.e., the minimization of $\overline{\mathcal{L}}^{e l, V}$ with respect to $\overline{\mathbf{x}}^{(E C)}$ and $V$, is such that

$$
\begin{align*}
\left(\frac{\partial \overline{\mathcal{L}}^{e l, V}\left(\overline{\mathbf{x}}^{(E C), *}, V^{*}, \bar{\lambda}\right)}{\partial V}\right)_{\overline{\mathbf{x}}^{(E C)}, \bar{\lambda}} & =\left(\frac{\partial \bar{A}^{e l}\left(T, V^{*}, \overline{\mathbf{x}}^{(E C), *}\right)}{\partial V}\right)_{T, \overline{\mathbf{x}}^{(E C)}}+P_{o},  \tag{52}\\
& =-P\left(T, V^{*}, \overline{\mathbf{x}}^{(E C), *}\right)+P_{o}, \\
& =0,
\end{align*}
$$

and

$$
\begin{align*}
\left({\frac{\partial \overline{\mathcal{L}}^{e l, V}\left(\overline{\mathbf{x}}^{(E C), *}, V^{*}, \bar{\lambda}\right)}{\partial \bar{x}_{i}}}^{(E C)}\right)_{\bar{x}_{j \neq i}^{(E C)}, V, \bar{\lambda}}= & \left(\frac{\partial \bar{A}^{e l}\left(T, V^{*}, \overline{\mathbf{x}}^{(E C), *}\right)}{\partial \bar{x}_{i}^{(E C)}}\right)_{T, V, \bar{x}_{j \neq i}^{(E C)}} \\
& -\bar{\lambda}_{i}, \quad \forall i \in \mathcal{C}^{(E C)},  \tag{53}\\
= & 0, \quad \forall i \in \mathcal{C}^{(E C)},
\end{align*}
$$


Eq. (52) ensures that at any solution $\left(\mathbf{x}^{\left.(\overline{E C}), *, V^{*}\right)}\right.$ of the lower-level minimization of the Lagrange function, the optimal molar volume is that corresponding to pressure $P_{o}$ and $\hat{G}^{e l}\left(T, P_{o}, V^{*}, \overline{\mathbf{x}}^{(E C), *}\right) =\bar{G}^{e l}\left(T, P_{o}, \overline{\mathbf{x}}^{(E C), *}\right)$. Furthermore, combining this with Eq. (53), the following relation holds at the solution of the lower-level problem:

$$
\begin{equation*}
\left(\frac{\partial \bar{G}^{e l}\left(T, P_{o}, \overline{\mathbf{x}}^{(E C), *}\right)}{\partial \bar{x}_{i}^{(E C)}}\right)_{T, P, \bar{x}_{j \neq i}^{(E C)}}=\bar{\lambda}_{i}, \quad \forall i \in \mathcal{C}^{(E C)} . \tag{54}
\end{equation*}
$$


By invoking the dual extremum principle for mixtures containing strong electrolytes and following the reasoning in Pereira et al. (2012, 2010), one can show that for any solution $\left(\mathbf{x}^{(\overline{E C}), *}, V^{*}, \bar{\lambda}^{*}\right)$ of dual problem (51), the hyperplane $T_{A}\left(T, P_{o}, V, \overline{\mathbf{x}}^{(E C)}\right)$

$$
\begin{align*}
T_{A}\left(T, P_{o}, V, \overline{\mathbf{x}}^{(E C)}\right)= & \bar{A}^{e l}\left(T, V^{*}, \overline{\mathbf{x}}^{(E C), *}\right)+P_{o}\left(V^{*}-V\right) \\
& +\sum_{i \in \mathcal{C}^{(E C)}} \bar{\lambda}_{i}\left(\bar{x}_{i}^{(E C)}-\bar{x}_{i}^{(E C), *}\right) \tag{55}
\end{align*}
$$

is a supporting hyperplane of $\hat{G}^{e l}\left(T, P_{o}, V, \overline{\mathbf{x}}^{(E C)}\right)$ on $\left[V^{L}, V^{U}\right] \times \bar{X}^{(E C)}$ that passes through the point ( $V^{*}, \overline{\mathbf{x}}^{(E C), *}$ ). The intersection of $T_{A}$ with the set $\mathcal{V}=\left\{V \in\left[V^{L}, V^{U}\right]: P\left(T, V, \overline{\mathbf{x}}^{(E C)}\right)=P_{o}\right\}$ defines a hyperplane in $\bar{X}^{(E C)}$,

$$
\begin{align*}
T_{A, r}\left(T, P_{o}, \overline{\mathbf{x}}^{(E C)}\right)=\left\{\overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)}:\right. & \bar{A}^{e l}\left(T, V^{*}, \overline{\mathbf{x}}^{(E C), *}\right)+P_{o}\left(V^{*}-V^{\prime}\right) \\
& \left.+\sum_{i \in \mathcal{C}^{(E C)}} \bar{\lambda}_{i}\left(\bar{x}_{i}^{(E C)}-\bar{x}_{i}^{(E C), *}\right), \forall V^{\prime} \in \mathcal{V}\right\}, \tag{56}
\end{align*}
$$

that is a supporting hyperplane of $\bar{G}^{e l}\left(T, P_{o}, \overline{\mathbf{x}}^{(E C)}\right)$ on $\bar{X}^{(E C)}$ that passes through the point $\overline{\mathbf{x}}^{(E C), *}$, as a consequence of the optimality conditions (52)-(53). This supporting hyperplane is tangent to $\bar{G}^{e l}\left(T, P_{o}, \overline{\mathbf{x}}^{(E C)}\right)$ at the modified mole fractions of all stable phases. This is stated formally as a theorem in Appendix B but the proof is not shown here for conciseness. Dual problem (51) is used in the remainder of this paper to design an algorithm to find all stable equilibrium phases of an electrolyte solution at given conditions.

\section*{4. The HELD2.0 algorithm for the solution of the dual problem}

As has been remarked by Mitsos and Barton (2007), although the dual problem is always convex, it is typically difficult to solve due to the presence of the (nonconvex) inner minimization. They proposed an iterative solution strategy based on the reformulation of the dual problem as a semi-infinite program (SIP) and on the algorithm of Blankenship and Falk (1976). This was extended in the HELD algorithm (Pereira et al., 2012,2010 ) to support the identification of all stable phases using the Helmholtz free energy reformulation. In our current work, we adapt the HELD algorithm presented in Table 1 of Pereira et al. (2010) to account for systems incorporating charged species. This includes introducing the variable changes and modified Gibbs free energy defined in Section 3.2, modifying the initialization strategy, and implementing the upper-level and lower-level problems given in Section 3.5. This extended version of the HELD algorithm, which we refer to here as HELD2.0, supersedes the original version (Pereira et al., 2010): it can be applied to mixtures of molecular species and strong electrolytes (in which case, there must be at least one molecular species and two charged species).
The algorithm comprises three main stages (see Algorithm 1). In Stage I, an initial stability test is conducted to determine whether the mixture is stable at the conditions of interest; if not, it is necessary to proceed to Stage II and all relevant quantities are initialized before doing so. In Stage II, candidate stable phases are identified by solving the dual problem. Finally, in stage III, convergence tests are applied to ensure the necessary conditions for equilibrium are met with sufficient accuracy. This is especially important from a numerical perspective as the computations are very sensitive to small changes in the chemical potentials and because in Stage II the pressure is obtained as a result of the optimality conditions (subject to the optimality tolerance), rather than by imposing an equality constraint (subject to a usually tighter feasibility tolerance). If the convergence criteria are not met, the algorithm is set to return to Stage II. The steps of the algorithm are described in more detail in the remainder of this section, following the scheme in Algorithm 1 and with particular emphasis on adaptations to account for the presence of charged species. This is followed by a brief description of our specific implementation.

\subsection*{4.1. Input-output}

The HELD algorithm takes as input the mixture temperature, $T$, pressure $P_{o}$, and total composition given as a mole fraction vector $\mathbf{x}_{o}$. The output is the number of phases at equilibrium, $m p$, and the mole fractions $\mathbf{x}^{j}$ in each phase $j$ and corresponding phase fractions $\phi^{j}$.

\subsection*{4.2. Stage I: Stability test and initialization}

Stage I consists of three steps. In Step 1, the variable transformation is implemented using Eq. (30). This step is only necessary for mixtures containing charged species. Without loss of generality, component $E$ is selected to be the species with the largest absolute charge as this ensures that $\left|z_{i} / z_{E}\right| \leq 1$ for all $i \in C$. This avoids some modified mole fractions becoming negative. It also results in the smallest possible
```
Algorithm 1 HELD2.0 algorithm for the solution of the $P, T$ fluid phase
equilibrium problem for mixtures containing strong electrolytes.
    procedure $\operatorname{HELD}\left(T, P_{o}, \mathbf{x}_{o}\right)$
        Stage I: Stability test and initialization
        Step 1: Define mole fractions and their bounds
        Apply change of variables, Eqs. (23) and (30)
        Set the bounds on the modified mole fractions, Eqs. (57) and (61)
        Step 2: Stability test at ( $T, P_{o}, \overline{\mathbf{x}}_{o}^{(E C)}$ )
        Solve stability test up to $N_{S}$ times
        If negative tangent plane distance found, go to Step 3
        Else terminate
        Step 3: initialization of dual problem
            (a) Set major iteration counter $k=0$
            (b) initialize $U B D^{V}, \bar{L}^{V}$, set $\mathcal{M}$, bounds on $\bar{\lambda}$
        Stage II: Identification of candidate stable phases
        Step 4: Solve the upper-level problem, Eq. (64)
            Update $\bar{\lambda}^{k}=\bar{\lambda}^{*}$
            Update the best upper bound $U B D^{V}$
        Step 5: Solve the lower-level problem, Eq. (65).
            Use multistart algorithm until $\bar{L}^{V} \leq U B D^{V}$
            Add the final values of $V$ and $\overline{\mathbf{x}}^{(E C)}$ to $\mathcal{M}$
        Step 6: Search $\mathcal{M}$ for candidate stable phases.
            Apply criteria set out in Eq. (66) to populate $\mathcal{M}^{*}$
            If $m p=\left|\mathcal{M}^{*}\right| \geq 2$, go to Step 8
        Step 7: Increment iteration counter $k=k+1$ and go to Step 4
        Stage III: Acceleration and convergence tests
        Step 8: Minimization of the total Gibbs free energy
            Solve Problem (67)
            If infeasible, set $k=k+1$ and return to Step 4
            If feasible, eliminate duplicate phases and update number of phases $m p$
        Step 9: Convergence test
            If Eqs. (68) and/or (69) are violated, set $k=k+1$ and go to Step 4
        Step 10: Refine trace component modified mole fractions
            If any trace components are present, use logarithmic transformation in
            Eqs (70)-(72)
    end procedure
```

allowable ranges for the modified mole fractions, which may be beneficial in terms of convergence/solution time. These ranges of values are given by

$$
\begin{equation*}
\bar{x}_{i}^{(E C)} \in\left[\bar{x}_{i}^{(E C), L}, \bar{x}_{i}^{(E C), U}\right], \forall i \in \mathcal{C}^{(E C)}, \tag{57}
\end{equation*}
$$

where

$$
\begin{equation*}
\bar{x}_{i}^{(E C), L}=0 \text { and } \bar{x}_{i}^{(E C), U}=\left(1-\frac{z_{i}}{z_{E}}\right) x_{i}^{(E C), U}, \quad \forall i \in \mathcal{C}^{(E C)}, \tag{58}
\end{equation*}
$$

and where

$$
\begin{equation*}
x_{i}^{(E C), U}=1-\frac{\left|z_{i}\right|}{\left|z_{i}\right|+\max \substack{j \in\{1, \ldots, E-1\} \\ \operatorname{sgn}\left(z_{j}\right) \neq \operatorname{sgn}\left(z_{i}\right)}}\left|z_{j}\right|, \quad i=1, \ldots, E-1, \tag{59}
\end{equation*}
$$


$$
\begin{equation*}
x_{i}^{(E C), U}=1, \quad i=E, \ldots, C-2, \tag{60}
\end{equation*}
$$

and where $\operatorname{sgn}\left(z_{i}\right)$ denotes the sign of $z_{i}$, i.e., determines whether species $i$ is a cation or anion. The formulation in Eq. (59) is a generalization of that shown in Eqs. (4) and (5).

In our implementation, a finite value $\bar{x}_{i}^{(E C), l}$ is used for the lower bound on the modified mole fraction of component $i$ (by default, $\bar{x}_{i}^{(E C), l}=10^{-10}\left(1-z_{i} / z_{E}\right)$ ) to avoid issues with the logarithmic terms in the chemical potential expressions, so we have

$$
\begin{equation*}
\bar{x}_{i}^{(E C), L}=\bar{x}^{(E C), l}, \quad \forall i \in \mathcal{C}^{(E C)} \tag{61}
\end{equation*}
$$


Since electrolyte systems may exhibit phases with very low mole fractions of electrolytes, this constraint is lifted in the final stages of the algorithm, in Step 10.

In Step 2, a stability test based on the tangent-plane distance criterion is performed at the initial modified mole fractions $\overline{\mathbf{x}}_{o}^{(E C)}$. The tangent-plane distance $d\left(V, \overline{\mathbf{x}}^{(E C)} ; T, P_{o}, \overline{\mathbf{x}}_{o}^{(E C)}\right)$ is given by
$d\left(V, \overline{\mathbf{x}}^{(E C)} ; T, P_{o}, \overline{\mathbf{x}}_{o}^{(E C)}\right)=\bar{A}^{e l}\left(T, V_{o}, \overline{\mathbf{x}}_{o}^{(E C)}\right)-T_{A}\left(T, P_{o}, V, V_{o}, \overline{\mathbf{x}}^{(E C)}, \overline{\mathbf{x}}_{o}^{(E C)}\right)$.
where $V_{o}$ is the molar volume corresponding to ( $T, P_{o}, \overline{\mathbf{x}}_{o}^{(E C)}$ ).
The stability test is based on the global minimization of the tangentplane distance:

$$
\begin{equation*}
\min _{V \in\left[V^{L}, V^{U}\right], \overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)}} d\left(V, \overline{\mathbf{x}}^{(E C)} ; T, P_{o}, \overline{\mathbf{x}}_{o}^{(E C)}\right) \tag{63}
\end{equation*}
$$

to determine whether there exists any ( $V^{\prime}, \overline{\mathbf{x}}^{(E C)^{\prime}}$ ) such that $d\left(V^{\prime}, \overline{\mathbf{x}}^{(E C)^{\prime}} ; T, P_{o}, \overline{\mathbf{x}}_{o}^{(E C)}\right)<0$, i.e., whether the system is unstable at $\left(T, P_{o}, \overline{\mathbf{x}}_{o}^{(E C)}\right)$. The unique global solution of Problem (63) is $\left(V_{o}, \overline{\mathbf{x}}_{o}^{(E C)}\right)$ (and the corresponding value of $d$ is zero) if and only if the system is stable at the total composition.

The current implementation of the stability test in HELD is based on the tunnelling global optimization method developed by Levy and Gómez (1985) and by Nichita et al. (2002). Because this approach does not guarantee the identification of the global minimum, it is applied $N_{S}$ times, with starting points obtained by a random number generator with fixed seed and set within the variable bounds. The molar volume bounds are chosen to be consistent with the molar volume of a fluid phase. Suitable values can be derived from the packing fraction, $\eta$, a reduced density (Papaioannou et al., 2014). No substance can exhibit a phase with a packing fraction beyond the theoretical limit of $\eta=0.74$ so that the range $\eta \in\left[10^{-6}, 0.74\right]$ is used. Furthermore, we use $N_{S}=10 C$ to reflect the fact that problems with more components may be more challenging to solve. The application of deterministic global solvers would be challenging due to the complexity of the SAFT models, but is in principle achievable as shown with an interval Newton algorithm by Xu et al. (2005) and with a branch-and-bound deterministic global optimization solver in Pereira et al. (2010) for different variants of the SAFT EoS. If the minimization of the tunnelling function derived from Eq. (62) indicates that the global minimum of Problem (63) is equal to zero, the algorithm terminates, indicating that the initial composition is stable.

In Step 3, further initialization steps are performed prior to the iterative solution of the dual problem. The iteration counter $k$ is set to 0 . The primal problem (49) is solved (trivially) with solution ( $V_{o}, \overline{\mathbf{x}}_{o}^{(E C)}$ ) and these values are stored in a set $\mathcal{M}$. The value of the objective function at this solution, $\bar{G}_{o}^{e l}$, gives the first upper bound on the global minimum Gibbs free energy, $U B D^{V}=\bar{G}_{o}^{e l}$. In addition, lower and upper bounds for $\bar{\lambda}$ are obtained by choosing $2 \times(C-2)$ values of $\overline{\mathbf{x}}^{(E C)}$, as shown in Appendix C.

The algorithm is now set to proceed to Stage II to seek the molar volumes and compositions of the stable phases.

\section*{Remarks.}
- It is not always necessary to solve Problem (63) to global optimality: if a negative value of the tangent plane distance is found, the tunnelling algorithm can be terminated early.
- The tunnelling algorithm is a stochastic global optimization algorithm, meaning that convergence to a non-negative solution does not guarantee that the system is stable. Multiple starting points are used to increase the reliability of the approach.
- The tangent plane distance can be minimized in the space of the original functions/variables, i.e., using the Gibbs free energy as a function of (unmodified) mole fractions. In this case, the electroneutrality condition should be imposed throughout.

\subsection*{4.3. Stage II: Identification of candidate stable phases}

In Step 4, the upper-level problem, a linear programming problem that approximates the dual problem, is solved to obtain an updated upper bound on the minimum Gibbs free energy and a new vector $\bar{\lambda}^{*}$. In the case of mixtures with strong electrolytes, the upper-level problem is expressed as

$$
\begin{align*}
U B D^{V}= & \max _{v, \bar{\lambda} \in \mathbb{R}^{C-2}} v \\
& \text { s.t. } \quad v \leq \bar{A}^{e l}\left(T, V^{m}, \overline{\mathbf{x}}^{(E C), m}\right)+P_{o} V^{m} \\
& \quad+\sum_{i \in C^{(E C)}} \bar{\lambda}_{i}\left(\bar{x}_{o, i}^{(E C)}-\bar{x}_{i}^{(E C), m}\right), \quad \forall\left(V^{m}, \overline{\mathbf{x}}^{(E C), m}\right) \in \mathcal{M} \\
& \quad v \leq \bar{G}_{o}^{e l} \tag{64}
\end{align*}
$$


The vector $\bar{\lambda}^{k}$ is set to $\bar{\lambda}^{*}$.
A new cutting plane is then generated in Step 5 by solving the lower-level problem for $\bar{\lambda}=\bar{\lambda}^{k}$ :

$$
\begin{align*}
\bar{L}^{V, k}= & \min _{V \in\left[V^{L}, V^{U}\right], \overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)}} \bar{A}^{e l}\left(T, V, \overline{\mathbf{x}}^{(E C)}\right)+P_{o} V \\
& +\sum_{i \in \mathcal{C}^{(E C)}} \bar{\lambda}_{i}^{k}\left(\bar{x}_{o, i}^{(E C)}-\bar{x}_{i}^{(E C)}\right) \tag{65}
\end{align*}
$$


The lower-level problem is nonconvex. In our implementation, it is solved using a multistart approach until $\bar{L}^{V, k} \leq U B D^{V}$, with initial values of $V$ and $\overline{\mathbf{x}}^{(E C)}$ generated within the appropriate bounds by a random number generator with fixed seed. The best solution generated, denoted by ( $V^{k}, \overline{\mathbf{x}}^{(E C), k}$ ), is added to the set $\mathcal{M}$.

In Step 6, we determine whether set $\mathcal{M}$ contains any candidate stable phases by checking a set of criteria modified from Pereira et al. (2010) for the case of electrolyte mixtures. Specifically, we identify $\mathcal{M}^{*} \subset \mathcal{M}$ as the set of distinct points in $\mathcal{M}$ such that
$\left|U B D^{V}-\bar{L}^{V, m}\right| \leq \epsilon_{b}, \quad m=1, \ldots, m p$,
$\left|\left(\frac{\partial \bar{A}^{e l}\left(T, V^{m}, \overline{\mathbf{x}}^{(E C), m}\right)}{\partial \bar{x}_{i}^{E C)}}\right)_{T, V, \bar{x}_{j \neq i}^{(E C)}}-\bar{\lambda}_{i}^{k}\right| \leq \epsilon_{\lambda}\left|\bar{\lambda}_{i}^{k}\right|, \quad \forall i \in \mathcal{I}^{m}, \quad m=1, \ldots, m p$,
EITHER $\left|\eta^{m}-\eta^{n}\right| \geq \epsilon_{\eta}, \quad m=1, \ldots, m p ; \quad n=1, \ldots, m p, \quad n \neq m$, OR $\quad \exists i \in \mathcal{C}^{(E C)}: \quad\left|\bar{x}_{i}^{(E C), m}-\bar{x}_{i}^{(E C), n}\right| \geq \epsilon_{x}, \quad m=1, \ldots, m p$;

$$
\begin{equation*}
n=1, \ldots, m p, \quad n \neq m \tag{66}
\end{equation*}
$$

where $m p=\left|\mathcal{M}^{*}\right|$ is the cardinality (number of elements) of set $\mathcal{M}^{*}$, the $\epsilon$ values $\left(\epsilon_{b}, \epsilon_{\lambda}, \epsilon_{\eta}, \epsilon_{x}\right)$ are user-defined tolerances and $\mathcal{I}^{m}$ is a set of $C_{p p}$ component indices in $\mathcal{C}^{(E C)}$ such that $i \in \mathcal{I}^{m} \Rightarrow \bar{x}_{i}^{(E C), m}>\bar{x}^{(E C), L}$, where $\bar{x}^{(E C), L}$ is the lower bound on the modified mole fractions and $C_{p p}$ is the number of components to be converged in Stage II, usually taken as $C-2$ if $C \leq 5$ or a number less than $C-2$ if $C>5$. The exact value of $C_{p p}$ can affect the speed of convergence, but does not affect the outcome of the calculations. The use of the reduced set $\mathcal{I}^{m}$ is important in electrolyte systems as some phases may contain very small amounts of ionic species, in which case the second constraint in Problem (66) is unlikely to be met for these components.

If $m p>1$, the algorithm is set to proceed to Stage III. If not, the iteration counter is incremented in Step 7, $k=k+1$, and the algorithm returned to Step 4 to solve the upper-level problem with the augmented set of cutting planes defined by $\mathcal{M}$.

\subsection*{4.4. Stage III: Acceleration and convergence tests}

In Step 8, the $m p$ candidate phases identified in Stage II are refined using a direct minimization of the total Gibbs free energy in the
neighbourhood of the state defined by $\mathcal{M}^{*}$ :

$$
\begin{align*}
\underline{\bar{G}}^{e l, *}= & \min _{\mathbf{V}^{\prime}, \underline{\bar{x}}^{(E C)^{\prime}}, \phi} \sum_{m=1}^{m p} \phi^{m}\left(\bar{A}^{e l}\left(T, V^{\prime m}, \overline{\mathbf{x}}^{(E C)^{\prime}}\right)+P_{o} V^{\prime m}\right) \\
\text { s.t. } & \left(\sum_{m=1}^{m p} \phi^{m} \bar{x}_{i}^{(E C)^{\prime}, m}\right)-\bar{x}_{o, i}^{(E C)}=0, \quad \forall i \in \mathcal{C}^{(E C)} \\
& \sum_{m=1}^{m p} \phi^{m}=1  \tag{67}\\
& \bar{x}_{i}^{(E C)^{\prime}, m} \in\left[\max \left\{\bar{x}_{i}^{(E C), m}-10^{-3}, x_{i}^{(E C), L}\right\}\right. \\
& \left.\min \left\{\bar{x}_{i}^{(E C), m}+10^{-3}, \bar{x}_{i}^{(E C), U}\right\}\right] \\
& \forall i \in \mathcal{C}^{(E C)} ; \quad m=1, \ldots, m p \\
& \phi \in[0,1]^{m p}, \\
& \mathbf{V}^{\prime} \in\left[V^{L}, V^{U}\right]^{m p}
\end{align*}
$$

where $\underline{\bar{G}}^{e l, *}$ is the extensive Gibbs free energy computed for one mole of mixture, $\mathbf{V}^{\prime}$ denotes a $m p$-dimensional vector of the molar volumes of each phase, $\underline{\mathbf{x}}^{(E C)^{\prime}}$ denotes the $m p \times(C-2)$ matrix of mole fractions, with element $\bar{x}_{i}^{(E C)^{\prime}, m}$ corresponding to the modified mole fraction of component $i$ in phase $m, \boldsymbol{\phi}$ denotes the $m p$-dimensional vector of phase fractions, and $\bar{A}^{e l}$ is the intensive Helmholtz free energy,

If not all of the stable phases are identified in Stage II, Problem (67) is infeasible. In this case, the iteration counter is incremented and the algorithm returns to Step 4 to seek additional phases. If the problem is feasible, the solution is examined to identify any phases that are identical (same composition and volume) and to remove duplicates before proceeding to Step 9. If any duplicates are found, the number of phases $m p$ is updated (reduced) accordingly.

In Step 9, convergence is further tested as follows:
- Has the free energy converged? If

$$
\begin{equation*}
0 \leq U B D^{V}-\underline{\bar{G}}^{e l, *} \leq \epsilon_{g}, \tag{68}
\end{equation*}
$$

where the extensive Gibbs free energy from Problem (67) can be used as it is computed on the basis of one mole of mixture and $\epsilon_{g}$ is a small positive tolerance (by default $\epsilon_{g}=10^{-6}$ ), then proceed. Else increment the iteration counter and return to Step 4.
- Are the modified chemical potentials converged? If $\left|\left(\bar{\mu}_{i}^{e l}\left(T, P_{o}, \overline{\mathbf{x}}^{(E C), *, m}\right)-\bar{\mu}_{i}^{e l}\left(T, P_{o}, \overline{\mathbf{x}}^{(E C), *, m+1}\right)\right) / \bar{\mu}_{i}^{e l}\left(T, P_{o}, \overline{\mathbf{x}}^{(E C), *, m}\right)\right| \leq \epsilon_{\mu}, \quad \forall i \in \mathcal{C}^{(E)}, m=1, \ldots, m p-1$,
where $\overline{\mathbf{x}}^{*, m}$ is the modified mole fraction vector for phase $m$ at the solution of Problem (67) and $\epsilon_{\mu}$ is a small positive tolerance (by default $\epsilon_{\mu}=10^{-6}$ ), then proceed. Otherwise, the iteration counter is incremented and the algorithm returns to Step 4.

In Step 10, the final step of the algorithm, we revert to the original mole fractions and follow the general strategy of Pereira et al. (2010). If a component $i$ has a modified mole fraction at the lower bound $\bar{x}^{(E C), l}$ in a phase $m$, its composition is refined by first recasting the vector of mole fractions in logarithmic space, i.e., defining the variable transformation $y_{i}^{(E C)}=\log _{10} x_{i}^{(E C)}, \quad \forall i \in \mathcal{C}^{(E C)}$.

The transformed mole fractions of all other components are set using the values obtained in Step 8:
$y_{j}^{(E C)}=\log _{10} \frac{\bar{x}_{j}^{(E C), m}}{1-\frac{z_{i}}{z_{E}}}, \quad \forall j \in C^{(E C)}, \quad j \neq i$,
and the following problem is then solved:

$$
\begin{equation*}
\min _{y_{i}^{(E C)} \in Y}\left(\bar{\mu}_{i}^{e l}\left(T, P_{o}, \mathbf{y}^{(E C)}\right)-\bar{\mu}_{i}^{e l, *}\right) \tag{72}
\end{equation*}
$$

where $Y=\left[y^{l}, y^{u}\right]$, with the bounds $y^{l}$ and $y^{u}$ set such that the lower bounds corresponds to a mole fraction of $10^{-300}$ and an upper of $5.0 \times 10^{-10}$, and where $\bar{\mu}_{i}^{e l, *}$ denotes the chemical potential of component
$i$ at the solution of Problem (67), in a phase in which the component is not at the lower bound in mole fraction.

\subsection*{4.5. Implementation}

HELD2.0 is implemented in FORTRAN90 using an in-house implementation of the tunnelling algorithm for the minimization of the tangent-plane distance and solvers from the Numerical Algorithms Group (NAG) (Numerical Algorithms Group, 2023) libraries to solve other optimization problems. The lower-level problem, Problem (65), is solved using the E04UCA routine, which is designed to minimize an arbitrary smooth function subject to constraints using a sequential quadratic programming (SQP) method, and the upper-level problem, Problem (64), is solved with the E04MFA routine, which is applicable to general linear programming problems. We use a 64-bit 3.40 GHz processor with 8 GB of RAM and the Windows 10 operating system to run all of the test cases.

Although the HELD2.0 algorithm can be applied to many different thermodynamic models, the only equation of state (EOS) currently implemented is the SAFT- $\gamma$ Mie group-contribution (GC) approach (Papaioannou et al., 2014; Dufal et al., 2014; Haslam et al., 2020) extended to electrolyte systems (Eriksen et al., 2016; Kohns et al., 2020), which accounts for the effects of shape, long-range dispersive interactions, strong interactions arising from hydrogen bonds, and the Coulombic and charge-solvent interactions present in electrolyte solutions. In this approach, the effect of the solvent on ion-ion interactions is described with a dielectric constant, $D$. In order to obtain a realistic description of the dielectric constant, we adopt the expression reported by Schreckenberg et al. (2014) following Uematsu and Frank (1980), which accounts for the change in the dielectric constant with thermodynamic conditions. For a mixture of $S$ solvents, the dielectric constant is given by
$D\left(T, P, \mathbf{x}^{\mathbf{s}}\right)=1+\rho_{\text {solv }}\left(T, P, \mathbf{x}^{\mathbf{s}}\right) d_{\text {solv }}\left(T, \mathbf{x}^{\mathbf{s}}\right)$,
where $\mathbf{x}^{\mathbf{s}}$ is the $S$-dimensional salt-free mole-fraction vector, $\rho_{\text {solv }}$ is the number density of the solvent or solvent mixture, and $d_{\text {solv }}$ is a solvent parameter that can be expressed as a function of temperature and composition. For a pure solvent $j$, we use
$d_{\text {solv }}(T, 1)=d_{j j}(T)$,
with
$d_{j j}(T)=d_{v, j}\left(\frac{d_{T, j}}{T}-1\right)$,
and where $d_{v, j}$ and $d_{T, j}$ are solvent-specific parameters that can be obtained by correlating experimental dielectric-constant data as outlined in Schreckenberg et al. (2014). For a mixture of $S$ solvents, we implement the van der Waals one-fluid mixing rule proposed by Harvey and Prausnitz (1987) to compute the parameter $d_{\text {solv }}\left(T, \mathbf{x}^{\mathbf{s}}\right)$ as a function of temperature and $\mathbf{x}^{s}$, as follows:
$d_{\text {solv }}\left(T, \mathbf{x}^{s}\right)=\sum_{i=1}^{S} \sum_{j=1}^{S} x_{i}^{s} x_{j}^{s} d_{i j}(T)$,
where $d_{i j}(T)$ is obtained using a simple arithmetic mean of the pure solvent values given by Eq. (75):
$d_{i j}(T)=\frac{d_{i i}(T)+d_{i j}(T)}{2}$.

It is of course possible to use other models of the dielectric constant, for instance taking into account the effect of salt concentration (MariboMogensen et al., 2013; Wang and Anderko, 2001).

\section*{5. Case studies and results}

In this section we apply the HELD2.0 algorithm to a variety of systems composed of salt(s) + molecular solvent(s) across a range of thermodynamic conditions and types of phase behaviour, as listed in

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 1
Description of the case studies considered, including a list of components, the relevant section in the paper, the type of phase behaviour observed, and the number of $P, T$ flash calculations carried out for this mixture.}
\begin{tabular}{|l|l|l|l|}
\hline Mixture & Section & Type of phase behaviour & Number of $P, T$ flash calculations \\
\hline $\mathrm{NaCl}+$ water & 5.1 & Saturated vapour pressure (VLE) & 27716 \\
\hline KCl + water & 5.1 & Saturated vapour pressure (VLE) & 48300 \\
\hline LiCl + water & 5.1 & Saturated vapour pressure (VLE) & 25714 \\
\hline water + methanol & 5.2.1 & VLE & 1300 \\
\hline $\mathrm{LiCl}+$ water + methanol & 5.2.1 & VLE at constant salt concentration & 9800 \\
\hline $\mathrm{LiCl}+$ water + 1-butanol & 5.2.2 & LLE & 1435 \\
\hline $\mathrm{NaCl}+$ water + acetic acid + 1-butanol & 5.2.3 & LLE at constant salt concentration & 5102 \\
\hline $\mathrm{CaCl}_{2}+$ water + acetone & 5.3.1 & LLE & 1750 \\
\hline $\mathrm{CaCl}_{2}+$ water + propanoic acid +1 -butanol & 5.3.2 & LLE & 1800 \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 2
Molecular weight (MW), estimated parameters for the calculation of the dielectric constant as described by Eqs. (73) and (75), and the corresponding percentage average absolute deviation from the experimental values (\% AAD) for three polar solvents. $N_{p}$ is the number of data points used in the estimation, and Ref. indicates the source of experimental data.}
\begin{tabular}{|l|l|l|l|l|l|l|}
\hline Solvent $j$ & $\mathrm{MW} /\left(\mathrm{g} \mathrm{mol}^{-1}\right)$ & $d_{v, j} /\left(\mathrm{dm}^{3} \mathrm{~mol}^{-1}\right)$ & $d_{T, j} / \mathrm{K}$ & \% AAD & $N_{p}$ & Ref. \\
\hline Acetone & 58.0791 & 0.2391 & 2221.700 & 4.07 & 7 & de Jesús-González et al. (2018) \\
\hline Acetic acid & 60.0520 & -0.7275 & 177.4429 & 2.66 & 15 & Lutskii and Mikhailenko (1963), Smyth and Rogers (1930) \\
\hline Propanoic acid & 74.0800 & -0.4796 & 187.5180 & 2.69 & 11 & Lutskii and Mikhailenko (1963) \\
\hline
\end{tabular}
\end{table}

Table 1. We begin by studying aqueous solutions of monovalent alkalihalide salts (brines), which represent the simplest case in terms of dimensionality (one salt + one solvent). The saturation pressure of the aqueous solutions is determined for varying salt concentrations, examining the performance of the algorithm when dealing with negligible (trace) amounts of ions in one of the phases (the vapour phase). The analysis is then extended to binary and ternary mixed solvents (alcohols and/or organic acids) with symmetric or asymmetric salts coexisting at equilibria. In all cases, we calculate the distribution of the ions in each equilibrium phase, computing phase boundaries as a function of salt concentration.

The dielectric constant parameters are obtained from the literature in the case of water, methanol, and 1-butanol (Schreckenberg et al., 2014). They are estimated based on experimental data (de Jesús-González et al., 2018; Smyth and Rogers, 1930; Lutskii and Mikhailenko, 1963), and reported in Table 2 in the case of acetone, acetic acid, and propanoic acid. Additional information on the thermodynamic model and on the parameters used within the SAFT- $\gamma$ Mie GC approach are presented in Appendix D.

\subsection*{5.1. Aqueous solutions of single salts}

The HELD2.0 algorithm is first tested on aqueous solutions of monovalent alkali-halides formed from $\mathrm{Li}^{+}, \mathrm{Na}^{+}, \mathrm{K}^{+}$, and $\mathrm{Cl}^{-}$. Rather than exploring the full phase diagram for each mixture, we concentrate on the more interesting thermodynamic conditions where phase changes occur, identifying points on/around the saturated vapour curve. Each point on the curves is generated by repeatedly solving the $P, T$ flash at fixed $\mathbf{x}_{o}$ and varying the pressure to identify a point (pressure $P^{*}$ ) on the phase boundary. A total of $50\left(T, \mathbf{x}_{o}\right)$ combinations are tested, resulting in 101,730 $P, T$ flash calculations as follows: NaCl brine, 27,716 performed for four (4) different temperatures (see Fig. 1(a)); KCl brine, 48,300 performed for four (4) temperatures (see Fig. 1(b)); and LiCl brine, 25,714 performed for three (3) temperatures (see Fig.1 (c)). While there are more efficient approaches for generating phase boundaries (Michelsen and Mollerup, 2018), this simple approach entails many HELD calculations around the curves shown in Fig. 1, thereby testing the robustness of the algorithm. Each point on a phase boundary corresponds to an aqueous mixture of the salt in equilibria with an essentially pure vapour phase, yet these solutions are identified without making any assumptions on the absence of ions in any of the phases. For this two-ion three-component mixture, Problem (65)
is two-dimensional, with variables $\bar{x}_{\text {Cation }}^{(E C)}$ (or equivalently $\bar{x}_{\mathrm{Cl}^{-}}^{(E C)}$ ) and $V$. Experimental data (Khaibullin and Borisov, 1966; Filiz and Gülen, 2008; Zarembo et al., 1976; Campbell and Bhatnagar, 1979; Patil et al., 1990) are shown in Fig. 1 alongside the calculated curves to illustrate that realistic phase boundaries can be obtained with the combination of HELD and SAFT- $\gamma$ Mie. These are reported with the caveat that the quality of the match between the experimental data and calculations does not provide any indication of algorithmic performance. It is important to point out that the calculations are carried up to a molality limit of 6.0 ; the model parameters used in SAFT- $\gamma$ Mie for these calculations were estimated from several properties of salt solutions at varying molalities lower than 6.0 molal (Eriksen et al., 2016).

Selected results are shown in Table 3, confirming that the vapour phase consists of water with a very small amount of ions. Both the cation and anion mole fractions in the vapour phase are found to be at the lower bound in Steps 6 and 9 and are thus refined in Step 10, using Eq. (72). As can be seen, the ion mole fractions sometimes remain close to the lower bound in Steps 6 and 9, as a result of the convergence tolerance used in solving Eq. (72). In other cases, there is a decrease in the mole fractions of the cation and anion, which are found to be essentially equal to zero. In the salt-rich liquid phase (the aqueous phase), the cation and anion mole fractions are derived directly from the modified mole fractions identified in Step 8 (Problem (67)) and satisfy the macroscopic electroneutrality condition.

Other methodologies to compute the phase equilibria of aqueous salt solutions, particularly for the description of VLE in brines, have been reported in the open literature (e.g., Eriksen et al., 2016, Novak et al., 2021, Rozmus et al., 2013, Held et al., 2008), but their computational performance has not been reported. In these studies, it was assumed that the vapour phase contains no ions to avoid numerical difficulties. Our approach is in excellent agreement with these calculations, especially for the vapour pressures, without requiring any such assumption.

\subsection*{5.2. Mixed-solvent brines with symmetric salts}

The HELD2.0 algorithm can be used to carry out calculations with systems containing any number of components. In this section, we examine its performance for brines containing one salt of monovalent ions in mixed solvents, considering vapour-liquid equilibria (VLE) and liquid-liquid (LLE) equilibria, for mixtures of up to 5 components.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7cde30c6-bbef-469d-8c04-f3706196d7ec-11.jpg?height=1758&width=639&top_left_y=193&top_left_x=251}
\captionsetup{labelformat=empty}
\caption{Fig. 1. Vapour pressure $P$ as a function of the concentration (molality, $m$ ) of aqueous solutions of monovalent alkali-halides: (a) NaCl at $T=373.15 \mathrm{~K}$ (black triangles Khaibullin and Borisov, 1966), $T=353.15 \mathrm{~K}$ (black circles Khaibullin and Borisov, 1966), $T=333.15 \mathrm{~K}$ (red triangles Filiz and Gülen, 2008), and $T=298 \mathrm{~K}$ (blue squares Filiz and Gülen, 2008); (b) KCl at $T=623.15 \mathrm{~K}$ (blue triangles Zarembo et al., 1976 ), $T=573.15 \mathrm{~K}$ (black circles Zarembo et al., 1976), $T=473.15 \mathrm{~K}$ (red triangles Zarembo et al., 1976), and $T=343.15 \mathrm{~K}$ (green squares Patil et al., 1994); (c) LiCl at $T=423.15 \mathrm{~K}$ (blue triangles Campbell and Bhatnagar, 1979), $T=373.15 \mathrm{~K}$ (black circles Campbell and Bhatnagar, 1979), and $T=348.15 \mathrm{~K}$ (red triangles Campbell and Bhatnagar, 1979, red squares Patil et al., 1990). The symbols correspond to the experimental data and the continuous curves are calculations with the HELD2.0 algorithm with the SAFT- $\gamma$ Mie GC approach.}
\end{figure}

\subsection*{5.2.1. VLE in LiCl + water + methanol mixtures}

The vapour-liquid equilibria (VLE) for the mixture water + methanol +LiCl is calculated with the HELD2.0 algorithm and presented in Fig. 2, where the solvent composition is expressed on a salt-free basis and the
calculations are performed by keeping a constant ratio of salt to water as per the experimental measurements reported in Boone et al. (1976). The calculations are carried out at fixed $P_{o}$, for a range of values for the salt-free mole fraction of methanol, $x_{o, \mathrm{MeOH}}^{s f}$, iterating over temperature for each $x_{o, \mathrm{MeOH}}^{s f}$ until the phase boundary is found, which requires carrying several HELD calculations near the phase boundary. In this case, Problem (65) is three-dimensional, with variables consisting of the modified mole fraction of one ion (e.g., $\bar{x}_{\mathrm{Li}^{+}}^{(E C)}$ ), that of one solvent (e.g., $\bar{x}_{\mathrm{MeOH}}^{(E C)}$ ), and $V$. A total of 100 combinations of $\left(P_{o}, x_{o, \mathrm{MeOH}}^{s f}\right)$ are considered, resulting in $9800 P, T$ flash calculations.

With the algorithm, one is able to identify the stable equilibrium phases in all cases tested and to handle a wide range of mole fractions. To illustrate this, detailed results are provided in Table 4 for selected total salt-free mole fractions of methanol. As previously, mole fractions in the vapour phases are found to decrease to practically zero or to remain of order $10^{-10}$, which is consistent with the convergence tolerance used. The number of iterations within the HELD algorithm (i.e., the number of times an upper-level problem is solved) and the CPU time are also reported in the table, for each bubble temperature. It should be noted that both iteration number and CPU times depend markedly on the values of the specified convergence tolerances and the settings of the multistart algorithms used to solve nonconvex subproblems. These have been chosen to achieve high reliability, but could be tuned further to reduce the computational cost.

Isobaric calculations of the VLE for water + methanol +LiCl system was also presented in Schreckenberg et al. (2014) and Gering and Lee (1989). In Gering and Lee (1989), a pseudo-solvent model was used to estimate the bubble point, assuming that the vapour phase behaves as an ideal gas dominated by one component (the pseudo-solvent) and using the equality of the pseudo-solvent fugacities in both phases. Similarly, in Schreckenberg et al. (2014), an iterative procedure was implemented to achieve equality of the chemical potential of the molecular components, under the assumption that the vapour phase contains no ions. The results presented in Fig. 2 and Table 4 confirm the validity of these assumptions and demonstrate that the addition of salt in a mixed solvent impacts the bubble points, the mutual solubilities of the solvent components and the equilibrium vapour phase compositions. No phase stability calculations were carried out in the earlier studies and no computational performance data were reported for the phase equilibrium calculations.

\subsection*{5.2.2. LLE in salt + water + 1-butanol mixtures}

In order to assess the performance of the HELD2.0 algorithm when the ionic species appear in more than one of the (liquid) phases coexisting at equilibria, we consider systems exhibiting heterogeneous liquid-liquid equilibria. The usual simplistic explanation of the effect of adding salts to partially miscible water + organic solvent mixtures is to reduce further the mutual solubility of the two solvents as the water molecules surrounding the ions become unavailable to solvate the organic compound, causing it to salt out from the aqueous phase as well as decreasing the concentration of water in the organic phase (Endo et al., 2012). Several studies however lead to the observation that the system $\mathrm{LiCl}+$ water +1 -butanol exhibits atypical behaviour (AlSahhaf and Kapetanovic, 1997; Gomis et al., 1999; Wakisaka et al., 2004). At some concentrations of LiCl , the concentration of water in the organic phase remains constant or increases, rather than decreasing as may be expected. The binodal curve features an inflection point on the organic-phase side, i.e., it is S-shaped, making the phase equilibria of this mixture challenging to model. The numerical solution of the phase stability and equilibria around the anomalous region is thus particularly demanding due to the non-linearity of the behaviour. A total of $1435 P, T$ flash calculations are carried out successfully to identify the LLE phase boundaries describing 35 tie lines. Only two modified mole fractions are considered in each phase in solving the dual problem (one ion and one solvent), and no assumptions are made

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7cde30c6-bbef-469d-8c04-f3706196d7ec-12.jpg?height=827&width=1021&top_left_y=183&top_left_x=523}
\captionsetup{labelformat=empty}
\caption{Fig. 2. Isobaric $T$ - $x$ representation of the vapour-liquid equilibria of water + methanol $(\mathrm{MeOH})+\mathrm{LiCl}$ mixtures at a pressure of $P_{o}=101.325 \mathrm{kPa}$ and constant salt concentration of 4.0 molal in terms of moles of $\mathrm{LiCl} /(\mathrm{kg}$ water), consistent with the units of the experimental data (Boone et al., 1976) represented by symbols. The continuous curves represent the calculations implementing the HELD2.0 algorithm and the SAFT- $\gamma$ Mie GC approach (liquid in blue, vapour in red). $x_{\mathrm{MeOH}}^{s f}$ is the salt-free mole fraction of methanol. The dashed curve represents the calculated vapour-liquid equilibria of water + methanol mixtures without salt, as calculated with HELD.}
\end{figure}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 3
Results of selected vapour-pressure calculations for aqueous solutions of monovalent alkali-halides with the HELD2.0 algorithm and the SAFT- $\gamma$ Mie GC approach: the first column indicates the cation; $m_{o, \text { salt }}$ is the total molality of the salt; $T$ the temperature; $P^{*}$ the computed vapour pressure; Phase indicates the fluid type; $\mathbf{x}$ the mole fraction vector of the stable phase (1) $\left.\left.X^{+}, 2\right) \mathrm{Cl}^{-}, 3\right)$ water); $\eta$ the dimensionless packing fraction of the stable phase; and $V$ its molar volume.}
\begin{tabular}{|l|l|l|l|l|l|l|l|}
\hline \multirow[t]{2}{*}{Cation} & \multirow{2}{*}{$m_{o, \text { salt }}$ /molal} & \multirow{2}{*}{T /K} & \multirow{2}{*}{$P^{*}$ /kPa} & \multirow[t]{2}{*}{Phase} & \multirow[t]{2}{*}{$\mathbf{x}^{T}=\left(x_{\text {cation }}, x_{\mathrm{Cl}^{-}}, x_{\mathrm{H}_{2} \mathrm{O}}\right)$} & \multirow[t]{2}{*}{$\eta$} & \multirow{2}{*}{$V /\left(\mathrm{m}^{3} \mathrm{~mol}^{-1}\right)$} \\
\hline & & & & & & & \\
\hline \multirow{2}{*}{$\mathrm{Li}^{+}$} & \multirow{2}{*}{5.0} & \multirow{2}{*}{348.15} & \multirow{2}{*}{29.890} & Vapour & ( $1.0000 \times 10^{-10} ; 1.0000 \times 10^{-10} ; 0.9999 \overline{9}$ ) & $8.994 \times 10^{-5}$ & $9.526 \times 10^{-2}$ \\
\hline & & & & Liquid & (0.077010; 0.077010; 0.84598) & 0.46706 & $1.775 \times 10^{-5}$ \\
\hline \multirow{2}{*}{$\mathrm{Na}^{+}$} & \multirow{2}{*}{5.6} & \multirow{2}{*}{298.15} & \multirow{2}{*}{2.5080} & Vapour & ( $\left.1.41063 \times 10^{-116} ; 1.41063 \times 10^{-116} ; 1.00000\right)$ & $8.706 \times 10^{-5}$ & $9.841 \times 10^{-2}$ \\
\hline & & & & Liquid & (0.086944; 0.086944; 0.826112) & 0.47224 & $1.787 \times 10^{-5}$ \\
\hline \multirow{2}{*}{$\mathrm{K}^{+}$} & \multirow{2}{*}{0.80} & \multirow{2}{*}{343.15} & \multirow{2}{*}{29.973} & Vapour & ( $\left.3.48366 \times 10^{-87} ; 3.48366 \times 10^{-87} ; 1.00000\right)$ & $9.168 \times 10^{-5}$ & $9.344 \times 10^{-2}$ \\
\hline & & & & Liquid & ( 0.0141510 .0141510 .97169 ) & 0.46087 & $9.168 \times 10^{-5}$ \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 4
Results of sample calculations with the HELD2.0 algorithm for methanol + water + LiCl at $P=101.325 \mathrm{kPa}$ and LiCl concentration of 4.0 molal for selected values of the total salt-free methanol mole fraction $x_{o, \mathrm{MeOH}}^{s f}$ : Phase is the type of stable phase; $\mathbf{x}$ represents the mole fraction vector in each phase (ordered as $\mathrm{Li}^{+}, \mathrm{Cl}^{-}$, methanol, water); $\eta$ is the dimensionless packing fraction of each phase; $V$ its molar volume; $T_{b}$ is the bubble temperature; Iter. is the number of iterations (upper-level problems solved); and CPU is the CPU time required by the HELD2.0 algorithm with the SAFT- $\gamma$ Mie GC approach.}
\begin{tabular}{|l|l|l|l|l|l|l|l|}
\hline $x_{o, \mathrm{MeOH}}^{s f}$ & Phase & $\mathbf{x}=\left(x_{\mathrm{Li}^{+}}, x_{\mathrm{Cl}^{-}}, x_{\text {methanol }}, x_{\text {water }}\right)$ & $\eta$ & $V /\left(\mathrm{m}^{3} \mathrm{~mol}^{-1}\right)$ & $T_{b} / \mathrm{K}$ & Iter. & CPU/s \\
\hline \multirow{2}{*}{0.0100} & Phase I (V) & ( $2.36935 \times 10^{-106} 2.36935 \times 10^{-106} 0.101640 .89836$ ) & $3.193 \times 10^{-4}$ & $2.983 \times 10^{-2}$ & \multirow{2}{*}{375.75} & \multirow{2}{*}{137} & \multirow{2}{*}{4.61} \\
\hline & Phase II (L) & (0.062368 0.0623680 .00997800 .86528 ) & 0.4563 & $1.849 \times 10^{-5}$ & & & \\
\hline \multirow{2}{*}{0.300} & Phase I (V) & ( $1.00000 \times 10^{-10} 1.00000 \times 10^{-10} 0.725160 .27483$ ) & $5.585 \times 10^{-4}$ & $2.760 \times 10^{-2}$ & \multirow{2}{*}{351.25} & \multirow{2}{*}{131} & \multirow{2}{*}{3.69} \\
\hline & Phase II (L) & (0.044213 0.0442130 .298800 .61277 ) & 0.4481 & $2.507 \times 10^{-5}$ & & & \\
\hline \multirow{2}{*}{0.990} & Phase I (V) & ( $1.00000 \times 10^{-10} 1.00000 \times 10^{-10} 0.996430 .0035688$ ) & $6.843 \times 10^{-4}$ & $2.628 \times 10^{-2}$ & \multirow{2}{*}{337.81} & \multirow[b]{2}{*}{149} & \multirow{2}{*}{4.81} \\
\hline & Phase II (L) & (0.00063048 0.000630480 .989990 .0087455 ) & 0.4221 & $4.243 \times 10^{-5}$ & & & \\
\hline
\end{tabular}
\end{table}
on the number or type of stable phases in carrying out the calculations. All of the HELD2.0 calculations are found to converge successfully. A summary of algorithmic performance and details of the calculations for selected conditions around the point of inflection are presented in Table 5. The results clearly confirm the significant concentrations of ionic species in both phases. All of the solutions fulfill the elec-
troneutrality condition exactly since the mole fraction of the second ion (which is not included explicitly in the modified mole fraction vector) is computed via Eqs. (30) and (31).

The description of the LLE of this system at 101.3 kPa and 298.15 K , as calculated with the HELD2.0 algorithm and the SAFT- $\gamma$ Mie EoS, is presented in Fig. 3. Although our emphasis is on the development of a

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 5
Sample calculations for $\mathrm{LiCl}+$ water +1 -butanol at $P_{o}=101.3 \mathrm{kPa}$ and $T=298.15 \mathrm{~K}$ for selected molalities of LiCl , $m_{o, \mathrm{LiCl}}$, around the point of inflection in the curvature of the organic-phase side in the binodal curve presented in Fig. 3. $\mathbf{x}$ represents the mole fraction vector for all the species in each phase (ordered as $\mathrm{Li}^{+}, \mathrm{Cl}^{-}$, water, 1-butanol); $\eta$ is the dimensionless packing fraction of each phase; $V$ is its molar volume; Iter. is the number of iterations (upper-level problems solved); and CPU is the CPU time taken by the HELD2.0 algorithm with the SAFT- $\gamma$ Mie GC approach.}
\begin{tabular}{|l|l|l|l|l|l|l|}
\hline $m_{o, \mathrm{LiCl}} / \mathrm{molal}$ & Phase & $\mathbf{x}=\left(x_{\mathrm{Li}^{+}}, x_{\mathrm{Cl}^{-}}, x_{\text {water }}, x_{1 \text {-butanol }}\right)$ & $\eta$ & $V /\left(\mathrm{m}^{3} \mathrm{~mol}^{-1}\right)$ & Iter. & CPU/s \\
\hline \multirow{2}{*}{4.58} & Phase II (org.) & (0.028517, 0.028517, 0.30442, 0.63855) & 0.4912 & $6.308 \times 10^{-5}$ & \multirow{2}{*}{59} & \multirow{2}{*}{2.58} \\
\hline & Phase I (aq.) & (0.13329, 0.13329, 0.68072, 0.052686) & 0.4942 & $2.014 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{4.95} & Phase II (org.) & (0.033131, 0.033131, 0.30719, 0.62655) & 0.4918 & $6.201 \times 10^{-5}$ & \multirow{2}{*}{54} & \multirow{2}{*}{2.60} \\
\hline & Phase I (aq.) & (0.13551, 0.13551, 0.67073, 0.058249) & 0.4949 & $2.047 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{5.74} & Phase II (org.) & (0.051112, 0.051112, 0.32413, 0.57364) & 0.4938 & $5.803 \times 10^{-5}$ & \multirow{2}{*}{61} & 2.76 \\
\hline & Phase I (aq.) & (0.13926, 0.13926, 0.65007, 0.071403) & 0.4965 & $2.129 \times 10^{-5}$ & & \\
\hline
\end{tabular}
\end{table}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7cde30c6-bbef-469d-8c04-f3706196d7ec-13.jpg?height=724&width=949&top_left_y=749&top_left_x=559}
\captionsetup{labelformat=empty}
\caption{Fig. 3. Effect of the concentration of lithium chloride ( LiCl ) on the liquid-liquid equilibria of water +1 -butanol mixtures at $P=101.3 \mathrm{kPa}$ and $T=298.15 \mathrm{~K} . w_{i}$ is the mass fraction of component $i$. The symbols correspond to experimental data (Al-Sahhaf and Kapetanovic, 1997) and the red curves are obtained with the HELD2.0 algorithm and the SAFT- $\gamma$ Mie GC approach. The dashed lines represent experimental (black) and computed (red) tie lines.}
\end{figure}
novel algorithm for $P, T$ flash calculations, we note in passing that the physical behaviour of the mixture is captured correctly with our model; this is important to highlight considering that 1-butanol and its interactions with water and the ions are modelled via a group-contribution approach. By accounting for the possible presence of all ionic species in all phases in equilibria, based on a rigorous thermodynamic framework, the methodology is seen to provide a quantitative description of the salting-out effect.

To the best of our knowledge, no other calculations or predictions have been reported to date for the LLE of the water + butanol +LiCl system. Gomis et al. (1999) correlated the experimental data to empirical expressions, such as the Setschenov equation, which describes the behaviour of an organic solvent in water as a function of salt concentration. Other approaches have, however, been used to calculate the LLE of salt + water + alcohol systems similar to those in this study. For instance, Nikolaidis et al. (2022) studied the LLE of NaCl + water + 1 -propanol by allowing ions to freely distribute between phases while imposing an electroneutrality constraint. The approach of Nikolaidis et al. (2022) does not include a phase stability check and thus requires specifying the number of phases in advance. Furthermore, it requires initial guesses for the species concentrations. Finally, no information on computational time was available for comparison with our proposed approach.

\subsection*{5.2.3. Phase behaviour of a mixture involving a salt and three-component solvent}

A common practice in multicomponent solvent extraction is the addition of salts to modify the liquid-liquid equilibrium in order to improve the separation process. It is thus of interest to assess the performance of the algorithm in dealing with multicomponent solvents and brines. We examine the impact of the addition of sodium chloride, NaCl , on the miscibility of a mixture of water + acetic acid +1 butanol, carrying out a total of $5102 P, T$ flash calculations with different values of the ratio of total moles of salt to total moles of water, $r$ : 1050 for the salt-free mixture ( $r=0$ ), describing 50 tie lines; 1647 for $r=0.016$, describing 27 tie lines; and 2405 for $r=0.05$, describing 37 tie lines. Two salt concentrations are investigated in addition to the salt-free mixture, and these are selected based on the availability of experimental measurements (Tan and Aravinth, 1999). The performance of the algorithm and the distribution of the salt in each phase for selected total compositions are given in Table 6. These 5-component calculations are found to be more challenging, with a ca. $20 \%$ increase in the average number of iterations and an increase in the CPU time by a factor of 2.6, relative to the four-component mixture of $\mathrm{LiCl}+$ water +1 -butanol, which also exhibits LLE. Nevertheless, all calculations terminate successfully. A significant amount of ionic species is present in each liquid phase.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7cde30c6-bbef-469d-8c04-f3706196d7ec-14.jpg?height=770&width=1025&top_left_y=189&top_left_x=521}
\captionsetup{labelformat=empty}
\caption{Fig. 4. Liquid-liquid equilibria of $\mathrm{NaCl}+$ water +1 -butanol + acetic acid system at $T=298.15 \mathrm{~K}$ and $P_{o}=101.3 \mathrm{kPa}$, represented on a salt-free basis for three total molar ratios, $r$, of NaCl to water: $r=0.0$ (black), $r=0.01623$ (blue), and $r=0.05063$ (red). $w_{i}^{s f}$ is the salt-free mass fraction of component $i$. The symbols represent the experimental mass fractions (Tan and Aravinth, 1999) and the continuous curves are predictions obtained with the HELD2.0 algorithm and the SAFT- $\gamma$ Mie GC approach. The continuous lines are the experimental tie lines (Tan and Aravinth, 1999) and dashed lines the predicted tie lines.}
\end{figure}

The corresponding calculations are presented in Fig. 4. The curves in the figure are depicted on the basis of salt-free mass fractions and describe the miscibility of the system at a fixed value of the ratio, $r$. Consistent with the experiments, it is apparent from the calculations that the higher the concentration of NaCl , the wider the two-phase region, i.e., the lower the miscibility of the aqueous and organic phases. The mass fractions of 1-butanol and acetic acid in the organic phase increase significantly as more NaCl is added, indicating that the presence of NaCl leads to salting-out of 1-butanol and acetic acid from the aqueous phase and of water from the organic phase, thus enhancing the separation of acetic acid.

The only calculations previously reported for this mixture, by Tan and Aravinth (1999), were based on correlating the LLE experimental data of the solvent-salt systems using the NRTL model to determine the activity coefficient of a solvent in a solvent-salt mixture. The equilibrium phases were characterized by ensuring equality of the solvent activities in both phases on a salt-free basis. This is the first time that this mixture is modelled without any assumptions on the number of stable phases.

\subsection*{5.3. Asymmetric electrolytes in mixed solvents}

The performance of the HELD2.0 algorithm for mixtures composed of mixed solvents and asymmetric electrolytes is tested next. Based on the availability of experimental measurements for such systems, we focus our analysis on $\mathrm{MX}_{2}(1: 2)$ electrolytes, such as $\mathrm{CaCl}_{2}$. As for symmetric electrolytes, we first study the phase separation of systems composed of $\mathrm{MX}_{2}$ salt + water + organic solvent.

\subsection*{5.3.1. Phase behaviour of an asymmetric salt + binary solvent mixture}

The mixture of $\mathrm{CaCl}_{2}+$ water + acetone is first investigated. Acetone and water are miscible but as has been shown in several studies $\mathrm{CaCl}_{2}$ is an effective salting-out agent for separating acetone from aqueous solutions (Matkovich and Christian, 1973; Bourayou and Meniai, 2007; Frankforter and Cohen, 1914). For this mixture, component $E$ is chosen to be $\mathrm{Ca}^{2+}$ because it has the largest absolute charge ( $z_{\mathrm{Ca}^{2+}}= z_{E}=2$ ). The solid-liquid solubility limit for calcium chloride in pure water ( $w_{\mathrm{CaCl}_{2}}=0.5023 \mathrm{~g} / 100 \mathrm{~g}$ ) is calculated from the solubility product, $\mathrm{K}_{s p}$, of the salt $\left(\mathrm{CaCl}_{2}\right)$ for a given temperature, using the

SAFT- $\gamma$ Mie EoS along with the tabulated standard thermodynamic properties of formation (see Wagman et al., 1982) for the Gibbs energy, $\Delta G_{f}^{0}$, and enthalpy, $\Delta H_{f}^{0}$, and the molar heat capacity, $C_{p}^{0}$, of the salt and the ions in aqueous solution (aq). Hydrates of calcium chloride are known to form at certain compositions (Richter et al., 2016) but this is not considered in this phase diagram as we focus on fluid-phase equilibria. We do not consider hydrates in our current calculations with the HELD2.0 algorithm which are carried out in the compositional space delimited by the solubility limit and the salt-free acetone-water edge. A total of $1750 P, T$ flash calculations are performed, describing 50 tie lines.
The partitioning of all species across the two equilibrium phases is presented in Table 7 for selected total compositions at 101.3 kPa and 293.15 K . The composition values are chosen to span the range of possible salt concentrations, from low values to those near the solubility limit of $\mathrm{CaCl}_{2}$ in water. Similar iteration numbers and CPU times are observed as for LLE calculations for $\mathrm{LiCl}+$ water + 1-butanol. Again, all HELD calculations converge successfully.

HELD2.0 calculations of the coexistence of an acetone-rich phase in equilibrium with a water-rich phase at 101.3 kPa and 293.15 K are depicted in Fig. 5, and compared with the available experimental data.

\subsection*{5.3.2. Phase behaviour of an asymmetric salt + ternary solvent mixture}

As a final application, we assess the performance of the algorithm for the case of multicomponent mixed solvents with asymmetric electrolytes, calculating the fluid-phase equilibria of mixtures of $\mathrm{CaCl}_{2}+$ water + propanoic acid +1 -butanol. The mutual solubility predictions along with the corresponding tie lines are presented in Fig. 6(a) in terms of salt-free mass fractions and in Fig. 6(b) in terms of mass fractions, corresponding to a total of $1800 P, T$ flash calculations describing 25 tie lines. Further information on the calculations is provided in Table 8. In agreement with the experimental data (Zurita et al., 1998), the results show the significant effect that the salt has on the solubility of the salt-free system ( $w_{\mathrm{CaCl}_{2}}=0$ ), represented by the binodal curve depicted in blue in Fig. 6. The size of the heterogeneous region increases considerably with the introduction of salt in the mixture. This large salting-out effect can facilitate the extraction of propanoic acid. The quaternary diagram in Fig. 6(b) highlights the facts that the ion concentrations are very different in the two phases.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 6
Sample calculations for $\mathrm{NaCl}+$ water + acetic acid +1 -butanol at $P_{o}=101.3 \mathrm{kPa}$ and $T=298.15 \mathrm{~K}$. for selected values of $r$, and total mole fraction of acetic acid (ac.ac) $x_{o, \text { ac.ac }}$. $\mathbf{x}$ represents the mole-fraction vector for each phase (ordered as $\mathrm{Na}^{+}, \mathrm{Cl}^{-}$, water, acetic acid, 1 -butanol); $\eta$ is the dimensionless packing fraction of each phase; $V$ is its molar volume; Iter. is the number of iterations (upper-level problems solved); and CPU is the CPU time taken by the HELD2.0 algorithm with the SAFT- $\gamma$ Mie GC approach.}
\begin{tabular}{|l|l|l|l|l|l|l|l|}
\hline $r$ & $x_{\mathrm{o}, \mathrm{AA}}$ & Phase & $\mathbf{x}=\left(x_{\mathrm{Na}^{+}}, x_{\mathrm{Cl}^{-}}, x_{\text {water }}, x_{\text {ac.ac }}, x_{1-\text { butanol }}\right)$ & $\eta$ & $V /\left(\mathrm{m}^{3} \mathrm{~mol}^{-1}\right)$ & Iter. & CPU/s \\
\hline \multirow{2}{*}{0.01623} & \multirow{2}{*}{0.010} & Phase I (aq.) & (0.021252, 0.021252,0.93450,0.0060706,0.016922) & 0.48007 & $1.924 \times 10^{-5}$ & \multirow{2}{*}{76} & \multirow{2}{*}{8.6} \\
\hline & & Phase II (org.) & (0.00043751, 0.00043751, 0.51150, 0.015079, 0.47254) & 0.49262 & $5.156 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{0.01623} & \multirow{2}{*}{0.10} & Phase I (aq.) & (0.019788, 0.019788, 0.86333,0.069121, 0.027969) & 0.48657 & $2.211 \times 10^{-5}$ & \multirow{2}{*}{90} & \multirow{2}{*}{8.18} \\
\hline & & Phase II (org.) & (0.0013339, 0.0013339, 0.58870, 0.14395, 0.26468) & 0.49204 & $4.151 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{0.01623} & \multirow{2}{*}{0.15} & Phase I (aq.) & (0.0158895, 0.015889, 0.79224, 0.13039, 0.045587) & 0.48958 & $2.549 \times 10^{-5}$ & \multirow{2}{*}{79} & \multirow{2}{*}{8.17} \\
\hline & & Phase II (org.) & (0.0042932, 0.0042932, 0.66043, 0.19158, 0.13939) & 0.49128 & $3.436 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{0.05063} & \multirow{2}{*}{0.0010} & Phase I (aq.) & (0.058480,0.058480, 0.87492, 0.00057041, 0.0075483) & 0.47564 & $1.841 \times 10^{-5}$ & \multirow{2}{*}{77} & \multirow{2}{*}{9.79} \\
\hline & & Phase II(org.) & (0.0045544, 0.0045544, 0.449893, 0.001581, 0.539416) & 0.49158 & $5.593 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{0.05063} & \multirow{2}{*}{0.10} & Phase I (aq.) & (0.053339, 0.053339, 0.81496, 0.065098, 0.013258) & 0.48283 & $2.096 \times 10^{-5}$ & \multirow{2}{*}{83} & \multirow{2}{*}{8.69} \\
\hline & & Phase II (org.) & (0.0018553, 0.0018553, 0.48427, 0.16549, 0.34653) & 0.48967 & $4.835 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{0.05063} & \multirow{2}{*}{0.15} & Phase I (aq.) & (0.048058,0.048058, 0.77163, 0.113116,0.019137) & 0.48568 & $2.305 \times 10^{-5}$ & \multirow{2}{*}{83} & \multirow{2}{*}{10.1} \\
\hline & & Phase II (org.) & (0.0032881, 0.0032881, 0.51744, 0.24401, 0.23197) & 0.48834 & $4.314 \times 10^{-5}$ & & \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 7
Sample calculations for $\mathrm{CaCl}_{2}+$ water + acetone at $P_{o}=101.325 \mathrm{kPa}$ and $T=293.15 \mathrm{~K}$ for selected total mole fractions of $\mathrm{CaCl}_{2}, x_{o, \mathrm{CaCl}_{2}} \cdot \mathbf{x}$ represents the mole fraction vector for each phase (ordered as $\mathrm{Ca}^{2+}, \mathrm{Cl}^{-}$, acetone, water); $\eta$ is the dimensionless packing fraction of each phase; $V$ is its molar volume, Iter. is the number of iterations (upper-level problems solved); and CPU is the CPU time taken by the HELD2.0 algorithm with the SAFT- $\gamma$ Mie GC approach.}
\begin{tabular}{|l|l|l|l|l|l|l|}
\hline $x_{o, \mathrm{CaCl}_{2}}$ & Phase & $\mathbf{x}=\left(x_{\mathrm{Ca}^{2+}}, x_{\mathrm{Cl}^{-}}, x_{\text {acetone }}, x_{\text {water }}\right)$ & $\eta$ & $V /\left(\mathrm{m}^{3} \mathrm{~mol}^{-1}\right)$ & Iter. & CPU/s \\
\hline \multirow{2}{*}{$0.012530\left(\% w_{o}=5.5\right)$} & Phase I (aq.) & (0.015038, 0.030076, 0.10863, 0.84625) & 0.4782 & $2.323 \times 10^{-5}$ & \multirow{2}{*}{58} & \multirow{2}{*}{2.64} \\
\hline & Phase II (org.) & (0.00036859, 0.00073719, 0.36411, 0.63478) & 0.4613 & $3.689 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{$0.024055\left(\% w_{o}=10\right)$} & Phase I (aq.) & (0.029036, 0.058073, 0.068618, 0.84427) & 0.4828 & $2.113 \times 10^{-5}$ & \multirow{2}{*}{56} & \multirow{2}{*}{2.81} \\
\hline & Phase II (org.) & ( $3.2922 \times 10^{-5}, 6.5846 \times 10^{-5}, 0.60576,0.39414$ ) & 0.4490 & $5.040 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{$0.038471\left(\% w_{o}=15\right)$} & Phase I (aq.) & (0.046408, 0.092817, 0.050879, 0.80989) & 0.4867 & $2.018 \times 10^{-5}$ & \multirow{2}{*}{47} & \multirow{2}{*}{2.31} \\
\hline & Phase II (org.) & ( $1.8237 \times 10^{-5}, 3.6475 \times 10^{-5}, 0.75604,0.24390$ ) & 0.4424 & $5.903 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{$0.054929\left(\% w_{o}=20\right)$} & Phase I (aq.) & (0.065838, 0.13167, 0.05090, 0.75157) & 0.4893 & $2.013 \times 10^{-5}$ & \multirow{2}{*}{59} & \multirow{2}{*}{7.84} \\
\hline & Phase II (org.) & ( $2.3117 \times 10^{-5}, 4.6235 \times 10^{-5}, 0.85193,0.14799$ ) & 0.4386 & $6.467 \times 10^{-5}$ & & \\
\hline
\end{tabular}
\end{table}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7cde30c6-bbef-469d-8c04-f3706196d7ec-15.jpg?height=885&width=1079&top_left_y=1322&top_left_x=495}
\captionsetup{labelformat=empty}
\caption{Fig. 5. Liquid-liquid equilibrium in $\mathrm{CaCl}_{2}+$ water + acetone at $T=293.15 \mathrm{~K}$ and $P_{o}=101.3 \mathrm{kPa} . w_{i}$ denotes the mass fraction of component $i$. The continuous (red) curve represents the liquid-liquid equilibria envelope calculated using the HELD2.0 algorithm and the SAFT- $\gamma$ Mie GC approach, and the (black) symbols are corresponding experimental data (Frankforter and Cohen, 1914). Dashed red lines are the calculated tie lines. The red square on the water- $\mathrm{CaCl}_{2}$ axis denotes the composition of the saturated aqueous solution of $\mathrm{CaCl}_{2}$ calculated at $\mathrm{T}=293.15 \mathrm{~K}$ to be in equilibrium with the solid salt. The continuous black line denotes the limit of fluid phase behaviour. Calcium chloride hydrates are not shown in the figure.}
\end{figure}

Mixtures involving asymmetric electrolytes (e.g., $\mathrm{CaCl}_{2}$ ) are rarely studied with phase equilibrium algorithms in the literature. We found no algorithms specifically designed for such systems that would allow us to benchmark the performance of our approach. Instead, most
approaches deal with these systems by solving the conventional LLE equations based on postulating the number of phases and carrying out activity coefficient calculations on a salt-free basis. For example, for systems similar to the ones presented in Figs. 5 and 6, modified versions

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/7cde30c6-bbef-469d-8c04-f3706196d7ec-16.jpg?height=1594&width=981&top_left_y=183&top_left_x=542}
\captionsetup{labelformat=empty}
\caption{Fig. 6. Liquid-liquid equilibria for the $\mathrm{CaCl}_{2}+$ water + propanoic acid (AP) +1 -butanol at $T=303.15 \mathrm{~K}, P=101.3 \mathrm{kPa}$ and a total $\mathrm{CaCl}_{2}$ composition of $4.3 \%$ by mass. Symbols correspond to the experimental data (Zurita et al., 1998) and the continuous red curves are the corresponding binodal curves calculated using the HELD2.0 algorithm and the SAFT- $\gamma$ Mie GC approach, with tie lines shown as dashed red lines. The continuous blue curve is presented as a reference and corresponds to the predicted liquid-liquid equilibria for the ternary system water + propanoic acid +1 -butanol (in the absence of salt). (a) Phase diagram on a salt-free basis, where $w_{i}^{s f}$ is the salt-free mass fraction for component $i$; (b) Quaternary phase diagram, where $w_{i}$ is the mass fraction of component $i$.}
\end{figure}
of the NRTL model (Bourayou and Meniai, 2007) and of the model of Hala (Kumagae et al., 1994) have been deployed, respectively, to fit the experimental data and extrapolate to other salt concentrations.

\section*{6. Conclusions and future work}

We have presented a formal statement of a phase stability criterion for mixtures containing strong electrolytes based on the tangent-plane distance. Our exposition takes into account the electroneutrality of all stable phases, resulting in a reduction of the dimensionality of the problem by one, via a variable transformation. To the best of our knowledge, we have reported the first proof of a stability criterion for charged systems. We have also recast the tangent-plane distance criterion within the formalism of the dual extremum principle of Mitsos and Barton (2007), stating the stability criterion for a mixture of $C$
components at given temperature, pressure, and total composition in terms of the Gibbs free energy (with $C-2$ degrees of freedom) and of the Helmholtz free energy (with $C-1$ degrees of freedom).

Building on the latter criterion, we have extended the HELD algorithm of Pereira et al. (2010) to mixtures containing strong electrolytes. Unlike most algorithms proposed for this type of mixtures, the HELD2.0 algorithm is applicable to any number of components and phases, and does not require any initial guesses in terms of phase number and compositions, or any assumptions on which phases may or may not contain electrolytes. The relevant dual problem is solved over $C-2$ Lagrange multipliers in the space of molar volumes and $C-2$ compositions, potentially enabling more efficient solution strategies as smaller optimization subproblems are solved. The condition of macroscopic electroneutrality is naturally met by each phase considered throughout the procedure.

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table 8
Results of sample calculations with the HELD2.0 algorithm for $\mathrm{CaCl}_{2}+$ water + propanoic acid +1 -butanol at $T=303.15 \mathrm{~K}$ and $P=101.325 \mathrm{kPa}$, and $\mathrm{CaCl}_{2}$ concentration of $4.3 \% \mathrm{w} / \mathrm{w} . w_{o, \mathrm{AP}}^{s f}$ is the initial solvent-free mass fraction of propanoic acid (AP); Phase is the type of stable phase; $\mathbf{x}$ represents the mole fraction vector in each phase of the compositions at equilibria (ordered as $\mathrm{Ca}^{+2}, \mathrm{Cl}^{-}$, water, AP , and butanol); $\eta$ is the dimensionless packing fraction of each phase; $V$ its molar volume; Iter. is the number of iterations; and CPU is the CPU time required by the HELD2.0 algorithm with the SAFT- $\gamma$ Mie GC approach.}
\begin{tabular}{|l|l|l|l|l|l|l|}
\hline $w_{o, \mathrm{AP}}^{s f}$ & Phase & $\mathbf{x}=\left(x_{\mathrm{Ca}^{+2}}, x_{\mathrm{Cl}^{-}}, x_{\text {water }}, x_{\mathrm{AP}}, x_{\text {butanol }}\right)$ & $\eta$ & $V /\left(\mathrm{m}^{3} \mathrm{~mol}^{-1}\right)$ & Iter. & CPU/s \\
\hline \multirow{2}{*}{0.0460} & Phase I(aq.) & (0.0013733, 0.027466, 0.95461, 0.0016659, 0.0025247) & 0.4797 & $1.817 \times 10^{-5}$ & \multirow{2}{*}{78} & \multirow{2}{*}{10.89} \\
\hline & Phase II (org.) & ( $2.01544 \times 10^{-8}, 4.03089 \times 10^{-8}, 0.54384,0.055722,0.40043$ ) & 0.4910 & $4.902 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{0.106} & Phase I (aq.) & (0.014170, 0.028340, 0.95131, 0.0041444, 0.0020310) & 0.4802 & $1.826 \times 10^{-5}$ & \multirow{2}{*}{80} & \multirow{2}{*}{10.17} \\
\hline & Phase II (org.) & ( $4.01478 \times 10^{-8}, 8.02957 \times 10^{-8}, 0.58375,0.11798,0.29826$ ) & 0.4917 & $4.501 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{0.151} & Phase I (aq.) & (0.014678, 0.029356, 0.94810, 0.0062496, 0.0016145) & 0.4807 & $1.833 \times 10^{-5}$ & \multirow{2}{*}{84} & \multirow{2}{*}{9.93} \\
\hline & Phase II (org.) & ( $8.73786 \times 10^{-8}, 1.74757 \times 10^{-7}, 0.61944,0.15464,0.22591$ ) & 0.4921 & $4.178 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{0.211} & Phase I (aq.) & (0.015970, 0.031940, 0.94225, 0.0088458, 0.00099817) & 0.4813 & $1.841 \times 10^{-5}$ & \multirow{2}{*}{79} & \multirow{2}{*}{9.94} \\
\hline & Phase II (org.) & $\left(4.21218 \times 10^{-7}, 8.42436 \times 10^{-7}, 0.67839,0.18495,0.13665\right)$ & 0.4927 & $3.699 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{0.256} & Phase I (aq.) & (0.017906, 0.035812, 0.93598, 0.0097616, 0.00054308) & 0.4819 & $1.841 \times 10^{-5}$ & \multirow{2}{*}{83} & \multirow{2}{*}{10.36} \\
\hline & Phase II (org.) & $\left(2.05279 \times 10^{-6}, 4.10559 \times 10^{-6}, 0.72845,0.19174,0.0798085\right)$ & 0.4930 & $3.329 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{0.301} & Phase I (aq.) & (0.020673, 0.041347, 0.92805, 0.0097160, 0.00021058) & 0.4825 & $1.836 \times 10^{-5}$ & \multirow{2}{*}{80} & \multirow{2}{*}{10.23} \\
\hline & Phase II (org.) & ( $8.6348 \times 10^{-6}, 1.7269 \times 10^{-5}, 0.76582,0.19617,0.037978$ ) & 0.4927 & $3.057 \times 10^{-5}$ & & \\
\hline \multirow{2}{*}{0.346} & Phase I (aq.) & (0.023642, 0.047284, 0.91965, 0.0093915, 0.000027896) & 0.4831 & $1.832 \times 10^{-5}$ & \multirow[b]{2}{*}{78} & \multirow{2}{*}{9.95} \\
\hline & Phase II (org.) & (0.000026523, 0.000053046, 0.78929, 0.20394, 0.0066814) & 0.4921 & $2.879 \times 10^{-5}$ & & \\
\hline
\end{tabular}
\end{table}

The HELD2.0 algorithm has been tested for a variety of systems composed of mixed organic solvents and aqueous solutions of symmetric and asymmetric electrolytes. The thermodynamic properties of all the mixtures were calculated using the SAFT- $\gamma$ Mie EoS which accounts for long-range ion-ion interactions and solvent-ion interactions. The rigorous description of the molecular solvents makes it possible to capture the effect of the presence of ions on fluid-phase equilibria. The same degree of reliability in the phase stability/equilibrium calculations has been achieved with the HELD2.0 algorithms for these highly nonideal systems as observed for mixtures of molecular (neutral) species (Pereira et al., 2010, 2012). The HELD2.0 algorithm has been found to deal with phases that contain traces or negligible amounts of ionic species, ensuring that electroneutrality is achieved even in challenging situations such as a vapour phase coexisting with liquid brine phases or highly uneven distributions of ions between two liquid phases at equilibria. By broadening the scope of the HELD algorithm to charged systems, our work allows one to study of the effect of electrolytes on solubility, making it possible to investigate the salting-out or salting-in effects that are commonly implemented in the design and optimization of solvent extraction and extractive crystallization processes.

We hope that by reporting computational metrics for our initial implementation of HELD2.0 we have encouraged others to develop multicomponent mulitphase algorithms for the phase equilibrium and stability of strong electrolyte mixtures and to investigate their computational performance. The proposed approach can be further strengthened through a focus on the implementation to accelerate computations and by adopting a reliable deterministic global optimization solver to replace the current multistart algorithm. Our work also paves the way for a further extension of the theoretical and algorithmic framework to weak electrolyte solutions in which one must accounts for chemical reactions/equilibria and changes in the numbers of moles of some species relative to the specified total composition. This will be the subject of a future publication.

\section*{CRediT authorship contribution statement}

Felipe A. Perdomo: Writing - original draft, Visualization, Validation, Software, Methodology, Investigation, Formal analysis. George Jackson: Writing - review \& editing, Supervision, Conceptualization. Alexander Mitsos: Writing - review \& editing, Validation, Methodology. Amparo Galindo: Writing - review \& editing, Visualization, Validation, Supervision, Resources, Project administration, Methodology, Conceptualization. Claire S. Adjiman: Writing - original draft, Supervision, Resources, Project administration, Methodology, Investigation, Funding acquisition, Formal analysis, Conceptualization.

\section*{Declaration of competing interest}

The authors declare the following financial interests/personal relationships which may be considered as potential competing interests: Claire Adjiman reports financial support was provided by Engineering and Physical Sciences Research Council. Claire Adjiman reports financial support was provided by European Commission. Claire Adjiman reports financial support was provided by Eli Lilly and Company. Amparo Galindo reports financial support was provided by Royal Academy of Engineering. Alexander Mitsos - Associate Editor Claire Adjiman - Editorial board member If there are other authors, they declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

\section*{Acknowledgments}

The authors are grateful to Terrence Crombie, Imperial College London, for his support with code development. The authors gratefully acknowledge support from the UK Engineering and Physical Sciences Research Council for the ADOPT International Centre to Centre grant (EP/W003317/1). Felipe A. Perdomo, Amparo Galindo, George Jackson, Claire S. Adjiman are grateful to have received funding from the European Union's Horizon 2020 research and innovation program (Grant 727503 - ROLINCAP - H2020-LCE-2016-2017/H2020-LCE-2016-RES-CCS-RIA) and to Eli Lilly and Company and the UK Engineering and Physical Sciences Research Council, through the PharmaSELProsperity Programme (EP/T005556/1). Amparo Galindo is thankful to the Royal Academy of Engineering and Eli Lilly and Company for support of a Research Chair (Grant RCSRF18193). We wish to acknowledge the use of the EPSRC-funded Physical Sciences Datascience Service hosted by the University of Southampton and STFC under grant number EP/S020357/1.

\section*{Appendix A. Proof of Theorem 3.1}

We follow the direct approach of Mitsos and Barton (2007) to prove the tangent plane stability criterion and begin by proving the necessary conditions hold true.
1. The tangent plane always lies below the modified Gibbs free energy surface. We make use of Lemma 12 in Mitsos and Barton (2007), which can readily be extended to the functions
considered here. Let there exist $\overline{\mathbf{x}}^{(E C)^{\prime}} \in \bar{X}^{(E C)}$ such that

$$
\begin{equation*}
T_{G}\left(\overline{\mathbf{x}}^{(E C)^{\prime}}\right)>\bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C)^{\prime}}\right) . \tag{A.1}
\end{equation*}
$$


Then, through the modified Lemma 12 applied to the line passing through $\overline{\mathbf{x}}^{(E C)^{\prime}}$ and $\overline{\mathbf{x}}^{(E C), j^{*}}$, there must exist point $\overline{\mathbf{x}}^{(E C)^{\prime \prime}}$ and $\kappa \in(0,1)$ such that

$$
\begin{equation*}
\overline{\mathbf{x}}^{(E C), j^{*}}=\kappa \overline{\mathbf{x}}^{(E C)^{\prime \prime}}+(1-\kappa) \overline{\mathbf{x}}^{(E C)^{\prime \prime}} \tag{A.2}
\end{equation*}
$$

and

$$
\begin{align*}
\bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j^{*}}\right)> & \kappa \bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C)^{\prime \prime}}\right) \\
& +(1-\kappa) \bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C)^{\prime}}\right) . \tag{A.3}
\end{align*}
$$


Since $\overline{\mathbf{x}}^{(E C), j^{*}} \in \operatorname{int}(\bar{X})$ and $\overline{\mathbf{x}}^{(E C)^{\prime \prime}}$ can be arbitrarily close to $\overline{\mathbf{x}}^{(E C), j^{*}}$, we have $\overline{\mathbf{x}}^{(E C)^{\prime \prime}} \in \bar{X}^{(E C)}$. It is therefore possible to decrease the modified Gibbs free energy by replacing $\overline{\mathbf{x}}^{(E C), j^{*}}$ with two new phases with modified mole fractions $\overline{\mathbf{x}}^{(E C)^{\prime}}$ and $\overline{\mathbf{x}}^{(E C)^{\prime \prime}}$. This contradicts the statement that the state is stable and we must therefore have

$$
\begin{equation*}
T_{G}\left(\overline{\mathbf{x}}^{(E C)^{\prime}}\right) \leq \bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C)^{\prime}}\right) . \tag{A.4}
\end{equation*}
$$

2. The tangent plane supports the modified Gibbs free energy at the composition of each stable phase. Per Eq. (29), equality of the modified electrochemical potentials must hold for $C-1$ components (excluding component $E$ ) across all phases

$$
\begin{equation*}
\bar{\mu}_{i}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right)=\bar{\mu}_{i}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j^{*}}\right), \quad \forall i \in \mathcal{C}^{(E)}, \quad \forall j \in J . \tag{A.5}
\end{equation*}
$$


Substituting Eqs. (33) and (34) into these necessary conditions, we have

$$
\left\{\begin{array}{l}
\bar{\mu}_{C}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right)+\bar{G}_{\bar{x}_{i}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right)  \tag{A.6}\\
\quad=\bar{\mu}_{C}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j^{*}}\right)+\bar{G}_{\bar{x}_{i}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j^{*}}\right), \forall i \in \mathcal{C}^{(E C)}, \forall j \in J, \\
\bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right)-\sum_{k \in \mathcal{C}^{(E C)}} \bar{G}_{\bar{x}_{k}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right) \bar{x}_{k}^{(E C), j}= \\
\bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j^{*}}\right)-\sum_{k \in \mathcal{C}^{(E C)}} \bar{G}_{\bar{x}_{k}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j^{*}}\right) \bar{x}_{k}^{(E C), j^{*}}, \forall j \in J .
\end{array}\right.
$$


Making use of the equality of the modified electrochemical potentials of component $C$ once more, the first equation yields:

$$
\begin{align*}
\bar{G}_{\bar{x}_{i}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right)=\bar{G}_{\bar{x}_{i}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j^{*}}\right) & , \\
& \forall i \in \mathcal{C}^{(E C)}, \forall j \in J . \tag{A.7}
\end{align*}
$$


Using this and adding $\sum_{k \in \mathcal{C}^{(E C)}} \bar{G}_{\bar{x}_{k}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j^{*}}\right) \bar{x}_{k}^{(E C)}$, or equivalently,

$$
\sum_{k \in \mathcal{C}^{(E C)}} \bar{G}_{\bar{x}_{k}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right) \bar{x}_{k}^{(E C)}
$$

to both sides of the second equation in (A.6), yields:

$$
\begin{align*}
\bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right)+\sum_{k \in \mathcal{C}^{(E C)}} \bar{G}_{\bar{x}_{k}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right)\left(\bar{x}_{k}^{(E C)}-\bar{x}_{k}^{(E C), j}\right) & \\
=\bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j^{*}}\right)-\sum_{k \in \mathcal{C}^{(E C)}} \bar{G}_{\bar{x}_{k}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j^{*}}\right)\left(\bar{x}_{k}^{(E C)}-\bar{x}_{k}^{(E C), j^{*}}\right), & \\
& \forall j \in J, \forall \overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)} . \tag{A.8}
\end{align*}
$$


Finally, we note the right-hand side of the second equation is the tangent at $\overline{\mathbf{x}}^{(E C), j^{*}}$ so that

$$
\begin{align*}
T_{G}\left(T, P, \overline{\mathbf{x}}^{(E C)}\right)= & \bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right) \\
& +\sum_{k \in \mathcal{C}^{(E C)}} \bar{G}_{\bar{x}_{k}^{(E C)}}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right)\left(\bar{x}_{k}^{(E C)}-\bar{x}_{k}^{(E C), j}\right), \\
& \quad \forall j \in J, \forall \overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)} . \tag{A.9}
\end{align*}
$$


This concludes the proof of the necessary conditions. We now consider sufficiency. Recall that the total mole number is the same regardless of whether it is obtained by summing mole numbers or modified mole numbers (Eq. (25)), so that we use $n_{t}$ to denote total mole numbers throughout. The extensive constrained Gibbs free energy of the state is $\underline{\bar{G}}^{e l, J}=\sum_{j \in J} n_{t}^{j} \bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right)$. From Eq. (A.9), this is equivalent to $\bar{G}^{e l}=\sum_{j \in J} n_{t}^{j} T_{G}\left(T, P, \overline{\mathbf{x}}^{(E C), j}\right)=n_{t, o} T_{G}\left(T, P, \overline{\mathbf{x}}_{o}^{(E C)}\right)$, where the mole balance has been used to obtain the last equality. Suppose that the tangent plane lies below the constrained Gibbs free energy surface and consider a different state with index set $K$, modified mole fraction vector $\overline{\mathbf{x}}^{k} \in \bar{X}$ and total mole numbers $n_{t}^{k}$ in each phase that satisfy the mole balance, $\sum_{k \in K} n_{t}^{, k} \bar{x}_{i}^{(E C), k}=\bar{n}_{o, i}^{(E)}, \forall i \in \mathcal{C}^{(E)}$.

We have $\underline{\bar{G}}^{e l, K}=\sum_{k \in K} n_{t}^{k} \bar{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), k}\right) \geq \sum_{k \in K} n_{t}^{k} T_{G}^{e l}\left(T, P, \overline{\mathbf{x}}^{(E C), k}\right)=n_{t}^{o} T_{G}\left(\overline{\mathbf{x}}_{o}^{(E C)}\right)$. Hence, $\underline{G}^{e l, K} \geq \underline{G}^{e l, J}$ and the state $J$ is stable.

\section*{Appendix B. Formal statement of the dual extremum principle using the Helmholtz free energy}

Theorem B.1. Consider a system of $C$ species, of which species 1 to $E$ are charged, $E<C$, at given $T$ and $P_{o}$ and total modified mole numbers $\bar{n}_{o, i}> 0, i \in \mathcal{C}^{(E)}=\{1, \ldots, E-1, E+1, \ldots, C\}$. Denote $\bar{n}_{t, o}=n_{t, o}=\sum_{i \in \mathcal{C}^{(E)}} \bar{n}_{o, i}$. Consider any solution ( $\bar{\lambda}^{*}, \overline{\mathbf{x}}^{(E C), *}, V^{*}$ ) of dual problem (51). The hyperplane

$$
\begin{equation*}
T_{A}\left(T, V, \overline{\mathbf{x}}^{(E C)} ; P_{o}\right)=\bar{A}^{e l}\left(T, V^{*}, \overline{\mathbf{x}}^{(E C), *}\right)+P_{o}\left(V-V^{*}\right)+\sum_{i \in \mathcal{C}^{(E C)}} \bar{\lambda}_{i}^{*}\left(\bar{x}_{i}^{(E C)}-\bar{x}_{i}^{(E C), *}\right) \tag{B.1}
\end{equation*}
$$

is a supporting hyperplane of $\hat{G}^{e l}$ on $\left[V^{L}, V^{U}\right] \times \bar{X}^{(E C)}$, i.e.,

$$
\begin{equation*}
T_{A}\left(T, V, \overline{\mathbf{x}}^{(E C)} ; P_{o}\right) \leq \hat{G}^{e l}\left(T, V, \overline{\mathbf{x}}^{(E C)} ; P_{o}\right), \quad \forall V \in\left[V^{L}, V^{U}\right], \forall \overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)} . \tag{B.2}
\end{equation*}
$$


Furthermore, the hyperplane defined by the intersection of $T_{A}$ with the set $\mathcal{V}=\left\{V \in\left[V^{L}, V^{U}\right]: P\left(T, V, \overline{\mathbf{x}}^{(E C)}\right)=P_{o}\right\}$,

$$
\begin{align*}
T_{A, r}\left(T, P_{o}, \overline{\mathbf{x}}^{(E C)}\right) & =\bar{A}^{e l}\left(T, V^{*}, \overline{\mathbf{x}}^{(E C), *}\right)+P_{o}\left(V^{*}-V^{\prime}\right) \\
+ & \sum_{i \in \mathcal{C}^{(E C)}} \bar{\lambda}_{i}\left(\bar{x}_{i}^{(E C)}-\bar{x}_{i}^{(E C), *}\right), \forall V^{\prime} \in \mathcal{V}, \tag{B.3}
\end{align*}
$$

is a supporting hyperplane of $\bar{G}^{e l}\left(T, P_{o}, \overline{\mathbf{x}}^{(E C)}\right)$ on $\bar{X}^{(E C)}$, i.e.,

$$
\begin{equation*}
T_{A, r}\left(T, P_{o}, \overline{\mathbf{x}}\right) \leq \bar{G}^{e l}\left(T, P_{o}, \overline{\mathbf{x}}^{(E C)}\right), \quad \forall \overline{\mathbf{x}}^{(E C)} \in \bar{X}^{(E C)} . \tag{B.4}
\end{equation*}
$$


Moreover, let $\left(\mathcal{V}^{*}, \bar{X}^{(E C), *)}\right.$ be the set of common points between $T_{A}$ as defined in Eq. (B.1) and $\hat{G}^{e l}$, i.e.,

$$
\begin{align*}
\left(\mathcal{V}^{*}, \bar{X}^{(E C), *}\right) & =\left\{\left(V, \overline{\mathbf{x}}^{(E C)}\right) \in\left[V^{L}, V^{U}\right] \times \bar{X}^{(E C)}: T_{A}\left(T, V, \overline{\mathbf{x}}^{(E C)} ; P_{o}\right)\right. \\
& \left.=\hat{G}^{e l}\left(T, V, \overline{\mathbf{x}}^{(E C)} ; P_{o}\right)\right\} . \tag{B.5}
\end{align*}
$$


Then, $\bar{X}^{(E C), *}$ is the set of common points between $T_{A, r}$ as defined in $E q$. (B.4) and $\bar{G}^{e l}$, i.e., $\bar{X}^{(E C), *} \quad= \left\{\overline{\mathbf{x}}^{(E C)} \in \times \bar{X}^{(E C)}: T_{A, r}\left(T, P_{o}, \overline{\mathbf{x}}^{(E C)}\right)=\bar{G}^{e l}\left(T, P_{o}, \overline{\mathbf{x}}^{(E C)}\right)\right\}$ and

$$
\begin{equation*}
\overline{\mathbf{x}}_{o}^{(E C)} \in \operatorname{conv}\left(\bar{X}^{(E C), *}\right) . \tag{B.6}
\end{equation*}
$$


Finally, a state described by a collection of phases with index set $J$, modified mole fractions $\overline{\mathbf{x}}^{(E C), j} \in \bar{X}^{(E C)}$, molar volume $V^{j}$ and with nonzero
total number of moles in each phase $j, n_{t}^{j}>0$, and such that $\overline{\mathbf{x}}_{o}^{(E C)} \in \operatorname{conv}\left(\bar{X}^{(E C), *}\right)$, is stable if and only if $\left(V^{j}, \overline{\mathbf{x}}^{(E C), j}\right) \in \mathcal{V}^{*} \times \bar{X}^{(E C), *}, \forall j \in J$, or equivalently all triplets ( $\bar{\lambda}^{*}, V^{j}, \overline{\mathbf{x}}^{(E C), j}$ ) are (global) solutions of dual problem (51).

\section*{Appendix C. Initialization of set $\mathcal{M}$}

The strategy presented in Pereira et al. (2012) to populate set $\mathcal{M}$ at the start of the HELD algorithm can be adapted to electrolyte systems and modified mole fractions as follows. Starting from unmodified mole fraction vectors, vectors $\hat{\mathbf{x}}^{i}$ and $\overline{\mathbf{x}}^{i}, \forall i \in C$, are chosen so that the $i^{\text {th }}$ component of the $i^{\text {th }}$ vectors satisfy $\hat{x}_{i}^{i}<x_{o, i}$ and $\bar{x}_{i}^{i}>x_{o, i}$. Specifically the following equations are used for each $i \in \mathcal{C}$ :
$\hat{x}_{i}^{i}=\frac{x_{o, i}}{2}$

$$
\begin{equation*}
\hat{x}_{k}^{i}=\frac{1}{C-1}\left(\frac{1}{\left(1-\frac{z_{k}}{z_{E}}\right)}-\hat{x}_{i}^{i}\right) \quad \forall k \in C^{(E C)}, k \neq i \tag{C.1}
\end{equation*}
$$

$\hat{x}_{E}^{i}=\sum_{k \in \mathcal{C}^{(E C)}}-\frac{z_{k}}{z_{E}} \hat{x}_{k}^{i}$,
$\hat{x}_{C}^{i}=1-\sum_{k=1}^{C-1} \hat{x}_{k}^{i}$
and
$\tilde{x}_{i}^{i}=\frac{1}{2(C-1)}\left(\frac{1}{1-\frac{z_{k}}{z_{E}}}+x_{o, i}\right)$
$\tilde{x}_{k}^{i}=\frac{1}{C-1}\left(\frac{1}{\left(1-\frac{z_{k}}{z_{E}}\right)}-\tilde{x}_{i}^{i}\right) \quad \forall k \in C^{(E C)}, k \neq i$
(C.2)
$\tilde{x}_{E}^{i}=\sum_{k \in \mathcal{C}^{(E C)}}-\frac{z_{k}}{z_{E}} \tilde{x}_{k}^{i}$,
$\tilde{x}_{C}^{i}=1-\sum_{k=1}^{C-1} \tilde{x}_{k}^{i}$
These can be transformed to a set of initial modified mole fractions, $\hat{\overline{\mathbf{x}}}^{(E C), i}$ and $\overline{\overline{\mathbf{x}}}^{(E C), i}$, by applying Eq. (30).

The value of $\hat{V}^{i}$ (respectively $\bar{V}^{i}$ ) corresponding to $\hat{\overline{\mathbf{x}}}^{(E C), i}$ (resp. $\overline{\overline{\mathbf{x}}}^{(E C), i}$ ) is determined by solving the pressure equation so that $P\left(T, \hat{V}^{i}, \hat{\hat{\mathbf{x}}}^{(E C), i}\right)=P_{o}$ (cf. $P\left(T, \bar{V}^{i}, \overline{\overline{\mathbf{x}}}^{(E C), i}\right)=P_{o}$ ). The pairs ( $\hat{V}^{i}, \hat{\overline{\mathbf{x}}}^{(E C), i}$ ) and ( $\bar{V}^{i}, \overline{\overline{\mathbf{x}}}^{(E C), i}$ ) are stored in the set $\mathcal{M}$.

\section*{Appendix D. SAFT- $\boldsymbol{\gamma}$ Mie parameters used in the calculations}

All the parameters needed to reproduce the results presented in the current work are given in Tables D. 9 and D.10. Details of the

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table D. 9
Unlike group dispersion energies $\varepsilon_{k l}$ and repulsive exponent $\lambda_{k l}^{r}$ between groups $k$ and $l$. CR indicates that $\lambda_{k l}^{r}$ is obtained from combining rules (Haslam et al., 2020). The $\dagger$ indicates that the parameter has been developed in the current work.}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|l|l|l|l|l|}
\hline $k$ & $l$ & Group $k$ & Group $l$ & $\left(\frac{\varepsilon_{k l}}{k_{B}}\right) / K$ & $\lambda_{k l}^{r}$ & Ref. & $k$ & $l$ & Group $k$ & Group $l$ & $\left(\frac{\varepsilon_{k l}}{k_{B}}\right) / K$ & $\lambda_{k l}^{r}$ & Ref. \\
\hline 1 & 2 & $\mathrm{Cl}^{-}$ & $\mathrm{Li}^{+}$ & 8.2904 & CR & Eriksen et al. (2016) & 7 & 8 & $\mathrm{CH}_{2}$ & $\mathrm{CH}_{3}$ & 350.77 & CR & Papaioannou et al. (2014) \\
\hline 1 & 3 & $\mathrm{Cl}^{-}$ & $\mathrm{Na}^{+}$ & 27.938 & CR & Eriksen et al. (2016) & 7 & 9 & $\mathrm{CH}_{2}$ & $\mathrm{CH}_{2} \mathrm{OH}$ & 423.17 & CR & Hutacharoen et al. (2017) \\
\hline 1 & 4 & $\mathrm{Cl}^{-}$ & $\mathrm{Ca}^{2}+$ & 76.931 & CR & Eriksen et al. (2016) & 7 & 10 & $\mathrm{CH}_{2}$ & COOH & 413.74 & CR & Dufal et al. (2014) \\
\hline 1 & 5 & $\mathrm{Cl}^{-}$ & $\mathrm{K}^{+}$ & 61.010 & CR & Eriksen et al. (2016) & 7 & 11 & $\mathrm{CH}_{2}$ & $\mathrm{CH}_{3} \mathrm{COCH}_{3}$ & 299.48 & 11.594 & Dufal et al. (2014) \\
\hline 1 & 6 & $\mathrm{Cl}^{-}$ & $\mathrm{CH}_{3} \mathrm{OH}$ & 136.53 & CR & † & 7 & 12 & $\mathrm{CH}_{2}$ & $\mathrm{H}_{2} \mathrm{O}$ & 423.63 & 100.00 & Dufal et al. (2014) \\
\hline 1 & 9 & $\mathrm{Cl}^{-}$ & $\mathrm{CH}_{2} \mathrm{OH}$ & 201.41 & CR & † & 8 & 9 & $\mathrm{CH}_{3}$ & $\mathrm{CH}_{2} \mathrm{OH}$ & 333.20 & CR & Hutacharoen et al. (2017) \\
\hline 1 & 10 & $\mathrm{Cl}^{-}$ & COOH & 314.23 & CR & † & 8 & 10 & $\mathrm{CH}_{3}$ & COOH & 255.99 & CR & Dufal et al. (2014) \\
\hline 1 & 11 & $\mathrm{Cl}^{-}$ & $\mathrm{CH}_{3} \mathrm{COCH}_{3}$ & 200.41 & CR & † & 8 & 11 & $\mathrm{CH}_{3}$ & $\mathrm{CH}_{3} \mathrm{COCH}_{3}$ & 233.48 & 14.449 & Dufal et al. (2014) \\
\hline 1 & 12 & $\mathrm{Cl}^{-}$ & $\mathrm{H}_{2} \mathrm{O}$ & 95.406 & CR & Eriksen et al. (2016) & 8 & 12 & $\mathrm{CH}_{3}$ & $\mathrm{H}_{2} \mathrm{O}$ & 358.18 & 100.00 & Dufal et al. (2014) \\
\hline 2 & 6 & $\mathrm{Li}^{+}$ & $\mathrm{CH}_{3} \mathrm{OH}$ & 849.05 & CR & † & 9 & 10 & $\mathrm{CH}_{2} \mathrm{OH}$ & COOH & 488.18 & CR & Haslam et al. (2020) \\
\hline 2 & 9 & $\mathrm{Li}^{+}$ & $\mathrm{CH}_{2} \mathrm{OH}$ & 1952.6 & CR & † & 9 & 11 & $\mathrm{CH}_{2} \mathrm{OH}$ & $\mathrm{CH}_{3} \mathrm{COCH}_{3}$ & 338.47 & CR & Haslam et al. (2020) \\
\hline 2 & 12 & $\mathrm{Li}^{+}$ & $\mathrm{H}_{2} \mathrm{O}$ & 1023.1 & CR & Eriksen et al. (2016) & 9 & 12 & $\mathrm{CH}_{2} \mathrm{OH}$ & $\mathrm{H}_{2} \mathrm{O}$ & 353.37 & CR & Hutacharoen et al. (2017) \\
\hline 3 & 9 & $\mathrm{Na}^{+}$ & $\mathrm{CH}_{2} \mathrm{OH}$ & 418.96 & CR & † & 10 & 11 & COOH & $\mathrm{CH}_{3} \mathrm{COCH}_{3}$ & 393.71 & CR & Dufal et al. (2014) \\
\hline 3 & 10 & $\mathrm{Na}^{+}$ & COOH & 380.02 & CR & † & 10 & 12 & COOH & $\mathrm{H}_{2} \mathrm{O}$ & 289.76 & CR & Dufal et al. (2014) \\
\hline 3 & 12 & $\mathrm{Na}^{+}$ & $\mathrm{H}_{2} \mathrm{O}$ & 539.68 & CR & Eriksen et al. (2016) & 11 & 12 & $\mathrm{CH}_{3} \mathrm{COCH}_{3}$ & $\mathrm{H}_{2} \mathrm{O}$ & 287.26 & CR & Dufal et al. (2014) \\
\hline 4 & 9 & $\mathrm{Ca}^{2}+$ & $\mathrm{CH}_{2} \mathrm{OH}$ & 1102.0 & CR & $\dagger$ & & & & & & & \\
\hline 4 & 10 & $\mathrm{Ca}^{2}+$ & COOH & 733.21 & CR & † & & & & & & & \\
\hline 4 & 11 & $\mathrm{Ca}^{2}+$ & $\mathrm{CH}_{3} \mathrm{COCH}_{3}$ & 1007.8 & CR & † & & & & & & & \\
\hline 4 & 12 & $\mathrm{Ca}^{2}+$ & $\mathrm{H}_{2} \mathrm{O}$ & 1460.8 & CR & Eriksen et al. (2016) & & & & & & & \\
\hline 5 & 12 & $\mathrm{K}^{+}$ & $\mathrm{H}_{2} \mathrm{O}$ & 376.25 & CR & Eriksen et al. (2016) & & & & & & & \\
\hline 6 & 7 & $\mathrm{CH}_{3} \mathrm{OH}$ & $\mathrm{CH}_{2}$ & 341.41 & 17.050 & Dufal et al. (2014) & & & & & & & \\
\hline 6 & 8 & $\mathrm{CH}_{3} \mathrm{OH}$ & $\mathrm{CH}_{3}$ & 275.76 & 15.537 & Dufal et al. (2014) & & & & & & & \\
\hline 6 & 12 & $\mathrm{CH}_{3} \mathrm{OH}$ & $\mathrm{H}_{2} \mathrm{O}$ & 278.45 & CR & Dufal et al. (2014) & & & & & & & \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table D. 10
Unlike group association energy $\varepsilon_{k l, a b}^{\mathrm{HB}}$ and bonding volume $K_{k l, a b}$ parameters describing the interaction between site type $a$ on group $k$ and site type $b$ on group $l$.}
\begin{tabular}{|l|l|l|l|l|l|l|l|}
\hline $k$ & $l$ & Group $k$ & Site $a$ of group $k$ & Group $l$ & Site $b$ of group $l$ & $\varepsilon_{k l, a b}^{\mathrm{HB}} / \mathrm{K}$ & $K_{k l, a b} / \AA^{3}$ \\
\hline 6 & 12 & $\mathrm{CH}_{3} \mathrm{OH}$ & e & $\mathrm{H}_{2} \mathrm{O}$ & H & 1993.5 & 104.11 \\
\hline 6 & 12 & $\mathrm{CH}_{3} \mathrm{OH}$ & H & $\mathrm{H}_{2} \mathrm{O}$ & e & 1993.5 & 104.11 \\
\hline 9 & 10 & $\mathrm{CH}_{2} \mathrm{OH}$ & e & COOH & H & 3238.4 & 36.05 \\
\hline 9 & 10 & $\mathrm{CH}_{2} \mathrm{OH}$ & H & COOH & e1 & 1062.1 & 210.67 \\
\hline 9 & 10 & $\mathrm{CH}_{2} \mathrm{OH}$ & H & COOH & e2 & 997.89 & 227.07 \\
\hline 9 & 11 & $\mathrm{CH}_{2} \mathrm{OH}$ & e & $\mathrm{CH}_{3} \mathrm{COCH}_{3}$ & H & 686.93 & 585.99 \\
\hline 9 & 11 & $\mathrm{CH}_{2} \mathrm{OH}$ & H & $\mathrm{CH}_{3} \mathrm{COCH}_{3}$ & e & 1844.8 & 991.95 \\
\hline 9 & 12 & $\mathrm{CH}_{2} \mathrm{OH}$ & e & $\mathrm{H}_{2} \mathrm{O}$ & H & 2153.2 & 147.40 \\
\hline 9 & 12 & $\mathrm{CH}_{2} \mathrm{OH}$ & H & $\mathrm{H}_{2} \mathrm{O}$ & e & 621.68 & 425.00 \\
\hline 10 & 12 & COOH & e1 & $\mathrm{H}_{2} \mathrm{O}$ & H & 1451.8 & 280.89 \\
\hline 10 & 12 & COOH & e2 & $\mathrm{H}_{2} \mathrm{O}$ & H & 1252.6 & 150.98 \\
\hline 10 & 12 & COOH & H & $\mathrm{H}_{2} \mathrm{O}$ & e & 2567.7 & 270.09 \\
\hline 11 & 12 & $\mathrm{CH}_{3} \mathrm{COCH}_{3}$ & e1 & $\mathrm{H}_{2} \mathrm{O}$ & H & 1588.7 & 772.77 \\
\hline 11 & 12 & $\mathrm{CH}_{3} \mathrm{COCH}_{3}$ & e2 & $\mathrm{H}_{2} \mathrm{O}$ & H & 417.24 & 1304.3 \\
\hline 11 & 13 & $\mathrm{CH}_{3} \mathrm{COCH}_{3}$ & H & $\mathrm{H}_{2} \mathrm{O}$ & e & 1386.8 & 188.83 \\
\hline
\end{tabular}
\end{table}
notation for the parameters and the expressions related to the EoS can be found in Papaioannou et al. (2014), Eriksen et al. (2016), Haslam et al. (2020).

\section*{Data availability}

All the values used in the calculations presented from Fig. 1 to Fig. 6 of this article are available on Zenodo at https://doi.org/10. 5281/zenodo. 13646853 and may be used under the Creative Commons Attribution license. The corresponding author can be contacted for access to the HELD2.0 algorithm implementation.

\section*{References}

Al-Sahhaf, T.A., Kapetanovic, E., 1997. Salt effects of lithium chloride, sodium bromide, or potassium iodide on liquid-liquid equilibrium in the system water + 1-butanol. J. Chem. Eng. Data 42, 74-77.

Artola, P.-A., Pereira, F.E., Adjiman, C.S., Galindo, A., Müller, E.A., Jackson, G., Haslam, A.J., 2011. Understanding the fluid phase behaviour of crude oil: Asphaltene precipitation. Fluid Phase Equilib. 306, 129-136.
Ascani, M., Sadowski, G., Held, C., 2022. Calculation of multiphase equilibria containing mixed solvents and mixed electrolytes: General formulation and case studies. J. Chem. Eng. Data 67, 1972-1984.
Baker, L.E., Pierce, A.C., Luks, K.D., 1982. Gibbs energy analysis of phase equilibria. Soc. Petroleum Eng. J. 22, 731-742.
Bazak, J.D., Krachkovskiy, S.A., Goward, G.R., 2017. Multi-temperature in situ magnetic resonance imaging of polarization and salt precipitation in lithium-ion battery electrolytes. J. Phys. Chem. C 121, 20704-20713.
Bazaraa, M.S., Sherali, H.D., Shetty, C.M., 2013. Nonlinear Programming: Theory and Algorithms. John Wiley \& Sons.
Blankenship, J.W., Falk, J.E., 1976. Infinitely constrained optimization problems. J. Optim. Theory Appl. 19, 261-281.
Boone, J.E., Rousseau, R.W., Schoenborn, E.M., 1976. The correlation of vapour-liquid equilibrium data for salt-containing systems. In: Advances in Chemistry. vol. 155, ACS Publications, pp. 36-52.
Bourayou, N., Meniai, A.-H., 2007. Effect of calcium chloride on the liquid-liquid equilibria of the water-acetone system. Desalination 206, 198-204.
Campbell, A.N., Bhatnagar, O.N., 1979. Osmotic and activity coefficients of lithium chloride in water from 50 to $150^{\circ} \mathrm{C}$. Can. J. Chem. 57, 2542-2545.
Chapman, W.G., Jackson, G., Gubbins, K.E., 1988. Phase equilibria of associating fluids: chain molecules with multiple bonding sites. Mol. Phys. 65, 1057-1079.
Cheluget, E.L., Missen, R.W., Smith, W.R., 1987. Computer calculation of ionic equilibria using species- or reaction-related thermodynamic data. J. Phys. Chem. 91, 2428-2432.
Cohen, E.R., Cvitaš, T., Frey, J.G., Holmström, B., Kuchitsu, K., Marquardt, R., Mills, I., Pavese, F., Quack, M., Stohner, J., Strauss, H.L., Takami, M., Thor, A.J., 2007. Quantities, units, and symbols in physical chemistry. In: International Union of Pure and Applied Chemistry. RSC Publishing.
Creusen, R., van Medevoort, J., Roelands, M., van Renesse van Duivenbode, A., Hanemaaijer, J.H., van Leerdam, R., 2013. Integrated membrane distillationcrystallization: Process design and cost estimations for seawater treatment and fluxes of single salt solutions. Desalination 323, 8-16.
de Jesús-González, N.E., Pérez de la Luz, A., López-Lemus, J., Alejandre, J., 2018. Effect of the dielectric constant on the solubility of acetone in water. J. Chem. Eng. Data 63, 1170-1179.
Dufal, S., Papaioannou, V., Sadeqzadeh, M., Pogiatzis, T., Chremos, A., Adjiman, C.S., Jackson, G., Galindo, A., 2014. Prediction of thermodynamic properties and phase behavior of fluids and mixtures with the SAFT- $\gamma$ Mie group-contribution equation of state. J. Chem. Eng. Data 59, 3272-3288.
Endo, S., Pfennigsdorff, A., Goss, K.-U., 2012. Salting-out effect in aqueous NaCl solutions: Trends with size and polarity of solute molecules. Environ. Sci. Technol. 46, 1496-1503.
Eriksen, D.K., Lazarou, G., Galindo, A., Jackson, G., Adjiman, C.S., Haslam, A.J., 2016. Development of intermolecular potential models for electrolyte solutions using an electrolyte SAFT-VR Mie equation of state. Mol. Phys. 114, 2724-2749.
Filiz, M., Gülen, J., 2008. Investigation of the aqueous salt solutions of some first and second group metals at various pressures. Fluid Phase Equilib. 267, 18-22.
Frankforter, G.B., Cohen, L., 1914. Equilibria in the systems, water, acetone and inorganic salts. J. Am. Chem. Soc. 36, 1103-1134.
Fu, H., Wang, X., Sun, Y., Yan, L., Shen, J., Wang, J., Yang, S.-T., Xiu, Z., 2017. Effects of salting-out and salting-out extraction on the separation of butyric acid. Sep. Purif. Technol. 180, 44-50.
Gautam, R., Seider, W.D., 1979a. Computation of phase and chemical equilibrium: Part I. Local and constrained minima in Gibbs free energy. AIChE J. 25, 991-999.

Gautam, R., Seider, W.D., 1979b. Computation of phase and chemical equilibrium: Part II. Phase-splitting. AIChE J. 25, 999-1006.

Gautam, R., Seider, W.D., 1979c. Computation of phase and chemical equilibrium: Part III. Electrolytic solutions. AIChE J. 25, 1006-1015.

Gering, K., Lee, L., 1989. Prediction of vapor-liquid equilibria of binary-solvent electrolytes. Fluid Phase Equilib. 53, 199-206.
Gomis, V., Ruiz, F., Boluda, N., Saquete, M.D., 1999. Unusual S-shaped binodal curves of the systems water + lithium chloride + 1-butanol or 2-butanol or 2-methyl-1-propanol. Fluid Phase Equilib. 155, 241-249.
Großmann, C., Maurer, G., 1995. On the calculation of phase equilibria in aqueous two-phase systems containing ionic solutes. Fluid Phase Equilib. 106, 17-25.
Guggenheim, E., 1935. L. The specific thermodynamic properties of aqueous solutions of strong electrolytes. London Edinb. Dublin Philos. Mag. J. Sci. 19, 588-643.
Harvey, A.H., Prausnitz, J.M., 1987. Dielectric constants of fluid mixtures over a wide range of temperature and density. J. Solut. Chem. 16, 857-869.
Haslam, A.J., González-Pérez, A., Di Lecce, S., Khalit, S.H., Perdomo, F.A., Kournopoulos, S., Kohns, M., Lindeboom, T., Wehbe, M., Febra, S., Jackson, G., Adjiman, C.S., Galindo, A., 2020. Expanding the applications of the SAFT- $\gamma$ Mie group-contribution equation of state: Prediction of thermodynamic properties and phase behavior of mixtures. J. Chem. Eng. Data 65, 5862-5890.
Hayashi, A., Sakuda, A., Tatsumisago, M., 2016. Development of sulfide solid electrolytes and interface formation processes for bulk-type all-solid-state Li and Na batteries. Front. Energy Res. 4, 25.
Held, C., Cameretti, L., Sadowski, G., 2008. Modeling aqueous electrolyte solutions: Part 1. Fully dissociated electrolytes. Fluid Phase Equilib. 270, 87-96.
Hosseinzadeh Dehaghani, Y., Assareh, M., Feyzi, F., 2022. Simultaneous prediction of equilibrium, interfacial, and transport properties of $\mathrm{CO}_{2}$-brine systems using molecular dynamics simulation: Applications to $\mathrm{CO}_{2}$ storage. Ind. Eng. Chem. Res. 61, 15390-15406.
Hutacharoen, P., Dufal, S., Papaioannou, V., Shanker, R.M., Adjiman, C.S., Jackson, G., Galindo, A., 2017. Predicting the solvation of organic compounds in aqueous environments: from alkanes and alcohols to pharmaceuticals. Ind. Eng. Chem. Res. 56, 10856-10876.
Khaibullin, I.K., Borisov, N.M., 1966. Experimental investigation of thermal properties of aqueous and vapour solutions of sodium and potassium chlorides at phase equilibrium. High Temp. 4, 489.
Kiendrebeogo, M., Estahbanati, M.K., Mostafazadeh, A.K., Drogui, P., Tyagi, R.D., 2021. Treatment of microplastics in water by anodic oxidation: A case study for polystyrene. Environ. Pollut. 269, 116168.
Kohns, M., Lazarou, G., Kournopoulos, S., Forte, E., Perdomo, F.A., Jackson, G., Adjiman, C.S., Galindo, A., 2020. Predictive models for the phase behaviour and solution properties of weak electrolytes: Nitric, sulphuric, and carbonic acids. Phys. Chem. Chem. Phys. 22, 15248-15269.
Kumagae, Y., Suzuta, T., Abe, T., Iwai, Y., Arai, Y., 1994. Liquid-liquid equilibria of heptane-methanol-toluene-calcium chloride and ethyl acetate-water-ethanol-calcium chloride quaternary systems. Can. J. Chem. Eng. 72, 695-700.
Lantagne, G., Marcos, B., Cayrol, B., 1988. Computation of complex equilibria by nonlinear optimization. Comput. Chem. Eng. 12, 589-599.
Lavi, O., Luski, S., Shpigel, N., Menachem, C., Pomerantz, Z., Elias, Y., Aurbach, D., 2020. Electrolyte solutions for rechargeable Li-ion batteries based on fluorinated solvents. ACS Appl. Energy Mater. 3, 7485-7499.
Levy, A.V., Gómez, S., 1985. The tunneling method applied to global optimization. Numer. Optim. 1981, 213-244.
Lutskii, A.E., Mikhailenko, S.A., 1963. The hydrogen bond and the static permittivity of liquids. J. Struct. Chem. 4, 12-14.
Maribo-Mogensen, B., Kontogeorgis, G., Thomsen, K., 2013. Modeling of dielectric properties of aqueous salt solutions with an equation of state. J. Phys. Chem. B 117, 10523-10533.
Matkovich, C.E., Christian, G.D., 1973. Salting-out of acetone from water. Basis of a new solvent extraction system. Anal. Chem. 45, 1915-1921.
McCabe, C., Galindo, A., 2010. SAFT associating fluids and fluid mixtures. In: Goodwin, A.R.H., Sengers, J.V. (Eds.), Applied Thermodynamics of Fluids. Royal Society of Chemistry, London, pp. 215-279.
McDonald, C.M., Floudas, C.A., 1995. Global optimization for the phase stability problem. AIChE J. 41, 1798-1814.
Michelsen, M.L., 1982a. The isothermal flash problem. Part I. Stability. Fluid Phase Equilib. 9, 1-19.
Michelsen, M.L., 1982b. The isothermal flash problem. Part II. Phase-split calculation. Fluid Phase Equilib. 9, 21-40.
Michelsen, M.L., Mollerup, J., 2018. Thermodynamic Models: Fundamental and Computational Aspects, second ed. Tie-Line Publications.
Mitsos, A., Barton, P.I., 2007. A dual extremum principle in thermodynamics. AIChE J. 53, 2131-2147.

Modell, M., Reid, R.C., 1983. Thermodynamics and Its Applications, Prentice-Hall International Series in the Physical and Chemical Engineering Sciences, second ed. Prentice-Hall, Englewood Cliffs.
Murphy, O.J., Hitchens, G.D., Kaba, L., Verostko, C.E., 1992. Direct electrochemical oxidation of organics for wastewater treatment. Water Res. 26, 443-451.
Nagarajan, N.R., Cullick, A.S., Griewank, A., 1991. New strategy for phase equilibrium and critical point calculations by thermodynamic energy analysis. Part I. Stability analysis and flash. Fluid Phase Equilib. 62, 191-210.

Nichita, D.V., Gomez, S., Luna, E., 2002. Phase stability analysis with cubic equations of state by using a global optimization method. Fluid Phase Equilib. 194, 411-437.
Nikolaidis, I.K., Novak, N., Kontogeorgis, G.M., Economou, I.G., 2022. Rigorous phase equilibrium calculation methods for strong electrolyte solutions: The isothermal flash. Fluid Phase Equilib. 558, 113441.
Novak, N., Kontogeorgis, G., Castier, M., Economou, I., 2021. Modeling of gas solubility in aqueous electrolyte solutions with the eSAFT-VR Mie equation of state. Ind. Eng. Chem. Res. 60, 15327-15342.
Numerical Algorithms Group, 2023. NAG library manual. URL: https://support.nag. com/numeric/nl/nagdoc_latest/, (accessed: 31.01.2024).
Pantoja, C.E., Nariyoshi, Y.N., Seckler, M.M., 2015. Membrane distillation crystallization applied to brine desalination: A hierarchical design procedure. Ind. Eng. Chem. Res. 54, 2776-2793.
Papaioannou, V., Lafitte, T., Avendaño, C., Adjiman, C.S., Jackson, G., Müller, E.A., Galindo, A., 2014. Group contribution methodology based on the statistical associating fluid theory for heteronuclear molecules formed from Mie segments. J. Chem. Phys. 140, 054107.

Patil, K.R., Olivé, F., Coronas, A., 1994. Experimental measurements of vapour pressures of electrolyte solutions by differential static method. J. Chem. Eng. Jpn. 27, 680-681.
Patil, K.R., Tripathi, A.D., Pathak, G., Katti, S.S., 1990. Thermodynamic properties of aqueous electrolyte solutions. 1. Vapor pressure of aqueous solutions of lithium chloride, lithium bromide, and lithium iodide. J. Chem. Eng. Data 35, 166-168.
Pereira, F.E., Jackson, G., Galindo, A., Adjiman, C.S., 2010. A duality-based optimisation approach for the reliable solution of (P, T) phase equilibrium in volume-composition space. Fluid Phase Equilib. 299, 1-23.
Pereira, F.E., Jackson, G., Galindo, A., Adjiman, C.S., 2012. The HELD algorithm for multicomponent, multiphase equilibrium calculations with generic equations of state. Comput. Chem. Eng. 36, 99-118.
Richter, M., Bouché, M., Linder, M., 2016. Heat transformation based on $\mathrm{CaCl}_{2} / \mathrm{H}_{2} \mathrm{O}$ Part A: Closed operation principle. Appl. Therm. Eng. 102, 615-621.
Rodriguez, J., Mac Dowell, N., Llovell, F., Adjiman, C.S., Jackson, G., Galindo, A., 2012. Modelling the fluid phase behaviour of aqueous mixtures of multifunctional alkanolamines and carbon dioxide using transferable parameters with the SAFT-VR approach. Mol. Phys. 110, 1325-1348.
Rozmus, J., de Hemptinne, J.-C., Galindo, A., Dufal, S., Mougin, P., 2013. Modeling of strong electrolytes with ePPC-SAFT up to high temperatures. Ind. Eng. Chem. Res. 52, 9979-9994.
Sassenburg, M., Kelly, M., Subramanian, S., Smith, W.A., Burdyny, T., 2022. Zerogap electrochemical $\mathrm{CO}_{2}$ reduction cells: Challenges and operational strategies for prevention of salt precipitation. ACS Energy Lett. 8, 321-331.
Schreckenberg, J.M.A., Dufal, S., Haslam, A.J., Adjiman, C.S., Jackson, G., Galindo, A., 2014. Modelling of the thermodynamic and solvation properties of electrolyte solutions with the statistical associating fluid theory for potentials of variable range. Mol. Phys. 112, 2339-2364.
Sevov, C.S., Hickey, D.P., Cook, M.E., Robinson, S.G., Barnett, S., Minteer, S.D., Sigman, M.S., Sanford, M.S., 2017. Physical organic approach to persistent, cyclable, low-potential electrolytes for flow battery applications. J. Am. Chem. Soc. 139, 2924-2927.

Shaahmadi, F., Smith, S.A., Schwarz, C.E., Burger, A.J., Cripwell, J.T., 2023. Groupcontribution SAFT equations of state: A review. Fluid Phase Equilib. 565, 113674.

Smith, J.V., Missen, R.W., Smith, W.R., 1993. General optimality criteria for multiphase multireaction chemical equilibrium. AIChE J. 39, 707-710.
Smyth, C.P., Rogers, H.E., 1930. The dielectric polarization of liquids. VIII. Acetic and butyric acids. J. Am. Chem. Soc. 52, 1824-1830.
Takano, K., Gani, R., Ishikawa, T., Kolar, P., 2002. Conceptual design and analysis methodology for crystallization processes with electrolyte systems. Fluid Phase Equilib. 194, 783-803.
Tan, T.C., Aravinth, S., 1999. Liquid-liquid equilibria of water/acetic acid/1-butanol system - Effects of sodium (potassium) chloride and correlations. Fluid Phase Equilib. 163, 243-257.
Tsanas, C., de Hemptinne, J.-C., Mougin, P., 2022. Calculation of phase and chemical equilibrium for multiple ion-containing phases including stability analysis. Chem. Eng. Sci. 248, 117174.
Tsanas, C., Stenby, E.H., Yan, W., 2019. Calculation of multiphase chemical equilibrium in electrolyte solutions with non-stoichiometric methods. Fluid Phase Equilib. 482, 81-98.
Uematsu, M., Frank, E.U., 1980. Static dielectric constant of water and steam. J. Phys. Chem. Ref. Data 9, 1291-1306.
Wagman, D.D., Evans, W.H., Parker, V.B., Schumm, R.H., Halow, I., 1982. The NBS tables of chemical thermodynamic properties. In: Selected Values for Inorganic and C1 and C2 Organic Substances in SI Units. Technical Report, National Standard Reference Data System.
Wakisaka, A., Mochizuki, S., Kobara, H., 2004. Cluster formation of 1-butanol-water mixture leading to phase separation. J. Solut. Chem. 33, 721-732.
Walas, S.M., 1985. Phase Equilibria in Chemical Engineering. Butterworth-Heinemann.
Wang, P., Anderko, A., 2001. Computation of dielectric constants of solvent mixtures and electrolyte solutions. Fluid Phase Equilib. 186, 103-122.
Wang, S., Edwards, I.M., Clarens, A.F., 2013. Wettability phenomena at the $\mathrm{CO}_{2}-$ brine-mineral interface: Implications for geologic carbon sequestration. Environ. Sci. Technol. 47, 234-241.
Wasylkiewicz, S.K., Doherty, M.F., Malone, M.F., 1999. Computing all homogeneous and heterogeneous azeotropes in multicomponent mixtures. Ind. Eng. Chem. Res. 38, 4901-4912.
Xu, G., Haynes, W.D., Stadtherr, M.A., 2005. Reliable phase stability analysis for asymmetric models. Fluid Phase Equilib. 235, 152-165.
Zarembo, V.I., Antonov, N.A., Gilyarov, V.N., Fedorov, M.K., 1976. Activity coefficients KCl in the system $\mathrm{KCl}-\mathrm{H}_{2} \mathrm{O}$ at temperatures from 150 to 350 degrees and at pressures up to $1500 \mathrm{~kg} / \mathrm{cm}^{2}$. Zhurnal Prikladnoi Khimii 46, 1221-1225.
Zemaitis, Jr., J.F., Clark, D.M., Rafal, M., Scrivner, N.C., 2010. Handbook of Aqueous Electrolyte Thermodynamics: Theory \& Application. John Wiley \& Sons.
Zuend, A., Seinfeld, J.H., 2013. A practical method for the calculation of liquidâ€liquid equilibria in multicomponent organicâ€waterâ€electrolyte systems using physicochemical constraints. Fluid Phase Equilib. 337, 201-213.
Zurita, J.L., Gramajo de Doz, M.B., Bonatti, C.M., Sólimo, H.N., 1998. Effect of addition of calcium chloride on the liquid-liquid equilibria of the water + propionic acid + 1-butanol system at 303.15 K. J. Chem. Eng. Data 43, 1039-1042.