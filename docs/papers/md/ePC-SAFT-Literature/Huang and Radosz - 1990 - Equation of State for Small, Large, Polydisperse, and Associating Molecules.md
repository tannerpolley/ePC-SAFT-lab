\title{
Equation of State for Small, Large, Polydisperse, and Associating Molecules
}

\author{
Stanley H. Huang and Maciej Radosz* \\ Exxon Research and Engineering Company, Annandale, New Jersey 08801
}

\begin{abstract}
Statistical Associating Fluid Theory (SAFT) has been extended to many real, molecular, and macromolecular fluids, such as chain, aromatic, and chlorinated hydrocarbons, ethers, alkanols (aliphatic alcohols), carboxylic acids, esters, ketones, amines, and polymers, having molar mass up to 100000 . The key result of this work is an accurate and physically sound equation of state for predicting density, vapor pressure, and other fluid properties. Practical calculations require three nonspecific parameters: segment number, segment volume, and segment-segment interaction energy (segment energy for short). For chain molecules, the segment volume and segment energy are found to be nearly constant upon increasing the molar mass, while the segment number is found to be a linear function of molar mass. As a result, this equation of state represents a useful, predictive correlation for many compounds, such as polymers, where no extensive experimental data are available and where parameters have to be estimated based on molar mass and chemical structure only. Specific interactions, such as hydrogen bonding, are characterized by two association parameters, the association energy and volume, characteristic of each site-site pair. These parameters, having well-defined physical meaning, control the bond strength and hence the degree of association.
\end{abstract}
Downloaded via BRIGHAM YOUNG UNIV on April 23, 2023 at 22:36:04 (UTC). See https://pubs.acs.org/sharingguidelines for options on how to legitimately share published articles.

\section*{Introduction}

Molecularly based equations of state not only provide a useful thermodynamic basis for deriving chemical potentials or fugacities that are needed for phase equilibrium simulations but also allow for separating and quantifying the effects of molecular structure and interactions on bulk properties and phase behavior. Examples of such effects are the molecular size and shape (e.g., chain length), association (e.g., hydrogen bonding) energy, and mean field (e.g., dispersion and induction) energy. Ideally, a single equation of state should incorporate all these effects.

A concept of such an equation of state has recently been proposed by Chapman et al. $(1989,1990)$ based on perturbation theory. The essence of their approach, referred to as the Statistical Associating Fluid Theory (SAFT), is to use a reference fluid that incorporates both the chain length (molecular size and shape) and molecular association, in place of the much simpler hard sphere reference fluid used in most existing engineering equations of state. Chapman et al. (1990) developed Helmholtz energy expressions accounting for the chain and association effects based on Wertheim's (1984, 1986a,b) cluster expansion theory.

Wertheim derived his theory by expanding the Helmholtz energy in a series of integrals of molecular distribution functions and the association potential. On the basis of physical arguments, Wertheim showed that many integrals in this series must be zero and, hence, a simplified expression for the Helmholtz energy can be obtained. This expression is a result of resummed terms in the expansion series (cluster expansion). The key result of Wertheim's theory is a relationship between the residual Helmholtz energy due to association and the monomer density. This monomer density, in turn, is related to a function $\Delta$ characterizing the "association strength".

A reference equation of state used in this work is based on the SAFT concept that captures the hard sphere, chain, and association effects. Effects due to other kinds of intermolecular forces (dispersion, induction, etc.), usually weaker, can be included through a mean field perturbation term. Our mean field term is similar to that proposed by Alder et al. (1972) and is creatively used in many recent equations of state, most notably by Beret and Prausnitz
(1975) in the Perturbed Hard Chain Theory (and in more recent PHCT versions) and by Chen and Kreglewski (1977) in their equation of state, also known as BACK and extended to mixtures by Simnick et al. (1979).

Our goal is to develop a practical but physically sound equation of state, applicable to small, large, chain, and associating molecules over the whole density range. While we are concerned with the quality of fit for various fluid properties, such as vapor pressures and liquid densities, our primary concern is the ease and reliability of extrapolating to large, often poorly defined and polydisperse pseudocomponents of real polymer and oil solutions. From this point of view, the key to success lies in well-behaved and hence easy to estimate equation of state parameters.

We will define model molecules, bulk fluid properties, and equation of state parameters to be derived from fitting real fluids. We will then define our equation of state in terms of the Helmholtz energy and compressibility factor. After presenting many correlation results and equation of state parameters for vapor pressures and liquid densities of over 100 real fluids, we will show an example of how a reliable equation of state can be used to estimate critical constants of large molecules, which cannot be determined experimentally due to thermal decomposition.

\section*{Real Fluids: Nonassociating and Self-Associating}

We will treat the effective molecular size (through hard sphere and chain terms) and molecular association as two major effects on the bulk properties of real fluids. This choice can be justified by using a simplified example for the vapor pressure. It is easy to show that the vapor pressure ( $p^{\text {sat }}$ ) can be approximately correlated with respect to temperature ( $T$ ) by using a Clausius-Clapeyron type of equation given below:

$$
\ln p^{\text {sat }}=A^{(1)}-A^{(2)} / T
$$

where $A^{(2)}$ is a constant proportional to the enthalpy of vaporization. $A^{(2)}$, obtained from fitting to experimental vapor pressure data, is log-log plotted against the molar mass in Figure 1a for nonassociating fluids and in Figure Ib for associating fluids. The data points shown in these figures are defined in Table I, along with symbols and data points used throughout this paper.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-02.jpg?height=1105&width=833&top_left_y=148&top_left_x=202}
\captionsetup{labelformat=empty}
\caption{Figure 1. $\log$-log plot of $A^{(2)}=\left(A^{(1)}-\ln p^{\text {sat }}\right) T$ versus molar mass. For nonassociating hydrocarbons, shown in the upper part (1a), $A^{(2)}$ can be correlated by a straight line. However, other compounds shown in the lower part (1b) can deviate from this line significantly due to strong self-association.}
\end{figure}

We will note that $A^{(2)}$ for nonassociating fluids in Figure 1a is a strong, essentially linear function of the molar mass and that all the points representing hydrocarbons of many different structures (chainlike, branched, and ringlike) tend to cluster around the average line. This means that the effect of structure, however significant and accounted for, is much smaller than the effect of molecular size. This is true even though we can observe a slight deviation from the average line for polynuclear aromatics, which can be explained by a small degree of $\Pi-\Pi$-induced aggregation.

By contrast, we will note that $A^{(2)}$ for associating fluids in Figure 1b shows strong deviations from $A^{(2)}$ for $n$-alkanes. Expectedly, the magnitude of these deviations depends on the degree of association. For example, carboxylic acids and alkanols (aliphatic alcohols), which are known to be strongly associated, exhibit greater deviations from the alkane behavior than tertiary amines and ethers do. Therefore, we will only treat acids, alkanols, primary amines, and secondary amines as significantly self-associating compounds.

\section*{Model Fluid Properties and Parameters}

Our model pure fluid is a mixture of equi-sized spherical segments interacting according to a square-well potential. In addition, we superimpose two kinds of bonds between these segments, covalent-like bonds to form chains and association bonds to interact specifically. As a result, our model molecules can approximate a broad range of molecules, from nonassociating near-spherical (for example, methane, neopentane) and nonspherical (chain alkanes, polymers) to associating near-spherical (methanol) and nonspherical (alkanols). Since this paper deals with pure

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table I. Nonassociating and Self-Associating Real Fluids}
\begin{tabular}{|l|l|}
\hline fluids & data points \\
\hline \multicolumn{2}{|l|}{nonassociating} \\
\hline $n$-alkanes & 0 \\
\hline polypropylene & 0 \\
\hline polyethylene & 0 \\
\hline polyisobutylene & 0 \\
\hline $n$-alkylcyclopentanes & △ \\
\hline $n$-alkylcyclohexanes & ∇ \\
\hline benzene derivatives & ![](https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-02.jpg?height=27\&width=26\&top_left_y=471\&top_left_x=1773) \\
\hline polynuclear aromatics & ০ \\
\hline ethers & A \\
\hline ketones & V \\
\hline tertiary amines & - \\
\hline esters & \\
\hline alkenes & \\
\hline chlorinated hydrocarbons & \\
\hline self-associating & \\
\hline acids & ■ \\
\hline alkanols (aliphatic alcohols) & - \\
\hline primary amines & ![](https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-02.jpg?height=29\&width=34\&top_left_y=810\&top_left_x=1773) \\
\hline secondary amines & ![](https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-02.jpg?height=29\&width=34\&top_left_y=842\&top_left_x=1773) \\
\hline
\end{tabular}
\end{table}
components only, associating means self-associating and nonassociating means non-self-associating. We should note that some non-self-associating molecules can be cross-associating in mixtures with other molecules.

The reduced fluid density $\eta$ (segment packing fraction), the same for segments and molecules, is defined as

$$
\begin{equation*}
\eta=\frac{\pi N_{\mathrm{Av}}}{6} \rho m d^{3} \tag{1}
\end{equation*}
$$

where $\rho$ is the molar density, $m$ is the segment number (number of segments in each molecule, our first pure component parameter), and $d$ is the effective segment diameter that is temperature dependent. This definition is equivalent to

$$
\begin{equation*}
\eta=\tau \rho m v^{\circ} \tag{2}
\end{equation*}
$$

where $\tau=0.74048$ and $v^{\circ}$ is the segment molar volume in a close-packed arrangement, i.e., the volume occupied by $N_{\text {Av }}$ closely packed segments, in milliliters per mole of segments. Hence, on the basis of eqs 1 and 2 , we can express $v^{o}$ as

$$
\begin{equation*}
v^{\mathrm{o}}=\frac{\pi N_{\mathrm{Av}}}{6 \tau} d^{3} \tag{3}
\end{equation*}
$$


Since $v^{\circ}$ is implicitly temperature dependent, because $d$ is temperature dependent, it is useful to introduce a corresponding, temperature-independent segment molar volume at $T=0$, which will be denoted $v^{\circ \circ}$ and referred to as the segment volume, our second pure component parameter:

$$
\begin{equation*}
v^{00}=\frac{\pi N_{\mathrm{Av}}}{6 \tau} \sigma^{3} \tag{4}
\end{equation*}
$$

where $\sigma$ is a temperature-independent segment diameter. Since a characteristic volume, rather than diameter, is traditionally selected as a pure component parameter, for example, $b$ in cubic equations of state, $V^{*}$ in the Perturbed Hard Chain Theory of Beret and Prausnitz (1975), and $v^{\circ \circ}$ in the Chen-Kreglewski (1977) equation of state, $v^{\circ \circ}$ will also be used in this work as one of the pure component parameters. However, while all the volume parameters were defined by others per mole of molecules, our $v^{\circ \circ}$ is defined per mole of segments.

