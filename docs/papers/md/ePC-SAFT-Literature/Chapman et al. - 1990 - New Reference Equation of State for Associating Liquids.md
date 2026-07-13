\title{
New Reference Equation of State for Associating Liquids
}

\author{
Walter G. Chapman, ${ }^{\dagger, \ddagger, \mathbb{8}}$ Keith E. Gubbins, ${ }^{*, \dagger}$ George Jackson, ${ }^{\dagger, \perp}$ and Maciej Radosz ${ }^{\ddagger}$ \\ School of Chemical Engineering, Cornell University, Ithaca, New York 14853, and Exxon Research and Engineering Company, Annandale, New Jersey 08801
}
Downloaded via BRIGHAM YOUNG UNIV on May 29, 2024 at 20:46:31 (UTC). See https://pubs.acs.org/sharingguidelines for options on how to legitimately share published articles.

\begin{abstract}
An equation of state for associating liquids is presented as a sum of three Helmholtz energy terms: Lennard-Lones (LJ) segment (temperature-dependent hard sphere + dispersion), chain (increment due to chain formation), and association (increment due to association). This equation of state has been developed by extending Wertheim's theory obtained from a resummed cluster expansion. Pure component molecules are characterized by segment diameter, segment-segment interaction energy, for example, Lennard-Jones $\sigma$ and $\epsilon$, and chain length expressed as the number of segments. There are also two association parameters, the association energy and volume, characteristic of each site-site pair. The agreement with molecular simulation data is shown to be excellent at all the stages of development for associating spheres, mixtures of associating spheres, and nonassociating chains. The model has been shown to reproduce experimental phase equilibrium data for a few selected real pure compounds.
\end{abstract}

\section*{1. Introduction}

Molecular association profoundly affects phase behavior and transport properties of fluid mixtures. This is because such associated fluid mixtures are known to contain not only monomeric molecules but also relatively long-lived (typically $1-10^{3} \mathrm{ps}$ ) clusters of like and unlike molecules, for example, hydrogen-bonded and donor-acceptor clusters. Since effective molecular properties of the clusters (size, energy, and shape) are very different from the monomeric molecules, the bulk fluid properties are also very different. For example, the vapor-liquid coexistence curves and critical points of the associated fluids are shifted to higher temperatures. Also, liquid-liquid phase equilibria, crucial to solvent extraction and extractive distillation, strongly depend on the delicate balance of associative interactions between solvent molecules (sol-vent-cosolvent and solvent-antisolvent), between separated molecules, and between solvent and separated molecules. These interactions can affect not only the distribution coefficients, and hence selectivities, but also the type of phase behavior, for example, transition from upper critical solution temperature to lower critical solution temperature behavior. The effects of association on the bulk properties discussed above are important in many fluids containing water, alcohols, carboxylic acids, and other polar solvents. The molecular association also affects phase behavior and rheology of many important complex

\footnotetext{
${ }^{\dagger}$ Cornell University.
${ }^{\ddagger}$ Exxon Research and Engineering Company.
${ }^{1}$ Current address: Shell Research, Houston, TX 77001.
${ }^{+}$Current address: Chemistry Department, University of Sheffield, Sheffield S3 7HF, U.K.
}
and macromolecular fluids, such as associating polymers, water-soluble polymers, asphaltenes, and biomolecular solutions.

As a result, there have been many attempts to model the association effects on fluid phase equilibria. Perhaps the best known concept is the chemical theory of Dolezalek (1908), which postulates the existence of distinct molecular species in solution, which are a result of chemical reactions assumed to be in a state of chemical equilibrium. This concept has been adopted in many approaches that usually utilize the chemical equilibrium constants involving the entropy and enthalpy terms (in effect binary parameters) to allow for temperature dependence; these are reviewed in, for example, Prausnitz et al. (1986). An alternative approach is that of the lattice theories based on modeling the fluid structure as having essentially a solid-like lattice structure. For example, the quasichemical approximation due to Guggenheim (1966), has been used to treat nonrandom mixtures. The most popular activity coefficient models applicable to nonrandom associating solutions, for example, the models of Wilson (1964), Abrams and Prausnitz (1975), and Renon and Prausnitz (1968), are based on these ideas.

There has been substantial progress recently in the molecular theory of associating solutions, which can result in practical models having greatly enhanced predictive power. The essence of this progress is to use statistical mechanical methods, such as perturbation theory, to quantify the relationship between well-defined site-site interactions and the bulk fluid behavior (Cummings and Stell, 1984; Cummings and Blum, 1986; Andersen, 1973, 1974; Wertheim, 1984a,b, 1986a-c; Stell and Zhou, 1989). Especially pertinent is Wertheim's contribution, which provides the basis for our model of associating fluids.

Wertheim derived his theory by expanding the Helmholtz energy in a series of integrals of molecular distribution functions and the association potential. On the basis of physical arguments explained in the next section, Wertheim showed that many integrals in this series must be zero and, hence, a simplified expression for the Helmholtz energy can be obtained. This expression is a result of resummed terms in the expansion series (cluster expansion). Specifically, the Helmholtz energy can be calculated from Wertheim's resummed cluster expansion using perturbation theory.

The key result of Wertheim's theory is a relationship between the residual Helmholtz energy due to association and the monomer density. This monomer density, in turn, is related to a function $\Delta$ characterizing the "association strength". Wertheim's theory has been extended to mixtures of spheres and of chain molecules and is tested against Monte Carlo simulations (Chapman, 1988; Chapman et al., 1988; Jackson et al., 1988).

In this paper we present an equation of state model of associating fluids that is based on the first-order theory of Wertheim. The equation of state itself is in the form of the residual Helmholtz energy, a sum of segment, chain, and association terms discussed in section 3. Sample results of testing prototype versions of the model and of fitting the model to some real compounds are shown in section 4. Other thermodynamic functions, such as the chemical potential, residual energy, compressibility factor, and second virial coefficient, are given in the Appendix. However, we start in section 2 with the definition of our model fluid, its molecular parameters, and approximations used in the theory, and we describe how to quantify concentrations of components, monomers, and clusters. The theoretical approximations arise from the restriction to Wertheim's first-order treatment and can be relaxed by including the second-order Helmholtz energy term. We plan to consider such an extension in a later paper.

The essence of our theory is to use a reference fluid that incorporates both the chain length (molecular shape) and molecular association, in place of the much simpler hard sphere reference fluid used in most existing engineering equations of state. We expect such a reference fluid to capture the major effects of both nonspherical shape and molecular association, and we use Wertheim's theory to predict the Helmholtz energy of this reference fluid. Effects due to other kinds of intermolecular forces (dispersion, induction, etc.) are expected to be weaker and are included through a mean field perturbation term in the usual way. We call this approach, regardless of the type of mean field term used, the Statistical Associating Fluid Theory (SAFT) and have recently given a brief preliminary account of it (Chapman et al., 1989).

\section*{2. Model Fluid and Molecular Parameters}

We start from a mixture of Lennard-Jones (LJ) spheres. We superimpose two kinds of bonds between these spheres, covalent-like bonds to form chains and association bonds to interact specifically. As a result, our model components can approximate a broad range of molecules, from nonassociating near-spherical (for example, methane and neopentane) and nonspherical (chain alkanes and polymers) to associating near-spherical (methanol) and nonspherical (alkanols). We will first discuss associating spheres and associating chains, then define LJ parameters for pure components and mixtures, and define concentration measures.

\subsection*{2.1. Association Energy and Volume Parameters.}

Examples of specific interactions are hydrogen bonding and donor-acceptor, which are of short range and highly

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-02.jpg?height=1989&width=634&top_left_y=130&top_left_x=1209}
\captionsetup{labelformat=empty}
\caption{Figure 1. Equipotential contour map obtained from ab initio molecular orbital calculations for water interacting with (a) IPA, (b) TFIPA, and (c) HFIPA. The orientation of the water molecule, whose center is in the $Y Z$ plane, was optimized to give the lowest energy. Then constant energy contours were drawn with spacings of $2 \mathrm{~kJ} / \mathrm{mol}$. Reprinted with permission from Kinugawa and Nakanishi. Copyright 1988 American Institute of Physics.}
\end{figure}
orientation-dependent site-site interactions. In Figure 1 we illustrate sizes and locations of hydrogen-bonding sites for water interacting with isopropyl alcohol (IPA), 1,1,1trifluoroisopropyl alcohol (TFIPA), and 1,1,1,3,3,3-hexafluoroisopropyl alcohol (HFIPA). The isoenergy contour plots, taken from the molecular orbital calculations of Kinugawa and Nakanishi (1988), show the minimum pair

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-03.jpg?height=553&width=841&top_left_y=148&top_left_x=194}
\captionsetup{labelformat=empty}
\caption{Figure 2. Model of hard spheres with a single associating site $A$ illustrating a simple case of molecular association due to short-distance, highly orientational, site-site attraction. The strength of association is modeled with a square-well potential.}
\end{figure}
interaction energy for a water molecule whose center is on the $y z$ plane, taken to include the C3, O, and H1 (hydroxyl $\mathrm{H})$ atoms. The deep potential wells near the H and O atoms of the hydroxyl group are the hydrogen bonds. The hydrogen-bond energy between the hydroxyl H and water is $-25.28 \mathrm{~kJ} / \mathrm{mol}$ for IPA, $-34.87 \mathrm{~kJ} / \mathrm{mol}$ for TFIPA, and $-36.94 \mathrm{~kJ} / \mathrm{mol}$ for HFIPA (energy increases on fluorination). The hydrogen-bond energy between the hydroxyl O and water is $-22.49 \mathrm{~kJ} / \mathrm{mol}$ for IPA, $-16.97 \mathrm{~kJ} / \mathrm{mol}$ for TFIPA, and $-14.49 \mathrm{~kJ} / \mathrm{mol}$ for HFIPA (energy decreases on fluorination). Key features of these hydrogen bonds are their strength, short range, and high degree of localization. The interaction of the $\mathrm{CH}_{3}$ or $\mathrm{CF}_{3}$ groups with water is much weaker ( -2 to $-6 \mathrm{~kJ} / \mathrm{mol}$ ) and less localized, as seen from the weak minima on the upper left of the plots (Figure 1).

