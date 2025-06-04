# Armourstone Design for Low-Crested Breakwaters in Baie des Bacon

**Author:** Antoine Lefebvre-Brossard  
**Date:** May 30, 2025

## 1. Executive Summary

This report evaluates the armourstone size required for the breakwaters designed by WSP in Baie des Bacon, Longue-Rive [WSP 2020]. We demonstrate that WSP's methodology using Hudson's equation is inappropriate for the low-crested breakwaters proposed for the given scenarios, given that even WSP's cited source discourages the use of this equation for this context [U.S. Army Corps of Engineers 2006, p. VI-7-52]. 

We present armourstone size results both using current recommended formulae for low-crested breakwaters and new ones from the most recent literature, showing that armourstone size can be greatly reduced. Through a sensitivity analysis and model scaling calculations, we recommend conservative armourstone sizes both for the prototype in Baie des Bacon and the model that will be evaluated in the INRS wave channel.

## 2. Introduction

### 2.1 Background

The Baie des Bacon, located in the municipality of Longue-Rive on Québec's Côte-Nord, is increasingly vulnerable to coastal erosion and marine submersion—issues expected to intensify due to climate change. These risks are especially significant for Route 138, the region's main transportation artery, which runs along a low-lying coastal zone characterised by salt marshes, an intertidal area, and a partially armoured shoreline.

Although past storm events have only minimally impacted this corridor, projections suggest that future conditions will increase erosion and flood risk, potentially leading to costly maintenance and temporary road closures.

In response to these challenges, the Ministère des Transports du Québec (MTQ) commissioned WSP to design coastal protection measures for the most vulnerable 1 km stretch of Route 138, between Ruisseau aux Vases and Ruisseau Rouge. WSP proposed a solution based on nature-based infrastructure—specifically, the installation of low-crested "living breakwaters" designed to reduce wave energy and promote habitat restoration along the shoreline.

As part of the design validation process, physical modelling of these breakwaters will be conducted at the INRS wave channel facility. These experiments will focus on the structures' performance under various wave conditions, particularly overtopping behaviour and the role of vegetation in wave dissipation. This testing aims to provide robust data to refine the design parameters and ensure that the breakwaters are both effective and stable under expected field conditions.

This report contributes to that process by critically examining the methodology WSP used to size the armourstone layers of the proposed breakwaters and confirms that using appropriate formulae for low-crested structures results in more economical designs while maintaining structural integrity. It identifies limitations in the application of Hudson's equation for low-crested, overtopped structures and offers alternative approaches from recent literature that provide more accurate and efficient design recommendations.

### 2.2 Objectives

The objectives of this report are to:

1. Demonstrate the inadequacy of Hudson's equation for the design conditions
2. Apply appropriate design methods for low-crested breakwaters
3. Compare armourstone sizes from various established and modern methods
4. Recommend a conservative design size that ensures stability
5. Prepare design parameters for physical model testing

## 3. Design Conditions and Breakwater Characteristics

### 3.1 Hydraulic Conditions

**Table 1: Proposed scenarios [WSP 2020, p. 18]**

| Hydraulic characteristic | Scenario #1<br>Storm (overload) | Scenario #2<br>Storm (design) | Scenario #3<br>Storm (typical) | Scenario #4<br>Average conditions |
|---|---|---|---|---|
| Design water level | 3.6 m<br>(1/100 years) | 3.6 m<br>(1/100 years) | 2.7 m<br>(12 hrs/year) | 1.6 m<br>(PMSMM¹) |
| Sea level rise considered | 0.3 m<br>(2070 projection) | 0.3 m<br>(2070 projection) | 0.0 m<br>(current) | 0.0 m<br>(current) |
| Significant wave height (zone 4), $H_s$ | 2.4 m<br>(1/100 years) | 1.5 m<br>(12 hrs/year) | 1.5 m<br>(12 hrs/year) | 1.0 m<br>(168 hrs/year) |

¹ Pleine mer supérieure de marée moyenne or Higher high water mean tide

Since we want structures that will be resistant to all scenarios, we'll only consider the worst one, scenario #1, for our calculations and modelling.

### 3.2 Breakwater Geometry

Two breakwater types are proposed:

- **Type A (Breakwaters #1, #2, #4, and #5):** Crest elevation 3.5 m
- **Type B (Breakwater #3):** Crest elevation 2.0 m

Both types have armourstone slopes of 1:1.75 with a core structure.

**Table 2: Breakwater physical information**

| Parameter | Value |
|---|---|
| Armourstone, $D_{n50}$ | 1.150 m |
| Slope, cot $\alpha$ | 1:1.75 |
| Rock density, $\rho_s$ | 2 600 kg/m³ |
| Water density, $\rho_w$ | 1 025 kg/m³ |
| Relative buoyant density, $\Delta = \frac{\rho_s-\rho_w}{\rho_w}$ | 1.537 |

### 3.3 Structure Classification

The freeboard analysis shows that both breakwater types function as low-crested structures under most scenarios, with significant negative freeboards indicating fully submerged conditions during storms.

**Table 3: Freeboard ($R_c$) and structure type under each scenario [CIRIA 2007, p. 560]**

| Scenario | Type | Breakwater crest (m) | Water level (m) | Significant wave height $H_s$ (m) | Freeboard $R_c$ (m) | $R_c - H_s$ (m) | Structure type |
|---|---|---|---|---|---|---|---|
| Scenario #1 | A | 3.5 | 3.6 | 2.4 | -0.1 | -2.5 | low-crested submerged |
|  | B | 2.0 | 3.6 | 2.4 | -1.6 | -4.0 | low-crested submerged |
| Scenario #2 | A | 3.5 | 3.6 | 1.5 | -0.1 | -1.6 | low-crested submerged |
|  | B | 2.0 | 3.6 | 1.5 | -1.6 | -3.1 | low-crested submerged |
| Scenario #3 | A | 3.5 | 2.7 | 1.5 | +0.8 | -0.7 | low-crested emergent |
|  | B | 2.0 | 2.7 | 1.5 | -0.7 | -2.2 | low-crested submerged |
| Scenario #4 | A | 3.5 | 1.6 | 1.0 | +1.9 | +0.9 | non- or marginally overtopped |
|  | B | 2.0 | 1.6 | 1.0 | +0.4 | -0.6 | low-crested emergent |

### 3.4 Wave Conditions

Following calculations for wave overtopping, we use wave periods of 3, 6, 9, and 12 seconds.

**Table 4: Wavelengths for studied wave periods**

| Period (s) | Wavelength (m) | h/L |
|---|---|---|
| 3 | 13.17 | 0.273 |
| 6 | 33.25 | 0.108 |
| 9 | 51.89 | 0.069 |
| 12 | 70.12 | 0.051 |

For all periods, the water depth of 3.6 m results in intermediate water conditions (0.05 < h/L < 0.5).

Although the water is of intermediate depth, we assume a Rayleigh distribution for wave heights, giving:

$$H_{2\%} \approx 1.4H_s \tag{1}$$

For the design calculations, we assume that the mean energy wave period $T_{m-1,0}$ is equal to the chosen wave period $T$.

## 4. Critique of WSP Methodology

### 4.1 Replication of WSP Results

WSP seems to use a modified Hudson equation with an additional shape coefficient [WSP 2020, p. 25], but this is unclear as they do not provide their equation and the referenced source does not mention a shape parameter:

$$W_{50} = \frac{\rho_s g H^3}{K_D K_{\Delta}(\frac{\rho_s}{\rho_w} - 1)^3 \cot \alpha}$$

$$D_{n50} = \sqrt[3]{\frac{W_{50}}{\rho_s g}} \tag{2}$$

**Table 5: Parameters defined by WSP**

| Parameter | Value |
|---|---|
| Significant wave height, $H$ | 2.4 m |
| Slope, cot $\alpha$ | 1.75 |
| Rock density, $\rho_s$ | 2 600 kg/m³ |
| Water density, $\rho_w$ | 1 025 kg/m³ |
| Stability coefficient, $K_D$ | 2.0 |
| Shape coefficient, $K_{\Delta}$ | 0.68 |

Using WSP's parameters, the calculation yields:

$$W_{50} = \frac{2600 \cdot 9.81 \cdot 2.4^3}{2.0 \cdot 0.68 \cdot (\frac{2600}{1025} - 1)^3 \cdot 1.75} = 40835 \text{ N}$$

$$D_{n50} = \sqrt[3]{\frac{40835}{2600 \cdot 9.81}} = 1.170 \text{ m} \tag{3}$$

which confirms WSP's result (rounded to the nearest 50 mm).

### 4.2 Limitations of Hudson's Equation

Hudson's equation is inappropriate for this application because:

- It is explicitly invalid for overtopped structures [U.S. Army Corps of Engineers 2006, p. VI-7-52]
- The shape coefficient $K_{\Delta}$ modification lacks clear documentation
- The method ignores critical parameters like wave period and freeboard [CIRIA 2007, p. 600]
- No consideration is given to the different stability requirements for submerged structures [Burcharth et al. 2006]

## 5. Appropriate Design Methods for Low-Crested Structures

### 5.1 Van der Meer Formulae [Van der Meer 1988; Van der Meer and Pilarczyk 1990]

Van der Meer developed formulae specifically for low-crested structures. For shallow water conditions [CIRIA 2007, p. 574]:

**For plunging conditions** ($\xi_{s-1,0} < \xi_{cr}$):

$$\frac{H_s}{\Delta D_{n50}} = c_{pl}P^{0.18}\left(\frac{S_d}{\sqrt{N}}\right)^{0.2}\left(\frac{H_s}{H_{2\%}}\right)(\xi_{s-1,0})^{-0.5}$$

**For surging conditions** ($\xi_{s-1,0} > \xi_{cr}$):

$$\frac{H_s}{\Delta D_{n50}} = c_s P^{-0.13}\left(\frac{S_d}{\sqrt{N}}\right)^{0.2}\left(\frac{H_s}{H_{2\%}}\right)\sqrt{\cot \alpha(\xi_{s-1,0})^P}$$

$$\xi_{cr} = \left(\frac{c_{pl}}{c_s}P^{0.31}\sqrt{\cot \alpha}\right)^{\frac{1}{P+0.5}} \tag{4}$$

Where:
- $H_s$: significant wave height at the toe of the structure (m)
- $H_{2\%}$: wave height exceeded by 2% of the incident waves at the toe (m)
- $\Delta$: relative buoyant density, $\frac{\rho_s - \rho_w}{\rho_w}$
- $P$: permeability coefficient
- $N$: number of incident waves at the toe
- $\xi_{s-1,0}$: surf similarity parameter using energy wave period
- $c_{pl}$: 8.4
- $c_s$: 1.3

For low-crested structures, Van der Meer proposes using $r_D D_{n50}$ instead of $D_{n50}$ [CIRIA 2007, p. 600] with:

$$r_D = \left(1.25 - 4.8\frac{R_c}{H_s}\sqrt{\frac{s_{op}}{2\pi}}\right)^{-1} \tag{5}$$

This is only applicable when:

$$0 < \frac{R_c}{H_s}\sqrt{\frac{s_{op}}{2\pi}} < 0.052$$

$$s_{op} = \frac{H_s}{L} \tag{6}$$

Since for most scenarios, the breakwaters are submerged, the freeboard $R_c$ will be negative and this reduction can't be used.

Assuming a permeability coefficient of 0.4 gives:

**Table 6: Stone diameter using Van der Meer formulae**

| Period (s) | $D_{n50}$ (m) | Wave conditions |
|---|---|---|
| 3 | 0.627 | plunging |
| 6 | 0.887 | plunging |
| 9 | 1.086 | plunging |
| 12 | 0.989 | surging |

### 5.2 Van Gent Formula [Van Gent, Smale, and Kuiper 2003]

Van Gent et al. proposed a simplified formula for structures with cores:

$$\frac{H_s}{\Delta D_{n50}} = 1.75\left(1 + \frac{D_{n50-core}}{D_{n50}}\right)\left(\frac{S}{\sqrt{N}}\right)^{0.2}(\cot \alpha)^{0.5} \tag{7}$$

Following WSP's methodology where core stones are 1/100 the mass of armour stones, this becomes:

$$D_{n50} = \frac{H_s}{1.75\Delta(1 + 100^{-1/3})}\left(\frac{S}{\sqrt{N}}\right)^{0.2}(\cot \alpha)^{0.5} \tag{8}$$

Since this formula depends neither on wave period nor crest height, it gives a single stone size of $D_{n50} = 0.964$ m.

### 5.3 Burcharth Formula [Burcharth et al. 2006]

Burcharth et al. proposed the following formula for "no-damage" low-crested breakwaters:

$$\frac{H_s}{\Delta D_{n50}} = 0.06\left(\frac{R_c}{D_{n50}}\right)^2 - 0.23\frac{R_c}{D_{n50}} + 1.36, \quad -3 < \frac{R_c}{D_{n50}} < 2 \tag{9}$$

**Table 7: Stone diameter using Burcharth formula**

| Breakwater type | $D_{n50}$ (m) |
|---|---|
| A | 1.091 |
| B | 0.824 |

### 5.4 Scaravaglione Modifications [Scaravaglione et al. 2025]

Scaravaglione et al. recently revised formulae for shallow water conditions:

**Modified Van Gent formula:**

$$D_{n50} = \frac{H_s}{\Delta}\frac{1}{3.3\sqrt{\cot \alpha}(1 + 100^{-1/3})}\left(\frac{L}{H_s}\right)^{0.1}\frac{\sqrt{N}}{S^{0.2}} \tag{10}$$

**Modified Eldrup and Andersen formula:**

$$D_{n50} = \frac{H_s}{\Delta}\frac{1}{3.55(1 + 100^{-0.3/3})^{0.6}}\frac{N^{0.1}}{(\cot \alpha)^{-0.33}S^{-0.167}}\left(\frac{L}{H_s}\right)^{0.05} \tag{11}$$

**Table 8: Stone diameter using modified formulae by Scaravaglione et al. 2025**

| Period (s) | Van Gent $D_{n50}$ (m) | Eldrup and Andersen $D_{n50}$ (m) |
|---|---|---|
| 3 | 0.606 | 0.528 |
| 6 | 0.665 | 0.553 |
| 9 | 0.695 | 0.565 |
| 12 | 0.717 | 0.574 |

## 6. Comparison of Methods

**Table 9: All armourstone size results**
*(When there are two numbers, the first is for type A and the second type B)*

| Period (s) | Hudson (m) | Van der Meer (m) | Van Gent (m) | Burcharth (m) | Modified Van Gent (m) | Modified Eldrup and Andersen (m) |
|---|---|---|---|---|---|---|
| 3 | 1.170 | 0.627 | 0.964 | 1.091/0.824 | 0.606 | 0.528 |
| 6 |  | 0.887 |  |  | 0.665 | 0.553 |
| 9 |  | 1.086 |  |  | 0.695 | 0.565 |
| 12 |  | 0.989 |  |  | 0.717 | 0.574 |

While there is large variation in armourstone size depending on the formula, especially when comparing the most recent modified versions by Scaravaglione et al., the original Hudson equation used by WSP was overestimating the needed stone size by a fair margin.

## 7. Sensitivity Analysis

To understand the robustness of our design calculations and identify which parameters have the most significant impact on armourstone sizing, we conducted a sensitivity analysis on four key variables:

- Permeability coefficient
- Significant wave height
- Water depth
- Stone density

Each parameter was varied by ±10% and ±20% from its baseline value to assess the impact on the calculated $D_{n50}$ values.

### Key Findings

1. **Stone density** has the most pronounced effect on all methods, with approximately linear inverse relationships. A 20% decrease in stone density results in about a 50% increase in required stone size for most methods.

2. **Significant wave height** shows a direct relationship, as expected. A 20% increase in wave height results in approximately 20% increase in required stone size.

3. **Water depth** primarily affects the Burcharth formula for Type B breakwaters due to its dependence on freeboard, with a change of around 10% for a 20% change in water depth. Other methods show minimal sensitivity.

4. **Permeability** only affects the Van der Meer formula. The effect is relatively minor, with a 20% change in permeability resulting in less than 6% change in stone size.

These results highlight the critical importance of accurate stone density determination and suggest that conservative estimates should be used for this parameter.

## 8. Model Scaling

The model scaling is based on the established geometric scale ratio of 1:2.42, corresponding to a reduction factor of 0.413. This scale factor was determined from wave channel constraints and is appropriate for investigating armourstone stability under the design wave conditions.

### 8.1 Scaled Armourstone Sizes

Following standard practice of using a 1/10 mass ratio between successive layers:

$$D_{n50-filter} = 10^{-1/3}D_{n50-armour} \approx 0.464D_{n50-armour}$$

$$D_{n50-core} = 10^{-1/3}D_{n50-filter} \approx 0.215D_{n50-armour} \tag{12}$$

**Table 10: Prototype and model stone sizes for breakwater Type B**

| Design Method | Prototype $D_{n50}$ (m) |  | Model $D_{n50}$ (m) |  |
|---|---|---|---|---|
|  | Armour | Filter/Core | Armour | Filter/Core |
| Van der Meer (6s period) | 0.887 | 0.411/0.191 | 0.366 | 0.170/0.079 |
| Van Gent | 0.964 | 0.447/0.207 | 0.398 | 0.185/0.086 |
| Burcharth | 0.824 | 0.382/0.177 | 0.340 | 0.158/0.073 |
| Modified Van Gent | 0.606–0.717 | 0.281–0.333/0.130–0.154 | 0.250–0.296 | 0.116–0.137/0.054–0.064 |
| Modified Eldrup and Andersen | 0.528–0.574 | 0.245–0.266/0.113–0.123 | 0.218–0.237 | 0.101–0.110/0.047–0.051 |

## 9. Conclusion and Recommendations

### 9.1 Conclusion

This analysis demonstrates that WSP's original application of Hudson's equation for the Baie des Bacon low-crested breakwaters significantly overestimated the required armourstone size. While WSP calculated $D_{n50} = 1.170$ m, our evaluation using appropriate low-crested breakwater methodologies indicates that much smaller stones can provide adequate stability:

- Van der Meer formula: $D_{n50} = 0.887$ m (24% reduction)
- Van Gent formula: $D_{n50} = 0.964$ m (18% reduction)
- Burcharth formulae: $D_{n50} = 0.824 - 1.091$ m (7-30% reduction)
- Recent modified approaches: $D_{n50} = 0.528 - 0.717$ m (39-55% reduction)

The sensitivity analysis reveals that stone density is the most critical parameter affecting all design methods, emphasising the importance of accurate material property determination. The proposed model scale factor of 0.413 (1:2.42 geometric scale) is appropriate for validating armourstone stability under the design conditions.

### 9.2 Recommendations

#### 9.2.1 Design Recommendations

1. **Stone sizing:** Use the Van der Meer formula with 6-second wave period as the baseline design:
   - Armourstone: $D_{n50} = 0.887$ m
   - Filter stone: $D_{n50} = 0.411$ m (mass = 1/10 of armourstone)
   - Core stone: $D_{n50} = 0.191$ m (mass = 1/100 of armourstone)

2. **Conservative approach:** Apply safety factors to account for construction variability and long-term performance.

3. **Stone sourcing:** Prioritise stone density determination and quality control, given the significant sensitivity of all design methods to material properties.

4. **Alternative evaluation:** Consider the potential cost savings offered by recent modified approaches, while acknowledging their newer validation basis.

#### 9.2.2 Model Testing Focus

For the physical model testing at INRS:

1. **Scale factor:** The 0.413 scale factor (1:2.42 geometric scale) is appropriate for validation under the design conditions.

2. **Stone sizes:** Use the conservative Van der Meer baseline in model scale:
   - Armourstone: $D_{n50} = 0.366$ m
   - Filter stone: $D_{n50} = 0.170$ m
   - Core stone: $D_{n50} = 0.079$ m

3. **Validation scope:** The model testing will validate the armourstone size requirements under the specified wave conditions and water depths.

## References

1. Burcharth, Hans F et al. (2006). "Structural stability of detached low crested breakwaters". *Coastal Engineering* 53.4, pp. 381–394.

2. CIRIA (2007). *The Rock Manual. The use of rock in hydraulic engineering*. 2nd edition. CIRIA, CUR, CETMEF.

3. Scaravaglione, Giulio et al. (2025). "The influence of shallow water on rock armour stability". *Coastal Engineering* 197, p. 104657.

4. U.S. Army Corps of Engineers (2006). "Coastal Engineering Manual, Engineer Manual 1110-2-1100". *USACE Publications*.

5. Van der Meer, Jentsje W (1988). *Rock slopes and gravel beaches under wave attack*. Vol. 396. Delft hydraulics Delft, Netherlands.

6. Van der Meer, Jentsje W and Krystian W Pilarczyk (1990). "Stability of low-crested and reef breakwaters". *Coastal Engineering 1990*, pp. 1375–1388.

7. Van Gent, Marcel RA, Alfons J Smale, and Coen Kuiper (2003). "Stability of rock slopes with shallow foreshores". *Coastal structures 2003*, pp. 100–112.

8. WSP (Aug. 2020). *Analyse de solutions à l'érosion et à la submersion côtière dans la Baie des Bacon*. Tech. rep. 181-09013-00. WSP.

## Acronyms

- **PMSMM** - Pleine mer supérieure de marée moyenne (Higher high water mean tide - HHWMT)
- **PMSGM** - Pleine mer supérieure de grande marée (Higher high water spring tide - HHWST)