Temperature dependence of the segment diameter $d$ in eq 3 is based on the Barker-Henderson approach (1967).

Specific equations for $d$ and $v^{\circ}$ given below,

$$
\begin{align*}
d & =\sigma\left[1-C \exp \left[\frac{-3 u^{\circ}}{k T}\right]\right]  \tag{5}\\
v^{\circ} & =v^{\circ \circ}\left[1-C \exp \left[\frac{-3 u^{\circ}}{k T}\right]\right]^{3} \tag{6}
\end{align*}
$$

are based on the work of Chen and Kreglewski (1977), who obtained eq 6 by solving the Barker-Henderson integral equation for $d$

$$
\begin{equation*}
d=\int_{0}^{d}[1-\exp (-u(r) / k T)] \mathrm{d} r \tag{7}
\end{equation*}
$$

using a square-well potential; $u^{\circ} / k$ in eqs 5 and 6 is the well depth, a temperature-independent energy parameter, characteristic of nonspecific segment-segment interactions, which will be referred to as the segment energy, in kelvin, our third pure component parameter. Similar to Chen and Kreglewski (1977), we set the integration constant $C=0.12$ and use their temperature dependence of $u$

$$
\begin{equation*}
u=u^{\circ}\left[1+\frac{e}{k T}\right] \tag{8}
\end{equation*}
$$

where $e / k$ is a constant that was related to Pitzer's acentric factor and the critical temperature (Chen and Kreglewski, 1977; Kreglewski, 1984) for various molecules. Since our energy parameter is for segments rather than for molecules, we set $e / k=10$ for all the molecules. The only exceptions are a few small molecules where the $e / k$ values close to those derived by Kreglewski have been used ( $e / k=0$ for argon; 1 for methane, ammonia, and water; 3 for nitrogen; 4.2 for CO ; 18 for chlorine; 38 for $\mathrm{CS}_{2}$; 40 for $\mathrm{CO}_{2}$; and 88 for $\mathrm{SO}_{2}$ ); larger values of $e / k$ for some of the molecules treated here as nonassociating may be caused by their weak self-association.

In addition to the three pure component parameters characterizing nonassociating molecules, $v^{\infty}, m$, and $u^{\circ}$, we use two association parameters, $\epsilon^{\mathrm{AA}}$ and $\kappa^{\mathrm{AA}}$. These association parameters have been proposed for a square-well model of specific interactions between two sites A (Chapman et al., 1990). The parameter $\epsilon^{\mathrm{AA}}$ characterizes the association energy (well depth), and the parameter ${ }^{\mathrm{AAA}}$ characterizes the association volume (corresponds to the well width $r^{\mathrm{AA}}$ ).

In general, the number of association sites on a single molecule is unlimited, but it has to be specified for each specific molecule. However, we do not specify the location of association sites. We label these sites with superscripts A, B, C, etc., to keep track of the specific site-site interactions. Each association site is assumed to have a different interaction with the various sites on another molecule. Cluster structure limitations, steric hindrance approximations, and size distributions are explained in detail elsewhere (Chapman et al., 1990).

In brief, the fraction of clusters of a given size can be estimated by using general statistical arguments (Flory, 1953 ). As an example, we shall consider a pure component system composed of molecules having two sites A and B , where only AB bonding and only chain clusters are allowed. The fractions of each chain length present (dimers, trimers, etc.) are functions of $X^{\mathrm{A}}$ and $X^{\mathrm{B}}$ (the fractions of molecules NOT bonded at sites A and B, respectively) that, in turn, are calculated from the equation of state described in section 3. Assuming that the activity of a site is independent of bonding at the other sites on the same molecule, the fraction of molecules that are present as monomers is $X^{\mathrm{A}} X^{\mathrm{B}}$, or $\left(X^{\mathrm{A}}\right)^{2}$ if $X^{\mathrm{A}}=X^{\mathrm{B}}$, which is the
case in our example. Similarly, the fraction of molecules that are present as dimers is given by $2\left(X^{\mathrm{A}}\right)^{2}\left(1-X^{\mathrm{A}}\right)$. The general result for the fraction of molecules present as $m$-mers is

$$
\begin{equation*}
X(m-\text { mer })=m\left(X^{\mathrm{A}}\right)^{2}\left(1-X^{\mathrm{A}}\right)^{m-1} \tag{9}
\end{equation*}
$$

and the average chain length is given by

$$
\begin{equation*}
m_{\text {ave }}=1 / X^{\mathrm{A}} \tag{10}
\end{equation*}
$$


Equation 9 expresses the "most probable distribution" of Flory (1953), which is in agreement with experimental results for polymer polydispersity.

\section*{Equation of State}

The theory results underlying our equation of state are given in this section in terms of the residual Helmholtz energy $a^{\text {res }}$ per mole, defined as $a^{\text {res }}(T, V, N)=a(T, V, N) -a^{\text {ideal }}(T, V, N)$, where $a(T, V, N)$ and $a^{\text {ideal }}(T, V, N)$ are the total Helmholtz energy per mole and the ideal gas Helmholtz energy per mole at the same temperature and density. The residual Helmholtz energy $a^{\text {res }}$ is a sum of three terms representing contributions from different intermolecular forces. The first term $a^{\text {seg }}$ accounts for the part of $a^{\text {res }}$ that represents segment-segment interactions, i.e., hard sphere and mean-field (dispersion) interactions. The second term $a^{\text {chain }}$ is due to the presence of covalent chain-forming bonds among the segments. The third term $a^{\text {assec }}$ accounts for the increment of $a^{\text {res }}$ due to the presence of site-site specific interactions among the segments, for example, hydrogen-bonding interactions. The general expression for the Helmholtz energy is given by

$$
\begin{equation*}
a^{\mathrm{res}}=a^{\mathrm{seg}}+a^{\mathrm{chain}}+a^{\mathrm{assoc}} \tag{11}
\end{equation*}
$$


The segment Helmholtz energy $a^{\text {seg }}$, per mole of molecules, can be calculated from

$$
\begin{equation*}
a^{\mathrm{seg}}=m a_{\mathrm{o}}{ }^{\mathrm{seg}} \tag{12}
\end{equation*}
$$

where $a_{0}{ }^{\text {seg }}$, per mole of segments, is the residual Helmholtz energy of nonassociated spherical segments and $m$ is the segment number. Let us allow $a_{0}{ }^{\text {seg }}$ to be composed of hard sphere and dispersion parts, as follows

$$
\begin{equation*}
a_{0}^{\mathrm{seg}}=a_{0}^{\mathrm{hs}}+a_{0}^{\mathrm{disp}} \tag{13}
\end{equation*}
$$


As usual, the hard sphere term can be calculated as proposed by Carnahan and Starling (1969)

$$
\begin{equation*}
\frac{a_{0}^{\mathrm{hs}}}{R T}=\frac{4 \eta-3 \eta^{2}}{(1-\eta)^{2}} \tag{14}
\end{equation*}
$$

where $\eta$ is the reduced density given by eqs 1 and 2 .
The dispersion term is a power series initially fitted by Alder et al. (1972) to molecular dynamics data for a square-well fluid. This equation, which also provided the basis for the Perturbed Hard Chain Theory of Beret and Prausnitz (1975), is given by

$$
\begin{equation*}
\frac{a_{0}{ }^{\text {disp }}}{R T}=\sum_{i} \sum_{j} D_{i j}\left[\frac{u}{k T}\right]^{i}\left[\frac{\eta}{\tau}\right]^{j} \tag{15}
\end{equation*}
$$

$D_{i j}$ are universal constants. In this work, we use $D_{i j}$ 's that have been refitted to accurate PVT, internal energy, and second viral coefficient data for argon, by Chen and Kreglewski (1977).

Both chain and association terms are the same as those described by Chapman et al. (1990). The chain term, the

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-04.jpg?height=495&width=806&top_left_y=143&top_left_x=217}
\captionsetup{labelformat=empty}
\caption{Figure 2. Segment number $m$ as a linear function of molar mass for $n$-alkanes and long-chain polymers; $\mathrm{PP}=$ polypropylene, $\mathrm{PE}=$ polyethylene, $\mathrm{PIB}=$ polyisobutene.}
\end{figure}

Helmoltz energy increment due to bonding, can be determined from

$$
\begin{equation*}
\frac{a^{\text {chain }}}{R T}=(1-m) \ln \frac{1-\frac{1}{2} \eta}{(1-\eta)^{3}} \tag{16}
\end{equation*}
$$


Equation 16 is derived based on the associating fluid theory, as explained by Chapman et al. (1990), where the association bonds are replaced by covalent, chain-forming bonds.

The Helmholtz energy change due to association is calculated for pure components from

$$
\begin{equation*}
\frac{a^{\text {assoc }}}{R T}=\sum_{\mathrm{A}}\left[\ln X^{\mathrm{A}}-\frac{X^{\mathrm{A}}}{2}\right]+\frac{1}{2} M \tag{17}
\end{equation*}
$$

where $M$ is the number of association sites on each molecule, $X^{\mathrm{A}}$ is the mole fraction of molecules NOT bonded at site A , and $\sum_{\mathrm{A}}$ represents a sum over all associating sites on the molecule.

The mole fraction of molecules NOT bonded at site A can be determined as follows

$$
X^{\mathrm{A}}=\left[1+N_{\mathrm{Av}} \sum_{\mathrm{B}} \rho X^{\mathrm{B}} \Delta^{\mathrm{AB}}\right]^{-1} \quad \text { (summation over ALL }
$$


$$
\begin{equation*}
\text { sites: } \mathrm{A}, \mathrm{~B}, \mathrm{C}, \ldots) \tag{18}
\end{equation*}
$$

where $N_{\mathrm{Av}}$ is Avogadro's number and $\rho$ is the molar density of molecules. $\Delta^{\mathrm{AB}}$ in eq 18 is the association strength that is approximated as

$$
\begin{equation*}
\Delta^{\mathrm{AB}}=g(d)^{\operatorname{seg}}\left[\exp \left(\epsilon^{\mathrm{AB}} / k T\right)-1\right]\left(\sigma^{3} \kappa^{\mathrm{AB}}\right) \tag{19}
\end{equation*}
$$

$\Delta^{\mathrm{AB}}$ is our key property characterizing the association bonds that depends on the segmental radial distribution function $g(d)^{\text {seg }}$. Since we approximate our segments as hard spheres, we approximate $g(d)^{\mathrm{seg}}$ as the hard sphere radial distribution function (Carnahan and Starling, 1969):