In Figure 2 is shown a simple example of prototype spheres, or spherical segments, with one associating site, A. Such spheres can only form an AA-bonded dimer when both distance and orientation are favorable. The degree of dimerization will depend on the AA bond strength. We quantify the associating bond strength with a square-well potential (whose center is on the A site), which, in turn, is characterized by two parameters. The parameter $\epsilon^{\mathrm{AA}}$ characterizes the association energy (well depth), and the parameter $\kappa{ }^{\text {AA }}$ characterizes the association volume (corresponds to the well width $r^{\mathrm{AA}}$ ).

In general, we do not constrain the number of association sites on a single molecule and label these sites with capital letters, A, B, C, etc. Each association site is assumed to have a different interaction with the various sites on another molecule. To keep track of these interactions, we label them with superscripts. For example, a superscript $\mathrm{A}_{i} \mathrm{~B}_{j}$ means interaction between site A on molecule $i$ and site B on molecule $j$.
2.2. Approximations. The first-order theory allows for chainlike or treelike associated clusters (at least two sites are needed to form clusters of three segments or more), but no ringlike clusters are allowed. In this firstorder theory, we do not specify the angle between bonding sites, which means that the properties of the fluid will be independent of the angle between sites. Also, the activity of a site is independent of bonding at other sites on the same molecule. Therefore, the effects of steric hindrance when two bonding sites are set so close together that they cannot bond simultaneously to two different molecules are ignored (Wertheim, 1986a-c, 1987). We will use this approximation later in this section to estimate the distribution of clusters.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-03.jpg?height=719&width=526&top_left_y=148&top_left_x=1272}
\captionsetup{labelformat=empty}
\caption{Figure 3. Model approximations representing types of steric incompatibility. (a) The repulsive cores of the molecules prevent more than two molecules from bonding at a single site. (b) No site on one molecule can bond simultaneously to two sites on another molecule. (c) Double bonding between molecules is not allowed.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-03.jpg?height=330&width=618&top_left_y=1060&top_left_x=1224}
\captionsetup{labelformat=empty}
\caption{Figure 4. Models of hard sphere (monomer) and chain ( $m$-mer) molecules with two associating sites A and B ; the chain model can represent nonspherical molecules. Note that, in the theory, site locations are not specified.}
\end{figure}

Furthermore, following Wertheim (1984a,b), we impose steric hindrance approximations illustrated in Figure 3. First, when molecules $i$ and $j$ are close enough that site A on molecule $i$ bonds to site B on molecule $j$, then the repulsive cores of molecules $i, j$, and $k$ prevent any site on molecule $k$ from coming close enough to bond to either site A or site B. Second, no site on molecule $i$ can bond simultaneously to two sites on molecule $j$. Third, no double bonding between two molecules is allowed. However, the third restriction can be relaxed (Wertheim, 1986a-c).
2.3. Chain Formation. In contrast to the associated clusters discussed above, multisegmented chain molecules, such as the $m$-mer in Figure 4, are formed by imposing strong, covalent-like bonds on the equisized segments, each of which has one or two bonding sites. For example, to form a chain of $m$ segment diameters in length, we create a fluid made up of $m$ species of LJ spheres. Numbering the species $1,2,3, \ldots, m$, we specify that spheres of type 1 bond only to spheres of type 2, and spheres of type 2 bond only to spheres of types 1 and $3, \ldots$, and spheres of type $m$ bond only to spheres of type $m-1$. Also, it is required that a stoichiometric ratio of spheres is present. As a result, all the spheres will be forced to bond as specified and, thus, create a chain.
2.4. Lennard-Jones Segments. As also shown in Figure 4, each segment is characterized by its diameter, $\sigma$, and each molecule is characterized by its number of segments, $m$. Since $\sigma$ is a temperature-independent sphere diameter, we can relate it, in the spirit of the BarkerHenderson theory (1967), to an effective (temperature-
dependent) hard sphere diameter, $d$

$$
\begin{equation*}
d=\sigma f\left(\frac{k T}{\epsilon}, m\right) \tag{1}
\end{equation*}
$$

where $f(k T / \epsilon, m)$ is a generic function of the reduced temperature and $\epsilon$ is an LJ intermolecular energy. For $f(k T / \epsilon, m)$, we use a function that is similar to that fitted to the Lennard-Jones potential by Cotterman et al. (1986):

$$
\begin{equation*}
f(k T / \epsilon, m)=\frac{1+0.2977 k T / \epsilon}{1+0.33163 k T / \epsilon+f(m)(k T / \epsilon)^{2}} \tag{2}
\end{equation*}
$$

where

$$
\begin{equation*}
f(m)=0.0010477+0.025337 \frac{m-1}{m} \tag{3}
\end{equation*}
$$


The functions of eqs 2 and 3 were arrived at after fitting $d, m$, and $\epsilon$ to saturated liquid densities and vapor pressures, over a temperature range from 10 K above the triple point to 10 K below the critical point, for alkanes up to $n$-octane. We note that for spherical molecules ( $m=1$ ) eq 2 reduces the Cotterman et al. (1986) temperature dependence, and eq 1 becomes the Barker-Henderson temperature dependence of the hard sphere diameter

$$
\begin{equation*}
d=\sigma f\left(\frac{k T}{\epsilon}, m=1\right) \tag{1a}
\end{equation*}
$$

2.5. van der Waals One-Fluid Theory: Conformal Solution of LJ Segments. We have introduced three parameters, the LJ segment parameters $\sigma$ and $\epsilon$ and the number of segments $m$ in a chain, which are required to model a nonassociating pure fluid. In order to model nonassociating mixtures, we must be able to calculate the Helmholtz energy of the fluid mixture of spherical LJ segments that exists before bonding and association take place. In this mixture, the mole fraction of LJ spheres of species $i$ is $y_{i}=X_{i} m_{i} / \sum_{j} X_{j} m_{j}$, where $X_{i}$ is the mole fraction of chain molecules of species $i$ (formed after bonding takes place) having $m_{i}$ segments. For the mixture of LJ segments, we can use a van der Waals one-fluid theory (vdW1), which has been shown to be in good agreement with computer simulation data (Rowlinson and Swinton, 1982) for LJ spheres of similar size. VdW1, which can be derived by using perturbation theory, is a well-established conformal solution theory that defines parameters ( $\sigma_{\mathrm{x}}$ and $\epsilon_{\mathrm{x}}$ ) of a hypothetical PURE fluid x having the same residual properties as the mixture of interest. Hence, for $\sigma_{\mathrm{x}}$ and $\epsilon_{\mathrm{x}}$, equivalent to $\sigma$ and $\epsilon$ for the mixture of interest, we have two mixing rules

$$
\begin{align*}
\sigma_{\mathrm{x}}^{3} & =\frac{\sum_{i} \sum_{j} X_{i} X_{j} m_{i} m_{j} \sigma_{i j}^{3}}{\left(\sum_{i} X_{i} m_{i}\right)^{2}}  \tag{4}\\
\epsilon_{\mathrm{x}} \sigma_{\mathrm{x}}^{3} & =\frac{\sum_{i} \sum_{j} X_{i} X_{j} m_{i} m_{j} \sigma_{i j}^{3} \epsilon_{i j}}{\left(\sum_{i} X_{i} m_{i}\right)^{2}} \tag{5}
\end{align*}
$$

where $X_{i}$ is the mole fraction of component $i$ and, as usual, the unlike-interaction energy parameter $\epsilon_{i j}$ is determined from a modified geometric average

$$
\begin{equation*}
\epsilon_{i j}=\xi_{i j}\left(\epsilon_{i i} \epsilon_{j j}\right)^{1 / 2} \tag{6}
\end{equation*}
$$

and the unlike-interaction size parameter $\sigma_{i j}$ is determined from an arithmetic average

$$
\begin{equation*}
\sigma_{i j}=\left(\sigma_{i i}+\sigma_{j j}\right) / 2 \tag{7}
\end{equation*}
$$


When $\xi_{i j}=1$ in eq 6, eqs 6 and 7 reduce to the LorentzBerthelot rules.

The effective hard sphere diameter of our hypothetical pure fluid is given by

$$
\begin{equation*}
d_{\mathrm{x}}=\sigma_{\mathrm{x}} f\left(\frac{k T}{\epsilon_{\mathrm{x}}}, m_{\mathrm{x}}\right) \tag{8}
\end{equation*}
$$

where $m_{\mathbf{x}}$, the effective chain length of the conformal fluid, can be approximated by

$$
\begin{equation*}
m_{\mathrm{x}}=\sum_{i} X_{i} m_{i} \tag{$\prime$}
\end{equation*}
$$

2.6. How To Derive Parameters. To sum up, for each pure component we need three molecular parameters, $\sigma$, $\epsilon / k$, and $m$, which are the (temperature-independent) segment diameter in angstroms, the LJ interaction energy in kelvins, and the number of segments per chain molecule, respectively. In addition, we need two association parameters, association energy $\epsilon^{\mathrm{A}_{i} \mathrm{~B}_{j}} / k$ in kelvins and volume $\kappa^{\mathrm{A}_{i} \mathrm{~B}_{j}}$ (dimensionless), for each site-site interaction. We note that the superscript $\mathrm{A}_{i} \mathrm{~B}_{j}$ is equivalent to $\mathrm{B}_{j} \mathrm{~A}_{i}$ but not to $\mathrm{A}_{j} \mathrm{~B}_{i}$. We also note that all these parameters are temperature independent.

The usual method for deriving the $\sigma, \epsilon$, and $m$ values is to fit vapor pressure and density data for pure components. The association parameters $\epsilon^{\mathrm{A}_{i} \mathrm{~B}_{j}}$ and $\kappa^{\mathrm{A}_{i} \mathrm{~B}_{j}}$ can be fitted to bulk phase equilibrium data. However, a preferred future way can be used to derive these parameters from spectroscopic data on associated solutions first and then derive $\sigma, \epsilon$, the $m$ from the bulk properties.
2.7. Mole Fractions of Components, Monomers, and Clusters. Since our model mixtures contain not only monomer species but also associated clusters, we need to define the mole fractions ( $X$ ) for the total components and their monomers. The mole fraction of all the molecules of component $i$ is $X_{i}$. The mole fraction of (in general, chain) molecules $i$ that are NOT bonded at site A is $X^{\mathrm{A}_{i}}$, and hence $1-X^{\mathrm{A}_{i}}$ is the mole fraction of molecules $i$ that are bonded at site A . This definition applies to both pure self-associated compounds and to mixture components and is given in terms of mole numbers in the Nomenclature section. The mole fraction of molecules $i$ that are NOT bonded at any site, that is, the mole fraction of monomers $i$, is $X_{i}$ (monomer) $=\Pi_{\mathrm{A}_{i}} X^{\mathrm{A}_{i}}$, and hence $1-X_{i}$ (monomer) is the mole fraction of molecules $i$ that are bonded.
2.8. Distribution of Clusters. The fraction of clusters of a given size can be estimated by using general statistical arguments (Jackson et al., 1988; Flory, 1953). As an example, we shall consider a pure component system composed of molecules having two sites, A and B , where only AB bonding and only chain clusters are allowed. The fractions of each chain length present (dimers, trimers, etc.) are functions of $X^{\mathrm{A}}$ and $X^{\mathrm{B}}$ (the fractions of molecules not bonded at sites A and B , respectively), which, in turn, are calculated from the equation of state described in section 3. Assuming that the activity of a site is independent of bonding at the other sites on the same molecule, the fraction of molecules that are present as monomers is $X^{\mathrm{A}} X^{\mathrm{B}}$, or $\left(X^{\mathrm{A}}\right)^{2}$ if $X^{\mathrm{A}}=X^{\mathrm{B}}$, which is the case in our example. Similarly, the fraction of molecules that are present as dimers is given by $2\left(X^{\mathrm{A}}\right)^{2}\left(1-X^{\mathrm{A}}\right)$. The general result for the fraction of molecules present as $m$-mers is

$$
\begin{equation*}
X(m \text {-mer })=m\left(X^{\mathrm{A}}\right)^{2}\left(1-X^{\mathrm{A}}\right)^{m-1} \tag{9}
\end{equation*}
$$

and the average chain length is given by

$$
\begin{equation*}
m_{\mathrm{ave}}=1 / X^{\mathrm{A}} \tag{10}
\end{equation*}
$$


Equation 9 expresses the "most probable distribution" of Flory (1953) that is in agreement with experimental results for polymer polydispersity.

\section*{3. Equation of State}

The equation of state is defined in this section in terms of the residual Helmholtz energy $a^{\text {res }}$ per mole, defined as $a^{\text {res }}(T, V, N)=a(T, V, N)-a^{\text {ideal }}(T, V, N)$, where $a(T, V, N)$ and $a^{\text {ideal }}(T, V, N)$ are the total Helmholtz energy per mole and the ideal gas Helmholtz energy per mole at the same temperature and density. The residual Helmholtz energy is a sum of three terms representing contributions from different intermolecular forces. The first term, $a^{\text {seg }}$, accounts for that part of $a^{\text {res }}$ that represents segment-segment interactions, i.e., Lennard-Jones (LJ) interactions. The second term, $a^{\text {chain }}$, is due to the presence of covalent chain-forming bonds among the LJ segments. The third term, $a^{\text {assoc }}$, accounts for the increment of $a^{\text {res }}$ due to the presence of site-site specific interactions among the segments, for example, hydrogen-bonding interactions. The general expression for the Helmholtz energy is given as

$$
\begin{equation*}
a^{\mathrm{res}}=a^{\mathrm{seg}}+a^{\mathrm{chain}}+a^{\mathrm{ass} \circ \mathrm{c}} \tag{11}
\end{equation*}
$$

which is short for

$$
\begin{aligned}
& a^{\text {res }}=a^{\text {seg }}(m \rho, T ; \sigma, \epsilon)+ \\
& \quad a^{\text {chain }}(\rho ; d, m)+\operatorname{mm} a^{\text {assoc }}\left(\rho, T ; d, \epsilon^{\mathrm{AB}}, \kappa^{\mathrm{AB}}\right)
\end{aligned}
$$

where $\rho$ is the molar density of molecules; we note that in the first term on the right side of this equation $a^{\text {seg }}$ is a function of the product $m \rho$.
3.1. Association Term for Pure Components. We start our analysis from the association term, first for pure self-associating compounds and second for mixtures of associating components. The Helmholtz energy change due to association is calculated for pure components from

$$
\begin{equation*}
\frac{a^{\mathrm{assoc}}}{R T}=\sum_{\mathrm{A}}\left[\ln X^{\mathrm{A}}-\frac{X^{\mathrm{A}}}{2}\right]+\frac{1}{2} M \quad \text { (general) } \tag{12}
\end{equation*}
$$

where $M$ is the number of association sites on each molecule, $X^{\mathrm{A}}$ is the mole fraction of molecules not bonded at site A , and $\sum_{\mathrm{A}}$ represents a sum over all associating sites on the molecule. Examples for molecules with two attractive sites and one attractive site are given as follows:

$$
\begin{gather*}
\frac{a^{\mathrm{assoc}}}{R T}=\ln X^{\mathrm{A}}-\frac{X^{\mathrm{A}}}{2}+\ln X^{\mathrm{B}}-\frac{X^{\mathrm{B}}}{2}+1 \quad(2 \text { sites })  \tag{13}\\
\frac{a^{\mathrm{ass} \mathrm{c}}}{R T}=\ln X^{\mathrm{A}}-\frac{X^{\mathrm{A}}}{2}+\frac{1}{2} \quad(1 \text { site }) \tag{14}
\end{gather*}
$$


The mole fraction of molecules not bonded at site A can be determined as follows

$$
\begin{array}{r}
X^{\mathrm{A}}=\left[1+N_{\mathrm{Av}} \sum_{\mathrm{B}} \rho X^{\mathrm{B}} \Delta^{\mathrm{AB}}\right]^{-1}(\text { summation over } \mathrm{ALL} \\
\text { sites: } \mathrm{A}, \mathrm{~B}, \mathrm{C}, \ldots) \tag{15}
\end{array}
$$

where $N_{\mathrm{Av}}$ is Avogadro's number and $\rho$ is the molar density of molecules. $\Delta^{\mathrm{AB}}$ in eq 15 is the "association strength" defined as

$$
\begin{equation*}
\Delta^{\mathrm{AB}}=4 \pi F^{\mathrm{AB}} \int_{d}^{r_{\mathrm{c}}} r^{2} \Omega(r) g(r)^{\operatorname{seg}} \mathrm{d} r \tag{16}
\end{equation*}
$$

where $4 \pi r^{2} \Omega(r) \mathrm{d} r$ is the bonding-site-overlap volume element (bonding is assumed to occur between hard sphere contact and $r_{\mathrm{c}}$ ) and $F^{\mathrm{AB}}$ is given by

$$
\begin{equation*}
F^{\mathrm{AB}}=\exp \left(\epsilon^{\mathrm{AB}} / k T\right)-1 \tag{17}
\end{equation*}
$$


The integral in eq 16 can be approximated, as explained by Chapman (1988) and Chapman et al. (1988), as follows

$$
\begin{equation*}
\Delta^{\mathrm{AB}}=d^{3} g(d)^{\operatorname{seg}_{\kappa} \mathrm{AB}}\left[\exp \left(\epsilon^{\mathrm{AB}} / k T\right)-1\right] \tag{18}
\end{equation*}
$$

which is our key property characterizing the association
bonds. The association strength, $\Delta^{\mathrm{AB}}$, given by eq 18 depends on two segment properties, the segment diameter, $d$, and the segment radial distribution function, $g(d)^{\text {seg }}$. Since we approximate our segments as hard spheres, we approximate $g(d)^{\text {seg }}$ as the hard sphere radial distribution function (Carnahan and Starling, 1969):

$$
\begin{equation*}
g(d)^{\mathrm{seg}} \approx g(d)^{\mathrm{hs}}=\frac{2-\eta}{2(1-\eta)^{3}} \tag{19}
\end{equation*}
$$

where $\eta$ is the reduced density defined as

$$
\begin{equation*}
\eta=\frac{\pi N_{\mathrm{Av}}}{6} \rho d^{3} m \tag{20}
\end{equation*}
$$

where $\rho$ is the molar density of molecules.
The association strength given by eq 18 also depends on two parameters characterizing the association energy and volume discussed in section 2. We note that the bonding volume $\kappa^{\mathrm{AB}}$ used here differs from $K^{\mathrm{AB}}$ used by Jackson et al. (1988) by a factor of ( $4 \pi / d^{3}$ ). The only density dependence in $\Delta^{\mathrm{AB}}$ is given by $g(d)^{\text {seg }}$, and the only explicit temperature dependence is given by the $\epsilon^{\mathrm{AB}} / k T$, in eq 18. However, we should also note the implicit temperature dependence of $d$, as discussed in section 2.
3.2. Association Term for Mixtures. Extension to multicomponent mixtures is straightforward. The Helmholtz energy of association is an average that is linear with respect to mole fractions

$$
\begin{equation*}
\frac{a^{\mathrm{assoc}}}{R T}=\sum_{i} X_{i}\left[\sum_{\mathrm{A}_{i}}\left[\ln X^{\mathrm{A}_{i}}-\frac{X^{\mathrm{A}_{i}}}{2}\right]+\frac{1}{2} M_{i}\right] \tag{21}
\end{equation*}
$$

where $X^{\mathrm{A}_{i}}$, the mole fraction of molecules $i$ not bonded at site A , in mixture with other components, is given by
$X^{\mathrm{A}_{i}}=\left[1+N_{\mathrm{Av}} \sum_{j} \sum_{\mathrm{B}_{j}} \rho_{j} X^{\mathrm{B}_{j}} \Delta^{\mathrm{A}_{i} \mathrm{~B}_{j}}\right]^{-1} \quad\left(\sum_{\mathrm{B}_{j}}\right.$ over ALL sites on molecule $j, \mathrm{~A}_{j}, \mathrm{~B}_{j}, \mathrm{C}_{j}, \ldots ; \sum_{j}$ over all components)

As we can see, $X^{A_{i}}$ depends on the molar density

$$
\begin{equation*}
\rho_{j}=X_{j} \rho_{\text {mixture }} \tag{23}
\end{equation*}
$$

and on the association strength