$$
\begin{equation*}
g(d)^{\mathrm{seg}} \approx g(d)^{\mathrm{hs}}=\frac{1-\frac{1}{2} \eta}{(1-\eta)^{3}} \tag{20}
\end{equation*}
$$


The only density dependence in $\Delta^{\mathrm{AB}}$ is given by $g(d)^{\text {seg }}$, and the only explicit temperature dependence is given by the $\epsilon^{\mathrm{AB}} / k T$, in eq 19. However, we should also note the temperature dependence of $d$ and hence, implicitly, $\eta$.

The temperature-independent segment diameter $\sigma$, used in eq 19 to make $\kappa^{\mathrm{AB}}$ dimensionless, can be calculated based on eq 4 as follows

$$
\begin{equation*}
\sigma=\left[\frac{6 \tau}{\pi N_{\mathrm{Av}}} v^{\infty}\right]^{1 / 3} \tag{21}
\end{equation*}
$$


\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-04.jpg?height=1012&width=786&top_left_y=143&top_left_x=1139}
\captionsetup{labelformat=empty}
\caption{Figure 3. Segment numbers $m$ for $n$-alkanes and polynuclear aromatics, as linear functions of molar mass, set boundaries for other hybrid classes of hydrocarbons. The branches of diamonds correspond to $n$-alkyl derivatives of the polynuclear aromatics, e.g., methyl-, ethyl-, $n$-propyl-, $n$-butylnaphthalene.}
\end{figure}

Our final equation of state can be presented as a sum of the compressibility factor terms $Z$, analogous to the Helmholtz energy terms in eq 11, as given below

$$
\begin{equation*}
Z-1=Z^{\mathrm{seg}}+Z^{\text {chain }}+Z^{\mathrm{assoc}} \tag{22}
\end{equation*}
$$

where

$$
\begin{gather*}
Z^{\mathrm{seg}}=m\left[\frac{4 \eta-2 \eta^{2}}{(1-\eta)^{3}}+\sum_{i} \sum_{j} j D_{i j}\left[\frac{u}{k T}\right]^{i}\left[\frac{\eta}{\tau}\right]^{j}\right]  \tag{23}\\
Z^{\text {chain }}=(1-m) \frac{\frac{5}{2} \eta-\eta^{2}}{(1-\eta)\left(1-\frac{1}{2} \eta\right)}  \tag{24}\\
Z^{\mathrm{assoc}}=\rho \sum_{\mathrm{A}}\left[\frac{1}{X^{\mathrm{A}}}-\frac{1}{2}\right] \frac{\partial X^{\mathrm{A}}}{\partial \rho} \tag{25}
\end{gather*}
$$


The equation of state presented above has been used to correlate vapor-liquid equilibria of over 100 real fluids. For each fluid, the pure component parameters ( $v^{\infty}, m$, and $u^{\circ} / k$ for non associating plus $\epsilon^{\mathrm{AA}}$ and $\kappa^{\mathrm{AA}}$ for associating fluids) have been regressed from the least-squares minimization using differences in calculated and experimental vapor pressure and liquid density data. Correlation results for both nonassociating and associating fluids are presented in the following two sections.

\section*{Segment Parameters for Real Nonassociating Fluids}