$$
\begin{equation*}
\Delta^{\mathrm{A}_{i} \mathrm{~B}_{j}}=d_{i j}{ }^{3} g_{i j}\left(d_{i j}\right)^{\operatorname{seg}_{K} \mathrm{~A}_{\mathrm{i}} \mathrm{~B}_{i}}\left[\exp \left(\epsilon^{\mathrm{A}_{\mathrm{i}} \mathrm{~B}_{j}} / k T\right)-1\right] \tag{24}
\end{equation*}
$$

where $d_{i j}=\left(d_{i i}+d_{j j}\right) / 2$. Similarly to eqs 18 and 19 for the pure component case, we approximate the segment radial distribution function in eq 24 with the expressions derived for mixtures of hard spheres (Reed and Gubbins, 1973)

$$
\begin{align*}
& g_{i j}\left(d_{i j}\right)^{\text {seg }} \approx g_{i j}\left(d_{i j}\right)^{\text {hs }}= \\
& \quad \frac{1}{1-\zeta_{3}}+\frac{3 d_{i i} d_{j j}}{d_{i i}+d_{j j}} \frac{\zeta_{2}}{\left(1-\zeta_{3}\right)^{2}}+2\left[\frac{d_{i i} d_{j j}}{d_{i i}+d_{j j}}\right]^{2} \frac{\zeta_{2}{ }^{2}}{\left(1-\zeta_{3}\right)^{3}} \tag{25}
\end{align*}
$$


Equation 25 for the like segments becomes

$$
\begin{align*}
g_{i i}\left(d_{i i}\right)^{\text {seg }} \approx g_{i i}\left(d_{i i}\right)^{\text {hs }}= & \\
& \frac{1}{1-\zeta_{3}}+\frac{3 d_{i i}}{2} \frac{\zeta_{2}}{\left(1-\zeta_{3}\right)^{2}}+2\left[\frac{d_{i i}}{2}\right]^{2} \frac{\zeta_{2}^{2}}{\left(1-\zeta_{3}\right)^{3}} \tag{26}
\end{align*}
$$


The hard segment distribution function in eqs 25 and 26 depends on the effective sphere diameter and on a function of density $\zeta_{k=0,1,2,3}$, which is defined as follows:

$$
\begin{equation*}
\zeta_{k}=\frac{\pi N_{\mathrm{Av}}}{6} \rho \sum_{i} X_{i} m_{i} d_{i i}^{k} \tag{27}
\end{equation*}
$$


We note that $\zeta_{3}$, but not $\zeta_{0}, \zeta_{1}$, and $\zeta_{2}$, is equivalent to the segment packing fraction.

The increment of the Helmholtz energy due to association can be determined from eqs $12-19$ for pure self-associating components and from eqs 21-27 for associating mixtures. The only inputs needed, in addition to mixture density and temperature, are the molecular parameters $d$ and $m$ and the association parameters $\epsilon^{\mathrm{AB}}$ and $\kappa^{\mathrm{AB}}$ for all site-site pairs.
3.3. Chain Term. The increment of the Helmholtz energy due to bonding, on the other hand, can be determined from

$$
\begin{equation*}
\frac{a^{\text {chain }}}{R T}=\sum_{i} X_{i}\left(1-m_{i}\right) \ln \left(g_{i i}\left(d_{i i}\right)^{\text {hs }}\right) \tag{28}
\end{equation*}
$$

where $g_{i i}$ is the hard sphere pair correlation function for the interaction of two spheres $i$ in a mixture of spheres, evaluated at the hard sphere contact, eq 26. Equation 28 is derived based on the associating fluid theory where the association bonds are replaced by covalent, chain-forming bonds, as explained in section 2.3, based on Chapman (1988) and Chapman et al. (1988).
3.4. LJ Segment Term. Finally, the segment Helmholtz energy, per mole of molecules, can be calculated from

$$
\begin{equation*}
a^{\operatorname{seg}}=a_{0}{ }^{\operatorname{seg}} \sum_{i} X_{i} m_{i} \tag{29}
\end{equation*}
$$

where $a_{0}{ }^{\text {seg }}$ is defined as the residual Helmholtz energy of nonassociated spherical segments. The $\sum_{i} X_{i} m_{i}$ term in eq 29 is a ratio of the number of segments to the number of molecules in the fluid. Let's assume that our segments are LJ spheres and allow $a_{0}^{\text {seg }}$ to be composed of two parts corresponding to the hard sphere (reference) and dispersion (perturbation) parts of the LJ intermolecular potential as follows
$a_{\mathrm{o}}{ }^{\text {seg }}=a_{0}{ }^{\text {hs }}+a_{\mathrm{o}}{ }^{\text {disp }}$ (reference + perturbation)

As usual, the hard sphere term for pure components and for mixtures can be calculated as proposed by Carnahan and Starling (1969)

$$
\begin{equation*}
\frac{a_{\mathrm{o}}^{\mathrm{hs}}}{R T}=\frac{4 \eta-3 \eta^{2}}{(1-\eta)^{2}} \tag{31}
\end{equation*}
$$

where $\eta$ is a segment packing fraction (reduced density) defined as follows

$$
\begin{gather*}
\eta=\frac{\pi N_{\mathrm{Av}}}{6} \rho d^{3} m \quad \text { (pure components) }  \tag{32}\\
\eta=\frac{\pi N_{\mathrm{Av}}}{6} \rho d^{3} \sum_{i} X_{i} m_{i} \text { (mixtures) } \tag{33}
\end{gather*}
$$


In eq 33 , we have assumed the vdW1 mixing rules, with $d$ given by $d_{\mathbf{x}}$ in eq 8 .

The dispersion term in eq 30, for pure components and mixtures, can be determined as a correlation of molecular simulation data for LJ fluids. One example of an expression for $a_{0}{ }^{\text {disp }}$ is given by eq 34, determined by Cotterman et al. (1986)

$$
\begin{equation*}
a_{\mathrm{o}}{ }^{\text {disp }}=\frac{\epsilon R}{k}\left(a_{\mathrm{o} 1}{ }^{\text {disp }}+\frac{a_{\mathrm{o} 2}{ }^{\text {disp }}}{T_{\mathrm{R}}}\right) \tag{34}
\end{equation*}
$$

where

$$
\begin{align*}
a_{\mathrm{o} 1}{ }^{\text {disp }}= & \rho_{\mathrm{R}}\left[-8.5959-4.5424 \rho_{\mathrm{R}}-2.1268 \rho_{\mathrm{R}}{ }^{2}+10.285 \rho_{\mathrm{R}}{ }^{3}\right]  \tag{35}\\
& (35) \\
a_{\mathrm{o} 2}{ }^{\text {disp }}= & \rho_{\mathrm{R}}[-1.9075+  \tag{36}\\
\left.9.9724 \rho_{\mathrm{R}}-22.216 \rho_{\mathrm{R}}{ }^{2}+15.904 \rho_{\mathrm{R}}{ }^{3}\right] & (36)
\end{align*}
$$


\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-06.jpg?height=782&width=656&top_left_y=139&top_left_x=1206}
\captionsetup{labelformat=empty}
\caption{Figure 5. Compressibility factor $Z=P /(\rho R T)$ for a hard sphere system with one attractive site as a function of reduced density $(\eta)$. The results of Monte Carlo simulations are represented by the circles; the solid curve represents theoretical predictions obtained from numerical integration, which are essentially the same as those obtained from the approximated model, for $\epsilon^{\mathrm{AA}} / k=7 T, \kappa^{\mathrm{AA}}=1.866 \times 10^{-3}$ (modified from Jackson et al. (1988)).}
\end{figure}
where $T_{\mathrm{R}}=k T / \epsilon$, a reduced temperature, and $\rho_{\mathrm{R}}=[6 /$ ( $2^{0.5} \pi$ ) $] \eta$, reduced density.

An alternative approach is to use an argon equation of state for the segment term $a_{0}{ }^{\text {seg }}$ in eq 29. For example, we used the argon equation of state of Twu et al. (1980) to obtain results for real compounds presented in section 4.

In summary, this section provides a complete definition (from molecular parameters to final equations) of the SAFT equation of state in the form of the residual Helmholtz energy for pure components and mixtures. Other thermodynamic properties needed in phase equilibrium calculations, such as the chemical potential, fugacity coefficient, compressibility factor, and second virial coefficient, are given in the Appendix in a way that is consistent with the terms introduced in this section.

\section*{4. Results}

The equation of state model described in the previous section, an extension of Wertheim's theory, is a result of a systematic development, from simple associating spheres and nonassociating chains, to associating mixtures of chains. At the early stages of this development, the prototype versions of the model were carefully verified against molecular simulation data. Since detailed comparisons have been reported elsewhere (Chapman, 1988; Chapman et al., 1986, 1987, 1988; Jackson et al., 1988; Joslin et al., 1987), only sample results are shown here.

The initial version of the theory, for the associating pure spheres, was found to be in excellent agreement with the Monte Carlo simulations of hard-core fluids (Joslin et al., 1987; Chapman, 1988; Jackson et al., 1988). This agreement is illustrated for the compressibility factor of a hard sphere fluid with single sites in Figure 5. Similar agreement was obtained for two-site systems and for other properties, such as the configurational energy and the fraction of monomers.

The theory has also been verified to be accurate for mixtures of associating spheres. For example, Figure 6 shows good agreement for the excess enthalpy calculated from the theory and that determined from the Monte

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-07.jpg?height=614&width=799&top_left_y=130&top_left_x=213}
\captionsetup{labelformat=empty}
\caption{Figure 6. Excess enthalpy ( $H^{\mathrm{E}} / R T$ ) from Monte Carlo simulations (circles) and from theory (solid curve), for a mixture of spheres 1 and 2 (modified from Joslin et al. (1987)).}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-07.jpg?height=621&width=592&top_left_y=874&top_left_x=315}
\captionsetup{labelformat=empty}
\caption{Figure 7. Compressibility factor from Monte Carlo simulations of Dickman and Hall (1988) (points) and from theory (solid curves), for varying chain lengths of $2,4,8$, and 16 as a function of reduced density, $\eta$, as given by eq 20 .}
\end{figure}

Carlo simulations for a binary mixture of associating spheres (Joslin et al., 1987). The initial simplified extension of the associating fluid theory to chain molecules has also been tested against the computer simulation results of Dickman and Hall (1988) for dimers, tetramers, octamers, and hexadecamers. The agreement shown in Figure 7 is believed to be satisfactory for our equation of state model.

The intermediate versions of the model, using a mean field approximation for the $a^{\text {disp }}$ term, have been used to predict qualitative effects of the model parameters, such as association energy and chain length, on various fluid properties (Jackson et al., 1988; Chapman et al., 1988). Only a few representative examples are shown here for the reduced vapor pressure as a function of temperature. In an example calculated for pure spheres with one association site, Figure 8, the reduced critical temperature increases with the increasing interaction energy. This is a result of increasing degree of association from the limiting case of pure monomers (highest pressure, 0 in Figure 8) to the limiting case of pure dimers (low-pressure limit, $\infty$ in Figure 8).

An example calculated for associating and nonassociating chains is shown in Figure 9. The reduced vapor pressure decreases with increasing chain length, from 1 to 8, for nonassociating chains. The reduced vapor pressure also decreases in going from a nonassociating to an asso-

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-07.jpg?height=523&width=743&top_left_y=130&top_left_x=1161}
\captionsetup{labelformat=empty}
\caption{Figure 8. Vapor pressure curves and critical locus for spheres with one attractive site and different association energies, $\epsilon^{\text {AA }} / \epsilon^{\text {mean }}$ field , for $\kappa^{\mathrm{AA}}=5.559 \times 10^{-4}$. The 0 curve corresponds to pure spheres (no association) and the $\infty$ curve corresponds to pure dimers (full association). Reduced pressure is $P \pi d^{3} / 6 \epsilon^{\text {mean field }}$; reduced temperature is $k T / \epsilon^{\text {mean field }}$.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-07.jpg?height=532&width=766&top_left_y=880&top_left_x=1159}
\captionsetup{labelformat=empty}
\caption{Figure 9. Vapor pressure curves and critical locus for nonassociating chains composed of $1,2,4$, and 8 segments, and for a 2 -segment associating chain with two attractive sites (2'). Reduced pressure is $P \pi d^{3} / 6 \epsilon^{\text {mean }}$ field ; reduced temperature is $k T / \epsilon^{\text {mean field }}$ (modified from Chapman et al. (1988)).}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-07.jpg?height=534&width=760&top_left_y=1618&top_left_x=1157}
\captionsetup{labelformat=empty}
\caption{Figure 10. Vapor pressure curves and critical locus for disphere chains ( $m=2$ ) with one attractive site and different association energies $\epsilon^{\mathrm{AA}} / \epsilon^{\text {mean field }}=0,1.5,2,2.5, \infty$. The $\epsilon^{\mathrm{AA}}=0$ curve corresponds to pure dimers (no association) and the $\infty$ curve corresonds to pure tetramers (full association). Reduced pressure is $P \pi d^{3} / 6 \epsilon^{\text {mean }}$ field ; reduced temperature is $k T / \epsilon^{\text {mean field }}$ (modified from Chapman et al. (1988)).}
\end{figure}
ciating chain at the same chain length, for example, from a nonassociating dimer (2 in Figure 9) to an associating dimer (2'). In a final example, the reduced vapor pressure for a disphere chain with one association site is shown as a function of reduced temperature for different values of the association energy ( 0 for pure dimer, $\infty$ for pure tet-

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-08.jpg?height=464&width=673&top_left_y=141&top_left_x=287}
\captionsetup{labelformat=empty}
\caption{Figure 11. Segment diameter $\sigma$ correlates with a function of chain length $(m-1) / m$ for $n$-alkanes, where $m=$ carbon number.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-08.jpg?height=473&width=697&top_left_y=700&top_left_x=274}
\captionsetup{labelformat=empty}
\caption{Figure 12. $f(m)$ function used in the temperature dependence of the segment diameter (eq 3) correlates with a function of chain length $(m-1) / m$ for $n$-alkanes, where $m=$ carbon number.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-08.jpg?height=1191&width=832&top_left_y=1278&top_left_x=191}
\captionsetup{labelformat=empty}
\caption{Figure 13. Propane vapor pressure and liquid density, experimental (squares (Physical Sciences Data, 1986)) and predicted (solid curves).}
\end{figure}
ramer) in Figure 10. In summary, the main effect of the association energy is to extend the range of vapor-liquid

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table I. SAFT Parameters for Hydrocarbons and Associating Compounds ${ }^{\text {a }}$}
\begin{tabular}{|l|l|l|l|l|l|}
\hline compd & $\sigma$ & $\epsilon / k$ & $m$ & $\epsilon^{\mathrm{OH}} / k$ & $\kappa^{\mathrm{OH}}$ \\
\hline methane & 3.7390 & 152.2 & 1 & & \\
\hline ethane & 3.2918 & 158.3 & 2 & & \\
\hline propane & 3.1514 & 152.3 & 3 & & \\
\hline $n$-butane & 3.0775 & 150.6 & 4 & & \\
\hline $n$-octane & 2.9766 & 148.1 & 8 & & \\
\hline benzene & 3.0190 & 193.5 & 4.25 & & \\
\hline methanol & 3.203 & 163.25 & 1.6 & 2964 & 0.053 \\
\hline acetic acid & 3.360 & 224.0 & 2.0 & 7200 & 0.00053 \\
\hline
\end{tabular}
\end{table}
${ }^{a} \sigma$ is in angstrom, $\epsilon / k$ is in kelvin, $\epsilon^{\mathrm{OH}} / k$ is in kelvin, $\kappa^{\mathrm{OH}}$ is dimensionless. All the data presented were obtained by using an argon equation of state (Twu et al., 1980) for the segment term ( $a_{0}{ }^{\text {seg }}$ in eq 29 ).

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-08.jpg?height=1073&width=745&top_left_y=683&top_left_x=1157}
\captionsetup{labelformat=empty}
\caption{Figure 14. n-Butane vapor pressure and liquid density, experimental (squares (Physical Sciences Data, 1986)) and predicted (solid curves).}
\end{figure}
coexistence to higher reduced temperatures and to increase the reduced critical temperature. However, the chain length effect is also important and, in fact, dominates the effect of association for the longer chains.

Once the key $a^{\text {assoc }}$ and $a^{\text {chain }}$ terms have been established and tested, as discussed above, the total equation of state model (11) was fitted to a few selected real compounds. The fitted values of $\sigma, \epsilon$, and $m$ for some $n$-alkanes and benzene are listed in Table I. For the alkanes, $m$ was set equal to the carbon number and $\sigma$ and $\epsilon$ were then regressed from vapor pressure and saturated liquid density data. We note that $\sigma$ is decreasing with increasing chain length as shown in Figure 11. This is a result of setting $m$ equal to the carbon number for the $n$-alkanes, which is our preliminary approximation. This approximation will be refined in the future. The function $f(m)$ used in eq 2, which gives the temperature dependence of $d$, is shown in Figure 12 for real alkanes. Representative vapor pressure and saturated liquid density results for propane, $n$-butane, and $n$-octane are shown in Figures 13-15. The fitted values of the equation of state parameters for two self-

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-09.jpg?height=1067&width=755&top_left_y=130&top_left_x=239}
\captionsetup{labelformat=empty}
\caption{Figure 15. $n$-Octane vapor pressure and liquid density, experimental (squares (Physical Sciences Data, 1986)) and predicted (solid curves).}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-09.jpg?height=1098&width=595&top_left_y=1315&top_left_x=317}
\captionsetup{labelformat=empty}
\caption{Figure 16. Acetic acid vapor pressure and liquid density, experimental (points (Physical Sciences Data, 1986)) and predicted (solid curves).}
\end{figure}
associating compounds, methanol and acetic acid, are listed in Table I. The parameters $\epsilon^{\mathrm{OH}}$ and $\kappa^{\mathrm{OH}}$ were regressed by minimizing the temperature dependence of $\sigma$ and $\epsilon$,

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-09.jpg?height=1129&width=584&top_left_y=126&top_left_x=1239}
\captionsetup{labelformat=empty}
\caption{Figure 17. Methanol vapor pressure and liquid density, experimental (points (Physical Sciences Data, 1986)) and predicted (solid curves).}
\end{figure}
which were fit to vapor pressures and saturated liquid densities at a number of temperatures between the triple point and the critical point of the fluid. Representative vapor pressure and saturated liquid density results for these compounds are shown in Figures 16 and 17.

In addition to the bulk phase equilibrium properties, the equation of state can be used to determine the degree of association. For example, the temperature dependence of the mole fraction of monomers is shown in Figure 18 for both vapor and liquid phases for the two self-associating compounds discussed above.

\section*{5. Conclusions}

An equation of state model has been developed for predicting phase equilibria, based on the Statistical Associating Fluid Theory. The agreement with molecular simulation data has been found to be excellent, at all the stages of model development, for associating spheres, mixtures of associating spheres, and nonassociating chains up to $m=8$. The model has been shown to reproduce experimental phase equilibrium data for a few selected real pure compounds. Because it has a sound basis in statistical thermodynamics, the equation of state offers greater predictive capabilities than previous empirical equations. In particular, mixing rules are not required when treating mixtures (they are "built in" by the theory), and the parameters can be related directly to details of the potential model (segment size, chain length, strength, and range of the hydrogen bond). The goal of future work will be to develop methodology for deriving the equation of state parameters, especially the association parameters, for pure components and mixtures.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/d2175b9c-6e30-4209-a123-4d22ecc40f6a-10.jpg?height=1161&width=570&top_left_y=139&top_left_x=324}
\captionsetup{labelformat=empty}
\caption{Figure 18. Temperature dependence of the monomer mole fraction in vapor and liquid phases for acetic acid and methanol; all curves predicted by the model.}
\end{figure}

\section*{Acknowledgment}

Partial support of this work by a grant from the Department of Energy is gratefully acknowledged.