For each nonassociating compound, Table II lists the molar mass (MM), temperature range, $v^{\circ \circ}, m, u^{\circ} / k$, percent

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table II. Segment Parameters for Real Nonassociating Fluids}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|}
\hline \multirow{2}{*}{} & \multirow[b]{2}{*}{MM} & \multirow[b]{2}{*}{$T$ range, K} & \multirow[b]{2}{*}{$v^{\infty}, \mathrm{mL} / \mathrm{mol}$} & \multirow[b]{2}{*}{$m$} & \multirow[b]{2}{*}{$u^{\circ} / k, \mathrm{~K}$} & \multicolumn{2}{|c|}{AAD \%} & \multirow[b]{2}{*}{data source ${ }^{\text {b }}$} \\
\hline & & & & & & $p^{\text {sat }}$ & $v^{\text {liq }}$ & \\
\hline nitrogen & 28.013 & & 19.457 & 1.0 & 123.53 & & & 1 \\
\hline argon & 39.948 & & 16.29 & 1.0 & 150.86 & & & 1 \\
\hline carbon monoxide & 28.010 & 72-121 & 15.776 & 1.221 & 111.97 & 0.68 (6) ${ }^{a}$ & 0.26 (6) ${ }^{a}$ & 2 \\
\hline carbon dioxide & 44.010 & 218-288 & 13.578 & 1.417 & 216.08 & 2.8 (8) & 0.86 (8) & 3 \\
\hline chlorine & 70.906 & 180-400 & 22.755 & 1.147 & 367.44 & 1.9 (12) & 0.76 (12) & 4 \\
\hline carbon disulfide & 76.131 & 278-533 & 23.622 & 1.463 & 396.05 & 4.5 (12) & 1.6 (12) & 5 \\
\hline sulfur dioxide & 64.063 & 283-413 & 22.611 & 1.133 & 335.84 & 1.1 (8) & 2.1 (6) & 2 \\
\hline \multicolumn{9}{|c|}{$n$-Alkanes} \\
\hline methane & 16.043 & 92-180 & 21.576 & 1.000 & 190.29 & 1.4 (10) & 0.35 (10) & 1 \\
\hline ethane & 30.070 & 160-300 & 14.460 & 1.941 & 191.44 & 1.8 (15) & 1.6 (15) & 6 \\
\hline propane & 44.097 & 190-360 & 13.457 & 2.696 & 193.03 & 2.1 (10) & 1.8 (10) & 7 \\
\hline butane & 58.124 & 220-420 & 12.599 & 3.458 & 195.11 & 2.3 (12) & 2.6 (12) & 8 \\
\hline pentane & 72.151 & 233-450 & 12.533 & 4.091 & 200.02 & 1.9 (12) & 3.0 (12) & 2, 9 \\
\hline hexane & 86.178 & 243-493 & 12.475 & 4.724 & 202.72 & 2.3 (14) & 3.5 (14) & 2 \\
\hline heptane & 100.205 & 273-523 & 12.282 & 5.391 & 204.61 & 1.8 (14) & 3.4 (14) & 2 \\
\hline octane & 114.232 & 303-543 & 12.234 & 6.045 & 206.03 & 1.6 (13) & 3.4 (13) & 2 \\
\hline nonane & 128.259 & 303-503 & 12.240 & 6.883 & 203.56 & 0.86 (11) & 1.9 (7) & 2 \\
\hline decane & 142.276 & 313-573 & 11.723 & 7.527 & 205.46 & 2.2 (14) & 3.5 (14) & 2, 10 \\
\hline dodecane & 170.340 & 313-523 & 11.864 & 8.921 & 205.93 & 0.71 (12) & 3.3 (12) & 2, 10 \\
\hline tetradecane & 198.394 & 313-533 & 12.389 & 9.978 & 209.40 & 0.82 (12) & 2.8 (11) & 2, 10 \\
\hline hexadecane & 226.432 & 333-593 & 12.300 & 11.209 & 210.65 & 2.1 (14) & 3.1 (12) & 2, 10 \\
\hline eicosane & 282.556 & 393-573 & 12.000 & 13.940 & 211.25 & 2.1 (10) & 2.6 (10) & 2, 10 \\
\hline octacosane & 394.77 & 449-704 & 12.0 & 19.287 & 209.96 & 1.3 (11) & & 10 \\
\hline hexatriacontane & 506.99 & 497-768 & 12.0 & 24.443 & 208.74 & 2.2 (11) & & 10 \\
\hline tetratetracontane & 619.21 & 534-725 & 12.0 & 29.252 & 207.73 & 4.8 (10) & & 10 \\
\hline \multicolumn{9}{|c|}{Polymers} \\
\hline poly & & & & & & & & \\
\hline propylene & 15700 & 263-303 & 12.0 & 822.68 & 209.96 & & 1.0 (30) & 11 \\
\hline ethylene & 25000 & 413-473 & 12.0 & 1274.08 & 216.15 & & 2.1 (24) & 12 \\
\hline isobutylene & 36000 & 333-383 & 12.0 & 1823.95 & 267.44 & & 0.77 (30) & 12 \\
\hline \multicolumn{9}{|c|}{$n$-Alkylcyclopentanes} \\
\hline cyclopentane & 70.135 & 253-483 & 12.469 & 3.670 & 226.70 & 1.7 (13) & 1.1 (5) & 2, 10 \\
\hline methyl & 84.162 & 263-503 & 13.201 & 4.142 & 223.25 & 1.5 (13) & 1.3 (5) & 2, 10 \\
\hline ethyl & 98.189 & 273-513 & 13.766 & 4.578 & 229.04 & 1.5 (13) & 1.6 (6) & 2,10 \\
\hline propyl & 112.216 & 293-423 & 14.251 & 5.037 & 232.18 & 0.39 (8) & 1.4 (6) & 10 \\
\hline butyl & 126.244 & 314-458 & 14.148 & 5.657 & 230.61 & 0.53 (9) & 1.1 (5) & 10 \\
\hline pentyl & 140.272 & 333-483 & 13.460 & 6.503 & 225.56 & 0.45 (9) & 0.94 (4) & 10 \\
\hline \multicolumn{9}{|c|}{$n$-Alkylcyclohexanes} \\
\hline cyclohexane & 84.162 & 283-513 & 13.502 & 3.970 & 236.41 & 0.68 (13) & 1.0 (5) & 2, 10 \\
\hline methyl & 98.189 & 273-533 & 15.651 & 3.954 & 248.44 & 1.3 (14) & 3.1 (14) & 2, 10 \\
\hline ethyl & 112.216 & 273-453 & 15.503 & 4.656 & 243.16 & 0.88 (10) & 1.4 (6) & 2, 10 \\
\hline propyl & 126.243 & 313-453 & 15.037 & 5.326 & 238.51 & 0.41 (8) & 0.99 (4) & 10 \\
\hline butyl & 140.270 & 333-484 & 14.450 & 6.060 & 234.30 & 0.44 (10) & 0.90 (4) & 10 \\
\hline pentyl & 154.297 & 353-503 & 14.034 & 6.804 & 230.91 & 0.43 (11) & 0.53 (4) & 10 \\
\hline \multicolumn{9}{|c|}{Benzene Derivatives} \\
\hline benzene & 78.114 & 300-540 & 11.421 & 3.749 & 250.19 & 1.4 (13) & 2.1 (13) & 2 \\
\hline methyl (toluene) & 92.141 & 293-533 & 11.789 & 4.373 & 245.27 & 2.6 (13) & 2.9 (13) & 2, 10 \\
\hline ethyl & 106.168 & 293-573 & 12.681 & 4.719 & 248.79 & 1.2 (15) & 3.0 (15) & 2,10 \\
\hline n-propyl & 120.195 & 323-573 & 12.421 & 5.521 & 238.66 & 1.5 (14) & 2.0 (9) & 10 \\
\hline $n$-butyl & 134.212 & 293-523 & 12.894 & 6.058 & 238.19 & 0.83 (13) & 2.1 (9) & 2, 10 \\
\hline $m$-xylene & 106.168 & 309-573 & 12.184 & 4.886 & 245.88 & 2.1 (14) & 2.9 (14) & 10 \\
\hline tetralin & 132.205 & 293-673 & 13.196 & 5.163 & 279.17 & 2.1 (20) & 3.9 (20) & 13 \\
\hline biphenyl & 154.213 & 433-653 & 12.068 & 6.136 & 280.54 & 2.5 (12) & 2.8 (12) & 2 \\
\hline \multicolumn{9}{|c|}{Polynuclear Aromatics} \\
\hline naphthalene & 128.174 & 373-693 & 13.704 & 4.671 & 304.80 & 1.8 (17) & 2.6 (17) & 14 \\
\hline 1-methyl & 142.201 & 383-551 & 13.684 & 5.418 & 293.45 & 0.43 (10) & 0.50 (3) & 10 \\
\hline 1-ethyl & 156.228 & 393-563 & 12.835 & 6.292 & 276.18 & 0.29 (11) & 0.53 (3) & 10 \\
\hline 1 - $n$-propyl & 170.255 & 403-546 & 13.304 & 6.882 & 266.82 & 4.2 (6) & 2.6 (1) & 10 \\
\hline 1 - $n$-butyl & 184.282 & 413-566 & 13.140 & 7.766 & 252.11 & 11.5 (9) & 7.0 (1) & 10 \\
\hline phenanthrene & 178.234 & 373-633 & 16.518 & 5.327 & 352.00 & 0.43 (14) & 1.6 (11) & 15 \\
\hline anthracene & 178.234 & 493-673 & 16.297 & 5.344 & 352.65 & 0.31 (10) & 1.1 (6) & 15 \\
\hline pyrene & 202.255 & 553-673 & 18.212 & 5.615 & 369.38 & 4.9 (7) & & 16 \\
\hline triphenylene & 228.293 & 573-773 & 21.271 & 6.016 & 379.12 & 2.2 (11) & & 16 \\
\hline \multicolumn{9}{|c|}{Ethers} \\
\hline dimethyl & 46.069 & 179-265 & 11.536 & 2.799 & 207.83 & 1.9 (8) & & 17 \\
\hline methyl ethyl & 60.096 & 266-299 & 10.065 & 3.540 & 203.54 & 2.4 (4) & & 17 \\
\hline methyl $n$-propyl & 74.123 & 267-335 & 10.224 & 4.069 & 208.13 & 2.7 (7) & & 17 \\
\hline diethyl & 74.123 & 273-453 & 10.220 & 4.430 & 191.92 & 2.4 (10) & 2.2 (10) & 2 \\
\hline phenyl & 170.212 & 523-633 & 12.100 & 6.358 & 276.13 & 0.37 (7) & 1.5 (7) & 2 \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table II (Continued)}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|}
\hline \multirow{2}{*}{} & \multirow[b]{2}{*}{MM} & \multirow[b]{2}{*}{$T$ range, K} & \multirow[b]{2}{*}{$v^{\infty}, \mathrm{mL} / \mathrm{mol}$} & \multirow[b]{2}{*}{$m$} & \multirow[b]{2}{*}{$u^{\circ} / k, \mathrm{~K}$} & \multicolumn{2}{|c|}{AAD \%} & \multirow[b]{2}{*}{data source ${ }^{\text {b }}$} \\
\hline & & & & & & $p^{\text {sat }}$ & $v^{\text {liq }}$ & \\
\hline & \multicolumn{8}{|c|}{Ketones} \\
\hline dimethyl (acetone) & 58.080 & 273-492 & 7.765 & 4.504 & 210.92 & 2.3 (10) & 1.0 (5) & 2,18 \\
\hline methyl ethyl & 72.107 & 257-376 & 11.871 & 4.193 & 229.99 & 1.3 (8) & & 17 \\
\hline methyl $n$-propyl & 86.134 & 274-399 & 11.653 & 4.644 & 230.40 & 2.0 (8) & & 17 \\
\hline diethyl & 86.134 & 275-399 & 10.510 & 4.569 & 235.24 & 1.4 (8) & & 17 \\
\hline \multicolumn{9}{|c|}{Tertiary Amines} \\
\hline trimethylamine & 59.111 & 193-277 & 14.102 & 3.459 & 196.09 & 0.90 (16) & & 19 \\
\hline triethylamine & 101.192 & 323-368 & 11.288 & 5.363 & 201.31 & 0.70 (5) & & 19 \\
\hline \multicolumn{9}{|c|}{Esters} \\
\hline methanoate & & & & & & & & \\
\hline methyl & 60.046 & 225-324 & 7.548 & 3.886 & 215.48 & 0.61 (8) & 0.53 (5) & 17 \\
\hline ethyl & 74.073 & 242-348 & 7.954 & 4.727 & 202.72 & 0.34 (8) & 1.0 (6) & 17 \\
\hline $n$-propyl & 88.100 & 262-377 & 8.671 & 5.276 & 203.98 & 0.71 (8) & 1.5 (7) & 17 \\
\hline $n$-butyl & 102.127 & 279-403 & 10.100 & 5.460 & 212.34 & 2.1 (8) & 1.5 (6) & 17 \\
\hline ethanoate & & & & & & & & \\
\hline methyl & 74.073 & 244-498 & 7.366 & 4.918 & 200.58 & 3.1 (12) & 2.9 (10) & 17, 20 \\
\hline ethyl & 88.100 & 273-493 & 7.897 & 5.566 & 196.19 & 1.5 (12) & 3.0 (12) & 2 \\
\hline $n$-propyl & 102.127 & 278-542 & 8.637 & 6.106 & 197.94 & 1.9 (11) & 2.5 (11) & 17, 20 \\
\hline $n$-butyl & 116.154 & 293-413 & 10.829 & 5.918 & 212.11 & 1.5 (7) & 0.82 (5) & 17 \\
\hline propanoate & & & & & & & & \\
\hline methyl & 88.100 & 261-512 & 7.991 & 5.493 & 199.61 & 1.7 (11) & 3.2 (10) & 17, 20 \\
\hline ethyl & 102.127 & 277-538 & 8.621 & 6.064 & 197.45 & 1.9 (11) & 3.1 (11) & 17, 20 \\
\hline $n$-propyl & 116.154 & 293-413 & 10.332 & 6.090 & 207.13 & 1.3 (7) & 1.4 (6) & 17 \\
\hline butanoate & & & & & & & & \\
\hline methyl & 102.127 & 285-533 & 8.634 & 6.176 & 196.83 & 1.3 (15) & 1.4 (5) & 17 \\
\hline ethyl & 116.154 & 298-423 & 11.273 & 5.675 & 214.04 & 2.9 (8) & 1.2 (5) & 17 \\
\hline $n$-propyl & 130.181 & 316-445 & 10.575 & 6.713 & 205.67 & 2.6 (8) & 1.2 (5) & 17 \\
\hline \multicolumn{9}{|c|}{Alkenes} \\
\hline ethene & 28.054 & 133-263 & 18.157 & 1.464 & 212.06 & 2.0 (8) & 0.68 (8) & 21 \\
\hline propene & 42.081 & 140-320 & 15.648 & 2.223 & 213.90 & 3.6 (10) & 1.5 (10) & 22 \\
\hline 1-butene & 56.108 & 203-383 & 13.154 & 3.162 & 202.49 & 1.8 (10) & 2.4 (10) & 2, 10 \\
\hline 1 -hexene & 84.156 & 213-403 & 12.999 & 4.508 & 204.71 & 2.3 (11) & 2.8 (11) & 2, 10 \\
\hline \multicolumn{9}{|c|}{Chlorinated Hydrocarbons} \\
\hline chloromethane & 50.488 & 213-333 & 10.765 & 2.377 & 238.37 & 0.75 (7) & 0.82 (7) & 2 \\
\hline dichloromethane & 84.933 & 230-333 & 10.341 & 3.114 & 253.03 & 2.2 (7) & 0.99 (7) & 17 \\
\hline trichloromethane & 119.378 & 244-357 & 10.971 & 3.661 & 240.31 & 0.25 (7) & 1.1 (6) & 17 \\
\hline tetrachloromethane & 153.823 & 273-523 & 13.730 & 3.458 & 257.46 & 1.1 (14) & 2.5 (14) & 2 \\
\hline chloroethane & 64.515 & 212-440 & 11.074 & 3.034 & 229.58 & 3.1 (13) & 3.4 (13) & 17, 20 \\
\hline 1-chloropropane & 78.542 & 238-341 & 11.946 & 3.600 & 229.14 & 0.50 (8) & 0.94 (6) & 17 \\
\hline 1-chlorobutane & 92.569 & 262-375 & 12.236 & 4.207 & 227.88 & 0.40 (8) & 1.2 (6) & 17 \\
\hline 1-chlorohexane & 120.623 & 306-435 & 12.422 & 5.458 & 225.82 & 0.33 (8) & 1.0 (4) & 17 \\
\hline chlorobenzene & 112.559 & 273-543 & 13.093 & 3.962 & 276.72 & 1.5 (15) & 2.7 (15) & 2 \\
\hline
\end{tabular}
\end{table}

\footnotetext{
${ }^{a}$ Numbers in parentheses indicate number of data points used in the correlation. ${ }^{b}$ (1) Parameter values are taken from Kreglewski (1984) without fitting. (2) Vargaftik, N. B. Tables on the Thermophysical Properties of Liquids and Gases; John Wiley \& Sons: New York, 1975. (3) IUPAC. Carbon Dioxide. International Tables of Fluid State; Pergamon Press: Oxford, 1976; Vol. 3. (4) IUPAC. Chlorine. International Tables of the Fluid State; Pergamon Press: Oxford, 1985; Vol. 8 (tentative tables). (5) O'Brien, L. J.; Alford, W. J. Ind. Eng. Chem. 1951, 43, 506. (6) Goodwin, R. D.; Roger, H. M.; Straty, G. C. Thermodynamic Properties of Ethane from 90 to 600 K and Pressures to 700 bar. NBS Technical Note 687; NBS: Boulder, CO, 1976. (7) Goodwin, R. D.; Haynes, W. M. Thermodynamic Properties of Propane from 85 to 700 K and Pressures to 70 Mpa ; NBS Monograph 170; NBS: Boulder, CO, 1982. (8) Haynes, W. M.; Goodwin, R. D. Thermodynamic Properties of n-Butane from 135 to 700 K and Pressures to 70 Mpa ; NBS Monograph 169; NBS: Boulder, CO, 1982. (9) Das, T. R., Reed, C. O., Jr. J. Chem. Eng. Data 1977, 22, 3. (10) Selected Values of Properties of Hydrocarbons and Related Compounds. Research Project 44 of the American Petroleum Institute and the Thermodynamic Research Center, Texas A\&M University: College Station, TX, Loose-leaf data supplements to 1989. (11) Passaglia, E.; Martin, G. M. J. Res. Natl. Bur. Stand., Sect. A 1964, 68A, 273. (12) Beret, S.; Prausnitz, J. M. Macromolecules 1975, 8, 536. (13) Kudchadker, A. P.; Kudchadker, S. A.; Wilhoit, R. C. Tetralin; API Monograph 705; API: Washington, DC, 1978. (14) Kudchadker, A. P.; Kudchadker, S. A.; Wilhoit, R. C. Naphthalene; API Monograph 707; API: Washington, DC, 1978. (15) Kudchadker, A. P.; Kudchadker, S. A.; Wilhoit, R. C. Anthracene and Phenanthrene; API Monograph 708; API: Washington, DC, 1979. (16) Kudchadker, A. P.; Kudchadker, S. A.; Wilhoit, R. C. Four-Ring Condensed Aromatic Compounds; API Monograph 709; API: Washington, DC, 1979. (17) Thermodynamic Tables for non-Hydrocarbons; Thermodynamic Research Center, Texas A\&M University: College Station, loose pages to 1988. (18) Ambrose, D.; Sprake, C. H. S.; Townsend, R. J. Chem. Thermodyn. 1974, 6, 693-700. (19) Boublik, T.; Fired, V.; Hala, E. The Vapor Pressure of Pure Substances, 2nd ed.; Elsevier, Amsterdam, 1984. (20) Perry, R. H.; Chilton, C. H. Chemical Engineer's Handbook, 5th ed.; McGraw-Hill: New York, 1973. (21) IUPAC. Ethylene. International Tables of the Fluid State; Pergamon Press: Oxford, 1976; Vol. 2. (22) IUPAC. Propylene (Propene). International Tables of the Fluid State; Pergamon Press: Oxford, 1980; Vol. 7.
}
average absolute deviation (AAD\%) in vapor pressure ( $p^{\text {sat }}$, except for polymers) and liquid molar volume ( $v^{\text {liq }}$ ), including the number of data points used in regression, and data source. The quality of fit for both vapor pressure and liquid density is as good as can be usually expected for a reasonable, three-parameter equation of state. However, our focus is not on the quality of fit but on the parameter
behavior. This is important because the key future challenge lies in estimating the equation of state parameters for polydispersed, poorly defined pseudocomponents of real fluid mixtures, rather than in fine-tuning precise predictions (however important) for well-defined pure components. Apart from the expected scatter due to inaccuracies in experimental data and fitting itself, the pa-

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-07.jpg?height=530&width=799&top_left_y=147&top_left_x=213}
\captionsetup{labelformat=empty}
\caption{Figure 4. Close-packed molar volumes $m v^{\infty}$ for $n$-alkanes and polynuclear aromatics, as linear functions of molar mass, set boundaries for other hybrid classes of hydrocarbons. The branches of diamonds correspond to $n$-alkyl derivatives of the polynuclear aromatics, e.g., methyl-, ethyl-, $n$-propyl-, $n$-butylnaphthalene.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-07.jpg?height=788&width=791&top_left_y=870&top_left_x=228}
\captionsetup{labelformat=empty}
\caption{Figure 5. Segment energies $u^{0} / k$ for $n$-alkanes and polynuclear aromatics as smooth but nonlinear functions of molar mass, set boundaries for other hybrid classes of hydrocarbons. The branches of diamonds correspond to $n$-alkyl derivatives of the polynuclear aromatics, e.g., methyl-, ethyl-, n-propyl-, n-butylnaphthalene.}
\end{figure}
rameter values reported in Table II are well-behaved and suggest predictable trends upon increasing the molar mass of similar compounds.

The segment number $m$ increases with increasing molar mass within each homologous series practically linearly. For example, $m$ for $n$-alkanes is plotted versus molar mass in Figure 2. It is reassuring to find that a single linear relationship holds not only for all the small $n$-alkanes, which is shown in the insert, but also for macromolecular chains of varying degree of branchiness, such as polypropylene, polyethylene, and polyisobutylene. It is also reassuring to find out that $m$ is essentially a linear function of molar mass for different homologous series of aromatic molecules, i.e., upon increasing the side chain length for alkylbenzenes, alkylnaphthalenes, etc., as shown in Figure 3. The plots in Figure 3 also suggest that the segment numbers $m$ for all hydrocarbons fall between two boundaries set by $n$-alkanes and plain polynuclear aromatics (PNA's) and that for a given molar mass $m$ will decrease with increasing aromaticity. This means that, if there are no accurate PVT data available, which often is the case, $m$ can be estimated from molar mass only.

$$
m=A^{(1)}+A^{(2)} \mathrm{MM}
$$


\begin{table}
\captionsetup{labelformat=empty}
\caption{Table III. Correlation of the Segment Number $m$ for Hydrocarbons}
\begin{tabular}{|l|l|l|l|}
\hline & $A^{(1)}$ & $A^{(2)}$ & MM range in fitting \\
\hline $n$-alkanes & 0.70402 & 0.046647 & 16-619 \\
\hline polynuclear aromatics & 2.6733 & 0.014781 & 78-202 \\
\hline $n$-alkylcyclopentanes & 0.82360 & 0.039044 & 70-140 \\
\hline $n$-alkylcyclohexanes & -0.010038 & 0.043096 & 84-154 \\
\hline $n$-alkylbenzenes & 0.51928 & 0.041112 & 78-134 \\
\hline $1-n$-alkylnaphthalenes & -2.3190 & 0.054566 & 128-184 \\
\hline
\end{tabular}
\end{table}

$$
m v^{00}=A^{(1)}+A^{(2)} \mathrm{MM}
$$


\begin{table}
\captionsetup{labelformat=empty}
\caption{Table IV. Correlation of the Close-Packed Molar Volume $m v^{\circ \circ}$ for Hydrocarbons}
\begin{tabular}{|l|l|l|l|}
\hline & $A^{(1)}$ & $A^{(2)}$ & MM range in fitting \\
\hline $n$-alkanes & 11.888 & 0.55187 & 16-619 \\
\hline polynuclear aromatics & 5.0117 & 0.46942 & 78-202 \\
\hline $n$-alkylcyclopentanes & 4.2053 & 0.59817 & 70-140 \\
\hline $n$-alkylcyclohexanes & 3.6438 & 0.59961 & 84-154 \\
\hline $n$-alkylbenzenes & -6.1400 & 0.62468 & 78-134 \\
\hline 1 - $n$-alkylnaphthalenes & -21.619 & 0.66647 & 128-184 \\
\hline
\end{tabular}
\end{table}

$$
u^{0} / k=A^{(1)}-A^{(2)} \exp \left[-A^{(3)} \mathrm{MM}\right]
$$


\begin{table}
\captionsetup{labelformat=empty}
\caption{Table V. Correlation of the Segment Energy $\boldsymbol{u}^{\circ} / \boldsymbol{k}$ for n-Alkanes and Polynuclear Aromatics}
\begin{tabular}{lcccc}
\hline & $A^{(1)}$ & $A^{(2)}$ & $A^{(3)}$ & \begin{tabular}{c} 
MM range \\
in fitting
\end{tabular} \\
\hline$n$-alkanes & 210.0 & 26.886 & 0.013341 & $16-619$ \\
polynuclear aromatics & 472.84 & 357.02 & 0.0060129 & $78-228$
\end{tabular}
\end{table}

$$
u^{0} / k=A^{(1)}-A^{(2)} \mathrm{MM}
$$


\begin{table}
\captionsetup{labelformat=empty}
\caption{Table VI. Correlation of the Segment Energy $u^{\circ} / k$ for Other Hydrocarbons}
\begin{tabular}{lcll}
\hline & $A^{(1)}$ & \multicolumn{1}{c}{$A^{(2)}$} & \begin{tabular}{c} 
MM range \\
in fitting
\end{tabular} \\
\hline$n$-alkylcyclopentane & 239.56 & 0.085618 & $98-140$ \\
$n$-alkylcyclohexanes & 278.59 & 0.31311 & $98-154$ \\
$n$-alkylbenzenes & 267.39 & 0.21825 & $78-134$ \\
$1-n$-alkylnaphthalenes & 425.70 & 0.94111 & $128-184$
\end{tabular}
\end{table}

We note that the effective segment numbers $m$ reported for hydrocarbons in Table II are systematically smaller than the corresponding carbon numbers. A physical picture of a $n$-alkane therefore is that of a chain of overlapping spherical segments. Hence, the segment volume $v^{\infty}$ should correspond to the volume occupied by such segments. Expectedly, the segment volume $v^{\circ \circ}$ for methane is the largest among alkanes because it corresponds to a single $(m=1) \mathrm{CH}_{4}$ unit, and it gradually decreases upon increasing the chain length, reaching an asymptotic value of 12 (set 12.0 for $\mathrm{C}_{20+}$ ) for long chains.

Since $v^{\circ \circ}$ does not vary much with chain length and remains constant for long chains and since $m$ is a linear function of the molar mass, the product $m v^{\infty}$ (volume occupied by a mole of molecules in a close-packed arrangement) is also a linear function of the molar mass, as shown in Figure 4. As for $m$ alone (Figure 3), $n$-alkanes and plain polynuclear aromatics set the boundaries for the $m v^{\circ 0}$ domain for all the hydrocarbons. Apart from testing these reassuring trends, a practical reason for developing a correlation for $m v^{\circ \circ}$ is to provide the basis for estimating $v^{\infty}$, if there are no accurate PVT data available, for a given $m$ and molar mass.

A similar molar mass correlation can be developed for the segment energy $u^{\circ} / k$, which is shown in Figure 5. As for $m$ and $m v^{\circ \circ}, n$-alkanes and plain polynuclear aromatics

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table VII. Monomer Fractions $\boldsymbol{X}^{\mathbf{A}}$ for Different Bonding Types}
\begin{tabular}{|l|l|l|l|}
\hline type & $\Delta$ approximations & $X^{\mathrm{A}}$ approximations & $X^{A}$ \\
\hline 1 & $\Delta^{\mathrm{AA}} \neq 0$ & & $\frac{-1+(1+4 \rho \Delta)^{1 / 2}}{2 \rho \Delta}$ \\
\hline 2A & $\Delta^{\mathrm{AA}}=\Delta^{\mathrm{AB}}=\Delta^{\mathrm{BB}} \neq 0$ & $X^{\mathrm{A}}=X^{\mathrm{B}}$ & $\frac{-1+(1+8 \rho \Delta)^{1 / 2}}{4 \rho \Delta}$ \\
\hline 2B & $$
\begin{aligned}
& \Delta^{\mathrm{AA}}=\Delta^{\mathrm{BB}}=0 \\
& \Delta^{\mathrm{AB}} \neq 0
\end{aligned}
$$ & $X^{\mathrm{A}}=X^{\mathrm{B}}$ & $\frac{-1+(1+4 \rho \Delta)^{1 / 2}}{2 \rho \Delta}$ \\
\hline 3A & $\Delta^{\mathrm{AA}}=\Delta^{\mathrm{AB}}=\Delta^{\mathrm{BB}}=\Delta^{\mathrm{AC}}=\Delta^{\mathrm{BC}}=\Delta^{\mathrm{CC}} \neq 0$ & $X^{\mathrm{A}}=X^{\mathrm{B}}=X^{\mathrm{C}}$ & $\frac{-1+(1+12 \rho \Delta)^{1 / 2}}{6 \rho \Delta}$ \\
\hline 3B & $$
\begin{aligned}
& \Delta^{\mathrm{AA}}=\Delta^{\mathrm{AB}}=\Delta^{\mathrm{BB}}=\Delta^{\mathrm{CC}}=0 \\
& \Delta^{\mathrm{AC}}=\Delta^{\mathrm{BC}} \neq 0
\end{aligned}
$$ & $$
\begin{aligned}
& X^{\mathrm{A}}=X^{\mathrm{B}} \\
& X^{\mathrm{C}}=2 X^{\mathrm{A}}-1
\end{aligned}
$$ & $\frac{-(1-\rho \Delta)+\left((1+\rho \Delta)^{2}+4 \rho \Delta\right)^{1 / 2}}{4 \rho \Delta}$ \\
\hline 4A & $$
\begin{gathered}
\Delta^{\mathrm{AA}}=\Delta^{\mathrm{AB}}=\Delta^{\mathrm{BB}}=\Delta^{\mathrm{AC}}=\Delta^{\mathrm{BC}}=\Delta^{\mathrm{CC}}=\Delta^{\mathrm{AD}}=\Delta^{\mathrm{BD}}=\Delta^{\mathrm{CD}}=\Delta^{\mathrm{DD}} \neq
\end{gathered}
$$ & $X^{\mathrm{A}}=X^{\mathrm{B}}=X^{\mathrm{C}}=X^{\mathrm{D}}$ & $\frac{-1+(1+16 \rho \Delta)^{1 / 2}}{8 \rho \Delta}$ \\
\hline 4B & $$
\begin{aligned}
& \Delta^{\mathrm{AA}}=\Delta^{\mathrm{AB}}=\Delta^{\mathrm{BB}}=\Delta^{\mathrm{AC}}=\Delta^{\mathrm{BC}}=\Delta^{\mathrm{CC}}=\Delta^{\mathrm{DD}}=0 \\
& \Delta^{\mathrm{AD}}=\Delta^{\mathrm{BD}}=\Delta^{\mathrm{CD}} \neq 0
\end{aligned}
$$ & $$
\begin{aligned}
& X^{\mathrm{A}}=X^{\mathrm{B}}=X^{\mathrm{C}} \\
& X^{\mathrm{D}}=3 X^{\mathrm{A}}-2
\end{aligned}
$$ & $\frac{-(1-2 \rho \Delta)+\left((1+2 \rho \Delta)^{2}+4 \rho \Delta\right)^{1 / 2}}{6 \rho \Delta}$ \\
\hline 4C & $$
\begin{aligned}
& \Delta^{\mathrm{AA}}=\Delta^{\mathrm{AB}}=\Delta^{\mathrm{BB}}=\Delta^{\mathrm{CC}}=\Delta^{\mathrm{CD}}=\Delta^{\mathrm{DD}}=0 \\
& \Delta^{\mathrm{AC}}=\Delta^{\mathrm{AD}}=\Delta^{\mathrm{BC}}=\Delta^{\mathrm{BD}} \neq 0
\end{aligned}
$$ & $X^{\mathrm{A}}=X^{\mathrm{B}}=X^{\mathrm{C}}=X^{\mathrm{D}}$ & $\frac{-1+(1+8 \rho \Delta)^{1 / 2}}{4 \rho \Delta}$ \\
\hline
\end{tabular}
\end{table}

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table VIII. Types of Bonding in Real Associating Fluids ${ }^{a}$}
\begin{tabular}{|l|l|l|l|}
\hline species & formula & rigorous type & assigned type \\
\hline acid & <smiles>CC1=COC(C)=OOO1</smiles> & 1 & 1 \\
\hline alkanol & ![](https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-08.jpg?height=83\&width=87\&top_left_y=1309\&top_left_x=387) & 3B & 2B \\
\hline water & <smiles>C1C[AsH2]1</smiles> & 4C & 3B \\
\hline amines & & & \\
\hline tertiary & ![](https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-08.jpg?height=90\&width=104\&top_left_y=1522\&top_left_x=387) & 1 & non-self-associating \\
\hline secondary & <smiles>C[NH+](C)C</smiles> & 2B & 2B \\
\hline primary & <smiles>CN1C[13CH2]1</smiles> & 3B & 3B \\
\hline ammonia & ![](https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-08.jpg?height=79\&width=125\&top_left_y=1805\&top_left_x=391) & 4B & 3B \\
\hline
\end{tabular}
\end{table}
set the boundaries for the $u^{\circ} / k$ domain for all the hydrocarbons. Unlike $m$ and $m v^{\infty}$, however, although smooth, $u^{\circ} / k$ is nonlinear with respect to the molar mass.