\section*{Nomenclature}
$a$ = molar Helmholtz energy (total, res, seg, bond, assoc, etc.), per mole of molecules
$a_{0}=$ segment molar Helmholtz energy (seg), per mole of segments
$k=$ Boltzmann's constant $\approx 1.381 \times 10^{-23} \mathrm{~J} / \mathrm{K}$
$m_{i}=$ effective number of segments within molecule $i$ (chain length)
$M_{i}=$ number of association sites on molecule $i$
molar = molar with respect to molecules
$n_{i}=$ number of molecules of component $i$
$N=$ total number of molecules
$N_{\text {Av }}=$ Avogadro's number $\approx 6.02 \times 10^{23}$ molecules $/ \mathrm{mol}$
$P=$ pressure
$R=$ gas constant
segment molar $=$ molar with respect to segments
segment ratio $=\sum_{i} X_{i} m_{i}$, ratio of the number of segments to the number of molecules in the fluid
$T=$ temperature, K
$V=$ total volume
$v=$ molar volume
$X=$ mole fraction
$X_{i}=n_{i} / N$, mole fraction of component $i$
$X_{i}($ monomer $)=n_{i}($ monomer $) / n_{i}=\prod_{\mathrm{A}_{i}} X^{\mathrm{A}_{i}}$, mole fraction of component i not bonded at any site
$X^{\mathrm{A}_{\mathrm{i}}}=n^{\mathrm{A}_{\mathrm{i}}} / n_{i}$, mole fraction of component $i$ not bonded at site A; for 1 attraction site this is the fraction of monomers
$Z=P v /(R T)$, compressibility factor
$\kappa^{\mathrm{A}_{1} \mathrm{~B}_{j}}=$ volume of interaction between site A on molecule $i$ and site B on molecule $j$, dimensionless
$\Delta^{\mathrm{A}_{i} \mathrm{~B}_{j}}=$ "strength of interaction" between site A on molecule $i$ and site B on molecule $j, \AA^{3}$
$\epsilon_{i j}=$ dispersion energy of interaction between segments of types $i$ and $j$, for example, Lennard-Jones, per segment (used to determine $a_{0}{ }^{\text {seg }}$ which is per mole of segments, not molecules), J
$\epsilon^{\mathrm{A}_{i} \mathrm{~B}_{j}}=$ association energy of interaction between site A on molecule $i$ and site B on molecule $j$, per molecule, J
$\xi_{i j}=$ combining rule parameter in eq 6
$\zeta_{k}=\left(\pi N_{\mathrm{Av}} / 6\right) \rho \sum_{i} X_{i} m_{i} d_{i i}{ }^{k}$
$\eta_{\mathrm{o}}=(\pi / 6) \rho_{\mathrm{n}} m d^{3}=\left(\pi N_{\mathrm{Av}} / 6\right) \rho m d^{3}$, pure component reduced density, same for segments and molecules
$\eta=\left(\pi N_{\mathrm{Av}} / 6\right) \rho d^{3} \sum_{i} X_{i} m_{i}$, mixture reduced density, same for segments and molecules
$\mu=$ chemical potential (res, seg, bond, assoc, etc.)
$\rho=\rho_{\mathrm{n}} / N_{\mathrm{Av}}$, molar density, $\mathrm{mol} / \AA^{3}$
$\rho_{i}=X_{i} \rho$, molar density of component i , $\mathrm{mol} / \AA^{3}$
$\rho_{\mathrm{n}}=$ number density (number of molecules in unit volume), $\AA^{-3}$
$\rho_{\mathrm{R}}=6 \eta /\left(2^{0.5} \pi\right)$, reduced density, used in eq 34-36
$d=$ temperature-dependent segment diameter $\left((\pi / 6) d^{3}\right.$ is segment volume), Å
$\sigma=$ Lennard-Jones segment diameter (temperature independent), Å
$\sum_{i}=$ summation over all the components
$\sum_{\mathrm{A}_{i}}=$ summation over all the sites (starting with A ) on molecule $i$
$\phi=$ fugacity coefficient

\section*{Subscripts}
no subscript means "for TOTAL fluid", either pure component or mixture
$i, j, k, l=$ for component $i, j, k, l$
$\mathrm{A}_{i}, \mathrm{~B}_{i}, \mathrm{C}_{i}$, etc. = for site $\mathrm{A}, \mathrm{B}, \mathrm{C}$, etc., on molecule $i$
$\mathrm{o}=$ per mole of segments, not molecules
$\mathrm{x}=$ for conformal fluid, equivalent to the mixture of interest
Superscripts
res $=$ residual
seg $=$ segment
assoc $=$ associating, or due to association
hs = hard sphere
ideal = ideal gas

\section*{Appendix}

Section 3 of this paper describes the SAFT model in terms of the molar residual Helmholtz energy ( $a^{\text {res }}$ ). This section provides other properties and functions needed to calculate phase equilibria, for example, total pressure ( $P$ ), compressibility factor ( $Z$ ), fugacity coefficient ( $\phi_{i}$ ), second virial coefficient ( $B$ ), and residual internal energy ( $u$ ). However, we start with the chemical potential ( $\mu_{i}$ ), the key phase equilibrium property, which is a derivative of the Helmholtz energy with respect to the mole number of component $i$ at constant temperature, volume, and non-i mole numbers.

Chemical Potential. We will present the chemical potential terms in the order used to present the correspondig Helmholtz energy terms, that is, the association, chain, and segment terms. The main equation is given by (cf. eq 11)

$$
\begin{equation*}
\mu_{i}^{\text {res }}=\mu_{i}^{\text {seg }}+\mu_{i}^{\text {chain }}+\mu_{i}^{\text {assoc }} \tag{A.1}
\end{equation*}
$$


The association contribution to the chemical potential, $\mu_{i}{ }^{\text {assoc }}$, can be expressed as (cf. eq 21)

$$
\begin{align*}
& \frac{\mu_{i}^{\mathrm{assoc}}}{R T}=\sum_{\mathrm{A}_{i}}\left[\ln X^{\mathrm{A}_{i}}-\frac{X^{\mathrm{A}_{i}}}{2}\right]+\frac{1}{2} M_{i}+ \\
& \sum_{j} \rho_{j} \sum_{\mathrm{A}_{j}}\left[\left(\frac{\partial X^{\mathrm{A}_{j}}}{\partial \rho_{i}}\right)_{T, \rho_{k \neq i}}\left[\frac{1}{X^{\mathrm{A}_{j}}}-\frac{1}{2}\right]\right] \tag{A.2}
\end{align*}
$$

where

$$
\begin{align*}
& {\left[\frac{\partial X^{\mathrm{A}_{j}}}{\partial \rho_{i}}\right]_{T, \rho_{k \times i}}=-\left(X^{\mathrm{A}_{j}}\right)^{2}\left[N_{\mathrm{Av}} \sum_{\mathrm{B}_{i}} X^{\mathrm{B}_{i}} \Delta^{\mathrm{A}_{j} \mathrm{~B}_{i}}+\right.} \\
& \left.\quad \sum_{k} \sum_{\mathrm{B}_{k}} N_{\mathrm{Av}} \rho_{k}\left[\Delta^{\mathrm{A}_{j} \mathrm{~B}_{k}}\left(\frac{\partial X^{\mathrm{B}_{k}}}{\partial \rho_{i}}\right)_{T, \rho_{l \times i}}+X^{\mathrm{B}_{k}}\left(\frac{\partial \Delta^{\mathrm{A}} \mathrm{~B}_{k}}{\partial \rho_{i}}\right)_{T, \rho_{l \neq i}}\right]\right] \tag{A.3}
\end{align*}
$$


The $\Delta^{\mathrm{A}_{j} \mathrm{~B}_{k}}$ is given by eq 24. Its partial derivative is given by

$$
\begin{align*}
& {\left[\frac{\partial \Delta^{\mathrm{A}} \mathrm{~B}_{k}}{\partial \rho_{i}}\right]_{T, \rho_{i w i}}=} \\
& \quad d_{j k}^{3}\left[\frac{\partial g_{j k}\left(d_{j k}\right)^{\mathrm{h}}}{\partial \rho_{i}}\right]_{T, \rho_{l \neq i}}\left[\exp \left(\epsilon^{\mathrm{A}_{j} \mathrm{~B}_{k}} / k T\right)-1\right] \kappa^{\mathrm{A}_{j} \mathrm{~B}_{k}} \tag{A.4}
\end{align*}
$$

where

$$
\begin{align*}
& {\left[\frac{\partial g_{j k}\left(d_{j k}\right)^{\mathrm{hs}}}{\partial \rho_{i}}\right]_{T, \rho_{1 * i}}=} \\
& \quad \frac{\pi N_{\mathrm{Av}}}{6} m_{i}\left\{\frac{d_{i i}{ }^{3}}{\left(1-\zeta_{3}\right)^{2}}+3 \frac{d_{j j} d_{k k}}{d_{j j}+d_{k k}}\left[\frac{d_{i i}{ }^{2}}{\left(1-\zeta_{3}\right)^{2}}+\right.\right. \\
& \left.\left.\quad \frac{2 d_{i i}{ }^{3} \zeta_{2}}{\left(1-\zeta_{3}\right)^{3}}\right]+2\left(\frac{d_{j j} d_{k k}}{d_{j j}+d_{k k}}\right)^{2}\left[\frac{2 d_{i i}{ }^{2} \zeta_{2}}{\left(1-\zeta_{3}\right)^{3}}+\frac{3 d_{i i}{ }^{3}\left(\zeta_{2}\right)^{2}}{\left(1-\zeta_{3}\right)^{4}}\right]\right\} \tag{A.5}
\end{align*}
$$


The chain contribution to the chemical potential, $\mu_{i}^{\text {chain }}$, can be expressed as (cf. eq 28)

$$
\begin{align*}
\frac{\mu_{i}^{\text {chain }}}{R T}= & \left(1-m_{i}\right) \ln \left(g_{i i}\left(d_{i i}\right)^{\text {hs }}\right)+ \\
& \sum_{j} X_{j} \rho\left(1-m_{j}\right)\left[\frac{\partial \ln g_{j j}\left(d_{j j}\right)^{\text {hs }}}{\partial \rho_{i}}\right]_{T, \rho_{k \rightarrow i}} \tag{A.6}
\end{align*}
$$

where the pair correlation function partial derivative is given by