For the ease of estimating, $m, m v^{\circ \circ}$, and $u^{\circ} / k$ have been regressed as simple functions of the molar mass (MM) for many homologous series. For example,

$$
\begin{align*}
m=A^{(1)}+A^{(2)} \mathrm{MM} \quad \text { for all hydrocarbons }  \tag{26}\\
m v^{00}=A^{(1)}+A^{(2)} \mathrm{MM} \quad \text { for all hydrocarbons }  \tag{27}\\
u^{0} / k=A^{(1)}-A^{(2)} \exp \left(-A^{(3)} \mathrm{MM}\right) \\
\quad \text { for } n \text {-alkanes and PNA's }  \tag{28}\\
u^{0} / k=A^{(1)}-A^{(2)} \mathrm{MM} \quad \text { for other hydrocarbons } \tag{29}
\end{align*}
$$


We note that eq 29 is only a linear approximation that is valid up to the MM of a corresponding $n$-alkane; for higher MM values, we set $u^{\circ} / k$ to be the same as that for a corresponding $n$-alkane. This can easily be tested and ad-
justed when accurate data become available for hybrid hydrocarbons, such as aromatic rings with long side chains.

The solid lines and curves shown in Figures 3-5 have been predicted from eqs 26-29. Specific values of the regression coefficients $A^{(i)}$ are reported in Tables III-VI. This way we have a useful method for estimating all the equation of state parameters for nonassociating pure fluids where no accurate data are available and, especially, for poorly defined pseudocomponents where only average molar mass and average aromaticity are available. Although this method is primarily applied to predicting phase equilibria in mixtures (Huang and Radosz, 1990), this method can also be used to estimate pure component properties, such as vapor pressures, densities, and critical properties.

\section*{Segment and Site-Site Parameters for Real Self-Associating Fluids}

Vapor pressure and liquid density correlations for self-associating fluids require the use of the $a^{\text {assoc }}$ term (eq 17 ; zero for the nonassociating fluids). Before we can calculate $a^{\text {assoc }}$, however, we have to define and specify all the non-zero site-site interactions and hence non-zero $\Delta$ 's (eq 19) needed to determine the monomer fractions $X^{\mathrm{A}}$ (eq 18). While eq 18 is not $X^{\mathrm{A}}$ explicit in general, it can be made $X^{\mathrm{A}}$ explicit in many specific cases. Examples of one-, two-, three-, and four-site models and $\Delta$ approximations are provided in Table VII along with analytical $X^{\mathrm{A}}$ expressions for each model that can be used in place of eq 18 .

In order to select a proper expression for $X^{\mathrm{A}}$ from Table VII, one has to assign association sites and non-zero sitesite interactions. Ideally, one should have detailed, independent data from spectroscopy on the association strength for each site-site interaction. Since such data are scarce and usually qualitative (we are addressing this problem in a separate project), one has to make simplifying approximations aimed at reducing the number of parameters that have to be fitted. For example, different hydrogen bonds are assumed to be equivalent, e.g., $\Delta^{\mathrm{AC}}= \Delta^{\mathrm{BC}}$, which means that different sites A and B form equivalent bonds with C , or double hydrogen bonds are

\begin{table}
\captionsetup{labelformat=empty}
\caption{Table IX. Segment and Site-Site Parameters for Real Self-Associating Fluids ${ }^{a}$}
\begin{tabular}{|l|l|l|l|l|l|l|l|l|l|l|}
\hline \multirow{2}{*}{} & \multirow[b]{2}{*}{MM} & \multirow[b]{2}{*}{$T$ range, K} & \multirow{2}{*}{$v^{\infty}$, mL/mol} & \multirow[b]{2}{*}{$m$} & \multirow[b]{2}{*}{$u^{\circ} / k, \mathrm{~K}$} & \multirow[b]{2}{*}{$\epsilon / k, \mathrm{~K}$} & \multirow[b]{2}{*}{$10^{2}{ }_{\kappa}$} & \multicolumn{2}{|c|}{AAD \%} & \multirow[b]{2}{*}{data source ${ }^{\text {b }}$} \\
\hline & & & & & & & & $p^{\text {sat }}$ & $v^{\text {liq }}$ & \\
\hline \multicolumn{11}{|c|}{(Model 3B)} \\
\hline ammonia & 17.032 & 200-380 & 10.0 & 1.503 & 283.18 & 893.1 & 3.270 & 1.6 (10) ${ }^{\text {a }}$ & 3.2 (10) ${ }^{\text {a }}$ & 1 \\
\hline water & 18.015 & 283-613 & 10.0 & 1.179 & 528.17 & 1809 & 1.593 & 1.3 (13) & 3.2 (13) & 1 \\
\hline hydrogen sulfide & 34.080 & 284-369 & 10.0 & 1.935 & 226.38 & 804.1 & 0.911 & 0.69 (14) & 1.4 (14) & 2 \\
\hline \multicolumn{11}{|c|}{Alkanols (Model 2B)} \\
\hline methanol & 32.042 & 273-487 & 12.0 & 1.776 & 216.13 & 2714 & 4.856 & 0.83 (12) & 0.88 (12) & 1, 3 \\
\hline ethanol & 46.069 & 302-483 & 12.0 & 2.457 & 213.48 & 2759 & 2.920 & 0.86 (10) & 0.83 (10) & 1 \\
\hline 1-propanol & 60.096 & 293-493 & 12.0 & 3.240 & 225.68 & 2619 & 1.968 & 0.16 (11) & 1.2 (11) & 1, 3 \\
\hline 1-butanol & 74.123 & 313-493 & 12.0 & 3.971 & 225.96 & 2605 & 1.639 & 0.23 (10) & 1.0 (6) & 3 \\
\hline 1-pentanol & 88.150 & 333-513 & 12.0 & 4.642 & 225.15 & 2587 & 1.637 & 0.32 (10) & 1.1 (5) & 3 \\
\hline 1-hexanol & 102.177 & 343-573 & 12.0 & 5.315 & 222.88 & 2556 & 1.873 & 0.77 (13) & 1.22 (5) & 3 \\
\hline 1-heptanol & 116.204 & 353-573 & 12.0 & 6.028 & 221.62 & 2579 & 1.654 & 0.61 (12) & 0.96 (4) & 3 \\
\hline 1-octanol & 130.231 & 373-593 & 12.0 & 6.642 & 220.69 & 2532 & 2.001 & 1.0 (13) & 1.0 (4) & 3 \\
\hline 1-nonanol & 144.258 & 383-613 & 12.0 & 7.322 & 219.18 & 2516 & 2.249 & 1.1 (14) & 0.47 (4) & 3 \\
\hline 1-decanol & 158.285 & 393-633 & 12.0 & 8.024 & 217.14 & 2448 & 2.892 & 2.1 (14) & 0.57 (4) & 3 \\
\hline 2-propanol & 60.096 & 273-373 & 12.0 & 3.249 & 202.94 & 2670 & 2.095 & 0.27 (11) & 0.96 (11) & 1, 3 \\
\hline 2-butanol & 74.123 & 293-393 & 12.0 & 3.933 & 216.41 & 2457 & 1.634 & 0.32 (11) & 1.2 (11) & 3 \\
\hline 2-methyl-1-propanol & 74.123 & 293-403 & 12.0 & 4.028 & 232.90 & 2698 & 0.4032 & 0.58 (12) & 1.4 (12) & 3 \\
\hline 2-methyl-2-propanol & 74.123 & 303-373 & 12.0 & 3.966 & 202.35 & 2515 & 1.118 & 0.21 (8) & 0.79 (8) & 3 \\
\hline phenol & 94.114 & 346-482 & 12.0 & 4.103 & 290.08 & 1894 & 4.315 & 0.24 (9) & 0.02 (1) & 3 \\
\hline \multicolumn{11}{|c|}{Acids (Model 1)} \\
\hline methanoic & 46.025 & 293-393 & 15.5 & 1.341 & 333.28 & 7522 & 0.1625 & 0.62 (6) & 0.49 (5) & 3 \\
\hline ethanoic & 60.052 & 313-553 & 14.5 & 2.132 & 290.73 & 3941 & 3.926 & 1.6 (13) & 0.69 (13) & 1 \\
\hline n-propanoic & 74.080 & 313-463 & 13.5 & 3.084 & 296.03 & 3400 & 0.8193 & 0.25 (9) & 0.10 (9) & 3 \\
\hline $n$-butanoic & 88.107 & 333-493 & 13.0 & 3.800 & 268.93 & 4155 & 0.3700 & 0.30 (9) & 0.84 (9) & 3 \\
\hline $n$-pentanoic & 102.134 & 353-483 & 12.0 & 4.719 & 248.63 & 4322 & 0.5103 & 0.21 (8) & 1.0 (8) & 3 \\
\hline $n$-hexanoic & 116.161 & 372-504 & 12.0 & 5.482 & 243.39 & 4683 & 0.2352 & 0.44 (7) & & 3 \\
\hline $n$-heptanoic & 130.187 & 385-522 & 12.0 & 6.059 & 241.50 & 4734 & 0.2309 & 0.46 (7) & & 3 \\
\hline $n$-octanoic & 144.215 & 399-540 & 12.0 & 6.628 & 240.41 & 4745 & 0.2430 & 0.60 (7) & & 3 \\
\hline $n$-nonanoic & 158.242 & 411-557 & 12.0 & 7.274 & 238.97 & 4798 & 0.2005 & 0.44 (7) & & 3 \\
\hline $n$-decanoic & 172.269 & 423-572 & 12.0 & 7.847 & 237.10 & 4906 & 0.1844 & 0.60 (7) & & 3 \\
\hline benzoic & 122.124 & 405-523 & 12.0 & 4.608 & 272.66 & 5930 & 0.3149 & 0.66 (8) & 0.43 (4) & 3 \\
\hline \multicolumn{11}{|c|}{Primary Amines (Model 3B)} \\
\hline methanamine & 31.057 & 204-413 & 12.0 & 2.026 & 226.86 & 1045 & 6.310 & 0.22 (13) & 0.38 (13) & 3 \\
\hline ethanamine & 45.084 & 221-433 & 12.0 & 2.781 & 208.61 & 940.3 & 10.65 & 0.27 (13) & 0.22 (12) & 3 \\
\hline 1-propanamine & 59.111 & 243-473 & 12.0 & 3.450 . & 211.36 & 779.1 & 17.94 & 1.3 (13) & 1.5 (10) & 3 \\
\hline 1-butanamine & 73.138 & 265-503 & 12.0 & 4.062 & 210.91 & 895.4 & 15.08 & 2.2 (13) & 2.6 (10) & 3 \\
\hline 1-pentamine & 87.165 & 285-401 & 12.0 & 4.773 & 215.81 & 746.1 & 15.15 & 2.3 (7) & 2.0 (7) & 3 \\
\hline 1-hexanamine & 101.192 & 307-429 & 12.0 & 5.476 & 215.73 & 722.0 & 16.63 & 0.84 (7) & 1.7 (6) & 3 \\
\hline 1-heptanamine & 115.219 & 325-457 & 12.0 & 6.153 & 218.62 & 553.9 & 16.57 & 1.5 (7) & 0.99 (3) & 3 \\
\hline aniline & 93.129 & 350-673 & 12.0 & 4.034 & 288.10 & 1269 & 11.27 & 2.6 (16) & 3.5 (16) & 3 \\
\hline \multicolumn{11}{|c|}{Secondary Amines (Model 2B)} \\
\hline dimethylamine & 45.084 & 208-436 & 12.0 & 2.637 & 208.23 & 1064 & 15.61 & 0.73 (12) & & 4 \\
\hline diethylamine & 73.138 & 240-483 & 12.0 & 3.996 & 212.62 & 581.3 & 15.36 & 3.2 (11) & & 4 \\
\hline
\end{tabular}
\end{table}

\footnotetext{
${ }^{\mathrm{a}}$ Numbers in parentheses indicate number of data points used in the correlation. ${ }^{b}$ (1) Vargaftik, N. B. Tables on the Thermophysical Properties of Liquids and Gases; John Wiley \& Sons: New York, 1975. (2) Sage, B. H.; Lacey, W. N. Some Properties of the Light Hydrocarbons, Hydrogen Sulfide, and Carbon Dioxide; API Monograph 37; API: New York, 1955. (3) Thermodynamic Tables for nonHydrocarbons; Thermodynamic Research Center, Texas A\&M University: College Station, TX, loose pages to 1988. (4) Perry, R. H.; Chilton, C. H. Chemical Engineer's Handbook, 5th ed.; McGraw-Hill: New York, 1973.
}
assumed to be represented as strong single bonds, e.g., between carboxylic groups. Other examples of rigorous and approximated sets of site-site interactions for selfassociating molecules that are used in this work are given in Table VIII. The sets defined as rigorous in Table VIII include all the electron-donor and -acceptor sites on each molecule.

An example for alkanols will illustrate the use of Tables VII and VIII. Each hydroxylic group ( OH ) in alkanols, in principle, has three association sites, labeled A and B on oxygen and C on hydrogen, as shown in Table VIII. The association strength $\Delta$ due to the like, oxygen-oxygen or hydrogen-hydrogen ( $\mathrm{AA}, \mathrm{AB}, \mathrm{BB}$, and CC ) interactions is assumed to be equal to zero. The only non-zero $\Delta$ is due to the unlike (AC and BC) interactions, which moreover are considered to be equivalent. Hence, the rigorous type selected for alkanols in Table VII is 3B. Another approximation is to allow only one site on oxygen (A) and one site on hydrogen (B). In this case, the assigned type for alkanols (Table VIII) is 2B, where the only non-zero
interactions AB and BA are equivalent. Although we tested both types of site assignment for alkanols, 3 B and 2B, we felt that the limited experimental data used for fitting did not justify the use of the rigorous type 3B. Therefore, we report results for the alkanols of type 2B in Table IX.

For each self-associating compound, Table IX lists the temperature range, $v^{\infty}, m, u^{\circ} / k, \epsilon^{\mathrm{AA}} / k, \kappa^{\mathrm{AA}}$, AAD\% in vapor pressure, AAD \% in liquid density, including the number of data points used in regression, and data source. Only $m, u^{\circ} / k, \epsilon^{\mathrm{AA}} / k$, and $\kappa^{\mathrm{AA}}$ have been allowed to be adjustable. The segment volumes $v^{\circ \circ}$ have been set equal to 12.0 , except for ammonia, water, and hydrogen sulfide where it has been set equal to 10.0 and except for small carboxylic acids where $v^{\circ \circ}$ has been made similar to those of corresponding $n$-alkanes.

Similar to the trends observed for the nonassociating fluids, the segment number $m$ increases with increasing molar mass within each homologous series, for example, for chain acids and alkanols.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-10.jpg?height=1247&width=760&top_left_y=142&top_left_x=230}
\captionsetup{labelformat=empty}
\caption{Figure 6. Plot of the associating energies $\epsilon / k$ and segment energies $u^{\circ} / k$ versus molar masses of organic compounds in homologous series. The ratio of the former to the latter is roughly 10 to 1 .}
\end{figure}