$$
\begin{align*}
& {\left[\frac{\partial \ln g_{j j}\left(d_{j j}\right)^{\mathrm{hs}}}{\partial \rho_{i}}\right]_{T, \rho_{\mathrm{h}=i}}=\frac{\pi}{6} \frac{N_{\mathrm{Av}} m_{i}}{g_{j j}\left(d_{j j}\right)^{\mathrm{hs}}}\left[\frac{d_{i i}{ }^{3}}{\left(1-\zeta_{3}\right)^{2}}+\right.} \\
& \left.\frac{3}{2} \frac{d_{j j} d_{i i}{ }^{2}}{\left(1-\zeta_{3}\right)^{2}}+\frac{3 d_{j j} d_{i i}{ }^{3} \zeta_{2}}{\left(1-\zeta_{3}\right)^{3}}+\frac{d_{j j}{ }^{2} d_{i i}{ }^{2} \zeta_{2}}{\left(1-\zeta_{3}\right)^{3}}+\frac{3}{2} \frac{d_{j j}{ }^{2} d_{i i}{ }^{3} \zeta_{2}{ }^{2}}{\left(1-\zeta_{3}\right)^{4}}\right] \tag{A.7}
\end{align*}
$$


The LJ segment contribution to the chemical potential, $\mu_{i}{ }^{\text {seg }}$, can be expressed as

$$
\begin{array}{r}
\frac{\mu_{i}^{\text {seg }}}{m_{i} R T}=\frac{a_{0}^{\text {seg }}}{R T}+\left(Z_{0}^{\text {seg }}-1\right)\left[\frac{2 \sum_{j} X_{j} m_{j} \sigma_{i j}{ }^{3}}{\sigma^{3} \sum_{j} X_{j} m_{j}}-1\right]+ \\
\frac{u_{0}^{\text {seg }}}{R T}\left[\frac{2 \sum_{j} X_{j} m_{j} \epsilon_{i j} \sigma_{i j}{ }^{3}}{\epsilon \sigma^{3} \sum_{j} X_{j} m_{j}}-\frac{2 \sum_{j} X_{j} m_{j} \sigma_{i j}{ }^{3}}{\sigma^{3} \sum_{j} X_{j} m_{j}}\right] \tag{A.8}
\end{array}
$$


This is the contribution of the segments to the chemical potential of the molecule and corresponds to $a^{\text {seg }}$ (per mole of molecules) given by eq 29. $a_{0}{ }^{\mathrm{seg}}$ (per mole of segments) is given by eq $30 . \mathrm{Z}_{\mathrm{o}}{ }^{\text {seg }}$ in eq A. 8 is the segment compressibility factor (but NOT residual), which is given by eq A.14. The $u_{\mathrm{o}}{ }^{\text {seg }}$ term in eq A. 8 is the residual internal energy, per mole of segments, not molecules, which is given
by eq A.19. $\sigma$ and $\epsilon$ in eq A. 8 are equivalent to $\sigma_{\mathrm{x}}$ and $\epsilon_{\mathrm{x}}$ from eqs 4 and 5.

Compressiblity Factor. We will present the compressibility factor terms in the order used to present the corresponding Helmholtz energy terms, that is, the association, chain, and segment terms. The main equation is given by

$$
\begin{equation*}
Z=Z^{\text {seg }}+Z^{\text {chain }}+Z^{\text {assoc }} \tag{A.9}
\end{equation*}
$$


The association term is given by

$$
\begin{equation*}
Z^{\mathrm{assoc}}=\sum_{i} X_{i} \frac{\mu_{i}^{\mathrm{assoc}}}{R T}-\frac{a^{\mathrm{assoc}}}{R T} \tag{A.10}
\end{equation*}
$$

where $\mu_{i}{ }^{\text {assoc }}$ is given by eq A. 2 and $a^{\text {assoc }}$ is given by eq 21.
The chain term is given by (cf. eq 28)

$$
\begin{equation*}
Z^{\text {chain }}=\sum_{i} X_{i}\left(1-m_{i}\right) \rho\left[\frac{\partial \ln g_{i i}\left(d_{i i}\right)^{\mathrm{hs}}}{\partial \rho}\right]_{T, X_{j}} \tag{A.11}
\end{equation*}
$$

where

$$
\begin{align*}
& \rho\left[\frac{\partial \ln g_{i i}\left(d_{i i}\right)^{\mathrm{hs}}}{\partial \rho}\right]_{T, X_{j}}=\frac{1}{g_{i i}\left(d_{i i}\right)^{\mathrm{hs}}}\left[\frac{\zeta_{3}}{\left(1-\zeta_{3}\right)^{2}}+\right. \\
& \left.\frac{3}{2} \frac{d_{i i} \zeta_{2}}{\left(1-\zeta_{3}\right)^{2}}+\frac{3 d_{i i} \zeta_{2} \zeta_{3}}{\left(1-\zeta_{3}\right)^{3}}+\frac{d_{i i}{ }^{2} \zeta_{2}{ }^{2}}{\left(1-\zeta_{3}\right)^{3}}+\frac{3}{2} \frac{d_{i i}{ }^{2} \zeta_{2}{ }^{2} \zeta_{3}}{\left(1-\zeta_{3}\right)^{4}}\right] \tag{A.12}
\end{align*}
$$


The segment term, which is our reference compressibility factor (for fluid of LJ molecules), is given by (cf. eq 29)

$$
\begin{equation*}
Z^{\mathrm{seg}}=1+\left(Z_{\mathrm{o}}^{\mathrm{seg}}-1\right) \sum_{i} X_{i} m_{i} \tag{A.13}
\end{equation*}
$$

where $Z_{0}{ }^{\text {seg }}$, needed in eq A.8, is the compressibility factor for the pure or conformal fluid of LJ segments, not molecules, which is defined as follows:

$$
\begin{equation*}
Z_{\mathrm{o}}{ }^{\mathrm{seg}}=Z_{\mathrm{o}}{ }^{\mathrm{hs}}+Z_{\mathrm{o}}{ }^{\mathrm{disp}} \tag{A.14}
\end{equation*}
$$

where (cf. eqs 31 and 34-36)