The segment energies $u^{\circ} / k$ are close to 200 K and, hence, are similar to those derived for nonassociating chain molecules, as shown in Figure 6. Especially, $u^{\circ} / k$ for amines and alkanols essentially matches $u^{\circ} / k$ for $n$-alkanes. Somewhat larger values for carboxylic acids are due to the one-site approximation of the double hydrogen bond. We tested this by allowing two and three sites on acid molecules and, as a result, obtaining $u^{\circ} / k$ values that were very close to 200 K .

Figure 6 also shows the association energies $\epsilon^{\mathrm{AA}}$ for acids (one-site approximation), alkanols, and amines. As expected, the association energies decrease upon going from acids to amines. The ratios of $\epsilon^{\mathrm{AA}} / u^{\mathrm{o}}$ are also in the reasonable range (of the order of 10 ).

\section*{Example: Critical Constants Can Be Estimated for Large Molecules}

While the critical temperature and pressure are commonly used in numerous engineering correlations, such as those based on cubic equations of state and corresponding states, they cannot be measured for high molar mass compounds because of thermal decomposition. Therefore, there have been various useful empirical methods proposed, such as that of Lee and Kesler (1975), that allow for extrapolating the critical temperature and pressure to high molar mass. An alternative, proposed by Mohan and Peng (1987), is to use a reliable equation of state for such extrapolation, which at least can be tested on other properties in the high molar mass range.

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-10.jpg?height=507&width=832&top_left_y=145&top_left_x=1116}
\captionsetup{labelformat=empty}
\caption{Figure 7. Critical temperatures for $n$-alkanes predicted by our equation of state falling between those predicted by others.}
\end{figure}

\begin{figure}
\includegraphics[alt={},max width=\textwidth]{https://cdn.mathpix.com/cropped/fd3dcf64-363a-4971-9d7b-d6d05332f16a-10.jpg?height=541&width=836&top_left_y=767&top_left_x=1109}
\captionsetup{labelformat=empty}
\caption{Figure 8. Critical pressures for $n$-alkanes predicted by our equation of state agreeing with those of Mohan and Peng (1987).}
\end{figure}

Mohan and Peng used the Perturbed Hard Chain equation of state (Cotterman et al., 1986) to extrapolate the critical properties for long chain alkanes up to polyethylene. As a result, they had to extrapolate all three parameters $C, V^{*}$, and $T^{*}$ (Mohan and Peng verified that the polyethylene density was correctly predicted). By contrast, the only parameter in our equation of state that has to be extrapolated is $m$, which is linear with respect to MM. Therefore, we found our equation of state to be particularly suitable for estimating the critical properties of large molecules.

Like all the analytical equations of state, this one overpredicts the critical temperature and critical pressure. However, since the differences between calculated and predicted values have been very consistent for all the $n$-alkanes for which there are experimental data, simple correlations have been developed as follows:

$$
\begin{align*}
& \ln T_{\mathrm{c}}=1.0169 \ln T_{\mathrm{c}}^{\mathrm{eos}}-0.14703  \tag{30}\\
& \ln P_{\mathrm{c}}=0.89858 \ln P_{\mathrm{c}}^{\mathrm{eos}}+0.18496 \tag{31}
\end{align*}
$$

where $T_{\mathrm{c}}$ is the critical temperature in kelvin, $P_{\mathrm{c}}$ is the critical pressure in bar, and the superscript eos means predicted from the equation of state, using a simplified set of parameters that are specialized for large molecules: $m =0.05096 \mathrm{MM}, v^{\infty}=12.0$, and $u^{\circ} / k=210$. Equations 30 and 31 are applicable to all the $n$-alkanes, including macromolecules, down to about $\mathrm{C}_{10}$.

Sample results are shown in Figure 7 for the critical temperature and in Figure 8 for the critical pressure. The pairs of solid curves shown in Figures 7 and 8 have been calculated from eqs 30 and 31, respectively. Each pair of curves corresponds to a $99.5 \%$ confidence band. Our
predicted critical temperatures agree well with the experimental data and with those predicted by Huang et al. (1988) but deviate somewhat from those predicted by Mohan and Peng (1987). Our predicted critical pressures on the other hand agree well with the experimental data and with those predicted by Mohan and Peng but deviate from those predicted by Huang et al. It is worth noting that, unlike Huang et al.'s, Mohan's and our critical pressures asymptotically reach zero as the molar mass increases to infinity, as should be expected (Tsonopoulos, 1987).

\section*{Conclusions}

The equation of state developed in this work is applicable to small, large, polydisperse, and associating molecules over the whole density range. The equation of state parameters, segment number, segment volume, and segment energy, derived for over 100 real fluids, can be readily extended to other hydrocarbon molecules based on molecular structure and molar mass only.

The association parameters, also derived in this work from bulk experimental data, characterize the strength of specific site-site interactions that lead to molecular association. This way one can separate and quantify the effects of nonspecific segment properties and specific site-site interactions on bulk fluid properties.

Our future work on this equation of state will focus on the phase behavior of binary mixtures and polymer solutions and on the use of spectroscopy for probing molecular interactions leading to association.

\section*{Acknowledgment}

This work is an extension of a joint project on associating fluid theory with the Cornell University group of Professor Keith E. Gubbins. Helpful comments and stimulating discussions with Professor Gubbins, John Walsh, and Karl Johnson are gratefully acknowledged.

\section*{Nomenclature}
$A^{(i)}=$ regression constants, each use defined in the text
$a=$ molar Helmholtz energy (total, res, seg, bond, assoc. etc.), per mole of molecules
$a_{0}=$ segment molar Helmholtz energy (seg), per mole of segments
$C=$ integration constant in eqs 5 and 6
$d=$ temperature-dependent segment diameter, $\AA$
$e / k=$ constant in eq 8
$k=$ Boltzmann's constant $\approx 1.381 \times 10^{-23} \mathrm{~J} / \mathrm{K}$
$m=$ effective number of segments within the molecule (segment number)
$m v^{\circ n}=$ volume occupied by 1 mole of molecules in a closepacked arrangement, mL/mol
$M=$ number of association sites on the molecule
MM = molar mass, g/mol
molar $=$ molar with respect to molecules
$N=$ total number of molecules
$N_{\text {Av }}=$ Avogadro's number $\approx 6.02 \times 10^{23}$ molecules $/ \mathrm{mol}$
$P=$ pressure
$P_{\mathrm{c}}=$ critical pressure, bar
$p^{\text {sat }}=$ saturated vapor pressure
$R=$ gas constant
segment molar = molar with respect to segments
$T=$ temperature, K
$T_{\mathrm{c}}=$ critical temperature, K
$u / k=$ temperature-dependent dispersion energy of interaction between segments, K
$u^{0} / k=$ temperature-independent dispersion energy of interaction between segments, K
$V=$ total volume
$v=$ molar volume,$v^{\text {liq }}=$ liquid molar volume, $\mathrm{mL} / \mathrm{mol}$ of bulk fluid
$v^{\circ}=$ temperature-dependent segment volume, $\mathrm{mL} / \mathrm{mol}$ of segments
$v^{\infty}=$ temperature-independent segment volume, $\mathrm{mL} / \mathrm{mol}$ of segments
$X=$ mole fraction
$X^{\mathrm{A}}=$ monomer mole fraction (mole fraction of molecules NOT bonded at site A)
$Z=P v /(R T)$, compressibility factor
$\kappa^{\mathrm{AB}}=$ volume of interaction between sites A and B
$J^{\mathrm{AB}}=$ "strength of interaction" between sites A and $\mathrm{B}, \AA^{3}$
$\epsilon^{\mathrm{AB}} / k=$ association energy of interaction between sites A and B, K
$\eta=(\pi / 6) \rho_{n} m d^{3}=\left(\pi N_{\mathrm{Av}} / 6\right) \rho m d^{3}$, pure component reduced density, the same for segments AND molecules
$\rho=\rho_{\mathrm{n}} / N_{\mathrm{Av}}$, molar density, mol/ $\AA^{3}$
$\rho_{\mathrm{n}}=$ number density (number of molecules in unit volume), $\AA^{-3}$
$\sigma=$ Lennard-Jones segment diameter (temperature independent), Å
$\Sigma_{\mathrm{A}}=$ summation over all the sites (starting with A)
Superscripts
A, B, C, D, ... = association sites
res $=$ residual
seg $=$ segment
assoc $=$ associating, or due to association
hs = hard sphere
ideal = ideal gas

\section*{Literature Cited}

Alder, B. J.; Young, D. A.; Mark, M. A. J. Chem. Phys. 1972, 56, 3013.

Barker, J. A.; Henderson, D. J. Chem. Phys. 1967, 47, 4714.
Beret, S.; Prausnitz, J. M. AIChE J. 1975, 21, 1123.
Carnahan, N. F.; Starling, K. E. J. Chem. Phys. 1969, 51, 635.
Chapman, W. G.; Gubbins, K. E.; Jackson, G.; Radosz, M. Fluid Phase Equilib. 1989, 52, 31-38.
Chapman, W. G.; Gubbins, K. E.; Jackson, G.; Radosz, M. Ind. Eng. Chem. Res. 1990, 29, 1709.
Chen, S. S., Kreglewski, A. Ber. Bunsen-Ges. Phys. Chem. 1977, 81, 1048.

Cotterman, R. L.; Schwartz, B. J.; Prausnitz, J. M. AIChE J. 1986, 32, 1787.
Flory, P. J. Principles of Polymer Chemistry; Cornell University Press: Ithaca, NY, 1953; pp 318-325.
Huang, S. H.; Radosz, M. Equation of State for Mixtures Containing Small, Large, Polydisperse, and Associating Molecules. Presented at the Annual AIChE Meeting, Chicago, Nov 1990.
Huang, S. H.; Lin, H. M.; Tsai, F. N.; Chao, K. C. Ind. Eng. Chem. Res. 1988, 27, 162.
Kreglewski, A. Equilibrium Properties of Fluids and Fluid Mixtures; The Texas Engineering Experiment Station (TEES) Monograph Series; Texas A \& M University Press: College Station. 1984.

Lee, B. I.; Kesler, M. G. AIChE J. 1975, 21, 510.
Mohan, R.; Peng, D. Y. Correlation for $\mathrm{T}_{\mathrm{c}}, \mathrm{P}_{\mathrm{c}}$ and Acentric Factor of High Molecular Weight n-Paraffins. Presented at the Annual AIChE Meeting, New York, Nov 1987.
Simnick, J. J.; Lin, H. M.; Chao, K. C. Adv. Chem. Ser. 1979, 182, 209.

Tsonopoulos, C. AIChE J. 1987, 33, 2080.
Wertheim, M. S. J. Stat. Phys. 1984, 35, 19, 35.
Wertheim, M. S. J. Stat. Phys. 1986a, 42, 459, 477.
Wertheim, M. S. J. Chem. Phys. 1986b, 85, 2929, 7323.