$$
\begin{gather*}
Z_{\mathrm{o}}{ }^{\text {hs }}=\frac{1+\eta+\eta^{2}-\eta^{3}}{(1-\eta)^{3}}  \tag{A.15}\\
Z_{\mathrm{o}}{ }^{\text {disp }}=Z_{\mathrm{o} 1}{ }^{\text {disp }} / T_{\mathrm{R}}+Z_{\mathrm{o} 2}{ }^{\text {disp }} / T_{\mathrm{R}}{ }^{2}  \tag{A.16}\\
Z_{\mathrm{o} 1}{ }^{\text {disp }}=\rho_{\mathrm{R}}\left[-8.595-2\left(4.5424 \rho_{\mathrm{R}}\right)-\right. \\
\left.3\left(2.1268 \rho_{\mathrm{R}}{ }^{2}\right)+4\left(10.285 \rho_{\mathrm{R}}{ }^{3}\right)\right](\mathrm{A}  \tag{A.17}\\
Z_{\mathrm{o} 2}{ }^{\text {disp }}=\rho_{\mathrm{R}}\left[-1.9075+2\left(9.9724 \rho_{\mathrm{R}}\right)-3\left(22.216 \rho_{\mathrm{R}}{ }^{2}\right)+\right. \\
\left.4\left(15.904 \rho_{\mathrm{R}}{ }^{3}\right)\right](\mathrm{A} \tag{A.18}
\end{gather*}
$$


Alternatively, the compressibility factor terms discussed in this section can be calculated from the definition equation as follows:

$$
Z=\frac{P}{\rho R T}=\frac{P v}{R T}
$$

where pressure is discussed further.
Internal Energy. The residual internal energy, $u_{0}{ }^{\text {seg }}$, per mole of segments, not molecules, as needed to determine the segment chemical potential from eq A.8, can be calculated as follows (cf. eq 30):

$$
\begin{equation*}
\frac{u_{0}{ }^{\mathrm{seg}}}{R T}=\frac{1}{T}\left[\frac{\partial\left(a_{0}{ }^{\mathrm{seg}} / R T\right)}{\partial(1 / T)}\right]-\left(Z_{\mathrm{o}}{ }^{\mathrm{seg}}-1\right) \frac{3}{d} T \frac{\partial d}{\partial T} \tag{A.19}
\end{equation*}
$$

where

$$
\begin{equation*}
\frac{1}{T}\left[\frac{\partial\left(a_{\mathrm{o}}{ }^{\mathrm{seg}} / R T\right)}{\partial(1 / T)}\right]=a_{\mathrm{o} 1}{ }^{\mathrm{disp}} / T_{\mathrm{R}}+2 a_{\mathrm{o} 2}{ }^{\mathrm{disp}} / T_{\mathrm{R}}{ }^{2} \tag{A.20}
\end{equation*}
$$


$$
\begin{align*}
& \frac{T}{d} \frac{\partial d}{\partial T}= \\
& {\left[\frac{1-f(m)(k T / \epsilon)^{2}}{1+0.33163 k T / \epsilon+f(m)(k T / \epsilon)^{2}}-\frac{1}{1+0.2977 k T / \epsilon}\right]} \tag{A.21}
\end{align*}
$$

where the temperature-dependence function $f(k T / \epsilon, m)$ is given by eq 2 in section 2.4.

The residual internal energy, $u^{\text {seg }}$, per mole of molecules, is given by (cf. eq 29)

$$
\begin{equation*}
\frac{u^{\mathrm{seg}}}{R T}=\frac{u_{0}^{\mathrm{seg}}}{R T} \sum_{i} X_{i} m_{i} \tag{A.22}
\end{equation*}
$$


Pressure. Pressure can be determined based on the chemical potential, density, and the Helmholtz energy as follows:

$$
\begin{equation*}
P=\sum_{i} \rho_{i} \mu_{i}-a \rho \tag{A.23}
\end{equation*}
$$


This equation gives the total pressure for a mixture of components $i=1,2, \ldots$, where $\rho_{i}$ is the molar density, $\mu_{i}$ is the total chemical potential

$$
\begin{equation*}
\mu_{i}=\mu_{i}^{\text {ideal gas }}+\mu_{i}^{\text {res }} \tag{A.24}
\end{equation*}
$$

where $\mu_{i}{ }^{\text {res }}$ is given by eq A.1. $a$ in eq A. 23 is the total Helmholtz energy

$$
\begin{equation*}
a=a^{\text {ideal gas }}+a^{\text {res }} \tag{A.25}
\end{equation*}
$$

where $a^{\text {res }}$ is given by eq 11 in section 3. $\rho$ in eq A. 23 is the mixture molar density

$$
\begin{equation*}
\rho=\rho_{i} / X_{i} \tag{A.26}
\end{equation*}
$$


Alternatively, pressure can be calculated based on the compressibility factor:

$$
\begin{equation*}
P=Z \rho R T \tag{A.27}
\end{equation*}
$$

where $P$ is one of the following: total $P, P^{\text {assoc }}, P^{\text {chain }}, P^{\text {seg }}$, etc. $Z$ is one of the following: total $Z$ (eq A.9), $Z^{\text {assoc }}$ (eq A.10), $Z^{\text {chain }}$ (eq A.11), $Z^{\text {seg }}$ (eq A.13), respectively.

Fugacity Coefficient. Fugacity coefficients can be determined from

$$
\begin{equation*}
R T \ln \phi_{i}=\mu_{i}^{\mathrm{res}}-R T \ln Z \tag{A.28}
\end{equation*}
$$

which is a general expression for various terms of $\phi_{i}$. Depending on the choice of terms (total, association, chain, segment, etc.), the appropriate terms of $\mu_{i}^{\text {res }}$ and $Z$ should be used in eq A.28.

Second Virial Coefficient (B). We will present the second virial coefficient terms in the order used to present the corresponding Helmholtz energy terms, that is, the association, chain, and segment terms. The main equation is given by

$$
\begin{equation*}
B=B^{\mathrm{assoc}}+B^{\text {chain }}+B^{\mathrm{seg}} \tag{A.29}
\end{equation*}
$$


The association term is given by

$$
\begin{equation*}
B^{\mathrm{assoc}}=\frac{-N_{\mathrm{Av}}}{2} \sum_{i} \sum_{j} X_{i} X_{j} \sum_{\mathrm{A}_{i}} \sum_{\mathrm{B}_{j}}\left[\Delta^{\mathrm{A}_{\mathrm{i}} \mathrm{~B}_{j}}\right] \quad \text { for } \rho=0 \tag{A.30}
\end{equation*}
$$


Wertheim's theory gives the exact second virial coefficient. However, our approximation (eq 18) of the integral in eq 16 is most accurate at intermediate liquid densities.

The chain term is given by

$$
\begin{equation*}
B^{\text {chain }}=\frac{\pi N_{\text {Av }}}{6} \sum_{i} X_{i}\left(1-m_{i}\right)\left[\sum_{j} X_{j} m_{j}\left(d_{j j}^{3}+\frac{3}{2} d_{i i} d_{j j}^{2}\right)\right] \tag{A.31}
\end{equation*}
$$


The segment term is given by

$$
\begin{equation*}
B^{\mathrm{seg}}=B^{\mathrm{hs}}+B^{\mathrm{disp}} \tag{A.32}
\end{equation*}
$$

where

$$
\begin{gather*}
B^{\mathrm{hs}}=\frac{2 \pi N_{\mathrm{Av}}}{3} d^{3}\left(\sum_{i} X_{i} m_{i}\right)^{2}  \tag{A.33}\\
B^{\mathrm{disp}}=\frac{N_{\mathrm{Av}}}{2^{0.5}} d^{3}\left(\sum_{i} X_{i} m_{i}\right)^{2}\left[\frac{-8.595}{T_{\mathrm{R}}}-\frac{1.9075}{T_{\mathrm{R}}^{2}}\right]
\end{gather*}
$$


All the variables without the component subscripts (i) in the equations presented in this section, such as $a_{0}{ }^{\text {seg }}$, $u_{0}{ }^{\text {seg }}, Z_{0}{ }^{\text {seg }}, \sigma$, and $\epsilon$, are for the fluid mixture, which is equivalent to the conformal fluid x (with subscript x in eqs 4 and 5).

\section*{Literature Cited}

Abrams, D.; Prausnitz, J. M. Statistical Thermodynamics of Liquid Mixtures: A New Expression for the Excess Gibbs Energy of Partly or Completely Miscible Systems. AIChE J. 1975, 21, 116-128.
Andersen, H. C. Cluster Expansions for Hydrogen Bonded Fluids. I. Molecular Association in Dilute Gases. J. Chem. Phys. 1973, 59, 4714-4725.
Andersen, H. C. Cluster Expansions for Hydrogen Bonded Fluids. II. Dense Liquids. J. Chem. Phys. 1974, 61, 4985-4992.

Barker, J. A.; Henderson, D. Perturbation Theory and Equation of State for Fluids. II. A Successful Theory of Liquids. J. Chem. Phys. 1967, 47, 4714-4721.
Carnahan, N. F.; Starling, K. E. Equation of State for Nonattracting Rigid Spheres. J. Chem. Phys. 1969, 51, 635-636.
Chapman, W. G. Theory and Simulation of Associating Liquid Mixtures. Ph.D. Dissertation, Cornell University, Ithaca, NY, 1988.

Chapman, W. G.; Gubbins, K. E.; Joslin, C. G.; Gray, C. G. Theory and Simulation of Associating Liquid Mixtures. Fluid Phase Equilib. 1986, 29, 337-346.
Chapman, W. G.; Gubbins, K. E.; Joslin, C. G.; Gray, C. G. Mixtures of Polar and Associating Molecules. Pure Appl. Chem. 1987, 59, 53-60.
Chapman, W. G.; Jackson, G.; Gubbins, K. E. Phase Equilibria of Associating Fluids: Chain Molecules with Multiple Bonding Sites. Molec. Phys. 1988, 65, 1057-1079.
Chapman, W. G.; Gubbins, K. E.; Jackson, G.; Radosz, M. SAFT: Equation of State Solution Model for Associating Fluids. Fluid Phase Equilib. 1989, 52, 31-38.
Cotterman, R. L.; Schwartz, B. J.; Prausnitz, J. M. Molecular Thermodynamics for Fluids at Low and High Densities. AIChE J. 1986, 32, 1787-1798.

Cummings, P. T.; Blum, L. Analytic Solution of the Molecular Ornstein-Zernike Equation for Nonspherical Molecules. Spheres with Anisotropic Surface Adhesion. J. Chem. Phys. 1986, 84, 1833-1842.
Cummings, P. T.; Stell, G. Statistical Mechanical Models of Chemical Reactions: Analytic Solution of Models of $A+B=A B$ in the Percus-Yevick Approximation. Molec. Phys. 1984, 51, 253-287.
Dickman, R.; Hall, C. High Density Monte Carlo Simulation of Chain Molecules: Bulk Equation of State and Density Profile Near Walls. J. Chem. Phys. 1988, 89, 3168-3174.
Dolezalek, F. Zur Theorie der Binären Gemische und Konzentrierten Löungen. Z. Phys. Chem. 1908, 64, 727-747.
Flory, P. J. Principles of Polymer Chemistry: Cornell University Press: Ithaca, NY, 1953; pp 318-325.
Guggenheim, E. A. Applications of Statistical Mechanics; Oxford University Press: Oxford, U.K., 1966.
Jackson, G.; Chapman, W. G.; Gubbins, K. E. Phase Equilibria of Associating Fluids: Spherical Molecules with Multiple Bonding Sites. Molec. Phys. 1988, 65, 1-31.
Joslin, C. G.; Gray, C. G.; Chapman, W. G.; Gubbins, K. E. Theory and Simulation of Associating Liquid Mixtures: Part II. Molec. Phys. 1987, 62, 843-860.
Kinugawa, K.; Nakanishi, K. Molecular Dynamics Simulations on the Hydration of Fluoroalcohols. J. Chem. Phys. 1988, 89, 5834-5842.
Mansoori, G. A.; Carnahan, N. F.; Starling, K. E.; Leland, T. W. Equilibrium Thermodynamic Properties of the Mixture of Hard Spheres. J. Chem. Phys. 1971, 54, 1523-1525.

Physical Sciences Data; Thermodynamic Data for Pure Compounds, Part A: Hydrocarbons and Ketones. Elsevier: New York, 1986; Vol. 25.
Prausnitz, J. M.; Lichtenthaler, R. N.; De Azevedo, E. G. Molecular Thermodynamics of Fluid Phase Equilibria; Prentice-Hall: Englewood Cliffs, NJ, 1986.
Reed, T. M.; Gubbins, K. E. Applied Statistical Mechanics; McGraw-Hill: New York, 1973.
Renon, H.; Prausnitz, J. M. Local Compositions in Thermodynamic Excess Functions for Liquid Mixtures. AIChE J. 1968, 14, 135-144.
Rowlinson, J. S.; Swinton, F. L. Liquid and Liquid Mixtures; Butterworth Scientific: London, 1982.
Stell, G.; Zhou, Y. Chemical Association in Simple Models of Molecular and Ionic Fluids. J. Chem. Phys. 1989, 91, 3618-3623.
Twu, C. H.; Lee, L. L.; Starling, K. E. Improved Analytical Representation of Argon Thermodynamic Behavior. Fluid Phase Equilib. 1980, 4, 35-44.
Wertheim, M. S. Fluids with Highly Directional Attractive Forces. I. Statistical Thermodynamics. J. Stat. Phys. 1984a, 35, 19-34.

Wertheim, M. S. Fluids with Highly Directional Attractive Forces. II. Thermodynamic Perturbation Theory and Integral Equations. J. Stat. Phys. 1984b, 35, 35-47.

Wertheim, M. S. Fluids with Highly Directional Attractive Forces. III. Multiple Attraction Sites. J. Stat. Phys. 1986a, 42, 459-476.

Wertheim, M. S. Fluids with Highly Directional Attractive Forces. IV. Equilibrium Polymerization. J. Stat. Phys. 1986b, 42, 477-492.
Wertheim, M. S. Fluids of Dimerizing Hard Spheres, and Fluid Mixtures of Hard Spheres and Dispheres. J. Chem. Phys. 1986c, 85, 2929-2936.
Wertheim, M. S. Thermodynamic Perturbation Theory of Polymerization. J. Chem. Phys. 1987, 87, 7323-7331.
Wilson, G. M. Vapor-Liquid Equilibrium. XI. A New Expression for the Excess Free Energy of Mixing. J. Am. Chem. Soc. 1964, 86, 127-130.

Received for review September 6, 1989
Revised manuscript received January 23, 1990
Accepted March 23, 1990
